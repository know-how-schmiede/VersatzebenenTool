"""Fusion command for creating evenly spaced planes and optional sketches."""

import math
import hashlib
import importlib.util
from pathlib import Path
import traceback

import adsk.core
import adsk.fusion

def _load_local_module(name):
    """Load our own file even when Fusion shares imports between add-ins.

    Use an isolated module name and reload on each add-in start so updates do
    not reuse cached versions or translations from a previous run.
    """
    directory = Path(__file__).resolve().parent
    namespace = hashlib.sha256(str(directory).encode('utf-8')).hexdigest()[:16]
    spec = importlib.util.spec_from_file_location(
        f'_versatzebenentool_{namespace}_{name}', directory / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    # These self-contained modules need no global sys.modules registration.
    spec.loader.exec_module(module)
    return module


VERSION = _load_local_module('version').VERSION
_localization = _load_local_module('localization')
initialize = _localization.initialize
tr = _localization.tr

COMMAND_ID = 'cmdCreateOffsetPlanes'
PANEL_ID = 'SolidCreatePanel'
RESOURCE_DIR = Path(__file__).resolve().parent / 'Resources'
BANNER_PATH = RESOURCE_DIR / 'banner.png'
BANNER_WIDTH = 2172
DEFAULT_NAME = 'vref'
MIN_PLANES, MAX_PLANES = 1, 50

# Fusion requires strong references to Python event handlers.
handlers = []
command_handlers = {}


def _connect(event, handler, references):
    event.add(handler)
    references.append(handler)


def _report_error(context):
    app = adsk.core.Application.get()
    if app and app.userInterface:
        app.userInterface.messageBox(
            tr('error', context=context, details=traceback.format_exc()))


def _remove_command(ui):
    panel = ui.allToolbarPanels.itemById(PANEL_ID)
    control = panel.controls.itemById(COMMAND_ID) if panel else None
    if control:
        control.deleteMe()
    definition = ui.commandDefinitions.itemById(COMMAND_ID)
    if definition:
        definition.deleteMe()
    handlers.clear()
    command_handlers.clear()


def run(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        initialize(app)
        _remove_command(ui)  # Restarting must not duplicate controls or handlers.
        panel = ui.allToolbarPanels.itemById(PANEL_ID)
        if not panel:
            raise RuntimeError(tr('panel_unavailable'))
        definition = ui.commandDefinitions.addButtonDefinition(
            COMMAND_ID, f"{tr('command')} (v{VERSION})",
            tr('description'), str(RESOURCE_DIR / 'MyIcons'))
        _connect(definition.commandCreated, CommandCreatedHandler(), handlers)
        panel.controls.addCommand(definition)
        if adsk.fusion.Design.cast(app.activeProduct):
            definition.execute()
    except Exception:
        _report_error('run')


def stop(context):
    try:
        _remove_command(adsk.core.Application.get().userInterface)
    except Exception:
        _report_error('stop')


def _is_planar(entity):
    if adsk.fusion.ConstructionPlane.cast(entity):
        return True
    face = adsk.fusion.BRepFace.cast(entity)
    return bool(face and adsk.core.Plane.cast(face.geometry))


def _has_history(design):
    return design.designType == adsk.fusion.DesignTypes.ParametricDesignType


def _valid_inputs(inputs):
    selection = inputs.itemById('planeSelection')
    offset = inputs.itemById('planeOffset')
    count = inputs.itemById('numPlanes').value
    size = inputs.itemById('planeDisplaySize')
    return (selection.selectionCount == 1
            and _is_planar(selection.selection(0).entity)
            and MIN_PLANES <= count <= MAX_PLANES
            and offset.isValidExpression
            and math.isfinite(offset.value)
            and size.isValidExpression
            and math.isfinite(size.value) and size.value > 0)


def _size_plane(plane, minimum_size):
    """Enlarge the display rectangle, preserving its center and existing size.

    Dimensions are in Fusion internal length units (cm). Name length is a
    heuristic: actual label visibility also depends on zoom and Fusion settings.
    """
    bounds = plane.displayBounds
    low, high = bounds.minPoint, bounds.maxPoint
    center_x, center_y = (low.x + high.x) / 2, (low.y + high.y) / 2
    width = max(high.x - low.x, minimum_size, len(plane.name) * minimum_size / 20)
    height = max(high.y - low.y, minimum_size)
    plane.displayBounds = adsk.core.BoundingBox2D.create(
        adsk.core.Point2D.create(center_x - width / 2, center_y - height / 2),
        adsk.core.Point2D.create(center_x + width / 2, center_y + height / 2))


def _create_planes(design, reference, count, spacing, plane_name, sketch_name,
                   create_sketches, group, show_planes=True, display_size=10.0):
    """Preserve zero offset for the first plane; Fusion owns the transaction."""
    root = design.rootComponent
    planes = root.constructionPlanes
    timeline = design.timeline if group and _has_history(design) else None
    start_index = timeline.markerPosition if timeline else None
    created_planes = []

    for index in range(count):
        plane_input = planes.createInput()
        if not plane_input.setByOffset(
                reference, adsk.core.ValueInput.createByReal(index * spacing)):
            raise RuntimeError(tr('plane_failed', number=index + 1))
        plane = planes.add(plane_input)
        if not plane:
            raise RuntimeError(tr('plane_failed', number=index + 1))
        plane.name = f'{plane_name} {index + 1}'
        created_planes.append(plane)
        if create_sketches:
            sketch = root.sketches.add(plane)
            sketch.name = f'{sketch_name} {index + 1}'

    grouped = False
    if timeline:
        end_index = timeline.markerPosition - 1
        if end_index >= start_index:
            timeline_group = timeline.timelineGroups.add(start_index, end_index)
            if not timeline_group:
                raise RuntimeError(tr('group_failed'))
            timeline_group.name = tr('group_name', name=plane_name)
            grouped = True
    # Sketch creation can hide its support plane. Apply the requested state
    # after all sketches and timeline operations, including the parent folder.
    if show_planes:
        root.isConstructionFolderLightBulbOn = True
    for plane in created_planes:
        _size_plane(plane, display_size)
        plane.isLightBulbOn = show_planes
    return grouped


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                app.userInterface.messageBox(tr('design_required'))
                return

            command = args.command
            command.setDialogInitialSize(480, 560)
            inputs = command.commandInputs
            if BANNER_PATH.is_file():
                banner = inputs.addImageCommandInput('banner', '', str(BANNER_PATH))
                banner.isFullWidth = True
                banner.scaleFactor = 420 / BANNER_WIDTH

            selection = inputs.addSelectionInput(
                'planeSelection', tr('select_plane'), tr('select_hint'))
            selection.addSelectionFilter('PlanarFaces')
            selection.addSelectionFilter('ConstructionPlanes')
            selection.setSelectionLimits(1, 1)
            inputs.addIntegerSpinnerCommandInput(
                'numPlanes', tr('count'), MIN_PLANES, MAX_PLANES, 1, 5)
            inputs.addValueInput(
                'planeOffset', tr('offset'), design.unitsManager.defaultLengthUnits,
                adsk.core.ValueInput.createByReal(1.0))
            inputs.addBoolValueInput('createSketches', tr('sketches'), True, '', False)
            inputs.addBoolValueInput('showPlanes', tr('show_planes'), True, '', True)
            display_size = inputs.addValueInput(
                'planeDisplaySize', tr('display_size'), design.unitsManager.defaultLengthUnits,
                adsk.core.ValueInput.createByReal(10.0))
            display_size.tooltip = tr('display_size_hint')
            inputs.addStringValueInput('planeName', tr('plane_name'), DEFAULT_NAME)
            sketch_name = inputs.addStringValueInput(
                'sketchName', tr('sketch_name'), DEFAULT_NAME)
            sketch_name.isEnabled = False
            group = inputs.addBoolValueInput(
                'groupInHistory', tr('group'), True, '', False)
            group.isEnabled = _has_history(design)
            group.tooltip = tr('history_required')

            references = []
            # Each dialog owns its handlers until its destroy event.
            key = id(references)
            command_handlers[key] = references
            _connect(command.destroy, CommandDestroyHandler(key), references)
            _connect(command.execute, CommandExecuteHandler(), references)
            _connect(command.validateInputs, ValidateInputsHandler(), references)
            _connect(command.inputChanged, InputChangedHandler(), references)
        except Exception:
            _report_error('CommandCreatedHandler')


class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            if args.input.id == 'createSketches':
                args.inputs.itemById('sketchName').isEnabled = args.input.value
        except Exception:
            _report_error('InputChangedHandler')


class ValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def notify(self, args):
        try:
            args.areInputsValid = _valid_inputs(args.inputs)
        except Exception:
            args.areInputsValid = False


class CommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self, key):
        super().__init__()
        self.key = key

    def notify(self, args):
        command_handlers.pop(self.key, None)


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                raise ValueError(tr('design_required'))
            inputs = args.firingEvent.sender.commandInputs
            if not _valid_inputs(inputs):
                raise ValueError(tr('invalid_inputs'))

            count = inputs.itemById('numPlanes').value
            create_sketches = inputs.itemById('createSketches').value
            grouped = _create_planes(
                design, inputs.itemById('planeSelection').selection(0).entity,
                count, inputs.itemById('planeOffset').value,
                inputs.itemById('planeName').value.strip() or DEFAULT_NAME,
                inputs.itemById('sketchName').value.strip() or DEFAULT_NAME,
                create_sketches, inputs.itemById('groupInHistory').value,
                inputs.itemById('showPlanes').value,
                inputs.itemById('planeDisplaySize').value)
            app.userInterface.messageBox(
                tr('success', count=count)
                + (tr('sketch_success') if create_sketches else '')
                + (tr('group_success') if grouped else ''))
        except Exception:
            # Mark the command failed so Fusion can abort its transaction.
            args.executeFailed = True
            args.executeFailedMessage = tr(
                'error', context=tr('command'), details=traceback.format_exc())

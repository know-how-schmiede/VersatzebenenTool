"""Regression tests for the active command using Fusion API doubles."""

import importlib.util
from pathlib import Path
import struct
import sys
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
ADDIN = ROOT / 'fusion_addin/VersatzebenenTool'


class Castable:
    @classmethod
    def cast(cls, value):
        return value if isinstance(value, cls) else None


class Plane(Castable):
    pass


class ConstructionPlane(Castable):
    pass


class BRepFace(Castable):
    def __init__(self, geometry):
        self.geometry = geometry


class CommandTests(unittest.TestCase):
    def setUp(self):
        adsk = ModuleType('adsk')
        adsk.core = ModuleType('adsk.core')
        adsk.fusion = ModuleType('adsk.fusion')
        for name in ('CommandCreatedEventHandler', 'CommandEventHandler',
                     'InputChangedEventHandler', 'ValidateInputsEventHandler'):
            setattr(adsk.core, name, type(name, (), {}))
        self.app = NS(userInterface=MagicMock(), activeProduct=None)
        adsk.core.Application = NS(get=lambda: self.app)
        adsk.core.Plane = Plane
        adsk.core.ValueInput = NS(createByReal=lambda value: value)
        adsk.fusion.ConstructionPlane = ConstructionPlane
        adsk.fusion.BRepFace = BRepFace
        adsk.fusion.Design = NS(cast=lambda value: value)
        adsk.fusion.DesignTypes = NS(ParametricDesignType=1)
        package = ModuleType('test_addin')
        package.__path__ = [str(ADDIN)]
        self.modules = patch.dict(sys.modules, {
            'adsk': adsk, 'adsk.core': adsk.core, 'adsk.fusion': adsk.fusion,
            'test_addin': package,
        })
        self.modules.start()
        self.addCleanup(self.modules.stop)
        spec = importlib.util.spec_from_file_location(
            'test_addin.command', ADDIN / 'VersatzebenenTool.py')
        self.command = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.command)

    def design(self, history=True):
        timeline = NS(markerPosition=3, count=20, timelineGroups=MagicMock())
        planes, sketches = MagicMock(), MagicMock()

        def add_plane(_):
            timeline.markerPosition += 1
            return NS()

        def add_sketch(_):
            timeline.markerPosition += 1
            return NS()

        planes.add.side_effect = add_plane
        sketches.add.side_effect = add_sketch
        design = NS(designType=1 if history else 0,
                    rootComponent=NS(constructionPlanes=planes, sketches=sketches),
                    unitsManager=NS(defaultLengthUnits='mm'))
        if history:
            design.timeline = timeline
        return design, timeline

    def test_standalone_load_ignores_other_addins_modules(self):
        foreign_version = ModuleType('version')  # InsertWizard has no VERSION.
        foreign_localization = ModuleType('localization')
        with patch.dict(sys.modules, {'version': foreign_version,
                                      'localization': foreign_localization}):
            spec = importlib.util.spec_from_file_location(
                'VersatzebenenTool', ADDIN / 'VersatzebenenTool.py')
            standalone = importlib.util.module_from_spec(spec)
            self.assertFalse(standalone.__package__)
            spec.loader.exec_module(standalone)
            self.assertEqual(standalone.VERSION, self.command.VERSION)
            self.assertEqual(standalone.tr('command'), 'Create offset planes')
            self.assertIs(sys.modules['version'], foreign_version)
            self.assertIs(sys.modules['localization'], foreign_localization)

    def test_reload_does_not_reuse_previous_localization_state(self):
        self.command._localization._language = 'de'
        fresh = self.command._load_local_module('localization')
        self.assertEqual(fresh.tr('command'), 'Create offset planes')
        self.assertIsNot(fresh, self.command._localization)

    def test_planar_faces_are_passed_to_offset_without_casting_to_plane(self):
        design, timeline = self.design()
        reference = BRepFace(Plane())
        self.assertTrue(self.command._is_planar(reference))
        self.assertFalse(self.command._is_planar(BRepFace(object())))
        grouped = self.command._create_planes(
            design, reference, 3, -2, 'P', 'S', True, True)
        calls = design.rootComponent.constructionPlanes.createInput.return_value.setByOffset.call_args_list
        self.assertEqual([call.args for call in calls],
                         [(reference, 0), (reference, -2), (reference, -4)])
        self.assertEqual(design.rootComponent.sketches.add.call_count, 3)
        timeline.timelineGroups.add.assert_called_once_with(3, 8)
        self.assertTrue(grouped)

    def test_direct_modeling_never_accesses_timeline(self):
        design, _ = self.design(history=False)
        self.assertFalse(self.command._create_planes(
            design, ConstructionPlane(), 1, 0, 'P', 'S', False, True))
        design.rootComponent.sketches.add.assert_not_called()

    def test_failed_plane_definition_stops_creation(self):
        design, _ = self.design()
        planes = design.rootComponent.constructionPlanes
        planes.createInput.return_value.setByOffset.return_value = False
        with self.assertRaises(RuntimeError):
            self.command._create_planes(design, ConstructionPlane(), 2, 1, 'P', 'S', False, False)
        planes.add.assert_not_called()

    def inputs(self):
        values = {
            'planeSelection': NS(selectionCount=1, selection=lambda _: NS(entity=ConstructionPlane())),
            'numPlanes': NS(value=5),
            'planeOffset': NS(value=1, isValidExpression=True),
        }
        return NS(itemById=values.get), values

    def test_validation_rejects_missing_selection_bad_count_and_nonfinite_offset(self):
        inputs, values = self.inputs()
        self.assertTrue(self.command._valid_inputs(inputs))
        for value in (float('nan'), float('inf')):
            values['planeOffset'].value = value
            self.assertFalse(self.command._valid_inputs(inputs))
        values['planeOffset'].value = -1
        self.assertTrue(self.command._valid_inputs(inputs))
        values['numPlanes'].value = 51
        self.assertFalse(self.command._valid_inputs(inputs))
        values['numPlanes'].value = 1
        values['planeSelection'].selectionCount = 0
        self.assertFalse(self.command._valid_inputs(inputs))
        values['planeSelection'].selectionCount = 1
        values['planeOffset'].isValidExpression = False
        self.assertFalse(self.command._valid_inputs(inputs))

    def test_execution_failure_requests_transaction_abort(self):
        args = NS(executeFailed=False)
        self.command.CommandExecuteHandler().notify(args)
        self.assertTrue(args.executeFailed)
        self.assertIn('Open a Fusion design', args.executeFailedMessage)

    def execution_args(self):
        inputs, values = self.inputs()
        values.update({
            'createSketches': NS(value=True),
            'planeName': NS(value='  '),
            'sketchName': NS(value=' Drawing '),
            'groupInHistory': NS(value=True),
        })
        return NS(firingEvent=NS(sender=NS(commandInputs=inputs)), executeFailed=False)

    def test_geometry_failure_is_reported_as_failed_transaction(self):
        self.app.activeProduct, _ = self.design()
        planes = self.app.activeProduct.rootComponent.constructionPlanes
        planes.add.side_effect = RuntimeError('Geometry failure')
        args = self.execution_args()
        self.command.CommandExecuteHandler().notify(args)
        self.assertTrue(args.executeFailed)
        self.assertIn('Geometry failure', args.executeFailedMessage)
        self.app.userInterface.messageBox.assert_not_called()

    def test_execute_preserves_name_defaults_and_reports_only_actual_grouping(self):
        self.app.activeProduct, _ = self.design(history=False)
        args = self.execution_args()
        with patch.object(self.command, '_create_planes', return_value=False) as create:
            self.command.CommandExecuteHandler().notify(args)
        self.assertFalse(args.executeFailed)
        self.assertEqual(create.call_args.args[4:6], ('vref', 'Drawing'))
        message = self.app.userInterface.messageBox.call_args.args[0]
        self.assertIn('5 offset planes', message)
        self.assertNotIn('grouped', message)

    def test_repeated_start_does_not_accumulate_handlers(self):
        for _ in range(2):
            self.command.run(None)
            self.assertEqual(len(self.command.handlers), 1)
        self.app.userInterface.messageBox.assert_not_called()
        definition = self.app.userInterface.commandDefinitions.addButtonDefinition.return_value
        definition.execute.assert_not_called()  # No design is open.

    def test_banner_and_dialog_handlers(self):
        self.app.activeProduct, _ = self.design(history=False)
        command = MagicMock()
        self.command.CommandCreatedHandler().notify(NS(command=command))
        self.app.userInterface.messageBox.assert_not_called()
        inputs = command.commandInputs
        inputs.addImageCommandInput.assert_called_once_with(
            'banner', '', str(self.command.BANNER_PATH))
        image = inputs.addImageCommandInput.return_value
        self.assertTrue(image.isFullWidth)
        with self.command.BANNER_PATH.open('rb') as stream:
            header = stream.read(24)
        self.assertEqual(header[:8], b'\x89PNG\r\n\x1a\n')
        width, height = struct.unpack('>II', header[16:24])
        self.assertAlmostEqual(width * image.scaleFactor, 420)
        self.assertAlmostEqual(height * image.scaleFactor, 140)
        self.assertEqual(inputs.addValueInput.call_args.args[2], 'mm')
        self.assertFalse(inputs.addBoolValueInput.return_value.isEnabled)
        self.assertEqual(len(self.command.command_handlers), 1)
        destroy = command.destroy.add.call_args.args[0]
        destroy.notify(NS())
        self.assertFalse(self.command.command_handlers)

    def test_cleanup_removes_control_before_definition_and_releases_handlers(self):
        ui = self.app.userInterface
        order = []
        ui.allToolbarPanels.itemById.return_value.controls.itemById.return_value.deleteMe.side_effect = lambda: order.append('control')
        ui.commandDefinitions.itemById.return_value.deleteMe.side_effect = lambda: order.append('definition')
        self.command.handlers.append(object())
        self.command.command_handlers[1] = [object()]
        self.command._remove_command(ui)
        self.assertEqual(order, ['control', 'definition'])
        self.assertFalse(self.command.handlers)
        self.assertFalse(self.command.command_handlers)


if __name__ == '__main__':
    unittest.main()

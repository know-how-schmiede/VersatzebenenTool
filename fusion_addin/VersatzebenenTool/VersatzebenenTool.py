import adsk.core, adsk.fusion, adsk.cam, traceback

try:
    from .version import VERSION
    from .localization import initialize, tr
except ImportError:
    from version import VERSION
    from localization import initialize, tr


COMMAND_ID = 'cmdCreateOffsetPlanes'


# Globalvariablen, um Referenzen auf EventHandler zu behalten.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        initialize(app)

        # Eine neue Befehl-Definition anlegen.
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            COMMAND_ID,
            f"{tr('command')} (v{VERSION})",
            tr('description'),
            'Resources/MyIcons/'             # Resource Folder Name (z.B. MyIcons/)
        )

        # EventHandler für die Aktivierung des Befehls registrieren.
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        createPanel.controls.addCommand(cmdDef)

        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        # Den Befehl automatisch starten.
        cmdDef.execute()

    except:
        if ui:
            ui.messageBox(tr('error', context='run', details=traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Befehl-Definition entfernen, wenn vorhanden.
        cmdDef = ui.commandDefinitions.itemById(COMMAND_ID)
        if cmdDef:
            cmdDef.deleteMe()

        # CommandControl entfernen, wenn vorhanden.
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        ctrl = createPanel.controls.itemById(COMMAND_ID)
        if ctrl:
            ctrl.deleteMe()

    except:
        if ui:
            ui.messageBox(tr('error', context='stop', details=traceback.format_exc()))


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """ EventHandler, der aufgerufen wird, sobald das Kommando erstellt wurde. """
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isPositionDependent = True

            # Eingabeelemente definieren.
            inputs = cmd.commandInputs

            # 1) Auswahl der Referenzebene
            selInput = inputs.addSelectionInput(
                'planeSelection',
                tr('select_plane'),
                tr('select_hint')
            )
            # Beschränken auf Ebenen oder planare Flächen
            selInput.addSelectionFilter('PlanarFaces')
            selInput.addSelectionFilter('ConstructionPlanes')
            selInput.setSelectionLimits(1,1)

            # 2) Anzahl der zu erstellenden Versatzebenen
            numPlanesInput = inputs.addIntegerSpinnerCommandInput(
                'numPlanes',
                tr('count'),
                1, 50, 1, 5
            )

            # 3) Versatz pro Ebene
            offsetValueInput = inputs.addValueInput(
                'planeOffset',
                tr('offset'),
                'cm',  # Einheit kann beliebig gewählt werden (mm, cm, etc.)
                adsk.core.ValueInput.createByReal(1.0)
            )

            # 4) Boolean-Checkbox, ob gleichzeitig eine Skizze auf jeder neuen Ebene erstellt werden soll
            createSketchInput = inputs.addBoolValueInput(
                'createSketches',
                tr('sketches'),
                True,   # Symboltyp: CheckBox
                '',
                False   # Standardwert: False
            )

            # 5) Name der Versatzebenen
            planeNameInput = inputs.addStringValueInput(
                'planeName',
                tr('plane_name'),
                'vref'  # Standardwert
            )

            # 6) Name der Skizze
            sketchNameInput = inputs.addStringValueInput(
                'sketchName',
                tr('sketch_name'),
                'vref'  # Standardwert
            )

            # 7) Boolean-Checkbox, ob die neuen Objekte in der Timeline gruppiert werden sollen
            groupInHistoryInput = inputs.addBoolValueInput(
                'groupInHistory',
                tr('group'),
                True,    # Symboltyp: CheckBox
                '',
                False    # Standardwert: False
            )

            # Reaktion auf "OK"/"Ausführen"
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(tr('error', context='CommandCreatedHandler', details=traceback.format_exc()))


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    """ EventHandler, der beim Klick auf OK (Ausführen) aufgerufen wird. """
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            design = adsk.fusion.Design.cast(app.activeProduct)

            cmd = args.firingEvent.sender
            inputs = cmd.commandInputs

            selInput = adsk.core.SelectionCommandInput.cast(inputs.itemById('planeSelection'))
            numPlanesInput = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('numPlanes'))
            offsetValueInput = adsk.core.ValueCommandInput.cast(inputs.itemById('planeOffset'))
            createSketchInput = adsk.core.BoolValueCommandInput.cast(inputs.itemById('createSketches'))
            planeNameInput = adsk.core.StringValueCommandInput.cast(inputs.itemById('planeName'))
            sketchNameInput = adsk.core.StringValueCommandInput.cast(inputs.itemById('sketchName'))
            groupInHistoryInput = adsk.core.BoolValueCommandInput.cast(inputs.itemById('groupInHistory'))

            # Eingegebene Werte auslesen
            selectedEntity = selInput.selection(0).entity
            numPlanes = numPlanesInput.value
            offsetVal = offsetValueInput.value  # Realwert
            createSketches = createSketchInput.value

            # Falls Eingaben leer sind, Standardwerte verwenden.
            planeName = planeNameInput.value.strip() or 'vref'
            sketchName = sketchNameInput.value.strip() or 'vref'

            # Soll in der Timeline gruppiert werden?
            shouldGroup = groupInHistoryInput.value

            rootComp = design.rootComponent
            constructions = rootComp.constructionPlanes

            # Prüfen, ob eine Fläche oder eine bereits vorhandene Baugruppen-Ebene ausgewählt wurde
            if isinstance(selectedEntity, adsk.fusion.ConstructionPlane):
                basePlane = selectedEntity
            else:
                # Falls eine (planare) Fläche ausgewählt wurde -> in ConstructionPlane konvertieren
                basePlane = adsk.fusion.ConstructionPlane.cast(selectedEntity)

            if not basePlane:
                ui.messageBox(tr('invalid_plane'))
                return

            # Vor dem Erstellen den Startpunkt für den Timeline-Eintrag merken
            timeline = design.timeline
            startIndex = timeline.count

            # Neue Versatzebenen erzeugen
            # Die erste Ebene liegt an der Position der ausgewählten Ebene (Versatz = 0)
            for i in range(numPlanes):
                currentOffsetValue = adsk.core.ValueInput.createByReal(i * offsetVal)

                planeInput = constructions.createInput()
                planeInput.setByOffset(basePlane, currentOffsetValue)
                offsetPlane = constructions.add(planeInput)

                # Namen für Ebene setzen: "Name i+1"
                offsetPlane.name = f"{planeName} {i+1}"

                # Falls vom Anwender gewünscht: Leere Skizze auf dieser Ebene erstellen
                if createSketches:
                    newSketch = rootComp.sketches.add(offsetPlane)
                    newSketch.name = f"{sketchName} {i+1}"

            # Timeline-Gruppierung vornehmen (wenn gewünscht)
            endIndex = timeline.count - 1  # Index nach unseren letzten Erstellungen
            if shouldGroup and endIndex >= startIndex:
                newGroup = timeline.timelineGroups.add(startIndex, endIndex)
                newGroup.name = tr('group_name', name=planeName)

            ui.messageBox(tr('success', count=numPlanes)
                          + (tr('sketch_success') if createSketches else "")
                          + (tr('group_success') if shouldGroup else ""))

        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox(tr('error', context='CommandExecuteHandler', details=traceback.format_exc()))

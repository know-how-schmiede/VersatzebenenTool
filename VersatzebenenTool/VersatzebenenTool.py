import adsk.core, adsk.fusion, adsk.cam, traceback

# Globalvariablen, um Referenzen auf EventHandler zu behalten.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Eine neue Befehl-Definition anlegen.
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            'cmdCreateOffsetPlanes',         # interner Bezeichner
            'Versatzebenen erstellen',       # Titel im UI
            'Erstellt eine variable Anzahl von Versatzebenen zu einer ausgewählten Ebene.',
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
            ui.messageBox('Fehler in run:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Befehl-Definition entfernen, wenn vorhanden.
        cmdDef = ui.commandDefinitions.itemById('cmdCreateOffsetPlanes')
        if cmdDef:
            cmdDef.deleteMe()

        # CommandControl entfernen, wenn vorhanden.
        createPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        ctrl = createPanel.controls.itemById('cmdCreateOffsetPlanes')
        if ctrl:
            ctrl.deleteMe()

    except:
        if ui:
            ui.messageBox('Fehler in stop:\n{}'.format(traceback.format_exc()))


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
                'Ebene wählen',
                'Wähle eine vorhandene Ebene oder Fläche aus, von der aus Versatzebenen erstellt werden sollen.'
            )
            # Beschränken auf Ebenen oder planare Flächen
            selInput.addSelectionFilter('PlanarFaces')
            selInput.addSelectionFilter('ConstructionPlanes')
            selInput.setSelectionLimits(1,1)

            # 2) Anzahl der zu erstellenden Versatzebenen
            numPlanesInput = inputs.addIntegerSpinnerCommandInput(
                'numPlanes',
                'Anzahl Versatzebenen',
                1, 50, 1, 5
            )

            # 3) Versatz pro Ebene
            offsetValueInput = inputs.addValueInput(
                'planeOffset',
                'Versatz (pro Ebene)',
                'cm',  # Einheit kann beliebig gewählt werden (mm, cm, etc.)
                adsk.core.ValueInput.createByReal(1.0)
            )

            # 4) Boolean-Checkbox, ob gleichzeitig eine Skizze auf jeder neuen Ebene erstellt werden soll
            createSketchInput = inputs.addBoolValueInput(
                'createSketches',
                'Leere Skizze erstellen',
                True,   # Symboltyp: CheckBox
                '',
                False   # Standardwert: False
            )

            # 5) Name der Versatzebenen
            planeNameInput = inputs.addStringValueInput(
                'planeName',
                'Name der Versatzebene',
                'vref'  # Standardwert
            )

            # 6) Name der Skizze
            sketchNameInput = inputs.addStringValueInput(
                'sketchName',
                'Name der Skizze',
                'vref'  # Standardwert
            )

            # 7) Boolean-Checkbox, ob die neuen Objekte in der Timeline gruppiert werden sollen
            groupInHistoryInput = inputs.addBoolValueInput(
                'groupInHistory',
                'In Timeline gruppieren',
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
            ui.messageBox('Fehler in CommandCreatedHandler:\n{}'.format(traceback.format_exc()))


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
                ui.messageBox("Auswahl ist keine gültige Ebene oder planare Fläche.")
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
                newGroup.name = f"{planeName} - Gruppe"

            ui.messageBox(f"{numPlanes} Versatzebenen wurden erfolgreich erstellt.\n"
                          + ("Skizzen wurden ebenfalls erstellt.\n" if createSketches else "")
                          + ("Timeline-Einträge wurden gruppiert." if shouldGroup else ""))

        except:
            ui = adsk.core.Application.get().userInterface
            ui.messageBox('Fehler in CommandExecuteHandler:\n{}'.format(traceback.format_exc()))
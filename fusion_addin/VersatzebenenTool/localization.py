"""Central translations for the active add-in UI; English is the fallback."""

LANGUAGE_NAMES = {
    'en': 'EnglishLanguage', 'de': 'GermanLanguage',
    'fr': 'FrenchLanguage', 'es': 'SpanishLanguage', 'pl': 'PolishLanguage',
}

# Each row contains English, German, French, Spanish and Polish, in that order.
_ROWS = {
    'command': ('Create offset planes', 'Versatzebenen erstellen', 'Créer des plans décalés', 'Crear planos de desfase', 'Utwórz płaszczyzny odsunięcia'),
    'description': ('Creates equally spaced offset planes from a selected plane.', 'Erstellt gleichmäßig versetzte Ebenen ausgehend von einer ausgewählten Ebene.', 'Crée des plans à intervalles réguliers à partir du plan sélectionné.', 'Crea planos a intervalos regulares a partir del plano seleccionado.', 'Tworzy równomiernie odsunięte płaszczyzny względem wybranej płaszczyzny.'),
    'select_plane': ('Select plane', 'Ebene wählen', 'Sélectionner un plan', 'Seleccionar plano', 'Wybierz płaszczyznę'),
    'select_hint': ('Select a construction plane or planar face.', 'Wähle eine Konstruktionsebene oder planare Fläche aus.', 'Sélectionnez un plan de construction ou une face plane.', 'Seleccione un plano de construcción o una cara plana.', 'Wybierz płaszczyznę konstrukcyjną lub płaską ścianę.'),
    'count': ('Number of offset planes', 'Anzahl Versatzebenen', 'Nombre de plans décalés', 'Número de planos de desfase', 'Liczba płaszczyzn odsunięcia'),
    'offset': ('Offset per plane', 'Versatz (pro Ebene)', 'Décalage par plan', 'Desfase por plano', 'Odsunięcie na płaszczyznę'),
    'sketches': ('Create empty sketches', 'Leere Skizzen erstellen', 'Créer des esquisses vides', 'Crear bocetos vacíos', 'Utwórz puste szkice'),
    'plane_name': ('Plane name', 'Name der Versatzebene', 'Nom du plan', 'Nombre del plano', 'Nazwa płaszczyzny'),
    'sketch_name': ('Sketch name', 'Name der Skizze', "Nom de l’esquisse", 'Nombre del boceto', 'Nazwa szkicu'),
    'group': ('Group in timeline', 'In Timeline gruppieren', 'Regrouper dans la chronologie', 'Agrupar en la línea de tiempo', 'Grupuj na osi czasu'),
    'group_name': ('{name} - Group', '{name} - Gruppe', '{name} - Groupe', '{name} - Grupo', '{name} - Grupa'),
    'invalid_inputs': ('Select a plane or planar face and enter a valid count and offset.', 'Wähle eine Ebene oder planare Fläche und gib eine gültige Anzahl und einen gültigen Versatz ein.', 'Sélectionnez un plan ou une face plane et saisissez un nombre et un décalage valides.', 'Seleccione un plano o una cara plana e introduzca una cantidad y un desfase válidos.', 'Wybierz płaszczyznę lub płaską ścianę i podaj prawidłową liczbę oraz odsunięcie.'),
    'design_required': ('Open a Fusion design first.', 'Öffne zuerst eine Fusion-Konstruktion.', 'Ouvrez d’abord une conception Fusion.', 'Abra primero un diseño de Fusion.', 'Najpierw otwórz projekt Fusion.'),
    'history_required': ('Timeline grouping requires design history.', 'Die Timeline-Gruppierung benötigt einen aktiven Konstruktionsverlauf.', 'Le regroupement nécessite un historique de conception actif.', 'La agrupación requiere un historial de diseño activo.', 'Grupowanie wymaga aktywnej historii projektu.'),
    'plane_failed': ('Could not create plane {number}.', 'Ebene {number} konnte nicht erstellt werden.', 'Impossible de créer le plan {number}.', 'No se pudo crear el plano {number}.', 'Nie udało się utworzyć płaszczyzny {number}.'),
    'group_failed': ('Could not create the timeline group.', 'Die Timeline-Gruppe konnte nicht erstellt werden.', 'Impossible de créer le groupe dans la chronologie.', 'No se pudo crear el grupo en la línea de tiempo.', 'Nie udało się utworzyć grupy na osi czasu.'),
    'panel_unavailable': ('The Create panel is unavailable.', 'Das Erstellen-Panel ist nicht verfügbar.', 'Le panneau Créer est indisponible.', 'El panel Crear no está disponible.', 'Panel tworzenia jest niedostępny.'),
    'success': ('Successfully created {count} offset planes.\n', '{count} Versatzebenen wurden erfolgreich erstellt.\n', '{count} plans décalés ont été créés.\n', 'Se han creado {count} planos de desfase.\n', 'Utworzono {count} płaszczyzn odsunięcia.\n'),
    'sketch_success': ('Sketches were also created.\n', 'Skizzen wurden ebenfalls erstellt.\n', 'Les esquisses ont également été créées.\n', 'También se han creado los bocetos.\n', 'Utworzono również szkice.\n'),
    'group_success': ('Timeline entries were grouped.', 'Timeline-Einträge wurden gruppiert.', 'Les éléments de la chronologie ont été regroupés.', 'Se han agrupado las entradas de la línea de tiempo.', 'Elementy osi czasu zostały zgrupowane.'),
    'error': ('Error in {context}:\n{details}', 'Fehler in {context}:\n{details}', 'Erreur dans {context} :\n{details}', 'Error en {context}:\n{details}', 'Błąd w {context}:\n{details}'),
}
TRANSLATIONS = {
    language: {key: row[index] for key, row in _ROWS.items()}
    for index, language in enumerate(LANGUAGE_NAMES)
}
_language = 'en'


def initialize(app):
    """Read Fusion's preference on add-in start without changing it."""
    global _language
    _language = 'en'
    try:
        import adsk.core
        selected = app.preferences.generalPreferences.userLanguage
        for language, enum_name in LANGUAGE_NAMES.items():
            candidate = getattr(adsk.core.UserLanguages, enum_name, None)
            if candidate is not None and selected == candidate:
                _language = language
                break
    except (AttributeError, RuntimeError):
        # Older Fusion versions may not expose every language or preference.
        pass
    return _language


def tr(key, **values):
    text = TRANSLATIONS.get(_language, TRANSLATIONS['en']).get(key)
    if text is None:
        text = TRANSLATIONS['en'][key]
    return text.format(**values)

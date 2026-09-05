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
    'select_hint': ('Select an existing construction plane.', 'Wähle eine vorhandene Konstruktionsebene aus.', 'Sélectionnez un plan de construction existant.', 'Seleccione un plano de construcción existente.', 'Wybierz istniejącą płaszczyznę konstrukcyjną.'),
    'count': ('Number of offset planes', 'Anzahl Versatzebenen', 'Nombre de plans décalés', 'Número de planos de desfase', 'Liczba płaszczyzn odsunięcia'),
    'offset': ('Offset per plane', 'Versatz (pro Ebene)', 'Décalage par plan', 'Desfase por plano', 'Odsunięcie na płaszczyznę'),
    'sketches': ('Create empty sketches', 'Leere Skizzen erstellen', 'Créer des esquisses vides', 'Crear bocetos vacíos', 'Utwórz puste szkice'),
    'plane_name': ('Plane name', 'Name der Versatzebene', 'Nom du plan', 'Nombre del plano', 'Nazwa płaszczyzny'),
    'sketch_name': ('Sketch name', 'Name der Skizze', "Nom de l’esquisse", 'Nombre del boceto', 'Nazwa szkicu'),
    'group': ('Group in timeline', 'In Timeline gruppieren', 'Regrouper dans la chronologie', 'Agrupar en la línea de tiempo', 'Grupuj na osi czasu'),
    'group_name': ('{name} - Group', '{name} - Gruppe', '{name} - Groupe', '{name} - Grupo', '{name} - Grupa'),
    'invalid_plane': ('The selection is not a valid construction plane.', 'Die Auswahl ist keine gültige Konstruktionsebene.', "La sélection n’est pas un plan de construction valide.", 'La selección no es un plano de construcción válido.', 'Wybrany obiekt nie jest prawidłową płaszczyzną konstrukcyjną.'),
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

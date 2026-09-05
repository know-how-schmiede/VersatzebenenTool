"""Translation and language-selection checks without a running Fusion UI."""

import importlib.util
from pathlib import Path
from string import Formatter
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'localization', ROOT / 'fusion_addin/VersatzebenenTool/localization.py')
localization = importlib.util.module_from_spec(spec)
spec.loader.exec_module(localization)


class LocalizationTests(unittest.TestCase):
    def test_catalogs_and_placeholders(self):
        english = localization.TRANSLATIONS['en']
        fields = lambda text: {name for _, name, _, _ in Formatter().parse(text) if name}
        for catalog in localization.TRANSLATIONS.values():
            self.assertEqual(set(english), set(catalog))
            for key, text in catalog.items():
                self.assertTrue(text)
                self.assertEqual(fields(english[key]), fields(text))

    def test_fusion_languages_and_fallback(self):
        adsk = ModuleType('adsk')
        core = ModuleType('adsk.core')
        adsk.core = core
        core.UserLanguages = SimpleNamespace(**{
            name: index for index, name in enumerate(localization.LANGUAGE_NAMES.values())})
        with patch.dict(sys.modules, {'adsk': adsk, 'adsk.core': core}):
            for index, language in enumerate(localization.LANGUAGE_NAMES):
                app = SimpleNamespace(preferences=SimpleNamespace(
                    generalPreferences=SimpleNamespace(userLanguage=index)))
                self.assertEqual(localization.initialize(app), language)
                self.assertEqual(localization.tr('group_name', name='Example'),
                                 localization.TRANSLATIONS[language]['group_name'].format(name='Example'))
            app.preferences.generalPreferences.userLanguage = 999
            self.assertEqual(localization.initialize(app), 'en')
            self.assertEqual(localization.initialize(SimpleNamespace()), 'en')
            del core.UserLanguages.PolishLanguage
            app.preferences.generalPreferences.userLanguage = 4
            self.assertEqual(localization.initialize(app), 'en')


if __name__ == '__main__':
    unittest.main()

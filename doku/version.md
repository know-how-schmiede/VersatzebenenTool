# Version history / Versionshistorie

<!-- version:start -->
**Current version / Aktuelle Version: 1.3.0**
<!-- version:end -->

[English README](../README.md) · [Deutsche README](../README.de.md)

## 1.3.0

- Added a default-enabled option to show created planes, applied after all sketches and timeline grouping so support planes remain visible. Disabling it hides only the newly created planes.
- Enable the root Construction folder when showing planes.
- Added a positive, configurable minimum display size (100 mm by default), with extra width for longer names and preservation of existing larger bounds and their center.
- Localized both new controls and the display-size guidance in all five languages.
- Documented Fusion's separate Construction Plane Names display setting and zoom-dependent label visibility.
- Added regression tests for visibility after sketch creation, hidden planes, display sizing and input validation.

## 1.2.2

- Fixed startup import collisions with other Fusion add-ins by loading version and localization directly from this add-in's directory, without shared module-cache entries.

- Added a shared CAD banner at the top of both READMEs and in the Fusion command dialog.
- Fixed planar-face references; removed the invalid construction-plane cast.
- Added input validation, design checks and document length units.
- Disabled timeline grouping without design history and use the timeline marker to group newly inserted features.
- Reused startup cleanup and release dialog event handlers on destruction.
- Report execution failures through Fusion command errors.
- Added regression coverage for geometry options, validation, lifecycle and banner integration.

## 1.2.1

- Added English, German, French, Spanish and Polish translations for the active command, selected from Fusion preferences with English fallback.
- Updated the English README and added a linked German README with installation instructions and known limitations.
- Updated runtime, manifest and installer versions to 1.2.1.
- Adjusted the installer source path to `fusion_addin/VersatzebenenTool`.
- Added `tools/sync_version.py` to synchronize and validate current version declarations.
- Native Fusion behavior and installer compilation require validation in their respective applications.

## 1.2

- Introduced the central version source, now at `fusion_addin/VersatzebenenTool/version.py`.
- Added the current version to the Fusion command title.
- Updated the manifest and Windows installer to version 1.2.

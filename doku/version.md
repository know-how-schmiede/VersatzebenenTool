# Version history / Versionshistorie

<!-- version:start -->
**Current version / Aktuelle Version: 1.2.2**
<!-- version:end -->

[English README](../README.md) · [Deutsche README](../README.de.md)

## 1.2.2

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

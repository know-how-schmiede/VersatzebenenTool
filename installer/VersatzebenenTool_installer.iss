#define MyAppName "VersatzebenenTool"
#define MyAppVersion "1.3.0"
#define MyAppPublisher "Rene Triebenstein"
#define MyAppSourceDir "..\fusion_addin\VersatzebenenTool"

[Setup]
AppId={{47D9E99E-DEAD-4332-9F42-984CBC586115}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={userappdata}\Autodesk\Autodesk Fusion 360\API\AddIns\{#MyAppName}
DisableDirPage=yes
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename={#MyAppName}_Setup_{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UsePreviousAppDir=yes
DirExistsWarning=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*,*.pyc,*.pyo,*.pyd,.venv\*,venv\*,env\*,ENV\*,.pytest_cache\*,.mypy_cache\*,.ruff_cache\*,.git\*,.github\*,.vscode\*,dist\*,build\*"

#define MyAppName "VersatzebenenTool"
#define MyAppVersion "1.3.1"
#define MyAppPublisher "Rene Triebenstein"
#define MyAppSourceDir "..\fusion_addin\VersatzebenenTool"

[Setup]
AppId={{47D9E99E-DEAD-4332-9F42-984CBC586115}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={userappdata}\Autodesk\Autodesk Fusion 360\API\AddIns\{#MyAppName}
DisableDirPage=no
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
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[CustomMessages]
english.PluginPathHint=Setup does not detect the add-in path registered in Fusion. Compare the folder below with the path shown for VersatzebenenTool in Fusion under Scripts and Add-Ins > Add-Ins. Select the VersatzebenenTool folder, not its parent AddIns folder.
german.PluginPathHint=Setup erkennt den in Fusion registrierten Add-in-Pfad nicht automatisch. Vergleichen Sie den folgenden Ordner mit dem Pfad des VersatzebenenTools in Fusion unter Skripte und Zusatzmodule > Zusatzmodule. Wählen Sie den Ordner VersatzebenenTool, nicht den übergeordneten AddIns-Ordner.
english.PluginPathFinished=Installed add-in folder:%n%1%n%nPlease verify that this matches the path registered for VersatzebenenTool in Fusion under Scripts and Add-Ins > Add-Ins. If it differs or the add-in is not listed, register this folder using Add (+).
german.PluginPathFinished=Installationsordner des Add-ins:%n%1%n%nBitte prüfen Sie, ob dieser Pfad mit dem in Fusion unter Skripte und Zusatzmodule > Zusatzmodule für VersatzebenenTool angegebenen Pfad übereinstimmt. Falls er abweicht oder das Add-in fehlt, registrieren Sie diesen Ordner über Hinzufügen (+).

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*,*.pyc,*.pyo,*.pyd,.venv\*,venv\*,env\*,ENV\*,.pytest_cache\*,.mypy_cache\*,.ruff_cache\*,.git\*,.github\*,.vscode\*,dist\*,build\*"

[Code]
procedure InitializeWizard;
begin
  WizardForm.SelectDirBrowseLabel.Caption := CustomMessage('PluginPathHint');
  WizardForm.SelectDirBrowseLabel.WordWrap := True;
  WizardForm.SelectDirBrowseLabel.AutoSize := True;
  WizardForm.DirEdit.Top := WizardForm.SelectDirBrowseLabel.Top +
    WizardForm.SelectDirBrowseLabel.Height + ScaleY(12);
  WizardForm.DirBrowseButton.Top := WizardForm.DirEdit.Top - ScaleY(1);
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
    WizardForm.FinishedLabel.Caption :=
      FmtMessage(CustomMessage('PluginPathFinished'), [ExpandConstant('{app}')]);
end;

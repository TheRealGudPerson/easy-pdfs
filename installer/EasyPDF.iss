#define MyAppName "EasyPDF"
#define MyAppPublisher "EasyPDF"
#define MyAppExeName "EasyPDF.exe"

#ifndef AppVersion
#define AppVersion "0.0.0"
#endif

[Setup]
AppId={{B9F9E2E4-4F61-4A8C-9C95-EASYPDF00001}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\EasyPDF
DefaultGroupName=EasyPDF

OutputDir=output
OutputBaseFilename=EasyPDF-Setup-{#AppVersion}

Compression=lzma
SolidCompression=yes

WizardStyle=modern

ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

DisableProgramGroupPage=yes

UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\EasyPDF.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\EasyPDF"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\EasyPDF"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch EasyPDF"; Flags: nowait postinstall skipifsilent
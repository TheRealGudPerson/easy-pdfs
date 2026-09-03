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

UninstallDisplayIcon={app}\EasyPDF.exe

[Files]
Source: "..\dist\EasyPDF\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\EasyPDF"; Filename: "{app}\EasyPDF.exe"

Name: "{autodesktop}\EasyPDF"; Filename: "{app}\EasyPDF.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\EasyPDF.exe"; Description: "Launch EasyPDF"; Flags: nowait postinstall skipifsilent
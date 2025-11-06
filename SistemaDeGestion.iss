
; SistemaDeGestion.iss - Inno Setup script generated
[Setup]
AppName=Sistema de Gestión
AppVersion=1.0
AppPublisher=Morales Sebastián
DefaultDirName={pf}\Sistema de Gestión
DefaultGroupName=Sistema de Gestión
UninstallDisplayIcon={app}\SistemaDeGestion.exe
OutputBaseFilename=SistemaDeGestion_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Files]
Source: "dist\SistemaDeGestion.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "templates\*"; DestDir: "{app}\templates"; Flags: recursesubdirs createallsubdirs
Source: "config\*"; DestDir: "{app}\config"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Sistema de Gestión"; Filename: "{app}\SistemaDeGestion.exe"
Name: "{commondesktop}\Sistema de Gestión"; Filename: "{app}\SistemaDeGestion.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Crear acceso directo en el Escritorio"; GroupDescription: "Accesos directos:"

[Run]
Filename: "{app}\SistemaDeGestion.exe"; Description: "Iniciar Sistema de Gestión"; Flags: nowait postinstall skipifsilent

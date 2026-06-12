[Setup]
AppName=Media Converter
AppVersion=1.2.0
AppPublisher=arikghre
AppPublisherURL=https://github.com/arikghre/audio-converter
AppSupportURL=https://github.com/arikghre/audio-converter/issues
AppUpdatesURL=https://github.com/arikghre/audio-converter/releases
DefaultDirName={autopf}\MediaConverter
DefaultGroupName=Media Converter
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=MediaConverter_Setup_v1.2.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis supplémentaires :"; Flags: unchecked

[Files]
Source: "dist\MediaConverter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Media Converter"; Filename: "{app}\MediaConverter.exe"
Name: "{group}\Désinstaller Media Converter"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Media Converter"; Filename: "{app}\MediaConverter.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MediaConverter.exe"; Description: "Lancer Media Converter maintenant"; Flags: nowait postinstall skipifsilent

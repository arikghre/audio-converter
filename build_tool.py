"""
Build tool for AG's Media Converter.
Generates dist/ via PyInstaller then compiles AGsMediaConverterSetup.exe via Inno Setup.
Run via build.bat or: python build_tool.py
"""
import os
import sys
import shutil
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))

ISS_TEMPLATE = r"""
[Setup]
AppName=AG's Media Converter
AppVersion=1.2.0
AppPublisher=arikghre
AppPublisherURL=https://github.com/arikghre/audio-converter
AppSupportURL=https://github.com/arikghre/audio-converter/issues
AppUpdatesURL=https://github.com/arikghre/audio-converter/releases
DefaultDirName={autopf}\AGsMediaConverter
DefaultGroupName=AG's Media Converter
AllowNoIcons=yes
SetupIconFile={root}\logo.ico
OutputDir={root}\installer
OutputBaseFilename=AGsMediaConverterSetup
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
Source: "{root}\dist\AGsMediaConverter\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\AG's Media Converter"; Filename: "{{app}}\AGsMediaConverter.exe"
Name: "{{group}}\Désinstaller AG's Media Converter"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\AG's Media Converter"; Filename: "{{app}}\AGsMediaConverter.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\AGsMediaConverter.exe"; Description: "Lancer AG's Media Converter"; Flags: nowait postinstall skipifsilent
""".strip()

ISCC_PATHS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
]


def step(msg):
    print(f"\n==> {msg}")


def run(cmd, **kwargs):
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"ERREUR (code {result.returncode})")
        sys.exit(1)


def find_iscc():
    for path in ISCC_PATHS:
        if os.path.exists(path):
            return path
    return None


def install_inno():
    print("Inno Setup introuvable — installation via winget...")
    subprocess.run(
        ["winget", "install", "JRSoftware.InnoSetup", "--source", "winget",
         "--accept-package-agreements", "--accept-source-agreements"],
        check=True,
    )
    return find_iscc()


if __name__ == "__main__":
    os.chdir(ROOT)

    step("Installation des dépendances Python...")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    step("Construction de l'application (PyInstaller)...")
    run([sys.executable, "-m", "PyInstaller", "AGsMediaConverter.spec", "--noconfirm"])

    exe_path = os.path.join(ROOT, "dist", "AGsMediaConverter", "AGsMediaConverter.exe")
    if not os.path.exists(exe_path):
        print("ERREUR : AGsMediaConverter.exe introuvable après PyInstaller.")
        sys.exit(1)

    step("Compilation de l'installeur (Inno Setup)...")
    iscc = find_iscc() or install_inno()
    if not iscc:
        print("ERREUR : Inno Setup introuvable même après installation.")
        sys.exit(1)

    iss_content = ISS_TEMPLATE.replace("{root}", ROOT.replace("\\", "\\\\"))
    iss_tmp = os.path.join(ROOT, "_ags_build_temp.iss")
    with open(iss_tmp, "w", encoding="utf-8") as f:
        f.write(iss_content)

    os.makedirs(os.path.join(ROOT, "installer"), exist_ok=True)
    run([iscc, iss_tmp])
    os.remove(iss_tmp)

    setup_path = os.path.join(ROOT, "installer", "AGsMediaConverterSetup.exe")
    if os.path.exists(setup_path):
        size_mb = os.path.getsize(setup_path) / (1024 * 1024)
        print(f"\n✓ SUCCÈS : AGsMediaConverterSetup.exe ({size_mb:.1f} MB)")
        print(f"  Chemin : {setup_path}")
    else:
        print("ERREUR : AGsMediaConverterSetup.exe introuvable.")
        sys.exit(1)

"""
AG's Media Converter — Build Tool
Double-clic sur build.exe pour generer AGsMediaConverterSetup.exe
"""
import os
import sys
import shutil
import subprocess

# When compiled as an exe, ROOT = folder containing the exe
if getattr(sys, "frozen", False):
    ROOT = os.path.dirname(sys.executable)
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))

ISS_TEMPLATE = """
[Setup]
AppName=AG's Media Converter
AppVersion=1.3.0
AppPublisher=arikghre
AppPublisherURL=https://github.com/arikghre/audio-converter
AppSupportURL=https://github.com/arikghre/audio-converter/issues
AppUpdatesURL=https://github.com/arikghre/audio-converter/releases
DefaultDirName={{autopf}}\\AGsMediaConverter
DefaultGroupName=AG's Media Converter
AllowNoIcons=yes
SetupIconFile={root}\\logo.ico
OutputDir={root}\\installer
OutputBaseFilename=AGsMediaConverterSetup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis supplémentaires :"; Flags: unchecked

[Files]
Source: "{root}\\dist\\AGsMediaConverter\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\AG's Media Converter"; Filename: "{{app}}\\AGsMediaConverter.exe"
Name: "{{group}}\\Désinstaller AG's Media Converter"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\AG's Media Converter"; Filename: "{{app}}\\AGsMediaConverter.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\AGsMediaConverter.exe"; Description: "Lancer AG's Media Converter"; Flags: nowait postinstall skipifsilent
""".strip()

ISCC_PATHS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
]


def step(msg):
    print(f"\n==> {msg}")


def find_python():
    for name in ("python", "python3"):
        path = shutil.which(name)
        if path:
            return path
    return None


def run(cmd):
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\nERREUR (code {result.returncode}). Build interrompu.")
        input("\nAppuyer sur Entree pour quitter...")
        sys.exit(1)


def find_iscc():
    for p in ISCC_PATHS:
        if os.path.exists(p):
            return p
    return None


def main():
    print()
    print("  ====================================")
    print("   AG's Media Converter  -  Build")
    print("  ====================================")

    os.chdir(ROOT)

    python = find_python()
    if not python:
        print("ERREUR : Python introuvable dans le PATH.")
        input("\nAppuyer sur Entree pour quitter...")
        sys.exit(1)

    step("Installation des dependances Python...")
    run([python, "-m", "pip", "install", "-r", os.path.join(ROOT, "requirements.txt")])

    step("Construction de l'application (PyInstaller)...")
    run([python, "-m", "PyInstaller",
         os.path.join(ROOT, "AGsMediaConverter.spec"), "--noconfirm"])

    exe_path = os.path.join(ROOT, "dist", "AGsMediaConverter", "AGsMediaConverter.exe")
    if not os.path.exists(exe_path):
        print("ERREUR : AGsMediaConverter.exe introuvable apres PyInstaller.")
        input("\nAppuyer sur Entree pour quitter...")
        sys.exit(1)

    step("Compilation de l'installeur (Inno Setup)...")
    iscc = find_iscc()
    if not iscc:
        print("Inno Setup introuvable — installation via winget...")
        subprocess.run([
            "winget", "install", "JRSoftware.InnoSetup",
            "--source", "winget",
            "--accept-package-agreements", "--accept-source-agreements"
        ])
        iscc = find_iscc()
    if not iscc:
        print("ERREUR : Inno Setup introuvable.")
        input("\nAppuyer sur Entree pour quitter...")
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
        print(f"\n  SUCCES : AGsMediaConverterSetup.exe ({size_mb:.1f} MB)")
        print(f"  Chemin : {setup_path}")
    else:
        print("ERREUR : AGsMediaConverterSetup.exe introuvable.")

    input("\nAppuyer sur Entree pour quitter...")


if __name__ == "__main__":
    main()

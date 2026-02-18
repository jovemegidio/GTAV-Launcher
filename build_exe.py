"""
GTA V Launcher - Script de build para criar executável .exe
Usa PyInstaller para gerar um executável standalone.
"""

import PyInstaller.__main__
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEP = os.pathsep  # ; on Windows

icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
assets_src = os.path.join(BASE_DIR, "assets")
modules_src = os.path.join(BASE_DIR, "modules")

args = [
    os.path.join(BASE_DIR, "main.py"),
    "--name=GTAVLauncher",
    "--onefile",
    "--windowed",
    "--clean",
    f"--distpath={os.path.join(BASE_DIR, 'dist')}",
    f"--workpath={os.path.join(BASE_DIR, 'build')}",
    f"--specpath={BASE_DIR}",
    # Incluir módulos
    "--hidden-import=customtkinter",
    "--hidden-import=PIL",
    "--hidden-import=modules.config",
    "--hidden-import=modules.game_manager",
    "--hidden-import=modules.socialclub_fixer",
    "--hidden-import=modules.network_manager",
    "--hidden-import=modules.optimizer",
    # Coletar dados do customtkinter
    "--collect-data=customtkinter",
    # Assets
    f"--add-data={assets_src}{SEP}assets",
    f"--add-data={modules_src}{SEP}modules",
]

if os.path.isfile(icon_path):
    args.append(f"--icon={icon_path}")

PyInstaller.__main__.run(args)

print("\n✅ Build concluído! Executável em: dist/GTAVLauncher.exe")

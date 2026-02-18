"""
Módulo de Configuração do Launcher GTA V
Gerencia todas as configurações e caminhos do jogo.
"""

import json
import os
import winreg
from pathlib import Path


CONFIG_DIR = Path(os.environ.get("APPDATA", "")) / "GTAVLauncher"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "game_path": "",
    "launch_mode": "offline",          # "offline" ou "online"
    "auto_fix_socialclub": True,
    "language": "pt-BR",
    "steam_version": False,
    "epic_version": False,
    "custom_args": "",
    "windowed": False,
    "borderless": False,
    "skip_launcher_intro": True,
    "disable_loading_screen": False,
    "population_density": 1.0,
    "last_played_mode": "offline",
    "theme": "dark",
}


def ensure_config_dir():
    """Garante que o diretório de configuração existe."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Carrega as configurações do arquivo JSON."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Mescla com defaults para campos novos
                config = {**DEFAULT_CONFIG, **saved}
                return config
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Salva as configurações no arquivo JSON."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def detect_game_path() -> str:
    """
    Tenta detectar automaticamente o caminho de instalação do GTA V.
    Verifica: Registry (Rockstar), Steam, Epic Games.
    """
    possible_paths = []

    # 1. Verificar Registry do Rockstar Games Launcher
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Rockstar Games\Grand Theft Auto V"
        )
        path, _ = winreg.QueryValueEx(key, "InstallFolder")
        winreg.CloseKey(key)
        if path:
            possible_paths.append(path)
    except (OSError, FileNotFoundError):
        pass

    # 2. Verificar Registry do Rockstar (32-bit)
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Rockstar Games\Grand Theft Auto V"
        )
        path, _ = winreg.QueryValueEx(key, "InstallFolder")
        winreg.CloseKey(key)
        if path:
            possible_paths.append(path)
    except (OSError, FileNotFoundError):
        pass

    # 3. Verificar Steam
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Valve\Steam"
        )
        steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
        winreg.CloseKey(key)
        steam_gta = os.path.join(steam_path, "steamapps", "common", "Grand Theft Auto V")
        possible_paths.append(steam_gta)
    except (OSError, FileNotFoundError):
        pass

    # 4. Verificar Epic Games
    epic_manifest_dir = Path(os.environ.get("PROGRAMDATA", "")) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"
    if epic_manifest_dir.exists():
        for manifest_file in epic_manifest_dir.glob("*.item"):
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "GTA" in data.get("DisplayName", "").upper():
                        install_loc = data.get("InstallLocation", "")
                        if install_loc:
                            possible_paths.append(install_loc)
            except (json.JSONDecodeError, IOError):
                continue

    # 5. Caminhos padrão comuns
    common_paths = [
        r"C:\Program Files\Rockstar Games\Grand Theft Auto V",
        r"C:\Program Files (x86)\Rockstar Games\Grand Theft Auto V",
        r"C:\Program Files (x86)\Steam\steamapps\common\Grand Theft Auto V",
        r"D:\Games\Grand Theft Auto V",
        r"D:\SteamLibrary\steamapps\common\Grand Theft Auto V",
        r"E:\Games\Grand Theft Auto V",
        r"E:\SteamLibrary\steamapps\common\Grand Theft Auto V",
    ]
    possible_paths.extend(common_paths)

    # Verificar qual caminho realmente tem o executável
    for path in possible_paths:
        gta_exe = os.path.join(path, "GTA5.exe")
        if os.path.isfile(gta_exe):
            return path

    return ""


def detect_platform(game_path: str) -> str:
    """Detecta a plataforma do jogo (Steam, Epic, Rockstar)."""
    if not game_path:
        return "unknown"

    game_path_lower = game_path.lower()

    if "steam" in game_path_lower or "steamapps" in game_path_lower:
        return "steam"
    elif "epic" in game_path_lower:
        return "epic"
    else:
        return "rockstar"


def validate_game_path(path: str) -> bool:
    """Verifica se o caminho contém uma instalação válida do GTA V."""
    if not path or not os.path.isdir(path):
        return False

    required_files = ["GTA5.exe"]
    for f in required_files:
        if not os.path.isfile(os.path.join(path, f)):
            return False
    return True


def get_game_version(game_path: str) -> str:
    """Tenta obter a versão do jogo."""
    try:
        import struct
        exe_path = os.path.join(game_path, "GTA5.exe")
        if not os.path.isfile(exe_path):
            return "Desconhecida"

        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        return f"~{size_mb:.0f} MB (exe)"
    except Exception:
        return "Desconhecida"

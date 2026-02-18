"""
Módulo Game Manager - Gerencia o lançamento do GTA V
Suporta modos Offline e Online com parâmetros oficiais.
"""

import os
import subprocess
import time
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("GTAVLauncher")


class GameManager:
    """Gerencia o lançamento e monitoramento do GTA V."""

    # Parâmetros oficiais de linha de comando do GTA V
    LAUNCH_PARAMS = {
        "offline": "-scOfflineOnly",
        "safe_mode": "-safemode",
        "windowed": "-windowed",
        "borderless": "-borderless",
        "fullscreen": "-fullscreen",
        "no_loading": "-noloadingscreen",
        "high_priority": "-highPriority",
        "dx10": "-DX10",
        "dx11": "-DX11",
        "no_pause_focus": "-noPauseOnFocusLoss",
        "benchmark": "-benchmark",
        "gpu_benchmark": "-benchmarkGpuMemoryTest",
        "straight_to_freemode": "-StraightIntoFreemode",
        "go_to_sp": "-goStraightToSP",
    }

    ROCKSTAR_LAUNCHER_EXE = "PlayGTAV.exe"
    GTA5_EXE = "GTA5.exe"
    GTA5_LAUNCHER_EXE = "GTAVLauncher.exe"

    def __init__(self, game_path: str):
        self.game_path = game_path
        self._process: Optional[subprocess.Popen] = None

    @property
    def play_exe_path(self) -> str:
        """Caminho do executável de lançamento."""
        return os.path.join(self.game_path, self.ROCKSTAR_LAUNCHER_EXE)

    @property
    def gta5_exe_path(self) -> str:
        """Caminho do executável principal do GTA V."""
        return os.path.join(self.game_path, self.GTA5_EXE)

    @property
    def launcher_exe_path(self) -> str:
        """Caminho do GTAVLauncher.exe."""
        return os.path.join(self.game_path, self.GTA5_LAUNCHER_EXE)

    def build_launch_args(self, config: dict) -> list:
        """
        Constrói os argumentos de lançamento baseado na configuração.

        Args:
            config: Dicionário de configurações do launcher.

        Returns:
            Lista de argumentos de linha de comando.
        """
        args = []

        # Modo offline/online
        mode = config.get("launch_mode", "offline")
        if mode == "offline":
            args.append(self.LAUNCH_PARAMS["offline"])
            # No modo offline, ir direto para Single Player
            args.append(self.LAUNCH_PARAMS["go_to_sp"])
        elif mode == "online":
            # No modo online, ir direto para freemode
            args.append(self.LAUNCH_PARAMS["straight_to_freemode"])

        # Opções de janela
        if config.get("windowed"):
            args.append(self.LAUNCH_PARAMS["windowed"])
            if config.get("borderless"):
                args.append(self.LAUNCH_PARAMS["borderless"])

        # Performance
        args.append(self.LAUNCH_PARAMS["no_pause_focus"])

        # Argumentos customizados
        custom_args = config.get("custom_args", "").strip()
        if custom_args:
            args.extend(custom_args.split())

        return args

    def launch_game(self, config: dict) -> Tuple[bool, str]:
        """
        Lança o GTA V com as configurações especificadas.

        Args:
            config: Dicionário de configurações.

        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        mode = config.get("launch_mode", "offline")

        # Verificar se o jogo já está rodando
        if self.is_game_running():
            return False, "⚠️ O GTA V já está em execução!"

        # Determinar qual executável usar
        exe_path = self._get_best_executable()
        if not exe_path:
            return False, "❌ Executável do GTA V não encontrado!"

        # Construir argumentos
        args = self.build_launch_args(config)

        # Montar comando
        cmd = [exe_path] + args

        logger.info(f"Lançando GTA V: {' '.join(cmd)}")
        logger.info(f"Modo: {'Offline' if mode == 'offline' else 'Online'}")

        try:
            # Aplicar correções pré-lançamento se necessário
            if mode == "offline" and config.get("auto_fix_socialclub"):
                self._prepare_offline_mode()

            # Lançar o jogo
            self._process = subprocess.Popen(
                cmd,
                cwd=self.game_path,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            )

            time.sleep(2)

            # Verificar se o processo iniciou
            if self._process.poll() is not None:
                return False, "❌ O jogo fechou inesperadamente após o lançamento."

            mode_text = "🔒 Offline (Single Player)" if mode == "offline" else "🌐 Online (GTA Online)"
            return True, f"✅ GTA V lançado com sucesso!\nModo: {mode_text}"

        except FileNotFoundError:
            return False, f"❌ Executável não encontrado: {exe_path}"
        except PermissionError:
            return False, "❌ Sem permissão para executar. Tente como Administrador."
        except Exception as e:
            return False, f"❌ Erro ao lançar: {str(e)}"

    def _get_best_executable(self) -> Optional[str]:
        """Determina o melhor executável para usar."""
        # Prioridade: PlayGTAV.exe > GTAVLauncher.exe > GTA5.exe
        candidates = [
            self.play_exe_path,
            self.launcher_exe_path,
            self.gta5_exe_path,
        ]
        for exe in candidates:
            if os.path.isfile(exe):
                return exe
        return None

    def _prepare_offline_mode(self):
        """Preparações para modo offline."""
        # Criar/verificar commandline.txt para persistir args
        cmdline_path = os.path.join(self.game_path, "commandline.txt")

        # Verificar se Social Club tem configuração offline
        sc_settings_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Rockstar Games" / "Social Club"
        if sc_settings_dir.exists():
            logger.info("Diretório Social Club encontrado, verificando configurações...")

    def is_game_running(self) -> bool:
        """Verifica se o GTA V está em execução."""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {self.GTA5_EXE}", "/NH"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return self.GTA5_EXE.lower() in result.stdout.lower()
        except Exception:
            return False

    def kill_game(self) -> Tuple[bool, str]:
        """Força o encerramento do GTA V."""
        try:
            result = subprocess.run(
                ["taskkill", "/F", "/IM", self.GTA5_EXE],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0:
                # Também encerrar o launcher
                subprocess.run(
                    ["taskkill", "/F", "/IM", self.GTA5_LAUNCHER_EXE],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                subprocess.run(
                    ["taskkill", "/F", "/IM", self.ROCKSTAR_LAUNCHER_EXE],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                return True, "✅ GTA V encerrado com sucesso."
            else:
                return False, "⚠️ GTA V não está em execução."
        except Exception as e:
            return False, f"❌ Erro ao encerrar: {str(e)}"

    def get_commandline_txt(self) -> str:
        """Lê o conteúdo do commandline.txt."""
        cmdline_path = os.path.join(self.game_path, "commandline.txt")
        if os.path.isfile(cmdline_path):
            with open(cmdline_path, "r") as f:
                return f.read()
        return ""

    def save_commandline_txt(self, content: str):
        """Salva o commandline.txt."""
        cmdline_path = os.path.join(self.game_path, "commandline.txt")
        with open(cmdline_path, "w") as f:
            f.write(content)

    def get_game_info(self) -> dict:
        """Retorna informações sobre a instalação do jogo."""
        info = {
            "path": self.game_path,
            "exe_exists": os.path.isfile(self.gta5_exe_path),
            "play_exe_exists": os.path.isfile(self.play_exe_path),
            "launcher_exists": os.path.isfile(self.launcher_exe_path),
            "running": self.is_game_running(),
        }

        # Tamanho da instalação
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.game_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
                # Limitar profundidade
                if dirpath != self.game_path:
                    break
            info["size_gb"] = total_size / (1024 ** 3)
        except Exception:
            info["size_gb"] = 0

        return info

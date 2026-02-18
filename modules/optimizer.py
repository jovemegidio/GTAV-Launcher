"""
Módulo de Otimização do GTA V
Gerencia commandline.txt e aplica otimizações baseadas no hardware.
"""

import os
import platform
import subprocess
import logging
import ctypes
from pathlib import Path
from typing import List, Tuple, Optional

logger = logging.getLogger("GTAVLauncher")


# ===== Presets de Otimização =====

OPTIMIZATION_PRESETS = {
    "performance": {
        "name": "🚀 Máxima Performance",
        "description": "Prioriza FPS acima de tudo. Ideal para PCs mais fracos.",
        "args": [
            "-high",
            "-noPauseOnFocusLoss",
            "-noInGameUi",
        ],
        "commandline_extra": [
            "-disableHyperthreading",
        ],
    },
    "balanced": {
        "name": "⚖️ Balanceado",
        "description": "Equilíbrio entre qualidade visual e desempenho.",
        "args": [
            "-noPauseOnFocusLoss",
        ],
        "commandline_extra": [],
    },
    "quality": {
        "name": "✨ Máxima Qualidade",
        "description": "Prioriza gráficos. Para PCs de alto desempenho.",
        "args": [
            "-noPauseOnFocusLoss",
            "-DX11",
        ],
        "commandline_extra": [],
    },
    "online_optimized": {
        "name": "🌐 Otimizado para Online",
        "description": "Melhor estabilidade para GTA Online.",
        "args": [
            "-noPauseOnFocusLoss",
            "-StraightIntoFreemode",
        ],
        "commandline_extra": [],
    },
    "streaming": {
        "name": "📺 Streaming / Gravação",
        "description": "Otimizado para quem faz live ou grava gameplay.",
        "args": [
            "-noPauseOnFocusLoss",
            "-windowed",
            "-borderless",
        ],
        "commandline_extra": [],
    },
}


# ===== Catálogo de Argumentos =====

ALL_ARGUMENTS = [
    # === Modo de Jogo ===
    {
        "arg": "-scOfflineOnly",
        "category": "Modo de Jogo",
        "name": "Modo Offline",
        "description": "Força o modo offline, sem Social Club",
        "icon": "🔒",
        "impact": "neutro",
    },
    {
        "arg": "-goStraightToSP",
        "category": "Modo de Jogo",
        "name": "Direto para Story Mode",
        "description": "Pula menus e vai direto para Single Player",
        "icon": "🎮",
        "impact": "positivo",
    },
    {
        "arg": "-StraightIntoFreemode",
        "category": "Modo de Jogo",
        "name": "Direto para GTA Online",
        "description": "Pula menus e vai direto para Freemode",
        "icon": "🌐",
        "impact": "positivo",
    },
    # === Performance ===
    {
        "arg": "-high",
        "category": "Performance",
        "name": "Prioridade Alta",
        "description": "Executa o jogo com prioridade alta do CPU",
        "icon": "⚡",
        "impact": "positivo",
    },
    {
        "arg": "-noPauseOnFocusLoss",
        "category": "Performance",
        "name": "Não Pausar ao Perder Foco",
        "description": "O jogo continua rodando em segundo plano",
        "icon": "▶️",
        "impact": "positivo",
    },
    {
        "arg": "-disableHyperthreading",
        "category": "Performance",
        "name": "Desativar Hyperthreading",
        "description": "Pode melhorar FPS em CPUs com hyperthreading",
        "icon": "🔧",
        "impact": "variável",
    },
    # === Gráficos ===
    {
        "arg": "-DX11",
        "category": "Gráficos",
        "name": "Forçar DirectX 11",
        "description": "Usa DirectX 11 (melhor compatibilidade)",
        "icon": "🎨",
        "impact": "neutro",
    },
    {
        "arg": "-DX10",
        "category": "Gráficos",
        "name": "Forçar DirectX 10",
        "description": "Usa DirectX 10 (para GPUs antigas)",
        "icon": "🎨",
        "impact": "negativo",
    },
    # === Tela ===
    {
        "arg": "-fullscreen",
        "category": "Tela",
        "name": "Tela Cheia",
        "description": "Executa em tela cheia exclusiva",
        "icon": "🖥️",
        "impact": "positivo",
    },
    {
        "arg": "-windowed",
        "category": "Tela",
        "name": "Modo Janela",
        "description": "Executa em modo janela",
        "icon": "🪟",
        "impact": "negativo",
    },
    {
        "arg": "-borderless",
        "category": "Tela",
        "name": "Sem Bordas",
        "description": "Remove bordas (usar com -windowed)",
        "icon": "🪟",
        "impact": "neutro",
    },
    # === Diagnóstico ===
    {
        "arg": "-safemode",
        "category": "Diagnóstico",
        "name": "Modo Seguro",
        "description": "Inicia com configurações mínimas",
        "icon": "🛡️",
        "impact": "negativo",
    },
    {
        "arg": "-benchmark",
        "category": "Diagnóstico",
        "name": "Benchmark",
        "description": "Executa o benchmark integrado",
        "icon": "📊",
        "impact": "neutro",
    },
    {
        "arg": "-benchmarkGpuMemoryTest",
        "category": "Diagnóstico",
        "name": "Teste de VRAM",
        "description": "Testa a memória da GPU",
        "icon": "📊",
        "impact": "neutro",
    },
]


class SystemAnalyzer:
    """Analisa o hardware do sistema para recomendações."""

    def __init__(self):
        self._info = None

    def get_system_info(self) -> dict:
        """Coleta informações do sistema."""
        if self._info:
            return self._info

        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count() or 4,
            "ram_gb": 0,
            "gpu_name": "Desconhecido",
            "vram_mb": 0,
        }

        # RAM total
        try:
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [
                    ("dwLength", c_ulong),
                    ("dwMemoryLoad", c_ulong),
                    ("dwTotalPhys", ctypes.c_uint64),
                    ("dwAvailPhys", ctypes.c_uint64),
                    ("dwTotalPageFile", ctypes.c_uint64),
                    ("dwAvailPageFile", ctypes.c_uint64),
                    ("dwTotalVirtual", ctypes.c_uint64),
                    ("dwAvailVirtual", ctypes.c_uint64),
                    ("dwAvailExtendedVirtual", ctypes.c_uint64),
                ]
            memstat = MEMORYSTATUS()
            memstat.dwLength = ctypes.sizeof(MEMORYSTATUS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memstat))
            info["ram_gb"] = round(memstat.dwTotalPhys / (1024 ** 3), 1)
        except Exception:
            info["ram_gb"] = 8  # fallback

        # GPU via WMIC
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name,AdapterRAM",
                 "/format:csv"],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=5,
            )
            lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
            if len(lines) >= 2:
                for line in lines[1:]:
                    parts = line.split(",")
                    if len(parts) >= 3:
                        try:
                            vram = int(parts[1]) if parts[1].isdigit() else 0
                        except (ValueError, IndexError):
                            vram = 0
                        name = parts[2] if len(parts) > 2 else ""
                        if name and ("NVIDIA" in name.upper() or "AMD" in name.upper()
                                     or "RADEON" in name.upper() or "GEFORCE" in name.upper()):
                            info["gpu_name"] = name.strip()
                            info["vram_mb"] = vram // (1024 * 1024) if vram > 1024 else vram
                            break
                # Fallback: pegar qualquer GPU listada
                if info["gpu_name"] == "Desconhecido" and len(lines) > 1:
                    parts = lines[1].split(",")
                    if len(parts) >= 3:
                        info["gpu_name"] = parts[2].strip() if parts[2].strip() else "Desconhecido"
        except Exception:
            pass

        self._info = info
        return info

    def get_recommended_preset(self) -> str:
        """Recomenda um preset baseado no hardware."""
        info = self.get_system_info()
        ram = info["ram_gb"]
        cores = info["cpu_count"]
        vram = info["vram_mb"]

        # PC fraco
        if ram < 8 or cores <= 4:
            return "performance"
        # PC gamer
        elif ram >= 16 and cores >= 8 and vram >= 4000:
            return "quality"
        # PC médio
        else:
            return "balanced"

    def get_recommended_args(self) -> List[str]:
        """Gera argumentos recomendados baseados no hardware."""
        info = self.get_system_info()
        args = []

        # Sempre recomendado
        args.append("-noPauseOnFocusLoss")

        # RAM baixa
        if info["ram_gb"] < 8:
            args.append("-high")

        # CPU com muitos cores -> desativar HT pode ajudar
        if info["cpu_count"] > 8:
            args.append("-disableHyperthreading")

        # GPU detection
        gpu = info["gpu_name"].upper()
        if "NVIDIA" in gpu or "GEFORCE" in gpu or "AMD" in gpu or "RADEON" in gpu:
            args.append("-DX11")

        return args


class OptimizationManager:
    """Gerencia otimizações do commandline.txt do GTA V."""

    def __init__(self, game_path: str = ""):
        self.game_path = game_path
        self.analyzer = SystemAnalyzer()

    @property
    def commandline_path(self) -> str:
        return os.path.join(self.game_path, "commandline.txt")

    def read_commandline(self) -> str:
        """Lê o commandline.txt atual."""
        if os.path.isfile(self.commandline_path):
            with open(self.commandline_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""

    def write_commandline(self, content: str) -> Tuple[bool, str]:
        """Escreve no commandline.txt."""
        try:
            with open(self.commandline_path, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")
            return True, "✅ commandline.txt salvo com sucesso!"
        except PermissionError:
            return False, "❌ Sem permissão para escrever. Verifique as permissões da pasta."
        except Exception as e:
            return False, f"❌ Erro: {str(e)}"

    def get_current_args(self) -> List[str]:
        """Retorna a lista de argumentos atuais."""
        content = self.read_commandline()
        if not content:
            return []
        return [arg.strip() for arg in content.split() if arg.strip().startswith("-")]

    def apply_preset(self, preset_key: str) -> Tuple[bool, str]:
        """Aplica um preset de otimização."""
        preset = OPTIMIZATION_PRESETS.get(preset_key)
        if not preset:
            return False, f"❌ Preset '{preset_key}' não encontrado."

        all_args = preset["args"] + preset.get("commandline_extra", [])
        content = "\n".join(all_args)
        return self.write_commandline(content)

    def apply_recommended(self) -> Tuple[bool, str]:
        """Aplica otimizações recomendadas pelo sistema."""
        args = self.analyzer.get_recommended_args()
        if not args:
            return True, "ℹ️ Nenhuma otimização adicional necessária."

        content = "\n".join(args)
        return self.write_commandline(content)

    def add_argument(self, arg: str) -> Tuple[bool, str]:
        """Adiciona um argumento ao commandline.txt."""
        current = self.get_current_args()
        if arg in current:
            return True, f"ℹ️ '{arg}' já está no commandline.txt"

        current.append(arg)
        content = "\n".join(current)
        return self.write_commandline(content)

    def remove_argument(self, arg: str) -> Tuple[bool, str]:
        """Remove um argumento do commandline.txt."""
        current = self.get_current_args()
        if arg not in current:
            return True, f"ℹ️ '{arg}' não está no commandline.txt"

        current.remove(arg)
        content = "\n".join(current)
        return self.write_commandline(content)

    def clear_commandline(self) -> Tuple[bool, str]:
        """Limpa o commandline.txt."""
        return self.write_commandline("")

    def get_system_info(self) -> dict:
        """Retorna info do sistema."""
        return self.analyzer.get_system_info()

    def get_recommended_preset(self) -> str:
        """Retorna o preset recomendado."""
        return self.analyzer.get_recommended_preset()

    def get_all_arguments(self) -> List[dict]:
        """Retorna catálogo completo de argumentos."""
        return ALL_ARGUMENTS

    def get_presets(self) -> dict:
        """Retorna todos os presets."""
        return OPTIMIZATION_PRESETS

"""
Módulo Social Club Fixer
Resolve problemas comuns do Rockstar Social Club.
"""

import os
import shutil
import subprocess
import logging
import winreg
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

logger = logging.getLogger("GTAVLauncher")


class SocialClubFixer:
    """Diagnostica e corrige problemas do Social Club."""

    # Caminhos importantes do Social Club
    SC_APPDATA_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Rockstar Games" / "Social Club"
    SC_PROFILES_DIR = SC_APPDATA_DIR / "Profiles"

    DOCUMENTS_DIR = Path(os.environ.get("USERPROFILE", "")) / "Documents" / "Rockstar Games" / "GTA V"
    DOCUMENTS_PROFILES_DIR = DOCUMENTS_DIR / "Profiles"
    SETTINGS_XML = DOCUMENTS_DIR / "settings.xml"

    SC_CACHE_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Rockstar Games" / "Social Club" / "cache"
    SC_LAUNCHER_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Rockstar Games" / "Launcher"

    BACKUP_DIR = Path(os.environ.get("APPDATA", "")) / "GTAVLauncher" / "backups"

    def __init__(self):
        self.issues_found: List[str] = []
        self.fixes_applied: List[str] = []

    def run_diagnostics(self) -> List[dict]:
        """
        Executa diagnóstico completo do Social Club.

        Returns:
            Lista de problemas encontrados com sugestões.
        """
        self.issues_found.clear()
        results = []

        # 1. Verificar diretórios do Social Club
        check = self._check_sc_directories()
        results.append(check)

        # 2. Verificar cache corrompido
        check = self._check_sc_cache()
        results.append(check)

        # 3. Verificar perfis
        check = self._check_profiles()
        results.append(check)

        # 4. Verificar settings.xml
        check = self._check_settings()
        results.append(check)

        # 5. Verificar serviços do Rockstar
        check = self._check_rockstar_services()
        results.append(check)

        # 6. Verificar registro do Windows
        check = self._check_registry()
        results.append(check)

        return results

    def _check_sc_directories(self) -> dict:
        """Verifica os diretórios do Social Club."""
        result = {
            "name": "Diretórios Social Club",
            "status": "ok",
            "message": "",
            "fixable": False,
        }

        if not self.SC_APPDATA_DIR.exists():
            result["status"] = "warning"
            result["message"] = "Diretório do Social Club não encontrado. O Social Club pode não estar instalado."
            result["fixable"] = True
        elif not self.SC_PROFILES_DIR.exists():
            result["status"] = "warning"
            result["message"] = "Diretório de perfis não encontrado. Nenhum login foi feito no Social Club."
        else:
            result["message"] = "✅ Diretórios do Social Club encontrados."

        return result

    def _check_sc_cache(self) -> dict:
        """Verifica se o cache do Social Club pode estar corrompido."""
        result = {
            "name": "Cache do Social Club",
            "status": "ok",
            "message": "",
            "fixable": True,
        }

        if self.SC_CACHE_DIR.exists():
            cache_size = sum(f.stat().st_size for f in self.SC_CACHE_DIR.rglob("*") if f.is_file())
            cache_size_mb = cache_size / (1024 * 1024)

            if cache_size_mb > 500:
                result["status"] = "warning"
                result["message"] = f"⚠️ Cache muito grande ({cache_size_mb:.1f} MB). Recomenda-se limpar."
            else:
                result["message"] = f"✅ Cache do Social Club OK ({cache_size_mb:.1f} MB)."
        else:
            result["message"] = "✅ Cache do Social Club não encontrado (limpo)."
            result["fixable"] = False

        return result

    def _check_profiles(self) -> dict:
        """Verifica perfis do Social Club."""
        result = {
            "name": "Perfis do Social Club",
            "status": "ok",
            "message": "",
            "fixable": False,
        }

        if self.DOCUMENTS_PROFILES_DIR.exists():
            profiles = list(self.DOCUMENTS_PROFILES_DIR.iterdir())
            if profiles:
                result["message"] = f"✅ {len(profiles)} perfil(is) encontrado(s)."
            else:
                result["status"] = "warning"
                result["message"] = "⚠️ Nenhum perfil de jogo encontrado."
        else:
            result["status"] = "info"
            result["message"] = "ℹ️ Diretório de perfis do jogo não encontrado. O jogo ainda não foi executado."

        return result

    def _check_settings(self) -> dict:
        """Verifica o arquivo de configurações."""
        result = {
            "name": "Configurações do Jogo",
            "status": "ok",
            "message": "",
            "fixable": True,
        }

        if self.SETTINGS_XML.exists():
            size = self.SETTINGS_XML.stat().st_size
            if size == 0:
                result["status"] = "error"
                result["message"] = "❌ settings.xml está vazio! O jogo pode não iniciar corretamente."
            elif size < 100:
                result["status"] = "warning"
                result["message"] = "⚠️ settings.xml parece corrompido (muito pequeno)."
            else:
                result["message"] = "✅ settings.xml encontrado e válido."
        else:
            result["status"] = "info"
            result["message"] = "ℹ️ settings.xml não encontrado. Será criado na primeira execução."
            result["fixable"] = False

        return result

    def _check_rockstar_services(self) -> dict:
        """Verifica serviços do Rockstar Launcher."""
        result = {
            "name": "Serviços Rockstar",
            "status": "ok",
            "message": "",
            "fixable": False,
        }

        try:
            output = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq RockstarService.exe", "/NH"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if "RockstarService.exe" in output.stdout:
                result["message"] = "✅ Rockstar Service está em execução."
            else:
                result["status"] = "info"
                result["message"] = "ℹ️ Rockstar Service não está em execução. Será iniciado ao abrir o jogo."
        except Exception:
            result["status"] = "info"
            result["message"] = "ℹ️ Não foi possível verificar os serviços."

        return result

    def _check_registry(self) -> dict:
        """Verifica entradas do registro do GTA V."""
        result = {
            "name": "Registro do Windows",
            "status": "ok",
            "message": "",
            "fixable": False,
        }

        found = False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Rockstar Games\Grand Theft Auto V"
            )
            winreg.CloseKey(key)
            found = True
        except (OSError, FileNotFoundError):
            pass

        if not found:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Rockstar Games\Grand Theft Auto V"
                )
                winreg.CloseKey(key)
                found = True
            except (OSError, FileNotFoundError):
                pass

        if found:
            result["message"] = "✅ Registro do GTA V encontrado."
        else:
            result["status"] = "warning"
            result["message"] = "⚠️ Registro do GTA V não encontrado. Pode causar problemas no lançamento."

        return result

    # ===== Correções =====

    def clear_social_club_cache(self) -> Tuple[bool, str]:
        """Limpa o cache do Social Club."""
        try:
            # Fazer backup primeiro
            if self.SC_CACHE_DIR.exists():
                self._backup_directory(self.SC_CACHE_DIR, "sc_cache")
                shutil.rmtree(self.SC_CACHE_DIR, ignore_errors=True)
                self.SC_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                return True, "✅ Cache do Social Club limpo com sucesso!"

            return True, "ℹ️ Cache já estava limpo."
        except PermissionError:
            return False, "❌ Sem permissão. Feche o Social Club e tente novamente."
        except Exception as e:
            return False, f"❌ Erro ao limpar cache: {str(e)}"

    def clear_launcher_cache(self) -> Tuple[bool, str]:
        """Limpa o cache do Rockstar Launcher."""
        try:
            if self.SC_LAUNCHER_DIR.exists():
                cache_dir = self.SC_LAUNCHER_DIR / "httpcache"
                if cache_dir.exists():
                    self._backup_directory(cache_dir, "launcher_cache")
                    shutil.rmtree(cache_dir, ignore_errors=True)
                    return True, "✅ Cache do Launcher limpo com sucesso!"

            return True, "ℹ️ Cache do Launcher já estava limpo."
        except PermissionError:
            return False, "❌ Sem permissão. Feche o Rockstar Launcher primeiro."
        except Exception as e:
            return False, f"❌ Erro ao limpar cache: {str(e)}"

    def reset_settings(self) -> Tuple[bool, str]:
        """Reseta o settings.xml (faz backup antes)."""
        try:
            if self.SETTINGS_XML.exists():
                self._backup_directory(self.SETTINGS_XML.parent, "settings")
                self.SETTINGS_XML.unlink()
                return True, "✅ settings.xml removido. Será recriado ao iniciar o jogo."
            return True, "ℹ️ settings.xml não existe."
        except Exception as e:
            return False, f"❌ Erro: {str(e)}"

    def fix_all(self) -> List[Tuple[bool, str]]:
        """Aplica todas as correções disponíveis."""
        results = []

        # Encerrar processos do Rockstar primeiro
        self._kill_rockstar_processes()

        results.append(("Cache SC", *self.clear_social_club_cache()))
        results.append(("Cache Launcher", *self.clear_launcher_cache()))

        return results

    def _kill_rockstar_processes(self):
        """Encerra processos do Rockstar."""
        processes = [
            "RockstarService.exe",
            "SocialClubHelper.exe",
            "LauncherPatcher.exe",
        ]
        for proc in processes:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", proc],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            except Exception:
                pass

    def _backup_directory(self, source: Path, label: str):
        """Faz backup de um diretório antes de modificá-lo."""
        try:
            self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.BACKUP_DIR / f"{label}_{timestamp}"

            if source.is_dir():
                shutil.copytree(source, backup_path, dirs_exist_ok=True)
            elif source.is_file():
                backup_path.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, backup_path / source.name)

            logger.info(f"Backup criado: {backup_path}")
        except Exception as e:
            logger.warning(f"Falha ao criar backup: {e}")

    def get_backup_list(self) -> List[dict]:
        """Lista os backups disponíveis."""
        backups = []
        if self.BACKUP_DIR.exists():
            for item in sorted(self.BACKUP_DIR.iterdir(), reverse=True):
                if item.is_dir():
                    size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                    backups.append({
                        "name": item.name,
                        "path": str(item),
                        "size_mb": size / (1024 * 1024),
                        "date": item.stat().st_mtime,
                    })
        return backups

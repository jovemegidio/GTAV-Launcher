"""
Módulo Network Manager - Gerencia regras de firewall para GTA V
Permite bloquear/desbloquear conexões de rede do jogo.
"""

import subprocess
import logging
import os
from typing import Tuple, List

logger = logging.getLogger("GTAVLauncher")


class NetworkManager:
    """
    Gerencia regras de firewall do Windows para GTA V.
    Permite bloquear completamente a conexão do jogo para modo offline total.
    """

    RULE_PREFIX = "GTAVLauncher"

    # Executáveis do GTA V que fazem conexões
    GTA_EXECUTABLES = [
        "GTA5.exe",
        "GTAVLauncher.exe",
        "PlayGTAV.exe",
    ]

    # Portas usadas pelo GTA Online
    GTA_ONLINE_PORTS = [
        ("6672", "UDP"),
        ("61455", "UDP"),
        ("61457", "UDP"),
        ("61458", "UDP"),
    ]

    def __init__(self, game_path: str = ""):
        self.game_path = game_path

    def is_admin(self) -> bool:
        """Verifica se o programa está rodando como administrador."""
        try:
            result = subprocess.run(
                ["net", "session"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return result.returncode == 0
        except Exception:
            return False

    def block_gta_network(self) -> Tuple[bool, str]:
        """
        Bloqueia todas as conexões de rede do GTA V via Windows Firewall.
        Requer privilégios de administrador.
        """
        if not self.is_admin():
            return False, (
                "❌ Requer privilégios de Administrador!\n"
                "Execute o launcher como Administrador para usar o bloqueio de rede."
            )

        errors = []
        success_count = 0

        for exe_name in self.GTA_EXECUTABLES:
            exe_path = os.path.join(self.game_path, exe_name) if self.game_path else exe_name

            # Bloquear saída (outbound)
            rule_name = f"{self.RULE_PREFIX}_Block_Out_{exe_name}"
            ok, msg = self._add_firewall_rule(
                rule_name=rule_name,
                direction="out",
                action="block",
                program=exe_path,
            )
            if ok:
                success_count += 1
            else:
                errors.append(msg)

            # Bloquear entrada (inbound)
            rule_name = f"{self.RULE_PREFIX}_Block_In_{exe_name}"
            ok, msg = self._add_firewall_rule(
                rule_name=rule_name,
                direction="in",
                action="block",
                program=exe_path,
            )
            if ok:
                success_count += 1
            else:
                errors.append(msg)

        if success_count > 0:
            msg = f"✅ {success_count} regra(s) de firewall criadas com sucesso!\n"
            msg += "O GTA V está bloqueado de acessar a internet."
            if errors:
                msg += f"\n⚠️ {len(errors)} regra(s) falharam."
            return True, msg
        else:
            return False, "❌ Falha ao criar regras de firewall.\n" + "\n".join(errors)

    def unblock_gta_network(self) -> Tuple[bool, str]:
        """
        Remove todas as regras de bloqueio do GTA V.
        Requer privilégios de administrador.
        """
        if not self.is_admin():
            return False, (
                "❌ Requer privilégios de Administrador!\n"
                "Execute o launcher como Administrador para remover o bloqueio."
            )

        removed = 0
        for exe_name in self.GTA_EXECUTABLES:
            for direction in ["Out", "In"]:
                rule_name = f"{self.RULE_PREFIX}_Block_{direction}_{exe_name}"
                ok, _ = self._remove_firewall_rule(rule_name)
                if ok:
                    removed += 1

        if removed > 0:
            return True, f"✅ {removed} regra(s) de firewall removidas!\nO GTA V pode acessar a internet novamente."
        else:
            return True, "ℹ️ Nenhuma regra de bloqueio encontrada para remover."

    def get_block_status(self) -> dict:
        """
        Verifica o status atual das regras de firewall do GTA V.

        Returns:
            Dict com status de cada executável.
        """
        status = {
            "is_blocked": False,
            "rules": [],
            "admin": self.is_admin(),
        }

        try:
            result = subprocess.run(
                [
                    "netsh", "advfirewall", "firewall", "show", "rule",
                    f"name=all", "verbose"
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
            )

            output = result.stdout
            has_block_rules = False

            for exe_name in self.GTA_EXECUTABLES:
                rule_out = f"{self.RULE_PREFIX}_Block_Out_{exe_name}"
                rule_in = f"{self.RULE_PREFIX}_Block_In_{exe_name}"

                out_exists = rule_out in output
                in_exists = rule_in in output

                if out_exists or in_exists:
                    has_block_rules = True
                    status["rules"].append({
                        "exe": exe_name,
                        "outbound_blocked": out_exists,
                        "inbound_blocked": in_exists,
                    })

            status["is_blocked"] = has_block_rules

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.warning(f"Erro ao verificar firewall: {e}")

        return status

    def _add_firewall_rule(
        self,
        rule_name: str,
        direction: str,
        action: str,
        program: str,
    ) -> Tuple[bool, str]:
        """Adiciona uma regra ao Windows Firewall."""
        try:
            # Remover regra existente primeiro
            self._remove_firewall_rule(rule_name)

            cmd = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={rule_name}",
                f"dir={direction}",
                f"action={action}",
                f"program={program}",
                "enable=yes",
                f"profile=any",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
            )

            if result.returncode == 0:
                logger.info(f"Regra de firewall criada: {rule_name}")
                return True, ""
            else:
                error = result.stderr.strip() or result.stdout.strip()
                logger.error(f"Erro ao criar regra {rule_name}: {error}")
                return False, error

        except subprocess.TimeoutExpired:
            return False, "Timeout ao criar regra de firewall."
        except Exception as e:
            return False, str(e)

    def _remove_firewall_rule(self, rule_name: str) -> Tuple[bool, str]:
        """Remove uma regra do Windows Firewall."""
        try:
            cmd = [
                "netsh", "advfirewall", "firewall", "delete", "rule",
                f"name={rule_name}",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
            )

            return result.returncode == 0, ""

        except Exception as e:
            return False, str(e)

    def get_firewall_rules_list(self) -> List[dict]:
        """Lista todas as regras de firewall do launcher."""
        rules = []
        try:
            result = subprocess.run(
                [
                    "netsh", "advfirewall", "firewall", "show", "rule",
                    f"name=all",
                ],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
            )

            current_rule = {}
            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line:
                    if current_rule and self.RULE_PREFIX in current_rule.get("name", ""):
                        rules.append(current_rule)
                    current_rule = {}
                    continue

                if ":" in line:
                    key, _, value = line.partition(":")
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    current_rule[key] = value

            # Não esquecer o último
            if current_rule and self.RULE_PREFIX in current_rule.get("name", ""):
                rules.append(current_rule)

        except Exception as e:
            logger.warning(f"Erro ao listar regras: {e}")

        return rules

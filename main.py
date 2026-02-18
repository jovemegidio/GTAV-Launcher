"""
GTA V Launcher — UI Profissional (Steam / Epic Style)
v3.0 — Interface dark premium com abas, efeitos e otimização.
"""

import sys, os, threading, logging, webbrowser, math, time
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.config import (
    load_config, save_config, detect_game_path,
    detect_platform, validate_game_path,
)
from modules.game_manager import GameManager
from modules.socialclub_fixer import SocialClubFixer
from modules.network_manager import NetworkManager
from modules.optimizer import OptimizationManager, ALL_ARGUMENTS, OPTIMIZATION_PRESETS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GTAVLauncher")

# ═══════════════════════════════════════════════════════
#  DESIGN TOKENS  (paleta inspirada em Steam / Epic)
# ═══════════════════════════════════════════════════════
C = {
    # Backgrounds
    "bg":               "#0d0d0d",
    "bg_alt":           "#111113",
    "sidebar":          "#0a0a0c",
    "card":             "#16161a",
    "card_hover":       "#1c1c22",
    "card_border":      "#232328",
    "input_bg":         "#1a1a20",
    # Accent
    "accent":           "#00e676",
    "accent_hover":     "#69f0ae",
    "accent_dim":       "#004d25",
    "blue":             "#2979ff",
    "blue_hover":       "#448aff",
    "orange":           "#ff9100",
    "orange_hover":     "#ffab40",
    "red":              "#ff1744",
    "red_hover":        "#ff5252",
    "purple":           "#7c4dff",
    # Text
    "t1":               "#e8eaed",
    "t2":               "#9aa0a6",
    "t3":               "#5f6368",
    "t4":               "#3c4043",
    # Misc
    "divider":          "#232328",
    "glow":             "#00e67633",
    "shadow":           "#00000066",
}

FONT = "Segoe UI"
FONT_MONO = "Cascadia Code"


# ═══════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════
class GTAVLauncher(ctk.CTk):

    VERSION = "3.0.0"

    def __init__(self):
        super().__init__()

        self.config = load_config()
        self.game_manager: GameManager | None = None
        self.sc_fixer = SocialClubFixer()
        self.net_mgr = NetworkManager()
        self.optimizer: OptimizationManager | None = None

        self._setup_window()
        self._auto_detect()
        self._build()
        self._refresh_status()

    # ── window ──────────────────────────────────────────
    def _setup_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("GTA V Launcher")
        self.configure(fg_color=C["bg"])
        w, h = 1080, 700
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(960, 640)

        icon = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.isfile(icon):
            self.iconbitmap(icon)

    def _auto_detect(self):
        gp = self.config.get("game_path", "")
        if not gp or not validate_game_path(gp):
            gp = detect_game_path()
            if gp:
                self.config["game_path"] = gp
                save_config(self.config)
        if validate_game_path(self.config.get("game_path", "")):
            self.game_manager = GameManager(self.config["game_path"])
            self.net_mgr.game_path = self.config["game_path"]
            self.optimizer = OptimizationManager(self.config["game_path"])

    # ══════════════════════════════════════════════════
    #  BUILD
    # ══════════════════════════════════════════════════
    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        # main area
        self.main = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=1)

        self.pages: dict[str, ctk.CTkFrame] = {}
        self._page_home()
        self._page_optimize()
        self._page_diag()
        self._page_network()
        self._page_settings()
        self._page_about()
        self._show("home")

    # ── sidebar ─────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=230, fg_color=C["sidebar"], corner_radius=0,
                          border_width=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        # brand
        br = ctk.CTkFrame(sb, fg_color="transparent")
        br.pack(fill="x", padx=22, pady=(28, 0))

        ctk.CTkLabel(br, text="GTA V", font=ctk.CTkFont(FONT, 28, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        ctk.CTkLabel(br, text="LAUNCHER", font=ctk.CTkFont(FONT, 11, "bold"),
                     text_color=C["t3"]).pack(anchor="w")
        ctk.CTkLabel(br, text=f"v{self.VERSION}", font=ctk.CTkFont(FONT, 9),
                     text_color=C["t4"]).pack(anchor="w", pady=(1, 0))

        ctk.CTkFrame(sb, height=1, fg_color=C["divider"]).pack(fill="x", padx=22, pady=(18, 12))

        # nav
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        items = [
            ("home",     "🎮   JOGAR"),
            ("optimize", "⚡   OTIMIZAÇÃO"),
            ("diag",     "🔧   DIAGNÓSTICO"),
            ("network",  "🛡️   REDE"),
            ("settings", "⚙️   CONFIGURAÇÕES"),
            ("about",    "ℹ️   SOBRE"),
        ]
        for key, label in items:
            b = ctk.CTkButton(
                sb, text=label, font=ctk.CTkFont(FONT, 13),
                fg_color="transparent", text_color=C["t2"],
                hover_color=C["card_hover"], anchor="w",
                height=40, corner_radius=8,
                command=lambda k=key: self._show(k),
            )
            b.pack(fill="x", padx=14, pady=1)
            self._nav_btns[key] = b

        # spacer
        ctk.CTkFrame(sb, fg_color="transparent").pack(fill="both", expand=True)

        # status pill
        self._pill = ctk.CTkFrame(sb, fg_color=C["card"], corner_radius=12,
                                  border_width=1, border_color=C["card_border"])
        self._pill.pack(fill="x", padx=14, pady=(0, 10))

        self._st_dot = ctk.CTkLabel(self._pill, text="⬤  Verificando…",
                                    font=ctk.CTkFont(FONT, 11), text_color=C["t3"])
        self._st_dot.pack(padx=14, pady=(10, 4))

        self._st_plat = ctk.CTkLabel(self._pill, text="",
                                     font=ctk.CTkFont(FONT, 10), text_color=C["t4"])
        self._st_plat.pack(padx=14, pady=(0, 10))

    # ── navigation ──────────────────────────────────────
    def _show(self, key):
        for k, p in self.pages.items():
            p.pack_forget()
        if key in self.pages:
            self.pages[key].pack(fill="both", expand=True)
        for k, b in self._nav_btns.items():
            if k == key:
                b.configure(fg_color=C["card"], text_color=C["accent"])
            else:
                b.configure(fg_color="transparent", text_color=C["t2"])
        if key == "network":
            self._refresh_fw()
        if key == "optimize":
            self._refresh_opt()

    # ══════════════════════════════════════════════════
    #  PAGE — HOME (JOGAR)
    # ══════════════════════════════════════════════════
    def _page_home(self):
        p = ctk.CTkFrame(self.main, fg_color=C["bg"])
        self.pages["home"] = p

        # scroll wrapper
        sc = ctk.CTkScrollableFrame(p, fg_color=C["bg"],
                                    scrollbar_button_color=C["card"],
                                    scrollbar_button_hover_color=C["card_hover"])
        sc.pack(fill="both", expand=True)

        # ── hero area ──
        hero = ctk.CTkFrame(sc, fg_color=C["card"], corner_radius=16,
                            border_width=1, border_color=C["card_border"])
        hero.pack(fill="x", padx=28, pady=(24, 12))

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=24, pady=22)

        ctk.CTkLabel(hero_inner, text="PRONTO PARA JOGAR",
                     font=ctk.CTkFont(FONT, 11, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        ctk.CTkLabel(hero_inner, text="Grand Theft Auto V",
                     font=ctk.CTkFont(FONT, 30, "bold"),
                     text_color=C["t1"]).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(hero_inner, text="Escolha seu modo e entre na ação",
                     font=ctk.CTkFont(FONT, 13), text_color=C["t2"]
                     ).pack(anchor="w", pady=(2, 0))

        # ── mode cards (side by side) ──
        cards = ctk.CTkFrame(sc, fg_color="transparent")
        cards.pack(fill="x", padx=28, pady=6)
        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)

        self._mode = ctk.StringVar(value=self.config.get("launch_mode", "offline"))

        self._card_off = self._mode_card(
            cards, col=0,
            icon="🔒", title="MODO OFFLINE",
            sub="Story Mode · Single Player",
            desc="Sem internet necessária\nSem problemas de Social Club",
            value="offline", color=C["accent"],
        )
        self._card_on = self._mode_card(
            cards, col=1,
            icon="🌐", title="MODO ONLINE",
            sub="GTA Online · Multiplayer",
            desc="Requer Social Club ativo\ne conexão com a internet",
            value="online", color=C["blue"],
        )

        # ── quick opts ──
        opts = ctk.CTkFrame(sc, fg_color=C["card"], corner_radius=12,
                            border_width=1, border_color=C["card_border"])
        opts.pack(fill="x", padx=28, pady=6)

        opts_head = ctk.CTkFrame(opts, fg_color="transparent")
        opts_head.pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkLabel(opts_head, text="OPÇÕES RÁPIDAS",
                     font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w")

        opts_row = ctk.CTkFrame(opts, fg_color="transparent")
        opts_row.pack(fill="x", padx=18, pady=(8, 14))

        self._ck_win = ctk.BooleanVar(value=self.config.get("windowed", False))
        self._ck_brd = ctk.BooleanVar(value=self.config.get("borderless", False))
        self._ck_fix = ctk.BooleanVar(value=self.config.get("auto_fix_socialclub", True))

        for text, var in [("Modo Janela", self._ck_win),
                          ("Sem Bordas", self._ck_brd),
                          ("Auto-fix Social Club", self._ck_fix)]:
            ctk.CTkCheckBox(opts_row, text=text, variable=var,
                            font=ctk.CTkFont(FONT, 12), text_color=C["t2"],
                            fg_color=C["accent"], hover_color=C["accent_hover"],
                            border_color=C["card_border"],
                            command=self._save_quick_opts,
                            ).pack(side="left", padx=(0, 22))

        # ── PLAY button ──
        self._btn_play = ctk.CTkButton(
            sc, text="▶   JOGAR OFFLINE",
            font=ctk.CTkFont(FONT, 22, "bold"), text_color="#000",
            height=68, corner_radius=14,
            fg_color=C["accent"], hover_color=C["accent_hover"],
            command=self._on_play,
        )
        self._btn_play.pack(fill="x", padx=28, pady=(12, 4))

        self._btn_kill = ctk.CTkButton(
            sc, text="⏹   ENCERRAR GTA V",
            font=ctk.CTkFont(FONT, 13, "bold"),
            height=38, corner_radius=10,
            fg_color=C["red"], hover_color=C["red_hover"],
            command=self._on_kill,
        )
        # hidden by default

        self._lbl_msg = ctk.CTkLabel(sc, text="", font=ctk.CTkFont(FONT, 12),
                                     text_color=C["t2"])
        self._lbl_msg.pack(padx=28, pady=(4, 16))

        # init visuals
        self._on_mode_changed()

    def _mode_card(self, parent, col, icon, title, sub, desc, value, color):
        sel = self._mode.get() == value
        card = ctk.CTkFrame(parent, fg_color=C["card"], corner_radius=14,
                            border_width=2,
                            border_color=color if sel else C["card_border"])
        card.grid(row=0, column=col, sticky="nsew", padx=6, pady=4)

        inn = ctk.CTkFrame(card, fg_color="transparent")
        inn.pack(fill="both", expand=True, padx=20, pady=18)

        ctk.CTkLabel(inn, text=f"{icon}  {title}",
                     font=ctk.CTkFont(FONT, 16, "bold"),
                     text_color=color if sel else C["t1"]).pack(anchor="w")
        ctk.CTkLabel(inn, text=sub, font=ctk.CTkFont(FONT, 11),
                     text_color=C["t2"]).pack(anchor="w", pady=(2, 8))
        ctk.CTkLabel(inn, text=desc, font=ctk.CTkFont(FONT, 11),
                     text_color=C["t3"], justify="left").pack(anchor="w")
        ctk.CTkRadioButton(inn, text="Selecionado" if sel else "Selecionar",
                           variable=self._mode, value=value,
                           font=ctk.CTkFont(FONT, 12), text_color=color,
                           fg_color=color, hover_color=color,
                           border_color=C["card_border"],
                           command=self._on_mode_changed).pack(anchor="w", pady=(12, 0))
        for w in (card, inn):
            w.bind("<Button-1>", lambda e, v=value: (self._mode.set(v), self._on_mode_changed()))
        return card

    def _on_mode_changed(self):
        m = self._mode.get()
        self.config["launch_mode"] = m
        save_config(self.config)
        if m == "offline":
            self._card_off.configure(border_color=C["accent"])
            self._card_on.configure(border_color=C["card_border"])
            self._btn_play.configure(text="▶   JOGAR OFFLINE",
                                     fg_color=C["accent"], hover_color=C["accent_hover"])
        else:
            self._card_off.configure(border_color=C["card_border"])
            self._card_on.configure(border_color=C["blue"])
            self._btn_play.configure(text="▶   JOGAR ONLINE",
                                     fg_color=C["blue"], hover_color=C["blue_hover"])

    def _save_quick_opts(self):
        self.config["windowed"] = self._ck_win.get()
        self.config["borderless"] = self._ck_brd.get()
        self.config["auto_fix_socialclub"] = self._ck_fix.get()
        save_config(self.config)

    # ══════════════════════════════════════════════════
    #  PAGE — OTIMIZAÇÃO
    # ══════════════════════════════════════════════════
    def _page_optimize(self):
        p = ctk.CTkScrollableFrame(self.main, fg_color=C["bg"],
                                   scrollbar_button_color=C["card"],
                                   scrollbar_button_hover_color=C["card_hover"])
        self.pages["optimize"] = p

        # header
        hd = ctk.CTkFrame(p, fg_color="transparent")
        hd.pack(fill="x", padx=28, pady=(24, 4))
        ctk.CTkLabel(hd, text="OTIMIZAÇÃO", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        ctk.CTkLabel(hd, text="Performance & Command Line",
                     font=ctk.CTkFont(FONT, 26, "bold"), text_color=C["t1"]
                     ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(hd, text="Otimize o GTA V para o seu hardware",
                     font=ctk.CTkFont(FONT, 13), text_color=C["t2"]
                     ).pack(anchor="w", pady=(2, 0))

        # ── System Info Card ──
        sys_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                                border_width=1, border_color=C["card_border"])
        sys_card.pack(fill="x", padx=28, pady=(14, 6))

        ctk.CTkLabel(sys_card, text="💻  SEU HARDWARE",
                     font=ctk.CTkFont(FONT, 11, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 6))

        self._sys_info_frame = ctk.CTkFrame(sys_card, fg_color="transparent")
        self._sys_info_frame.pack(fill="x", padx=18, pady=(0, 14))

        # ── Recomendação do Sistema ──
        rec_card = ctk.CTkFrame(p, fg_color=C["accent_dim"], corner_radius=14,
                                border_width=1, border_color=C["accent"])
        rec_card.pack(fill="x", padx=28, pady=6)

        rec_inner = ctk.CTkFrame(rec_card, fg_color="transparent")
        rec_inner.pack(fill="x", padx=18, pady=14)

        rec_left = ctk.CTkFrame(rec_inner, fg_color="transparent")
        rec_left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(rec_left, text="⭐  RECOMENDAÇÃO DO SISTEMA",
                     font=ctk.CTkFont(FONT, 11, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        self._rec_desc = ctk.CTkLabel(rec_left, text="Analisando seu hardware…",
                                      font=ctk.CTkFont(FONT, 12),
                                      text_color=C["t1"])
        self._rec_desc.pack(anchor="w", pady=(2, 0))
        self._rec_args = ctk.CTkLabel(rec_left, text="",
                                      font=ctk.CTkFont(FONT_MONO, 11),
                                      text_color=C["t2"])
        self._rec_args.pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(rec_inner, text="⚡ Aplicar Recomendado",
                      font=ctk.CTkFont(FONT, 12, "bold"),
                      width=170, height=38, corner_radius=8,
                      fg_color=C["accent"], hover_color=C["accent_hover"],
                      text_color="#000",
                      command=self._apply_recommended
                      ).pack(side="right", padx=(12, 0))

        # ── Presets ──
        pre_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                                border_width=1, border_color=C["card_border"])
        pre_card.pack(fill="x", padx=28, pady=6)

        ctk.CTkLabel(pre_card, text="🎯  PRESETS DE OTIMIZAÇÃO",
                     font=ctk.CTkFont(FONT, 11, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 4))

        self._presets_frame = ctk.CTkFrame(pre_card, fg_color="transparent")
        self._presets_frame.pack(fill="x", padx=18, pady=(4, 14))

        # ── Arguments Toggle Grid ──
        arg_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                                border_width=1, border_color=C["card_border"])
        arg_card.pack(fill="x", padx=28, pady=6)

        ctk.CTkLabel(arg_card, text="🔧  ARGUMENTOS INDIVIDUAIS",
                     font=ctk.CTkFont(FONT, 11, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 4))
        ctk.CTkLabel(arg_card, text="Ative ou desative argumentos individualmente. Cada mudança é salva imediatamente.",
                     font=ctk.CTkFont(FONT, 11), text_color=C["t4"]
                     ).pack(anchor="w", padx=18, pady=(0, 6))

        self._args_frame = ctk.CTkFrame(arg_card, fg_color="transparent")
        self._args_frame.pack(fill="x", padx=18, pady=(0, 14))

        # ── Command Line Editor ──
        cmd_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                                border_width=1, border_color=C["card_border"])
        cmd_card.pack(fill="x", padx=28, pady=6)

        cmd_head = ctk.CTkFrame(cmd_card, fg_color="transparent")
        cmd_head.pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(cmd_head, text="📝  COMMANDLINE.TXT  —  Editor Direto",
                     font=ctk.CTkFont(FONT, 11, "bold"),
                     text_color=C["t3"]).pack(side="left")

        self._cmdline_box = ctk.CTkTextbox(
            cmd_card, height=110, fg_color=C["input_bg"], text_color=C["t1"],
            font=ctk.CTkFont(FONT_MONO, 12), corner_radius=8,
            border_width=1, border_color=C["card_border"],
        )
        self._cmdline_box.pack(fill="x", padx=18, pady=(4, 8))

        cmd_btns = ctk.CTkFrame(cmd_card, fg_color="transparent")
        cmd_btns.pack(fill="x", padx=18, pady=(0, 14))

        ctk.CTkButton(cmd_btns, text="💾  Salvar", font=ctk.CTkFont(FONT, 12, "bold"),
                      height=36, corner_radius=8,
                      fg_color=C["accent"], hover_color=C["accent_hover"],
                      text_color="#000", command=self._save_cmdline).pack(side="left", padx=(0, 6))
        ctk.CTkButton(cmd_btns, text="🔄  Recarregar", font=ctk.CTkFont(FONT, 12),
                      height=36, corner_radius=8,
                      fg_color=C["card_hover"], hover_color=C["t4"],
                      command=self._refresh_opt).pack(side="left", padx=(0, 6))
        ctk.CTkButton(cmd_btns, text="🗑️  Limpar Tudo", font=ctk.CTkFont(FONT, 12),
                      height=36, corner_radius=8,
                      fg_color=C["red"], hover_color=C["red_hover"],
                      command=self._clear_cmdline).pack(side="left")

    def _refresh_opt(self):
        """Popula / atualiza toda a página de otimização."""
        if not self.optimizer:
            self.optimizer = OptimizationManager(self.config.get("game_path", ""))
        self.optimizer.game_path = self.config.get("game_path", "")

        # --- sys info ---
        for w in self._sys_info_frame.winfo_children():
            w.destroy()
        info = self.optimizer.get_system_info()
        specs = [
            ("CPU", info["processor"][:50] or "N/A", f'{info["cpu_count"]} threads'),
            ("RAM", f'{info["ram_gb"]} GB', ""),
            ("GPU", info["gpu_name"][:45], f'{info["vram_mb"]} MB VRAM' if info["vram_mb"] else ""),
            ("OS",  f'Windows {info["os_release"]}', info["architecture"]),
        ]
        for label, val, extra in specs:
            row = ctk.CTkFrame(self._sys_info_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, width=50, font=ctk.CTkFont(FONT, 11, "bold"),
                         text_color=C["accent"], anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(FONT, 11),
                         text_color=C["t1"], anchor="w").pack(side="left", padx=(4, 8))
            if extra:
                ctk.CTkLabel(row, text=extra, font=ctk.CTkFont(FONT, 10),
                             text_color=C["t3"], anchor="w").pack(side="left")

        # --- recommended ---
        rec_key = self.optimizer.get_recommended_preset()
        rec_preset = OPTIMIZATION_PRESETS.get(rec_key, {})
        rec_args = self.optimizer.analyzer.get_recommended_args()
        self._rec_desc.configure(text=f"Preset recomendado: {rec_preset.get('name', rec_key)}")
        self._rec_args.configure(text="  ".join(rec_args) if rec_args else "Nenhum argumento adicional")

        # --- presets ---
        for w in self._presets_frame.winfo_children():
            w.destroy()
        for key, preset in OPTIMIZATION_PRESETS.items():
            is_rec = key == rec_key
            row = ctk.CTkFrame(self._presets_frame,
                               fg_color=C["accent_dim"] if is_rec else C["input_bg"],
                               corner_radius=10)
            row.pack(fill="x", pady=3)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)
            left = ctk.CTkFrame(inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)
            name_txt = preset["name"] + ("  ⭐" if is_rec else "")
            ctk.CTkLabel(left, text=name_txt, font=ctk.CTkFont(FONT, 13, "bold"),
                         text_color=C["t1"]).pack(anchor="w")
            ctk.CTkLabel(left, text=preset["description"], font=ctk.CTkFont(FONT, 11),
                         text_color=C["t3"]).pack(anchor="w")
            # mostrar args do preset
            args_text = "  ".join(preset["args"] + preset.get("commandline_extra", []))
            ctk.CTkLabel(left, text=args_text, font=ctk.CTkFont(FONT_MONO, 10),
                         text_color=C["t4"]).pack(anchor="w", pady=(2, 0))
            ctk.CTkButton(inner, text="Aplicar", width=80, height=32, corner_radius=8,
                          font=ctk.CTkFont(FONT, 11, "bold"),
                          fg_color=C["accent"] if is_rec else C["blue"],
                          hover_color=C["accent_hover"] if is_rec else C["blue_hover"],
                          text_color="#000",
                          command=lambda k=key: self._apply_preset(k)
                          ).pack(side="right")

        # --- argument toggles ---
        for w in self._args_frame.winfo_children():
            w.destroy()

        current_args = self.optimizer.get_current_args()
        self._arg_vars = {}
        cats = {}
        for a in ALL_ARGUMENTS:
            cats.setdefault(a["category"], []).append(a)

        for cat, items in cats.items():
            ctk.CTkLabel(self._args_frame, text=cat.upper(),
                         font=ctk.CTkFont(FONT, 10, "bold"),
                         text_color=C["t3"]).pack(anchor="w", pady=(10, 3))
            for item in items:
                row = ctk.CTkFrame(self._args_frame, fg_color=C["input_bg"], corner_radius=8)
                row.pack(fill="x", pady=2)
                ri = ctk.CTkFrame(row, fg_color="transparent")
                ri.pack(fill="x", padx=12, pady=8)
                var = ctk.BooleanVar(value=item["arg"] in current_args)
                self._arg_vars[item["arg"]] = var
                sw = ctk.CTkSwitch(ri, text="", variable=var, width=44,
                                   fg_color=C["t4"], progress_color=C["accent"],
                                   button_color=C["t1"], button_hover_color=C["accent_hover"],
                                   command=lambda a=item["arg"]: self._toggle_arg(a))
                sw.pack(side="left")
                impact_colors = {"positivo": C["accent"], "negativo": C["red"],
                                 "neutro": C["t2"], "variável": C["orange"]}
                ctk.CTkLabel(ri, text=f'{item["icon"]}  {item["name"]}',
                             font=ctk.CTkFont(FONT, 12, "bold"),
                             text_color=C["t1"]).pack(side="left", padx=(8, 6))
                ctk.CTkLabel(ri, text=item["description"],
                             font=ctk.CTkFont(FONT, 11),
                             text_color=C["t3"]).pack(side="left", padx=(0, 6))
                dot_col = impact_colors.get(item["impact"], C["t3"])
                ctk.CTkLabel(ri, text=f'● {item["impact"]}',
                             font=ctk.CTkFont(FONT, 10), text_color=dot_col).pack(side="right")

        # --- commandline textbox ---
        self._cmdline_box.delete("1.0", "end")
        self._cmdline_box.insert("1.0", self.optimizer.read_commandline())

    def _apply_preset(self, key):
        if not self.optimizer:
            return
        ok, msg = self.optimizer.apply_preset(key)
        if ok:
            self._refresh_opt()
        messagebox.showinfo("Preset", msg)

    def _apply_recommended(self):
        if not self.optimizer:
            return
        ok, msg = self.optimizer.apply_recommended()
        if ok:
            self._refresh_opt()
        messagebox.showinfo("Recomendação", msg)

    def _toggle_arg(self, arg):
        if not self.optimizer:
            return
        var = self._arg_vars.get(arg)
        if var and var.get():
            self.optimizer.add_argument(arg)
        else:
            self.optimizer.remove_argument(arg)
        self._cmdline_box.delete("1.0", "end")
        self._cmdline_box.insert("1.0", self.optimizer.read_commandline())

    def _save_cmdline(self):
        if not self.optimizer:
            return
        content = self._cmdline_box.get("1.0", "end").strip()
        ok, msg = self.optimizer.write_commandline(content)
        messagebox.showinfo("Salvar", msg)
        if ok:
            self._refresh_opt()

    def _clear_cmdline(self):
        if not self.optimizer:
            return
        if messagebox.askyesno("Limpar", "Limpar todo o commandline.txt?"):
            self.optimizer.clear_commandline()
            self._refresh_opt()

    # ══════════════════════════════════════════════════
    #  PAGE — DIAGNÓSTICO
    # ══════════════════════════════════════════════════
    def _page_diag(self):
        p = ctk.CTkScrollableFrame(self.main, fg_color=C["bg"],
                                   scrollbar_button_color=C["card"],
                                   scrollbar_button_hover_color=C["card_hover"])
        self.pages["diag"] = p

        hd = ctk.CTkFrame(p, fg_color="transparent")
        hd.pack(fill="x", padx=28, pady=(24, 4))
        ctk.CTkLabel(hd, text="DIAGNÓSTICO", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        ctk.CTkLabel(hd, text="Social Club & Integridade",
                     font=ctk.CTkFont(FONT, 26, "bold"), text_color=C["t1"]
                     ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(hd, text="Verifique e corrija problemas automaticamente",
                     font=ctk.CTkFont(FONT, 13), text_color=C["t2"]
                     ).pack(anchor="w", pady=(2, 0))

        # actions
        act = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                           border_width=1, border_color=C["card_border"])
        act.pack(fill="x", padx=28, pady=(14, 6))
        ctk.CTkLabel(act, text="AÇÕES RÁPIDAS", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 6))
        row = ctk.CTkFrame(act, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 14))

        for txt, color, hov, tcol, cmd in [
            ("🔍 Diagnóstico Completo", C["blue"], C["blue_hover"], "#fff", self._run_diag),
            ("🧹 Limpar Cache SC", C["orange"], C["orange_hover"], "#000", self._clear_sc),
            ("🧹 Cache Launcher", C["orange"], C["orange_hover"], "#000", self._clear_lc),
            ("🔄 Resetar Settings", C["red"], C["red_hover"], "#fff", self._reset_sett),
        ]:
            ctk.CTkButton(row, text=txt, font=ctk.CTkFont(FONT, 12, "bold"),
                          height=38, corner_radius=8, fg_color=color, hover_color=hov,
                          text_color=tcol,
                          command=cmd).pack(side="left", padx=(0, 6))

        self._diag_frame = ctk.CTkFrame(p, fg_color="transparent")
        self._diag_frame.pack(fill="x", padx=28, pady=6)

        # tips
        tip = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                           border_width=1, border_color=C["card_border"])
        tip.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(tip, text="💡  DICAS", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 6))
        for t in [
            "Cache corrompido é a causa #1 de problemas do Social Club",
            "Limpar cache NÃO apaga saves ou progresso",
            "Backup automático é criado antes de qualquer correção",
            "Use -scOfflineOnly para evitar problemas de autenticação",
        ]:
            ctk.CTkLabel(tip, text=f"  •  {t}", font=ctk.CTkFont(FONT, 11),
                         text_color=C["t3"], anchor="w").pack(anchor="w", padx=18, pady=1)
        ctk.CTkFrame(tip, height=10, fg_color="transparent").pack()

    def _run_diag(self):
        for w in self._diag_frame.winfo_children():
            w.destroy()
        results = self.sc_fixer.run_diagnostics()
        for r in results:
            st = r["status"]
            col = {"ok": C["accent"], "warning": C["orange"],
                   "error": C["red"], "info": C["blue"]}.get(st, C["t3"])
            ico = {"ok": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}.get(st, "•")
            card = ctk.CTkFrame(self._diag_frame, fg_color=C["card"], corner_radius=10,
                                border_width=1, border_color=C["card_border"])
            card.pack(fill="x", pady=3)
            inn = ctk.CTkFrame(card, fg_color="transparent")
            inn.pack(fill="x", padx=14, pady=10)
            ctk.CTkLabel(inn, text=f"{ico}  {r['name']}", font=ctk.CTkFont(FONT, 13, "bold"),
                         text_color=col).pack(anchor="w")
            ctk.CTkLabel(inn, text=r["message"], font=ctk.CTkFont(FONT, 11),
                         text_color=C["t2"]).pack(anchor="w", padx=(24, 0))

    def _clear_sc(self):
        _, m = self.sc_fixer.clear_social_club_cache()
        messagebox.showinfo("Cache", m)

    def _clear_lc(self):
        _, m = self.sc_fixer.clear_launcher_cache()
        messagebox.showinfo("Cache", m)

    def _reset_sett(self):
        if messagebox.askyesno("Reset", "Remover settings.xml? (backup criado)"):
            _, m = self.sc_fixer.reset_settings()
            messagebox.showinfo("Reset", m)

    # ══════════════════════════════════════════════════
    #  PAGE — REDE
    # ══════════════════════════════════════════════════
    def _page_network(self):
        p = ctk.CTkScrollableFrame(self.main, fg_color=C["bg"],
                                   scrollbar_button_color=C["card"],
                                   scrollbar_button_hover_color=C["card_hover"])
        self.pages["network"] = p

        hd = ctk.CTkFrame(p, fg_color="transparent")
        hd.pack(fill="x", padx=28, pady=(24, 4))
        ctk.CTkLabel(hd, text="REDE & FIREWALL", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        ctk.CTkLabel(hd, text="Controle de Conexão",
                     font=ctk.CTkFont(FONT, 26, "bold"), text_color=C["t1"]
                     ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(hd, text="Bloqueie as conexões do GTA V para modo offline total",
                     font=ctk.CTkFont(FONT, 13), text_color=C["t2"]
                     ).pack(anchor="w", pady=(2, 0))

        # status
        st_card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                               border_width=1, border_color=C["card_border"])
        st_card.pack(fill="x", padx=28, pady=(14, 6))
        ctk.CTkLabel(st_card, text="STATUS", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 4))
        self._fw_st = ctk.CTkLabel(st_card, text="", font=ctk.CTkFont(FONT, 14, "bold"),
                                   text_color=C["t2"])
        self._fw_st.pack(anchor="w", padx=18, pady=(0, 2))
        self._fw_admin = ctk.CTkLabel(st_card, text="", font=ctk.CTkFont(FONT, 11),
                                      text_color=C["t3"])
        self._fw_admin.pack(anchor="w", padx=18, pady=(0, 14))

        # actions
        act = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                           border_width=1, border_color=C["card_border"])
        act.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(act, text="AÇÕES", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 6))
        row = ctk.CTkFrame(act, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkButton(row, text="🔒  Bloquear GTA V", height=42, corner_radius=8,
                      font=ctk.CTkFont(FONT, 13, "bold"),
                      fg_color=C["red"], hover_color=C["red_hover"],
                      command=self._fw_block).pack(side="left", padx=(0, 6))
        ctk.CTkButton(row, text="🔓  Desbloquear GTA V", height=42, corner_radius=8,
                      font=ctk.CTkFont(FONT, 13, "bold"),
                      fg_color=C["accent"], hover_color=C["accent_hover"],
                      text_color="#000", command=self._fw_unblock).pack(side="left", padx=(0, 6))
        ctk.CTkButton(row, text="🔄  Atualizar", height=42, corner_radius=8,
                      font=ctk.CTkFont(FONT, 12),
                      fg_color=C["card_hover"], hover_color=C["t4"],
                      command=self._refresh_fw).pack(side="left")

        # rules
        self._fw_rules = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                                      border_width=1, border_color=C["card_border"])
        self._fw_rules.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(self._fw_rules, text="REGRAS ATIVAS",
                     font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 4))
        self._fw_rules_list = ctk.CTkFrame(self._fw_rules, fg_color="transparent")
        self._fw_rules_list.pack(fill="x", padx=18, pady=(0, 14))

        # info
        info = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                            border_width=1, border_color=C["card_border"])
        info.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(info, text="ℹ️  COMO FUNCIONA", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 6))
        for t in [
            "Cria regras no Windows Firewall impedindo GTA V de acessar a internet",
            "Requer privilégios de Administrador para funcionar",
            "Lembre-se de DESBLOQUEAR antes de jogar Online!",
            "As regras persistem após reiniciar o PC — remova quando quiser",
        ]:
            ctk.CTkLabel(info, text=f"  •  {t}", font=ctk.CTkFont(FONT, 11),
                         text_color=C["t3"]).pack(anchor="w", padx=18, pady=1)
        ctk.CTkFrame(info, height=10, fg_color="transparent").pack()

    def _refresh_fw(self):
        self.net_mgr.game_path = self.config.get("game_path", "")
        s = self.net_mgr.get_block_status()
        if s["is_blocked"]:
            self._fw_st.configure(text="🔒  GTA V BLOQUEADO — sem acesso à internet",
                                  text_color=C["red"])
        else:
            self._fw_st.configure(text="🔓  GTA V livre — acesso normal",
                                  text_color=C["accent"])
        self._fw_admin.configure(
            text="✅ Executando como Administrador" if s["admin"]
            else "⚠️ Execute como Admin para bloquear/desbloquear",
            text_color=C["accent"] if s["admin"] else C["orange"])

        for w in self._fw_rules_list.winfo_children():
            w.destroy()
        if s["rules"]:
            for r in s["rules"]:
                parts = []
                if r.get("outbound_blocked"):
                    parts.append("Saída")
                if r.get("inbound_blocked"):
                    parts.append("Entrada")
                ctk.CTkLabel(self._fw_rules_list,
                             text=f'🔴 {r["exe"]}  —  {" + ".join(parts)} bloqueada',
                             font=ctk.CTkFont(FONT, 11), text_color=C["red"]).pack(anchor="w", pady=1)
        else:
            ctk.CTkLabel(self._fw_rules_list, text="Nenhuma regra de bloqueio ativa",
                         font=ctk.CTkFont(FONT, 11), text_color=C["t3"]).pack(anchor="w")

    def _fw_block(self):
        self.net_mgr.game_path = self.config.get("game_path", "")
        _, m = self.net_mgr.block_gta_network()
        messagebox.showinfo("Firewall", m)
        self._refresh_fw()

    def _fw_unblock(self):
        self.net_mgr.game_path = self.config.get("game_path", "")
        _, m = self.net_mgr.unblock_gta_network()
        messagebox.showinfo("Firewall", m)
        self._refresh_fw()

    # ══════════════════════════════════════════════════
    #  PAGE — CONFIGURAÇÕES
    # ══════════════════════════════════════════════════
    def _page_settings(self):
        p = ctk.CTkScrollableFrame(self.main, fg_color=C["bg"],
                                   scrollbar_button_color=C["card"],
                                   scrollbar_button_hover_color=C["card_hover"])
        self.pages["settings"] = p

        hd = ctk.CTkFrame(p, fg_color="transparent")
        hd.pack(fill="x", padx=28, pady=(24, 4))
        ctk.CTkLabel(hd, text="CONFIGURAÇÕES", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        ctk.CTkLabel(hd, text="Caminhos & Preferências",
                     font=ctk.CTkFont(FONT, 26, "bold"), text_color=C["t1"]
                     ).pack(anchor="w", pady=(2, 0))

        # path
        pc = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                          border_width=1, border_color=C["card_border"])
        pc.pack(fill="x", padx=28, pady=(14, 6))
        ctk.CTkLabel(pc, text="📁  CAMINHO DO JOGO", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 6))
        pr = ctk.CTkFrame(pc, fg_color="transparent")
        pr.pack(fill="x", padx=18, pady=(0, 14))
        self._path_entry = ctk.CTkEntry(pr, placeholder_text="Caminho de instalação do GTA V…",
                                        font=ctk.CTkFont(FONT, 12), height=40,
                                        fg_color=C["input_bg"], border_color=C["card_border"],
                                        text_color=C["t1"])
        self._path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        if self.config.get("game_path"):
            self._path_entry.insert(0, self.config["game_path"])
        ctk.CTkButton(pr, text="📂", width=40, height=40, corner_radius=8,
                      fg_color=C["card_hover"], hover_color=C["t4"],
                      font=ctk.CTkFont(size=16),
                      command=self._browse).pack(side="left", padx=(0, 4))
        ctk.CTkButton(pr, text="🔍 Auto-detectar", width=120, height=40, corner_radius=8,
                      fg_color=C["accent"], hover_color=C["accent_hover"],
                      text_color="#000", font=ctk.CTkFont(FONT, 11, "bold"),
                      command=self._auto_set).pack(side="left")

        # custom args
        ac = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                          border_width=1, border_color=C["card_border"])
        ac.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(ac, text="🖥️  ARGUMENTOS EXTRAS DO LAUNCHER",
                     font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 4))
        ctk.CTkLabel(ac, text="Estes argumentos são adicionados a CADA lançamento (além do commandline.txt)",
                     font=ctk.CTkFont(FONT, 11), text_color=C["t4"]
                     ).pack(anchor="w", padx=18, pady=(0, 6))
        self._args_entry = ctk.CTkEntry(ac, placeholder_text="Ex: -high -noPauseOnFocusLoss",
                                        font=ctk.CTkFont(FONT_MONO, 12), height=40,
                                        fg_color=C["input_bg"], border_color=C["card_border"],
                                        text_color=C["t1"])
        self._args_entry.pack(fill="x", padx=18, pady=(0, 14))
        if self.config.get("custom_args"):
            self._args_entry.insert(0, self.config["custom_args"])

        # save
        ctk.CTkButton(p, text="💾   SALVAR CONFIGURAÇÕES",
                      font=ctk.CTkFont(FONT, 16, "bold"), height=52, corner_radius=12,
                      fg_color=C["accent"], hover_color=C["accent_hover"],
                      text_color="#000", command=self._save_cfg
                      ).pack(fill="x", padx=28, pady=14)

    def _browse(self):
        d = filedialog.askdirectory(title="Pasta do GTA V",
                                   initialdir=self.config.get("game_path", "C:\\"))
        if d:
            self._path_entry.delete(0, "end")
            self._path_entry.insert(0, d)

    def _auto_set(self):
        d = detect_game_path()
        if d:
            self._path_entry.delete(0, "end")
            self._path_entry.insert(0, d)
            messagebox.showinfo("Detectado", f"GTA V encontrado:\n{d}")
        else:
            messagebox.showwarning("Não encontrado", "GTA V não detectado automaticamente.")

    def _save_cfg(self):
        path = self._path_entry.get().strip()
        if path and not validate_game_path(path):
            messagebox.showwarning("Inválido", "GTA5.exe não encontrado nessa pasta.")
            return
        self.config["game_path"] = path
        self.config["custom_args"] = self._args_entry.get().strip()
        save_config(self.config)
        if validate_game_path(path):
            self.game_manager = GameManager(path)
            self.net_mgr.game_path = path
            self.optimizer = OptimizationManager(path)
        self._refresh_status()
        messagebox.showinfo("Salvo", "Configurações salvas! ✅")

    # ══════════════════════════════════════════════════
    #  PAGE — SOBRE
    # ══════════════════════════════════════════════════
    def _page_about(self):
        p = ctk.CTkScrollableFrame(self.main, fg_color=C["bg"],
                                   scrollbar_button_color=C["card"],
                                   scrollbar_button_hover_color=C["card_hover"])
        self.pages["about"] = p

        # Header grande
        hd = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=16,
                          border_width=1, border_color=C["card_border"])
        hd.pack(fill="x", padx=28, pady=(24, 12))
        hd_inner = ctk.CTkFrame(hd, fg_color="transparent")
        hd_inner.pack(fill="x", padx=24, pady=22)
        ctk.CTkLabel(hd_inner, text="GTA V", font=ctk.CTkFont(FONT, 42, "bold"),
                     text_color=C["accent"]).pack(anchor="w")
        ctk.CTkLabel(hd_inner, text="LAUNCHER", font=ctk.CTkFont(FONT, 16, "bold"),
                     text_color=C["t3"]).pack(anchor="w")
        ctk.CTkLabel(hd_inner, text=f"Versão {self.VERSION}  •  2026",
                     font=ctk.CTkFont(FONT, 12),
                     text_color=C["t4"]).pack(anchor="w", pady=(4, 0))

        # about
        card = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                            border_width=1, border_color=C["card_border"])
        card.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(card, text=(
            "Launcher profissional para GTA V com suporte a modo Offline e Online.\n"
            "Inclui otimização de commandline, diagnóstico do Social Club e\n"
            "controle de firewall — tudo em uma interface moderna e intuitiva.\n\n"
            "✅  Usa parâmetros oficiais da Rockstar Games\n"
            "✅  Não modifica arquivos do jogo\n"
            "✅  Não bypassa proteções DRM\n"
            "✅  Para uso com cópias legítimas"
        ), font=ctk.CTkFont(FONT, 12), text_color=C["t2"],
            justify="left").pack(padx=18, pady=16, anchor="w")

        # features
        fc = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                          border_width=1, border_color=C["card_border"])
        fc.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(fc, text="FUNCIONALIDADES",
                     font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["t3"]).pack(anchor="w", padx=18, pady=(14, 6))
        for ico, nm, ds in [
            ("🔒", "Modo Offline", "Jogue sem internet com -scOfflineOnly"),
            ("🌐", "Modo Online", "Direto para GTA Online Freemode"),
            ("⚡", "Otimização", "Presets e edição de commandline.txt"),
            ("🔧", "Diagnóstico", "Detecte e corrija problemas do Social Club"),
            ("🛡️", "Firewall", "Bloqueio de rede via Windows Firewall"),
            ("📁", "Auto-detecção", "Steam, Epic Games, Rockstar Launcher"),
        ]:
            row = ctk.CTkFrame(fc, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=3)
            ctk.CTkLabel(row, text=f"{ico}  {nm}", width=170,
                         font=ctk.CTkFont(FONT, 12, "bold"),
                         text_color=C["accent"], anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=ds, font=ctk.CTkFont(FONT, 11),
                         text_color=C["t3"]).pack(side="left")
        ctk.CTkFrame(fc, height=10, fg_color="transparent").pack()

        # legal
        lc = ctk.CTkFrame(p, fg_color=C["card"], corner_radius=14,
                          border_width=1, border_color=C["card_border"])
        lc.pack(fill="x", padx=28, pady=6)
        ctk.CTkLabel(lc, text="⚖️  AVISO LEGAL", font=ctk.CTkFont(FONT, 10, "bold"),
                     text_color=C["orange"]).pack(anchor="w", padx=18, pady=(14, 4))
        ctk.CTkLabel(lc, text=(
            "GTA V e Social Club são marcas da Rockstar Games / Take-Two Interactive.\n"
            "Este projeto não é afiliado nem endossado pela Rockstar Games."
        ), font=ctk.CTkFont(FONT, 11), text_color=C["t3"],
            justify="left").pack(anchor="w", padx=18, pady=(0, 14))

    # ══════════════════════════════════════════════════
    #  ACTIONS  (play / kill / status)
    # ══════════════════════════════════════════════════
    def _on_play(self):
        if not self.game_manager:
            messagebox.showerror("Erro", "Configure o caminho do GTA V em Configurações.")
            self._show("settings")
            return

        self.config["launch_mode"] = self._mode.get()
        self.config["windowed"] = self._ck_win.get()
        self.config["borderless"] = self._ck_brd.get()
        self.config["auto_fix_socialclub"] = self._ck_fix.get()
        save_config(self.config)

        self._btn_play.configure(state="disabled", text="⏳  LANÇANDO…")
        self._lbl_msg.configure(text="Preparando lançamento…", text_color=C["orange"])
        self.update()

        def t():
            ok, msg = self.game_manager.launch_game(self.config)
            self.after(0, lambda: self._play_done(ok, msg))
        threading.Thread(target=t, daemon=True).start()

    def _play_done(self, ok, msg):
        m = self._mode.get()
        txt = "▶   JOGAR OFFLINE" if m == "offline" else "▶   JOGAR ONLINE"
        self._btn_play.configure(state="normal", text=txt)
        if ok:
            self._lbl_msg.configure(text=msg, text_color=C["accent"])
            self._btn_kill.pack(fill="x", padx=28, pady=(6, 0))
        else:
            self._lbl_msg.configure(text=msg, text_color=C["red"])

    def _on_kill(self):
        if self.game_manager:
            ok, msg = self.game_manager.kill_game()
            self._lbl_msg.configure(text=msg, text_color=C["accent"] if ok else C["red"])
            if ok:
                self._btn_kill.pack_forget()

    def _refresh_status(self):
        gp = self.config.get("game_path", "")
        if validate_game_path(gp):
            plat = detect_platform(gp)
            names = {"steam": "Steam", "epic": "Epic Games",
                     "rockstar": "Rockstar Launcher", "unknown": "Desconhecido"}
            self._st_dot.configure(text="⬤  Jogo Detectado", text_color=C["accent"])
            self._st_plat.configure(text=f"🎮 {names.get(plat, '?')}", text_color=C["t2"])
        else:
            self._st_dot.configure(text="⬤  Não Encontrado", text_color=C["red"])
            self._st_plat.configure(text="Configure em ⚙️", text_color=C["t4"])
        self._on_mode_changed()


def main():
    logger.info("Iniciando GTA V Launcher v3…")
    app = GTAVLauncher()
    app.mainloop()


if __name__ == "__main__":
    main()

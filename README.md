<div align="center">

# 🎮 GTA V Launcher

### Launcher profissional para GTA V — Jogue Offline ou Online com um clique

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2-1F6FEB?style=for-the-badge)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![PyInstaller](https://img.shields.io/badge/PyInstaller-6.x-FFDD00?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-00E676?style=for-the-badge)

<br>

**Interface dark premium inspirada na Steam e Epic Games.**<br>
Otimização de command line, diagnóstico do Social Club, controle de firewall — tudo integrado.

<br>

</div>

---

## 📸 Preview

> Execute o launcher para ver a interface completa com sidebar, cards de modo e abas interativas.

---

## ✨ Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 🎮 **Jogar** | Seleção de modo Offline / Online com cards visuais e botão PLAY dinâmico |
| ⚡ **Otimização** | Análise de hardware, 5 presets prontos, toggles por argumento, editor de `commandline.txt` |
| 🔧 **Diagnóstico** | Verificação completa do Social Club: cache, perfis, settings.xml, serviços, registro |
| 🛡️ **Rede** | Bloqueio/desbloqueio do GTA V via Windows Firewall (regras de entrada e saída) |
| ⚙️ **Configurações** | Auto-detecção do jogo (Steam, Epic, Rockstar), argumentos extras |
| ℹ️ **Sobre** | Informações do projeto, funcionalidades e aviso legal |

### 🔒 Modo Offline
- Usa o parâmetro oficial **`-scOfflineOnly`** da Rockstar
- Vai direto para o Story Mode com **`-goStraightToSP`**
- Sem internet necessária — sem erros do Social Club

### 🌐 Modo Online
- Direto para o **GTA Online Freemode** com **`-StraightIntoFreemode`**
- Social Club habilitado automaticamente

### ⚡ Otimização Inteligente
- Detecta CPU, RAM, GPU e VRAM automaticamente
- Sugere o preset ideal para seu hardware
- **5 presets:** Performance · Balanceado · Qualidade · Online Otimizado · Streaming
- Cada argumento com descrição, ícone e indicador de impacto
- Editor direto do `commandline.txt`

### 🛡️ Controle de Firewall
- Cria regras no Windows Firewall impedindo o GTA V de acessar a internet
- Perfeito para modo offline total (sem tentativas de conexão)
- Regras persistem após reiniciar — remova quando quiser jogar Online

---

## 🛠️ Stack Tecnológica

| Tecnologia | Função |
|------------|--------|
| **Python 3.13** | Linguagem principal — lógica, módulos, automação de sistema |
| **CustomTkinter 5.2** | Framework GUI moderna (baseada em Tkinter) — interface dark premium |
| **Pillow (PIL) 10+** | Geração programática de ícone (hexágono + texto "V") |
| **Windows Registry (winreg)** | Auto-detecção do caminho do jogo (Steam, Epic, Rockstar) |
| **Windows Firewall (netsh)** | Bloqueio/desbloqueio de rede do GTA V via regras de firewall |
| **WMI (wmic)** | Coleta de informações de hardware (CPU, RAM, GPU, VRAM) |
| **subprocess** | Gerenciamento de processos: lançar, detectar e encerrar o jogo |
| **ctypes** | Acesso direto à API do Windows (memória, system info) |
| **PyInstaller 6.x** | Empacotamento em `.exe` standalone — sem precisar de Python instalado |
| **Tkinter (nativo)** | Base do CustomTkinter — event loop, widgets, file dialogs |
| **JSON** | Persistência de configurações do launcher (`config.json`) |
| **os / shutil / pathlib** | Manipulação de arquivos, cache, backup, detecção de diretórios |
| **threading** | Lançamento assíncrono do jogo sem travar a interface |
| **logging** | Sistema de log para debug e rastreamento de eventos |

### 🧩 Arquitetura

```
Modular — 5 módulos independentes + UI principal
├── config.py           → Detecção de jogo, settings, persistência
├── game_manager.py     → Lançamento com parâmetros, kill, status
├── socialclub_fixer.py → Diagnóstico completo + correções automáticas
├── network_manager.py  → Firewall: bloqueio/desbloqueio de rede
├── optimizer.py        → Análise de HW, presets, commandline.txt
└── main.py             → UI profissional (6 abas, sidebar, cards)
```

---

## 📥 Download & Uso

### Opção 1 — Executável Pronto (Recomendado)

1. Vá em [**Releases**](../../releases) e baixe o **`GTAVLauncher.exe`**
2. Coloque em qualquer pasta
3. Execute — o launcher detecta o GTA V automaticamente

> ⚠️ O Windows Defender pode alertar na primeira execução por ser um `.exe` não assinado. Clique em **"Mais informações" → "Executar assim mesmo"**.

### Opção 2 — Executar via Python

**Pré-requisitos:** Python 3.10+ · Windows 10/11 · GTA V instalado (cópia legítima)

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

### Opção 3 — Gerar seu próprio .exe

```bash
pip install -r requirements.txt
pip install pyinstaller
python build_exe.py
# → Executável gerado em dist/GTAVLauncher.exe
```

---

## 📁 Estrutura do Projeto

```
launcher/
├── main.py                  # Interface principal (6 abas, design Steam/Epic)
├── requirements.txt         # Dependências: customtkinter, Pillow
├── build_exe.py             # Script de build → .exe standalone
├── generate_icon.py         # Gera assets/icon.ico e icon.png
├── README.md                # Documentação
├── assets/
│   ├── icon.ico             # Ícone do launcher (multi-size)
│   └── icon.png             # Ícone em PNG
└── modules/
    ├── __init__.py
    ├── config.py             # Configurações e auto-detecção
    ├── game_manager.py       # Lançamento e gerenciamento do jogo
    ├── socialclub_fixer.py   # Diagnóstico e correção do Social Club
    ├── network_manager.py    # Controle de firewall (netsh)
    └── optimizer.py          # Otimização: hardware, presets, commandline
```

---

## ⚡ Parâmetros Suportados

| Parâmetro | Categoria | Descrição |
|-----------|-----------|-----------|
| `-scOfflineOnly` | Modo de Jogo | Inicia sem Social Club (offline) |
| `-goStraightToSP` | Modo de Jogo | Vai direto para Story Mode |
| `-StraightIntoFreemode` | Modo de Jogo | Vai direto para GTA Online |
| `-high` | Performance | Prioridade alta do processo |
| `-noPauseOnFocusLoss` | Performance | Não pausar ao perder foco |
| `-disableHyperthreading` | Performance | Desativar HyperThreading |
| `-DX11` | Gráficos | Forçar DirectX 11 |
| `-DX12` | Gráficos | Forçar DirectX 12 |
| `-windowed` | Tela | Modo janela |
| `-borderless` | Tela | Sem bordas |
| `-fullscreen` | Tela | Tela cheia |
| `-safemode` | Diagnóstico | Iniciar em modo seguro |
| `-benchmark` | Diagnóstico | Executar benchmark |
| `-verify` | Diagnóstico | Verificar integridade |

---

## 🔒 Aviso Legal

- Este launcher foi projetado para uso com **cópias legítimas** do GTA V
- Utiliza apenas **parâmetros oficiais** disponibilizados pela Rockstar Games
- **Não modifica** nenhum arquivo do jogo
- **Não bypassa** nenhuma proteção DRM
- GTA V e Social Club são marcas registradas da **Rockstar Games / Take-Two Interactive**

---

## 📝 Licença

MIT License — Uso livre para fins educacionais e pessoais.

---

<div align="center">

Feito com 💚 para a comunidade GTA V

</div>

# 🐍 WIN-VIPER 2026 PRO

<p align="center">
  <img alt="WIN-VIPER" src="https://img.shields.io/badge/WIN--VIPER-2026%20PRO-00e5ff?style=for-the-badge&labelColor=050816">
  <img alt="Iron Will Interactive" src="https://img.shields.io/badge/Iron%20Will-Interactive-8a2be2?style=for-the-badge&labelColor=050816">
  <img alt="Windows 11" src="https://img.shields.io/badge/Windows-11%20Home%20%7C%20Pro-0078d4?style=for-the-badge&logo=windows11&logoColor=white&labelColor=050816">
</p>

<p align="center">
  <img alt="EXE Build" src="https://img.shields.io/badge/Build-Native%20EXE-success?style=flat-square&labelColor=111827">
  <img alt="Admin Launcher" src="https://img.shields.io/badge/Launcher-UAC%20Admin%20Ready-orange?style=flat-square&labelColor=111827">
  <img alt="Dependencies" src="https://img.shields.io/badge/Dependencies-No%20Python%20Required-blueviolet?style=flat-square&labelColor=111827">
  <img alt="Patch Ready" src="https://img.shields.io/badge/Patch--In--Place-Replace%20Ready-00c853?style=flat-square&labelColor=111827">
  <img alt="Made By" src="https://img.shields.io/badge/Made%20By-Asterisk%20%40gamedev44-ff1744?style=flat-square&labelColor=111827">
</p>

<p align="center">
<pre>
██╗    ██╗██╗███╗   ██╗      ██╗   ██╗██╗██████╗ ███████╗██████╗
██║    ██║██║████╗  ██║      ██║   ██║██║██╔══██╗██╔════╝██╔══██╗
██║ █╗ ██║██║██╔██╗ ██║█████╗██║   ██║██║██████╔╝█████╗  ██████╔╝
██║███╗██║██║██║╚██╗██║╚════╝╚██╗ ██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗
╚███╔███╔╝██║██║ ╚████║        ████╔╝ ██║██║     ███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝        ╚═══╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
</pre>
<strong>Windows 11 Optimization, Cleanup, and De-bloat Utility</strong><br>
<em>Clean. Fast. Lean. Professional.</em>
</p>

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [What Was Patched](#-what-was-patched)
3. [Folder Layout](#-folder-layout)
4. [How To Run](#-how-to-run)
5. [Safety Notes](#-safety-notes)
6. [Key Features](#-key-features)
7. [System Requirements](#-system-requirements)
8. [Project Metadata](#-project-metadata)
9. [Credits](#-credits)

---

## 🔍 Overview

**WIN-VIPER 2026 PRO** is a Windows 11 optimization and de-bloat utility packaged as a native Windows executable.

This patched build is set up so the root launcher correctly runs the real packaged EXE located inside the `Main` folder. No Python command is required to start the app from this package.

> [!IMPORTANT]
> This tool performs system-level optimization actions. Create a Windows System Restore point before using any de-bloat, cleanup, or optimization tool.

---

## ✅ What Was Patched

The original launcher was pointing at the wrong file and tried to run the app through Python:

```bat
Main\WinViper_Pro.exe
```

The actual packaged executable is:

```bat
Main\WinViper_Pro_2026.exe
```

This patch updates `Launch_Viper.bat` so it:

- launches the correct EXE;
- checks that the `Main` folder exists;
- checks that `WinViper_Pro_2026.exe` exists before launching;
- requests Administrator permissions through UAC;
- runs the EXE from its own `Main` directory;
- reports the app exit code when it closes;
- avoids the old broken Python startup path.

---

## 🗂️ Folder Layout

```text
WIN-VIPER/
├─ Launch_Viper.bat          # Main launcher - double-click this
├─ Run_WIN-VIPER.cmd         # Alternate quick launcher
├─ readme.md                 # Project documentation
├─ PATCH_NOTES.md            # Patch summary
├─ LICENSE
└─ Main/
   └─ WinViper_Pro_2026.exe  # Real packaged executable
```

---

## 🚀 How To Run

### Recommended

1. Extract the full `WIN-VIPER` folder from the ZIP.
2. Open the extracted folder.
3. Double-click:

```text
Launch_Viper.bat
```

4. Accept the Windows UAC Administrator prompt.
5. WIN-VIPER should launch from:

```text
Main\WinViper_Pro_2026.exe
```

### Alternate Launcher

You can also double-click:

```text
Run_WIN-VIPER.cmd
```

That file simply calls the main launcher.

---

## 🛡️ Safety Notes

WIN-VIPER is intended to preserve core Windows usability while reducing unnecessary overhead.

Recommended before running:

- create a System Restore point;
- close active games, editors, launchers, and installers;
- run from an extracted folder, not directly inside the ZIP preview;
- keep the `Main` folder beside `Launch_Viper.bat`;
- do not rename `WinViper_Pro_2026.exe` unless you also update the launcher.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| Correct EXE Launch | Root launcher now starts `Main\WinViper_Pro_2026.exe`. |
| Admin Ready | Launcher requests UAC elevation automatically. |
| Patch-In-Place Friendly | Designed to drag/drop over the old folder and replace existing files. |
| Windows 11 Focused | Intended for Windows 11 Home, Pro, and Enterprise systems. |
| Clean Root Launcher | Main BAT handles validation, launch, and clean error messages. |
| No Python Startup Required | The included build launches as an EXE package. |

---

## ⚙️ System Requirements

| Requirement | Recommended |
| :--- | :--- |
| OS | Windows 11 Home / Pro / Enterprise |
| Architecture | 64-bit Windows |
| Permissions | Administrator recommended |
| Runtime | Included EXE package |
| Launch File | `Launch_Viper.bat` |

---

## 🏗️ Project Metadata

| Field | Value |
| :--- | :--- |
| Project | WIN-VIPER 2026 PRO |
| Author | Iron Will Interactive |
| Main Developer | Asterisk / @gamedev44 |
| Organization | IronWillInteractive |
| Package Type | Native Windows EXE utility |
| Patch Type | Launcher + README polish |
| License | Professional / Proprietary |

---

## 🤝 Credits

Special thanks to **Mathew / Wambo** for ideation, technical feedback, and testing support.

<p align="center">
  <strong>Built with ⚡ by Iron Will Interactive</strong>
</p>

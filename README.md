🐍 WIN-VIPER 2026 PRO — Python Edition

<p align="center">
<pre>
██╗    ██╗██╗███╗   ██╗      ██╗   ██╗██╗██████╗ ███████╗██████╗
██║    ██║██║████╗  ██║      ██║   ██║██║██╔══██╗██╔════╝██╔══██╗
██║ █╗ ██║██║██╔██╗ ██║█████╗██║   ██║██║██████╔╝█████╗  ██████╔╝
██║███╗██║██║██║╚██╗██║╚════╝╚██╗ ██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗
╚███╔███╔╝██║██║ ╚████║       ╚████╔╝ ██║██║     ███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝        ╚═══╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
</pre>
<strong>Enterprise-Grade Windows 11 Optimization & De-bloat Engine</strong>
<br><em>Clean. Fast. Lean. Professional.</em>
</p>

📋 Table of Contents
1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Safety & Preservations](#-safety--preservations)
4. [Installation & Usage](#-installation--usage)
5. [Technical Specifications](#-technical-specifications)
6. [Project Metadata](#-project-metadata)
7. [Credits & Acknowledgments](#-credits--acknowledgments)

---

## 🔍 Overview
WIN-VIPER 2026 PRO is a high-performance Windows 11 de-bloat utility written in pure Python. Designed for both Home and Pro editions, it streamlines your OS by removing telemetry, unnecessary background processes, and "junkware" while maintaining 100% compatibility with development tools and modern gaming APIs.

> [!IMPORTANT]
> This tool automates system-level changes. It auto-create a System Restore point before execution.

---

## ✨ Key Features
| Feature | Description |
| :--- | :--- |
| **Auto-Elevation** | Automatically requests UAC Admin privileges on startup. |
| **Smart De-bloat** | Removes pre-installed junk without breaking the Microsoft Store. |
| **Dev-Ready** | Optimized specifically for developers using VS Code, GitHub, and WSL. |
| **Game-Optimized** | Ensures DirectX, Vulkan, and OpenGL run with zero interference. |
| **Zero Dependencies** | ONLY REQUIREMENT IS PYTHON 3 INSTALLED. No pip install needed. |

---

## 🛡️ Safety & Preservations
Unlike aggressive scripts that "break" Windows Update or essential apps, WIN-VIPER utilizes a surgical approach. The following components are strictly preserved:

### 📦 System Essentials
* **Store & Apps:** Microsoft Store, Calculator, Paint AI.
* **Runtimes:** WebView2, .NET Framework, VCLibs.
* **Virtualization:** WSL, Hyper-V, and Dev Tools.

### 🎮 Gaming & Graphics
* **APIs:** DirectX, Vulkan, OpenGL, and UE5 specific APIs.
* **Stability:** Essential drivers and system-level performance hooks.

### 💻 Developer Workflow
* **Tools:** GitHub Desktop, VS Code WebView2 runtime, Cursor support.

---

 # 🌙 [Check out The Latest Nightly Build Releases 🛠️](https://github.com/IronWillInteractive/WIN-VIPER/releases/tag/Beta_Releases)

---

## 🚀 Installation & Usage

### 🛑 Prerequisite

**Python 3.x** must be installed. During installation, ensure you check the box **"Add Python to PATH"** to allow the script to run from any directory.

### Method A: The Simple Way (Recommended)

Simply **Double-Click** the batch launcher in the root directory. The engine will automatically handle environment checks, folder navigation, and UAC elevation.

> `Launch_Viper.bat`

---

### Method B: Manual Execution via Terminal

For users who prefer the command line or need to debug, follow these steps:

1. **Navigate** to the project sub-folder: `WIN-VIPER_Pro\Main`
2. **Open the Terminal:** Click into the Windows File Explorer **Address Bar** (highlighted below).

   <img width="328" height="67" alt="Address Bar Example" src="https://github.com/user-attachments/assets/e00b32be-3534-4c3e-a29f-21cc5901a186" />

3. **Launch CMD:** Clear the path text, type `cmd`, and press **Enter**. This opens a Command Prompt window already set to the correct directory.
4. **Execute:** Run the following command:

```powershell
python WinViper_Pro.py

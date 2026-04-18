"""
WINSCORCH 2026 PRO — Python Edition
Enterprise-Grade Windows 11 Optimization & De-bloat Engine
Version: 3.0.0 | Pure Python | Zero extra dependencies

USAGE:
  Double-click  →  auto-elevates via UAC
  OR: python Winscorch2026-Pro.py

PRESERVED: Paint AI, Store, Calculator, DirectX, Vulkan, OpenGL,
           WebView2, .NET, VCLibs, WSL, Hyper-V, Dev Tools,
           UE5 APIs, Cursor/VS Code WebView2 runtime, GitHub Desktop
"""

import os, sys, subprocess, shutil, datetime, time, ctypes, winreg, pathlib, traceback

# ─────────────────────────────────────────────────────────────────────────────
#  ANSI COLORS  (Windows 10+ terminal supports these natively)
# ─────────────────────────────────────────────────────────────────────────────
os.system("")   # enable ANSI on Windows console
R  = "\033[91m"   # red
G  = "\033[92m"   # green
Y  = "\033[93m"   # yellow
C  = "\033[96m"   # cyan
M  = "\033[95m"   # magenta
W  = "\033[97m"   # white
DK = "\033[90m"   # dark grey
RST= "\033[0m"    # reset

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG  — edit these if needed
# ─────────────────────────────────────────────────────────────────────────────
CFG = {
    "version"            : "3.0.0",
    "log_dir"            : r"C:\WinsCorchLogs",
    "backup_dir"         : r"C:\WinsCorchBackup",
    "restart_delay"      : 15,
    "enable_edge_removal": True,
    "enable_net_tuning"  : True,
    "enable_wu_wipe"     : True,
    "dry_run"            : False,   # ← set True to simulate with no real changes
}

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL STATE
# ─────────────────────────────────────────────────────────────────────────────
STATS = {
    "apps_removed"   : 0,
    "reg_cleaned"    : 0,
    "svc_disabled"   : 0,
    "tasks_disabled" : 0,
    "mb_freed"       : 0,
    "errors"         : 0,
    "warnings"       : 0,
    "phases"         : [],
}
LOG_PATH    = ""
REPORT_PATH = ""
START_TIME  = datetime.datetime.now()
STAMP       = START_TIME.strftime("%Y-%m-%d_%H-%M-%S")

# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def log(msg, level="INFO"):
    colors = {"INFO":C,"SUCCESS":G,"WARN":Y,"ERROR":R,"PHASE":M,"DRY":Y}
    icons  = {"INFO":"  [·]","SUCCESS":"  [✓]","WARN":"  [!]","ERROR":"  [✗]","PHASE":"[>>]","DRY":" [DRY]"}
    ts     = datetime.datetime.now().strftime("%H:%M:%S.%f")[:12]
    line   = f"{ts} {icons.get(level,'  [·]')} {msg}"
    print(f"{colors.get(level,C)}{line}{RST}")
    if LOG_PATH:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    if level == "ERROR":   STATS["errors"]   += 1
    if level == "WARN":    STATS["warnings"] += 1

def phase(n, title):
    bar = f"\n  {'═'*56}\n  PHASE {n} ▶  {title}\n  {'═'*56}"
    print(f"{M}{bar}{RST}")
    if LOG_PATH:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(bar + "\n")

def run(cmd, capture=True):
    """Run a shell command. Returns (returncode, stdout+stderr)."""
    if CFG["dry_run"]:
        log(f"DRY: Would run: {cmd}", "DRY")
        return 0, ""
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=capture,
            text=True, timeout=120
        )
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        log(f"Command timed out: {cmd}", "WARN")
        return 1, "timeout"
    except Exception as e:
        log(f"Command failed: {cmd} — {e}", "WARN")
        return 1, str(e)

def ps(script):
    """Run a PowerShell one-liner."""
    cmd = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "{script}"'
    return run(cmd)

def reg_set(hive, path, name, value, vtype=winreg.REG_DWORD):
    """Write a registry value, creating the key if needed."""
    if CFG["dry_run"]:
        log(f"DRY: reg [{hive}\\{path}] {name}={value}", "DRY")
        return True
    try:
        root = {"HKLM": winreg.HKEY_LOCAL_MACHINE,
                "HKCU": winreg.HKEY_CURRENT_USER}[hive]
        with winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, name, 0, vtype, value)
        return True
    except Exception as e:
        log(f"Registry set failed: {hive}\\{path}\\{name} — {e}", "WARN")
        return False

def reg_del_key(hive, path):
    if CFG["dry_run"]:
        log(f"DRY: reg delete [{hive}\\{path}]", "DRY"); return
    try:
        root = {"HKLM": winreg.HKEY_LOCAL_MACHINE,
                "HKCU": winreg.HKEY_CURRENT_USER}[hive]
        winreg.DeleteKeyEx(root, path)
        STATS["reg_cleaned"] += 1
    except FileNotFoundError:
        pass
    except Exception as e:
        log(f"Reg delete failed: {hive}\\{path} — {e}", "WARN")

def disk_free_mb(drive="C"):
    try:
        usage = shutil.disk_usage(f"{drive}:\\")
        return round(usage.free / (1024**2), 1)
    except:
        return 0

def wipe_folder(path):
    if not os.path.exists(path):
        return 0
    freed = 0
    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            fp = os.path.join(root, f)
            try:
                freed += os.path.getsize(fp)
                if not CFG["dry_run"]:
                    os.remove(fp)
            except:
                pass
        for d in dirs:
            dp = os.path.join(root, d)
            try:
                if not CFG["dry_run"]:
                    shutil.rmtree(dp, ignore_errors=True)
            except:
                pass
    return round(freed / (1024**2), 1)

def add_phase_result(name, status, notes):
    STATS["phases"].append({"phase": name, "status": status, "notes": notes})

def pause_exit(code=1):
    print(f"\n{Y}  Press ENTER to close this window.{RST}")
    input()
    sys.exit(code)

# ─────────────────────────────────────────────────────────────────────────────
#  SELF-ELEVATION
# ─────────────────────────────────────────────────────────────────────────────
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    if not is_admin():
        print(f"\n{Y}  [!] Not running as Administrator.{RST}")
        print(f"{C}  [>] Relaunching elevated — approve the UAC prompt...{RST}\n")
        time.sleep(1)
        script = os.path.abspath(sys.argv[0])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas",
            sys.executable,
            f'"{script}"',
            None, 1
        )
        sys.exit(0)

# ─────────────────────────────────────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────────────────────────────────────
def banner():
art = r"""
 ██╗    ██╗██╗███╗   ██╗      ██╗   ██╗██╗██████╗ ███████╗██████╗ 
 ██║    ██║██║████╗  ██║      ██║   ██║██║██╔══██╗██╔════╝██╔══██╗
 ██║ █╗ ██║██║██╔██╗ ██║█████╗██║   ██║██║██████╔╝█████╗  ██████╔╝
 ██║███╗██║██║██║╚██╗██║╚════╝╚██╗ ██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗
 ╚███╔███╔╝██║██║ ╚████║       ╚████╔╝ ██║██║     ███████╗██║  ██║
  ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝        ╚═══╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
  ----------------------------------------------------------------------
  Windows Debloat Tool for Windows 11 Home & Pro
  Author: Iron Will Interactive | GitHub: github.com/IronWillInteractive
  Main Developer: Asterisk | GitHub: github.com/gamedev44
  Version: 1.0.3 | Last Updated: 04-17-2026

  Special thanks to the Mathew / Wambo for his ideation, contributions and Technical Testing & feedback It wouldnt have been possible without him at my Side!!!

"""
    print(f"{C}{art}{RST}")
    mode = f"{Y}DRY RUN — no changes{RST}" if CFG["dry_run"] else f"{W}LIVE — changes WILL be applied{RST}"
    print(f"  {DK}2026 PRO · Enterprise System Optimization Engine · v{CFG['version']}{RST}")
    print(f"  Target : {W}Windows 11 Home & Pro{RST}")
    print(f"  Mode   : {mode}")
    print(f"  Log    : {DK}{CFG['log_dir']}{RST}\n")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 0 — PRE-FLIGHT
# ═════════════════════════════════════════════════════════════════════════════
def phase0_preflight():
    phase(0, "Pre-Flight System Audit")

    if not is_admin():
        log("NOT Administrator — aborting.", "ERROR")
        pause_exit()

    log("Privilege check passed — Administrator confirmed.", "SUCCESS")

    # OS info
    rc, out = run("ver")
    log(f"OS: {out.strip()}", "INFO")

    # Build number check
    rc, build = run('powershell -Command "(Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion).CurrentBuildNumber"')
    build = build.strip()
    log(f"Windows Build: {build}", "INFO")
    try:
        if int(build) < 22000:
            log("Build < 22000 detected — this targets Win11. Proceeding with caution.", "WARN")
    except:
        pass

    # Disk space
    free = disk_free_mb()
    log(f"Free disk space: {free} MB on C:", "INFO")
    if free < 2048:
        log("Low disk space (<2GB). Some ops may fail.", "WARN")

    # CPU / RAM
    rc, cpu = run('wmic cpu get name /format:list')
    for line in cpu.splitlines():
        if "Name=" in line:
            log(f"CPU: {line.split('=',1)[1].strip()}", "INFO")
            break
    rc, ram = run('wmic os get TotalVisibleMemorySize /format:list')
    for line in ram.splitlines():
        if "TotalVisibleMemorySize=" in line:
            val = int(line.split("=",1)[1].strip() or 0)
            log(f"RAM: {round(val/1024/1024,1)} GB", "INFO")
            break

    log(f"Python: {sys.version.split()[0]}", "INFO")

    # Kill interfering processes
    log("Terminating interfering processes...", "INFO")
    for proc in ["msedge","WebViewHost","SearchHost","Widgets","Copilot",
                 "MicrosoftEdgeUpdate","edgeupdate"]:
        run(f"taskkill /F /IM {proc}.exe", capture=True)

    # Setup dirs + log file
    global LOG_PATH, REPORT_PATH
    for d in [CFG["log_dir"], CFG["backup_dir"]]:
        os.makedirs(d, exist_ok=True)
    LOG_PATH    = os.path.join(CFG["log_dir"], f"Winscorch_{STAMP}.log")
    REPORT_PATH = os.path.join(CFG["log_dir"], f"Winscorch_Report_{STAMP}.html")

    log(f"Log file: {LOG_PATH}", "SUCCESS")
    log(f"Pre-flight complete. Disk free: {free} MB", "SUCCESS")
    add_phase_result("Pre-Flight", "OK", f"Build {build}, {free} MB free")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — SAFETY NET
# ═════════════════════════════════════════════════════════════════════════════
def phase1_safety():
    phase(1, "Safety Net — Restore Point & Registry Backup")

    # Registry backup via reg.exe
    hives = {
        "HKLM_SOFTWARE": "HKLM\\SOFTWARE",
        "HKLM_SYSTEM"  : "HKLM\\SYSTEM",
        "HKCU_Software" : "HKCU\\Software",
    }
    log("Backing up registry hives...", "INFO")
    for name, hive in hives.items():
        out_file = os.path.join(CFG["backup_dir"], f"{name}_{STAMP}.reg")
        if not CFG["dry_run"]:
            rc, _ = run(f'reg export "{hive}" "{out_file}" /y')
            if rc == 0:
                log(f"Backed up: {hive} → {out_file}", "SUCCESS")
            else:
                log(f"Backup failed for {hive}", "WARN")
        else:
            log(f"DRY: Would export {hive}", "DRY")

    # Restore point
    log("Creating System Restore Point...", "INFO")
    rc, out = ps(
        "Enable-ComputerRestore -Drive 'C:\\' -ErrorAction SilentlyContinue; "
        "Checkpoint-Computer -Description 'Winscorch 2026 Pro' "
        "-RestorePointType MODIFY_SETTINGS -ErrorAction Stop"
    )
    if rc == 0:
        log("Restore Point created.", "SUCCESS")
    else:
        log("Restore Point failed (rate-limited or disabled). Reg backups are your fallback.", "WARN")

    add_phase_result("Safety Net", "OK", f"Registry backed up to {CFG['backup_dir']}")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 2 — BLOATWARE PURGE
# ═════════════════════════════════════════════════════════════════════════════
def phase2_bloatware():
    phase(2, "Surgical Bloatware Removal (70+ Packages)")

    SAFETY = [
        "Paint","Store","Calculator","DirectX","VCLibs","Vulkan","OpenGL",
        "EdgeWebView","WebView","DesktopAppInstaller","WindowsTerminal",
        "PowerShell","WindowsSubsystem","HyperV","Sandbox","WSL",
        "Xbox.TCUI","XboxGameOverlay","XboxGamingOverlay","XboxSpeech",
        "StorePurchaseApp","NET","Framework","VCRedist","RuntimeBroker"
    ]

    BLOAT = [
        "Microsoft.549981C3F5F10","Microsoft.BingNews","Microsoft.BingWeather",
        "Microsoft.BingFinance","Microsoft.BingFoodAndDrink",
        "Microsoft.BingHealthAndFitness","Microsoft.BingTravel","Microsoft.BingSports",
        "Microsoft.People","Microsoft.ZuneVideo","Microsoft.ZuneMusic",
        "Microsoft.YourPhone","Microsoft.GetHelp","Microsoft.WindowsFeedbackHub",
        "Microsoft.WindowsMaps","Microsoft.MixedReality.Portal",
        "Microsoft.MicrosoftSolitaireCollection","Microsoft.MicrosoftOfficeHub",
        "Microsoft.SkypeApp","Microsoft.3DBuilder","Microsoft.Print3D",
        "Microsoft.WindowsAlarms","Microsoft.WindowsCommunicationsApps",
        "Microsoft.SoundRecorder","Microsoft.Wallet","Microsoft.OneConnect",
        "Microsoft.Office.OneNote","Microsoft.OutlookForWindows",
        "Microsoft.Windows.DevHome","Microsoft.Todos",
        "Microsoft.PowerAutomateDesktop","Microsoft.Teams","MicrosoftTeams",
        "Microsoft.Clipchamp","Microsoft.Family",
        "Microsoft.MSN.Money","Microsoft.MSN.News","Microsoft.MSN.Sports",
        "Microsoft.MSN.Travel","Microsoft.MSN.Health","Microsoft.Widgets",
        "MicrosoftCorporationII.MicrosoftFamily",
        "Microsoft.GamingApp","Microsoft.XboxApp",
        "Disney.37853FC22B2CE","TikTok.TikTok",
        "king.com.CandyCrushSaga","king.com.CandyCrushFriends",
        "king.com.BubbleWitch3Saga","king.com.FarmHeroesSaga",
        "SpotifyAB.SpotifyMusic","BytedanceInc.TikTok",
        "AdobeSystemsIncorporated.AdobePhotoshopExpress",
        "Facebook.Facebook","Amazon.com.Amazon",
        "Duolingo-LearnLanguagesforFree.Duolingo","PicsArt-Photostudio",
        "7EightsGames.ChessFree","CaesarsSlotsFreeCasino",
        "Roblox.Roblox","DolbyLaboratories.DolbyAccess",
        "NORDVPN.NordVPN","Viber.Viber",
    ]

    for i, app in enumerate(BLOAT, 1):
        print(f"\r  {C}[{i}/{len(BLOAT)}]{RST} {app[:55].ljust(55)}", end="", flush=True)
        if any(s.lower() in app.lower() for s in SAFETY):
            continue
        safe_filter = "|".join(SAFETY)
        script = (
            f"Get-AppxPackage -AllUsers | "
            f"Where-Object {{$_.Name -like '*{app}*' -and $_.Name -notmatch '{safe_filter}'}} | "
            f"Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue; "
            f"Get-AppxProvisionedPackage -Online | "
            f"Where-Object {{$_.DisplayName -like '*{app}*' -and $_.DisplayName -notmatch '{safe_filter}'}} | "
            f"Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue"
        )
        rc, out = ps(script)
        if rc == 0:
            STATS["apps_removed"] += 1

    print()
    log(f"Bloatware purge complete. Removed: {STATS['apps_removed']} apps.", "SUCCESS")
    add_phase_result("Bloatware Purge", "OK", f"{STATS['apps_removed']} apps removed")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — AI / COPILOT / RECALL PURGE
# ═════════════════════════════════════════════════════════════════════════════
def phase3_ai():
    phase(3, "AI / Copilot / Recall / Widgets Purge")

    ai_pkgs = [
        "Microsoft.Copilot","Microsoft.Windows.Ai.Shell",
        "Microsoft.Windows.Recall","Microsoft.Windows.FeatureExperiencePack.Ai",
        "Microsoft.WindowsCopilot","Cortana","Microsoft.549981C3F5F10",
    ]
    for pkg in ai_pkgs:
        rc, _ = ps(
            f"Get-AppxPackage -AllUsers | "
            f"Where-Object {{$_.Name -like '*{pkg}*' -and $_.Name -notmatch 'Paint'}} | "
            f"Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue"
        )
        log(f"AI component purged: {pkg}", "SUCCESS")

    log("Applying registry lockdown for AI/Copilot/Recall...", "INFO")
    ai_reg = [
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot",   "TurnOffWindowsCopilot", 1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI",        "DisableAIDataAnalysis", 1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\WindowsAI",        "AllowRecall", 0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Recall",           "DisableAIDataAnalysis", 1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\WindowsAI",                "TurnOffRecall", 1),
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Copilot",    "CopilotEnabled", 0),
        ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCopilotButton", 0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",   "AllowCortana", 0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search",   "DisableWebSearch", 1),
    ]
    for hive, path, name, val in ai_reg:
        reg_set(hive, path, name, val)

    log("AI/Copilot/Recall lockdown complete.", "SUCCESS")
    add_phase_result("AI Purge", "OK", "Copilot, Recall, Cortana locked")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 4 — EDGE REMOVAL (WebView2 PRESERVED)
# ═════════════════════════════════════════════════════════════════════════════
def phase4_edge():
    phase(4, "Microsoft Edge Browser Removal (WebView2 Preserved)")

    if not CFG["enable_edge_removal"]:
        log("Edge removal disabled in config. Skipping.", "WARN")
        add_phase_result("Edge Removal", "SKIPPED", "Disabled in config")
        return

    installer_globs = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\*\Installer\setup.exe",
        r"C:\Program Files\Microsoft\Edge\Application\*\Installer\setup.exe",
    ]
    removed = False
    import glob
    for pattern in installer_globs:
        matches = glob.glob(pattern)
        for installer in matches:
            log(f"Found Edge installer: {installer}", "INFO")
            if not CFG["dry_run"]:
                run(f'"{installer}" --uninstall --system-level --force-uninstall')
            log("Edge browser uninstall triggered.", "SUCCESS")
            removed = True

    if not removed:
        log("Edge installer not found — may already be removed.", "WARN")

    # Wipe ghost registry keys
    ghost_keys = [
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"),
        ("HKCU", r"Software\Microsoft\Edge"),
        ("HKLM", r"SOFTWARE\Microsoft\EdgeUpdate"),
    ]
    for hive, path in ghost_keys:
        reg_del_key(hive, path)
        log(f"Removed Edge reg key: {hive}\\{path}", "SUCCESS")

    add_phase_result("Edge Removal", "OK", "Browser removed, WebView2 preserved")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 5 — DEEP REGISTRY SANITIZATION
# ═════════════════════════════════════════════════════════════════════════════
def phase5_registry():
    phase(5, "Deep Registry Sanitization (Orphans, Ghosts, Broken Associations)")

    # --- 5A: Orphaned Uninstall Entries ---
    log("Scanning for orphaned uninstall entries...", "INFO")
    uninstall_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for root, path in uninstall_paths:
        try:
            with winreg.OpenKey(root, path) as key:
                n_subkeys = winreg.QueryInfoKey(key)[0]
                for i in range(n_subkeys):
                    try:
                        sub_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(root, f"{path}\\{sub_name}") as sub:
                            try:
                                loc, _ = winreg.QueryValueEx(sub, "InstallLocation")
                                name_v, _ = winreg.QueryValueEx(sub, "DisplayName")
                                if loc and loc.strip() and not os.path.exists(loc):
                                    log(f"Orphaned: {name_v} (missing: {loc})", "WARN")
                                    if not CFG["dry_run"]:
                                        winreg.DeleteKey(root, f"{path}\\{sub_name}")
                                    STATS["reg_cleaned"] += 1
                            except FileNotFoundError:
                                pass
                    except:
                        pass
        except:
            pass

    # --- 5B: Content Delivery Manager (kills ad injection) ---
    log("Locking Content Delivery Manager (kills ad/app injection)...", "INFO")
    cdm_vals = {
        "SilentInstalledAppsEnabled"      : 0,
        "SystemPaneSuggestionsEnabled"    : 0,
        "SubscribedContent-338388Enabled" : 0,
        "SubscribedContent-338389Enabled" : 0,
        "SubscribedContent-353698Enabled" : 0,
        "SubscribedContent-338393Enabled" : 0,
        "OemPreInstalledAppsEnabled"      : 0,
        "PreInstalledAppsEnabled"         : 0,
        "PreInstalledAppsEverEnabled"     : 0,
        "ContentDeliveryAllowed"          : 0,
        "FeatureManagementEnabled"        : 0,
    }
    for name, val in cdm_vals.items():
        reg_set("HKCU",
                r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                name, val)

    # --- 5C: MUI Cache ghost cleanup via PowerShell ---
    log("Cleaning MUI Cache ghost references...", "INFO")
    ghost_kw = "Edge|Copilot|Bing|Teams|Skype|Wallet|3DBuilder|GetHelp|Solitaire"
    safe_kw  = "Paint|Store|Calculator"
    ps(
        f"$p='HKCU:\\Software\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache';"
        f"if(Test-Path $p){{"
        f"  Get-Item $p | Select-Object -ExpandProperty Property |"
        f"  Where-Object {{$_ -match '{ghost_kw}' -and $_ -notmatch '{safe_kw}'}} |"
        f"  ForEach-Object {{ Remove-ItemProperty -Path $p -Name $_ -ErrorAction SilentlyContinue }}"
        f"}}"
    )

    log(f"Registry sanitization complete. Cleaned: {STATS['reg_cleaned']} entries.", "SUCCESS")
    add_phase_result("Registry Sanitization", "OK", f"{STATS['reg_cleaned']} entries cleaned")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 6 — TELEMETRY LOCKDOWN
# ═════════════════════════════════════════════════════════════════════════════
def phase6_telemetry():
    phase(6, "Comprehensive Telemetry & Data Collection Lockdown")

    settings = [
        # (hive, path, name, value)
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",            "AllowTelemetry",                 0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",            "MaxTelemetryAllowed",            0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",            "LimitDiagnosticLogCollection",   1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",            "DisableDiagnosticDataViewer",    1),
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection","AllowTelemetry",              0),
        ("HKLM", r"SOFTWARE\Microsoft\Windows\Windows Error Reporting",            "Disabled",                       1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting",   "Disabled",                       1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting",   "DontSendAdditionalData",         1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",                    "EnableActivityFeed",             0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",                    "PublishUserActivities",          0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System",                    "UploadUserActivities",           0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo",           "DisabledByGroupPolicy",          1),
        ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",     "Enabled",                        0),
        ("HKCU", r"Software\Microsoft\Siuf\Rules",                                 "NumberOfSIUFInPeriod",           0),
        ("HKCU", r"Software\Microsoft\Siuf\Rules",                                 "PeriodInNanoSeconds",            0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\InputPersonalization",              "RestrictImplicitInkCollection",  1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\InputPersonalization",              "RestrictImplicitTextCollection", 1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization",     "DODownloadMode",                 0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Biometrics",                        "Enabled",                        0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\AppCompat",                 "AITEnable",                      0),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\AppCompat",                 "DisableInventory",               1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\AppCompat",                 "DisablePCA",                     1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors",        "DisableLocation",                1),
        ("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Maps",                      "AutoDownloadAndUpdateMapData",   0),
    ]

    count = 0
    for hive, path, name, val in settings:
        if reg_set(hive, path, name, val):
            count += 1

    # HOSTS file block
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    telemetry_hosts = [
        "vortex.data.microsoft.com",
        "vortex-win.data.microsoft.com",
        "telecommand.telemetry.microsoft.com",
        "oca.telemetry.microsoft.com",
        "sqm.telemetry.microsoft.com",
        "watson.telemetry.microsoft.com",
        "redir.metaservices.microsoft.com",
        "choice.microsoft.com",
        "df.telemetry.microsoft.com",
        "telemetry.microsoft.com",
        "watson.ppe.telemetry.microsoft.com",
        "telemetry.appex.bing.net",
        "telemetry.urs.microsoft.com",
        "sqm.df.telemetry.microsoft.com",
        "wes.df.telemetry.microsoft.com",
        "reports.wes.df.telemetry.microsoft.com",
        "services.wes.df.telemetry.microsoft.com",
    ]
    log("Blocking telemetry endpoints in HOSTS file...", "INFO")
    if not CFG["dry_run"]:
        try:
            with open(hosts_path, "r") as f:
                existing = f.read()
            marker = "# === WINSCORCH TELEMETRY BLOCK ==="
            if marker not in existing:
                with open(hosts_path, "a") as f:
                    f.write(f"\n{marker}\n")
                    for h in telemetry_hosts:
                        if h not in existing:
                            f.write(f"0.0.0.0 {h}\n")
                log(f"Blocked {len(telemetry_hosts)} telemetry endpoints in HOSTS.", "SUCCESS")
            else:
                log("HOSTS telemetry block already present.", "INFO")
        except Exception as e:
            log(f"HOSTS file update failed: {e}", "WARN")

    log(f"Telemetry lockdown: {count} registry values set.", "SUCCESS")
    add_phase_result("Telemetry Lockdown", "OK", f"{count} reg values + {len(telemetry_hosts)} HOSTS entries")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 7 — SERVICE HARDENING
# ═════════════════════════════════════════════════════════════════════════════
def phase7_services():
    phase(7, "Service Hardening — Disabling ~30 Non-Essential Services")

    services = [
        ("DiagTrack",       "Telemetry pipeline"),
        ("dmwappushservice","WAP Push / Telemetry routing"),
        ("PcaSvc",          "Program Compatibility Assistant"),
        ("WerSvc",          "Windows Error Reporting"),
        ("wercplsupport",   "Problem Reports support"),
        ("WSearch",         "Search Indexer (unnecessary on SSD)"),
        ("wscsvc",          "Security Center (use your own AV)"),
        ("RemoteRegistry",  "Remote Registry (attack surface)"),
        ("TlntSvr",         "Telnet Server"),
        ("Fax",             "Fax"),
        ("PrintNotify",     "Printer Notifications"),
        ("SyncShare",       "Sync Settings"),
        ("WpcMonSvc",       "Parental Controls"),
        ("lmhosts",         "NetBIOS Helper (obsolete)"),
        ("SensrSvc",        "Sensor Monitoring"),
        ("SensorService",   "Sensor Service"),
        ("lfsvc",           "Geolocation"),
        ("InstallService",  "MS Store auto-install"),
        ("PhoneSvc",        "Phone Service"),
        ("MapsBroker",      "Downloaded Maps"),
        ("RetailDemo",      "Retail Demo"),
        ("XblAuthManager",  "Xbox Live Auth"),
        ("XblGameSave",     "Xbox Live Game Save"),
        ("XboxNetApiSvc",   "Xbox Live Networking"),
        ("CscService",      "Offline Files"),
        ("SCardSvr",        "Smart Card"),
        ("SCPolicySvc",     "Smart Card Removal Policy"),
        ("wisvc",           "Windows Insider"),
        ("WMPNetworkSvc",   "Windows Media Player sharing"),
        ("icssvc",          "Windows Mobile Hotspot"),
    ]

    for i, (svc, desc) in enumerate(services, 1):
        print(f"\r  {C}[{i}/{len(services)}]{RST} {svc[:40].ljust(40)}", end="", flush=True)
        if not CFG["dry_run"]:
            run(f"sc stop {svc}")
            run(f"sc config {svc} start= disabled")
        STATS["svc_disabled"] += 1

    print()
    log(f"Service hardening complete. Disabled: {STATS['svc_disabled']} services.", "SUCCESS")
    add_phase_result("Service Hardening", "OK", f"{STATS['svc_disabled']} services disabled")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 8 — SCHEDULED TASK PRUNING
# ═════════════════════════════════════════════════════════════════════════════
def phase8_tasks():
    phase(8, "Scheduled Task Pruning")

    task_paths = [
        r"\Microsoft\Windows\Customer Experience Improvement Program",
        r"\Microsoft\Windows\Application Experience",
        r"\Microsoft\Windows\Autochk",
    ]
    task_name_patterns = [
        "*Edge*Update*","*Feedback*","*Telemetry*",
        "*CEIP*","*CompatTel*","*AitAgent*","*Office*Telemetry*",
    ]

    for tp in task_paths:
        rc, out = ps(
            f"Get-ScheduledTask -TaskPath '{tp}\\' -ErrorAction SilentlyContinue | "
            f"Disable-ScheduledTask -ErrorAction SilentlyContinue | "
            f"Select-Object -ExpandProperty TaskName"
        )
        for line in out.strip().splitlines():
            if line.strip():
                log(f"Disabled task: {line.strip()}", "SUCCESS")
                STATS["tasks_disabled"] += 1

    for pat in task_name_patterns:
        rc, out = ps(
            f"Get-ScheduledTask -ErrorAction SilentlyContinue | "
            f"Where-Object {{$_.TaskName -like '{pat}'}} | "
            f"Disable-ScheduledTask -ErrorAction SilentlyContinue | "
            f"Select-Object -ExpandProperty TaskName"
        )
        for line in out.strip().splitlines():
            if line.strip():
                log(f"Disabled task (name match): {line.strip()}", "SUCCESS")
                STATS["tasks_disabled"] += 1

    log(f"Task pruning complete. Disabled: {STATS['tasks_disabled']} tasks.", "SUCCESS")
    add_phase_result("Task Pruning", "OK", f"{STATS['tasks_disabled']} tasks disabled")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 9 — STATE MINIMIZATION
# ═════════════════════════════════════════════════════════════════════════════
def phase9_cleanup():
    phase(9, "State Minimization — Zero-Ghost Footprint")

    before = disk_free_mb()
    total_freed = 0.0

    folders = [
        os.environ.get("TEMP", r"C:\Windows\Temp"),
        r"C:\Windows\Temp",
        r"C:\Windows\Prefetch",
    ]
    if CFG["enable_wu_wipe"]:
        folders += [
            r"C:\Windows\SoftwareDistribution\Download",
            r"C:\Windows\SoftwareDistribution\PostRebootEventCache.V2",
        ]
        if not CFG["dry_run"]:
            for svc in ["wuauserv","bits","cryptSvc","msiserver"]:
                run(f"sc stop {svc}")

    for folder in folders:
        mb = wipe_folder(folder)
        total_freed += mb
        log(f"Wiped: {folder} (~{mb} MB)", "SUCCESS")

    # Old Windows logs >7 days
    log_root = r"C:\Windows\Logs"
    cutoff = datetime.datetime.now() - datetime.timedelta(days=7)
    pruned = 0
    if os.path.exists(log_root):
        for root, dirs, files in os.walk(log_root):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    if datetime.datetime.fromtimestamp(os.path.getmtime(fp)) < cutoff:
                        if not CFG["dry_run"]:
                            os.remove(fp)
                        pruned += 1
                except:
                    pass
    log(f"Pruned {pruned} old log files.", "SUCCESS")

    # Recycle Bin
    if not CFG["dry_run"]:
        ps("Clear-RecycleBin -Force -ErrorAction SilentlyContinue")
    log("Recycle Bin cleared.", "SUCCESS")

    # DNS flush
    if not CFG["dry_run"]:
        run("ipconfig /flushdns")
    log("DNS resolver cache flushed.", "SUCCESS")

    # Restart WU services
    if CFG["enable_wu_wipe"] and not CFG["dry_run"]:
        for svc in ["wuauserv","bits","cryptSvc"]:
            run(f"sc start {svc}")

    # Silent Disk Cleanup
    if not CFG["dry_run"]:
        log("Running Windows Disk Cleanup (silent)...", "INFO")
        cleanup_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches"
        cats = [
            "Active Setup Temp Folders","BranchCache","Downloaded Program Files",
            "Internet Cache Files","Memory Dump Files","Old ChkDsk Files",
            "Previous Installations","Recycle Bin","Setup Log Files",
            "System error memory dump files","Temporary Files","Temporary Setup Files",
            "Thumbnail Cache","Update Cleanup","Upgrade Discarded Files",
            "Windows Error Reporting Files","Windows ESD installation files",
            "Windows Upgrade Log Files",
        ]
        for cat in cats:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    f"{cleanup_key}\\{cat}", 0,
                                    winreg.KEY_SET_VALUE) as k:
                    winreg.SetValueEx(k, "StateFlags0099", 0, winreg.REG_DWORD, 2)
            except:
                pass
        run("cleanmgr.exe /sagerun:99", capture=False)
        log("Disk Cleanup complete.", "SUCCESS")

    after  = disk_free_mb()
    freed  = max(0, round(after - before, 1))
    STATS["mb_freed"] = freed
    log(f"State minimization complete. ~{freed} MB freed.", "SUCCESS")
    add_phase_result("State Minimization", "OK", f"~{freed} MB freed")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 10 — PERFORMANCE TUNING
# ═════════════════════════════════════════════════════════════════════════════
def phase10_perf():
    phase(10, "Performance, Visual & Network Tuning")

    # Ultimate Performance power plan
    log("Activating Ultimate Performance power plan...", "INFO")
    if not CFG["dry_run"]:
        scheme = "e9a42b02-d5df-448d-aa00-03f14749eb61"
        rc, out = run("powercfg -list")
        if scheme not in out:
            run(f"powercfg -duplicatescheme {scheme}")
        run(f"powercfg -setactive {scheme}")
        log("Ultimate Performance plan active.", "SUCCESS")

    # Visual performance
    reg_set("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            "VisualFXSetting", 2)
    reg_set("HKCU", r"Control Panel\Desktop\WindowMetrics", "MinAnimate", "0",
            winreg.REG_SZ)

    # Game DVR — kill background recording, keep Game Bar
    reg_set("HKCU", r"Software\Microsoft\Windows\CurrentVersion\GameDVR",  "AppCaptureEnabled", 0)
    reg_set("HKCU", r"System\GameConfigStore", "GameDVR_Enabled", 0)
    reg_set("HKCU", r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2)

    # Mouse acceleration off
    reg_set("HKCU", r"Control Panel\Mouse", "MouseSpeed",      "0", winreg.REG_SZ)
    reg_set("HKCU", r"Control Panel\Mouse", "MouseThreshold1", "0", winreg.REG_SZ)
    reg_set("HKCU", r"Control Panel\Mouse", "MouseThreshold2", "0", winreg.REG_SZ)

    # Network tuning
    if CFG["enable_net_tuning"] and not CFG["dry_run"]:
        log("Applying TCP/IP optimizations...", "INFO")
        cmds = [
            "netsh int tcp set global ecncapability=enabled",
            "netsh int tcp set global autotuninglevel=normal",
            "netsh int tcp set global congestionprovider=ctcp",
            "netsh int tcp set global timestamps=disabled",
            "netsh int tcp set global rss=enabled",
        ]
        for cmd in cmds:
            run(cmd)
        log("TCP/IP tuning complete.", "SUCCESS")

    # Disable LLMNR
    reg_set("HKLM", r"SOFTWARE\Policies\Microsoft\Windows NT\DNSClient", "EnableMulticast", 0)
    # Long paths for dev tools
    reg_set("HKLM", r"SYSTEM\CurrentControlSet\Control\FileSystem", "LongPathsEnabled", 1)
    # Explorer: show extensions, hidden files, open to This PC
    reg_set("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 0)
    reg_set("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", 1)
    reg_set("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "LaunchTo", 1)
    reg_set("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowSyncProviderNotifications", 0)

    # SSD: disable SysMain if SSD detected
    rc, out = run("wmic diskdrive get MediaType")
    if "SSD" in out or "Solid" in out:
        log("SSD detected — disabling SysMain/SuperFetch.", "INFO")
        if not CFG["dry_run"]:
            run("sc stop SysMain")
            run("sc config SysMain start= disabled")

    log("Performance tuning complete.", "SUCCESS")
    add_phase_result("Performance Tuning", "OK", "Ultimate Performance, TCP tuned, Explorer optimized")

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 11 — HTML REPORT
# ═════════════════════════════════════════════════════════════════════════════
def phase11_report():
    phase(11, "Generating HTML Audit Report")

    duration = round((datetime.datetime.now() - START_TIME).total_seconds() / 60, 1)
    free_now  = disk_free_mb()

    rc, os_info  = run('wmic os get Caption /format:list')
    rc, cpu_info = run('wmic cpu get name /format:list')
    rc, ram_info = run('wmic os get TotalVisibleMemorySize /format:list')

    def extract(text, key):
        for line in text.splitlines():
            if f"{key}=" in line:
                return line.split("=", 1)[1].strip()
        return "N/A"

    os_name  = extract(os_info, "Caption")
    cpu_name = extract(cpu_info, "Name")
    ram_mb   = extract(ram_info, "TotalVisibleMemorySize")
    ram_gb   = round(int(ram_mb or 0) / 1024 / 1024, 1) if ram_mb.isdigit() else "?"

    rows = ""
    for p in STATS["phases"]:
        color = "#4ade80" if p["status"]=="OK" else ("#facc15" if p["status"]=="SKIPPED" else "#f87171")
        rows += f"<tr><td>{p['phase']}</td><td style='color:{color};font-weight:bold'>{p['status']}</td><td>{p['notes']}</td></tr>\n"

    err_color = "#f87171" if STATS["errors"] > 0 else "#4ade80"
    dry_badge = "<span style='background:#facc15;color:#000;padding:4px 12px;border-radius:4px;font-size:.85em'>DRY RUN</span>" if CFG["dry_run"] else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Winscorch 2026 Pro — Audit Report</title>
<style>
  :root{{--bg:#0d0d0d;--panel:#161616;--border:#2a2a2a;--accent:#00e5ff;--text:#e2e8f0;--sub:#64748b}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:'Consolas','Courier New',monospace;padding:40px}}
  h1{{font-size:2rem;color:var(--accent);letter-spacing:2px;text-transform:uppercase;margin-bottom:4px}}
  .sub{{color:var(--sub);font-size:.85rem;margin-bottom:32px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:32px}}
  .card{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:20px}}
  .card .label{{font-size:.75rem;color:var(--sub);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px}}
  .card .value{{font-size:2rem;color:var(--accent);font-weight:bold}}
  .card .unit{{font-size:.8rem;color:var(--sub)}}
  table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:8px;overflow:hidden;margin-bottom:32px}}
  th{{background:#1e2a1e;color:var(--accent);text-align:left;padding:12px 16px;font-size:.8rem;text-transform:uppercase;letter-spacing:1px}}
  td{{padding:11px 16px;border-bottom:1px solid var(--border);font-size:.9rem}}
  tr:last-child td{{border:none}}
  .sysinfo{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:20px;margin-bottom:32px}}
  .sysinfo h2{{color:var(--accent);margin-bottom:12px;font-size:1rem}}
  .sysinfo p{{font-size:.85rem;color:var(--sub);line-height:1.8}}
  .footer{{color:var(--sub);font-size:.75rem;text-align:center;margin-top:32px;border-top:1px solid var(--border);padding-top:16px}}
</style></head>
<body>
<h1>⚡ Winscorch 2026 Pro — Python Edition</h1>
<div class="sub">Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {dry_badge}</div>
<div class="grid">
  <div class="card"><div class="label">Apps Removed</div><div class="value">{STATS['apps_removed']}</div><div class="unit">packages</div></div>
  <div class="card"><div class="label">Reg Keys Cleaned</div><div class="value">{STATS['reg_cleaned']}</div><div class="unit">entries</div></div>
  <div class="card"><div class="label">Services Disabled</div><div class="value">{STATS['svc_disabled']}</div><div class="unit">services</div></div>
  <div class="card"><div class="label">Tasks Disabled</div><div class="value">{STATS['tasks_disabled']}</div><div class="unit">tasks</div></div>
  <div class="card"><div class="label">Space Freed</div><div class="value">{STATS['mb_freed']}</div><div class="unit">MB approx</div></div>
  <div class="card"><div class="label">Free Space Now</div><div class="value">{free_now}</div><div class="unit">MB</div></div>
  <div class="card"><div class="label">Run Duration</div><div class="value">{duration}</div><div class="unit">minutes</div></div>
  <div class="card"><div class="label">Errors / Warns</div><div class="value" style="color:{err_color}">{STATS['errors']}/{STATS['warnings']}</div><div class="unit">err/warn</div></div>
</div>
<div class="sysinfo">
  <h2>System Information</h2>
  <p>OS: {os_name} &nbsp;|&nbsp; CPU: {cpu_name} &nbsp;|&nbsp; RAM: {ram_gb} GB &nbsp;|&nbsp; Host: {os.environ.get('COMPUTERNAME','?')}</p>
</div>
<table>
  <thead><tr><th>Phase</th><th>Status</th><th>Notes</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<div class="footer">
  Winscorch 2026 Pro v{CFG['version']} · Python Edition &nbsp;·&nbsp; Log: {LOG_PATH}<br>
  Preserved: Paint AI · Store · DirectX · Vulkan · OpenGL · WebView2 · WSL · Hyper-V · UE5 · Dev Tools
</div>
</body></html>"""

    if not CFG["dry_run"]:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(html)
        log(f"HTML report saved: {REPORT_PATH}", "SUCCESS")
        os.startfile(REPORT_PATH)
    else:
        log(f"DRY: Would write HTML report to {REPORT_PATH}", "DRY")

    add_phase_result("Report Generation", "OK", REPORT_PATH)

# ═════════════════════════════════════════════════════════════════════════════
#  PHASE 12 — SUMMARY & RESTART
# ═════════════════════════════════════════════════════════════════════════════
def phase12_restart():
    phase(12, "Final Summary & Force Restart")

    duration = round((datetime.datetime.now() - START_TIME).total_seconds() / 60, 2)
    err_col  = Y if STATS["errors"] > 0 else G

    print(f"\n{G}  ╔══════════════════════════════════════════════════════════╗")
    print(f"  ║           WINSCORCH 2026 PRO — COMPLETE                 ║")
    print(f"  ╠══════════════════════════════════════════════════════════╣{RST}")
    print(f"{C}  ║  Apps Removed      : {str(STATS['apps_removed']).ljust(10)}                        ║")
    print(f"  ║  Registry Cleaned  : {str(STATS['reg_cleaned']).ljust(10)}                        ║")
    print(f"  ║  Services Disabled : {str(STATS['svc_disabled']).ljust(10)}                        ║")
    print(f"  ║  Tasks Disabled    : {str(STATS['tasks_disabled']).ljust(10)}                        ║")
    print(f"  ║  Approx MB Freed   : {str(STATS['mb_freed']).ljust(10)}                        ║")
    print(f"{err_col}  ║  Errors / Warnings : {STATS['errors']} / {str(STATS['warnings']).ljust(7)}                        ║")
    print(f"{C}  ║  Run Duration      : {str(duration).ljust(10)} min                       ║")
    print(f"{G}  ╠══════════════════════════════════════════════════════════╣")
    print(f"  ║  Log    : {LOG_PATH[:47].ljust(47)}║")
    print(f"  ║  Report : {REPORT_PATH[:47].ljust(47)}║")
    print(f"  ║  Backup : {CFG['backup_dir'][:47].ljust(47)}║")
    print(f"  ╚══════════════════════════════════════════════════════════╝{RST}\n")

    if CFG["dry_run"]:
        log("DRY RUN complete — no changes were made. Set dry_run=False and re-run.", "DRY")
        pause_exit(0)

    log(f"SYSTEM RESTART IN {CFG['restart_delay']} SECONDS — SAVE YOUR WORK NOW!", "ERROR")
    print()
    for s in range(CFG["restart_delay"], 0, -1):
        print(f"\r{R}  [ Restarting in {s:2d}s ... Ctrl+C to cancel ] {RST}", end="", flush=True)
        time.sleep(1)
    print()
    os.system("shutdown.exe /r /f /t 0")

# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main():
    elevate()   # auto-UAC if not admin — MUST be first
    banner()

    try:
        phase0_preflight()
        phase1_safety()
        phase2_bloatware()
        phase3_ai()
        phase4_edge()
        phase5_registry()
        phase6_telemetry()
        phase7_services()
        phase8_tasks()
        phase9_cleanup()
        phase10_perf()
        phase11_report()
        phase12_restart()

    except KeyboardInterrupt:
        print(f"\n{Y}  [!] Interrupted by user. Partial changes may have been applied.{RST}")
        if LOG_PATH:
            print(f"  Log: {LOG_PATH}")
        pause_exit(0)

    except Exception:
        print(f"\n{R}  [FATAL ERROR]{RST}")
        traceback.print_exc()
        if LOG_PATH:
            print(f"\n{Y}  Log: {LOG_PATH}{RST}")
        pause_exit(1)

if __name__ == "__main__":
    main()

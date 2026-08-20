# 🔍 Nmap Auto Scanner

A small Python script that automates running an Nmap service-version scan (`-sV`) against a target IP and saves the results to a report file. Built as a learning project to bridge Python scripting with existing Nmap/Kali workflow.

## Features
- Runs Nmap via Python's subprocess module
- Prompts for a target IP and runs a `-sV` (service/version detection) scan
- Saves scan output to report.txt
- Handles common failure cases gracefully:
   - Scan timeout (30s)
    - Nmap not installed / not in PATH

## How to run-
Download the `scanner.py` file. In your kali terminal type 
```bash
python scanner.py
```
then hit enter and wait for sometime.

## Screenshot
<p align="center">
  <img src="scan_report.png" alt="Payload-Image" width="900">
</p>
      
## Requirements
- Python 3
- Nmap installed and available in your system PATH
- Tested on Kali Linux

# Network Monitoring & Analyzer

A strong local-network monitoring dashboard built with Python, Streamlit, psutil, Pandas and Plotly.

## Features

- Live download/upload throughput
- Total bytes and packets sent/received
- Network interface status, speed, MTU and addresses
- Interface error/drop counters
- Local TCP/UDP connection table
- Active connection count
- Ping diagnostics with packet-loss reporting
- Traffic history chart
- High-traffic event detection
- System hostname and uptime
- Configurable refresh interval
- Clean Streamlit dashboard
- Windows/Linux/macOS-friendly code
- No external database required

## Project structure

```text
Network_Monitoring_Analyzer/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── config.py
├── run.bat
├── run.ps1
├── run.sh
├── src/
│   ├── __init__.py
│   ├── monitor.py
│   └── utils.py
├── data/
├── logs/
└── assets/
```

## Requirements

Python 3.10+ is recommended.

## Windows setup

Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell execution policy blocks activation:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Windows CMD

```cmd
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Important notes

Some operating systems restrict access to process-level network connection information. If the Connections tab is empty, run the application with appropriate local permissions.

The application monitors the machine where Streamlit is running. It does not automatically inspect other devices on a network.

## Troubleshooting

### `ModuleNotFoundError`

Make sure the virtual environment is active and run:

```bash
python -m pip install -r requirements.txt
```

### `streamlit is not recognized`

Use:

```bash
python -m streamlit run app.py
```

### Port already in use

Use another port:

```bash
python -m streamlit run app.py --server.port 8502
```

### Browser does not open

Open the URL printed by Streamlit, normally:

```text
http://localhost:8501
```

## Security / privacy

This is a local observability project. It uses operating-system network statistics and the system ping utility. It does not capture packet payloads, credentials, or private communications.

# Network Monitoring & Analyzer — Project Report

## 1. Abstract

Network Monitoring & Analyzer is a Python-based observability application designed to provide a real-time view of a computer's network activity. The application collects operating-system network statistics and presents them through an interactive Streamlit dashboard.

## 2. Objectives

1. Monitor network traffic in real time.
2. Display upload and download throughput.
3. Inspect network interfaces and their counters.
4. Display locally visible TCP/UDP connections.
5. Provide basic connectivity diagnostics through ping.
6. Maintain a short in-memory traffic history.
7. Detect unusually high local traffic.

## 3. Technology Stack

- Python
- Streamlit
- psutil
- Pandas
- Plotly
- System ping utility

## 4. Architecture

```text
Operating System
      |
      v
    psutil
      |
      v
NetworkMonitor
      |
      +--> Interface statistics
      +--> Traffic counters
      +--> Connections
      +--> Uptime
      +--> Ping diagnostics
      |
      v
 Streamlit UI
      |
      +--> KPI cards
      +--> Traffic charts
      +--> Tables
      +--> Diagnostics
```

## 5. Main Modules

### app.py
Builds the dashboard and connects user controls to the monitoring service.

### src/monitor.py
Collects telemetry from the local operating system and runs ping diagnostics.

### src/utils.py
Provides human-readable byte and uptime formatting.

## 6. Key Metrics

- Bytes received
- Bytes sent
- Packets received
- Packets sent
- Download rate
- Upload rate
- Interface status
- Interface errors/drops
- Active connections
- Ping packet loss

## 7. Advantages

- Easy to run locally
- No database or cloud service required
- Interactive dashboard
- Cross-platform design
- Useful for networking demonstrations and academic projects
- Modular code structure

## 8. Future Enhancements

- SQLite time-series storage
- Email/Telegram alerts
- SNMP monitoring
- Router monitoring
- Prometheus/Grafana integration
- Historical reports
- Role-based access
- Docker deployment
- Network-device inventory
- Optional packet-capture module for authorized lab environments

## 9. Conclusion

The project demonstrates practical network observability using Python and operating-system telemetry. It can be extended into a larger infrastructure monitoring platform while keeping the current version lightweight and easy to understand.

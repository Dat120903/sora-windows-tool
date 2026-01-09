# Sora Automation Tool

## 📁 Structure
```
sora_tool/
├── core/                  # Phase 1 + 2 (LOCKED)
│   ├── models.py          # Data classes
│   ├── persistence.py     # SQLite
│   ├── account_manager.py # Account logic
│   ├── state_machine.py   # Job lifecycle
│   ├── queue_engine.py    # Job queue
│   ├── scheduler.py       # Background loop
│   ├── mock_sora_client.py
│   ├── sora_api_adapter.py
│   ├── client_factory.py
│   ├── config.py
│   ├── auth_store.py
│   └── telemetry.py
├── gui/                   # Phase 3
│   ├── controller.py      # Glue layer
│   └── main_window.py     # Tkinter UI
├── tests/
│   ├── test_simulation.py
│   ├── test_shadow_mode.py
│   └── test_canary.py
├── run_gui.py             # GUI launcher
└── requirements.txt
```

## 🚀 Quick Start

### Run GUI
```bash
cd sora_tool
python run_gui.py
```

### Run Tests
```bash
# Core engine test
python tests/test_simulation.py

# Shadow mode test
python tests/test_shadow_mode.py

# Canary test
python tests/test_canary.py
```

## 🖥️ GUI Features

| Section | Description |
|---------|-------------|
| **Job Queue** | View all jobs (ID, Status, Prompt, Retry, Account) |
| **Accounts** | View accounts (Status, Quota, Cooldown) |
| **Logs** | Real-time log output |
| **Controls** | Start / Pause / Stop buttons |
| **Kill Switch** | Emergency stop all operations |
| **Toggles** | Real API / Shadow Mode |

## 🔒 Feature Flags

Config: `~/.sora_tool/config.json`

| Flag | Default | Description |
|------|---------|-------------|
| `use_real_api` | `false` | Use mock client |
| `shadow_mode` | `true` | Read-only mode |
| `kill_switch` | `false` | Emergency stop |

## 🛑 Kill Switch

```python
from sora_tool.core.config import config
config.activate_kill_switch()
```

Or click the **🔴 KILL SWITCH** button in GUI.

## 📦 Dependencies

```bash
pip install -r requirements.txt
```

- `requests` (for real API adapter)
- Tkinter (included with Python on Windows)

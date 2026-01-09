# Sora Automation Tool

## 📁 Structure
```
sora_tool/
├── core/
│   ├── models.py              # Data classes
│   ├── persistence.py         # SQLite
│   ├── account_manager.py     # Account logic
│   ├── state_machine.py       # Job lifecycle
│   ├── queue_engine.py        # Job queue
│   ├── scheduler.py           # Background loop
│   ├── mock_sora_client.py    # Phase 1 mock
│   ├── sora_api_adapter.py    # Real API adapter
│   ├── client_factory.py      # Mock/Real selector
│   ├── config.py              # Feature flags
│   ├── auth_store.py          # Credential storage
│   ├── cookie_import.py       # [NEW] Cookie parser
│   └── telemetry.py           # Latency tracking
├── gui/
│   ├── controller.py          # Glue layer
│   └── main_window.py         # Tkinter UI
├── tests/
│   ├── test_simulation.py     # E2E test (mock)
│   ├── test_shadow_mode.py    # Shadow mode test
│   ├── test_canary.py         # Canary test
│   └── test_readonly_api.py   # [NEW] Real API test
├── run_gui.py                 # GUI launcher
└── requirements.txt
```

## 🚀 Quick Start

### Run GUI
```bash
python run_gui.py
```

### Run Tests
```bash
# Mock tests
python tests/test_simulation.py
python tests/test_shadow_mode.py

# Real API test (requires cookies)
python tests/test_readonly_api.py
```

## 🔐 Cookie Import (Phase 4B-1)

### Step 1: Export cookies from browser
1. Login to sora.com
2. Install [Cookie-Editor](https://cookie-editor.cgagnier.ca/) extension
3. Click extension icon → Export → JSON
4. Save file to: `~/.sora_tool/auth/cookies_export.json`

### Step 2: Import cookies
```python
from sora_tool.core.auth_store import auth_store

# Import cookies for an account
auth_store.import_from_file("my_account", "path/to/cookies.json")
```

### Step 3: Run read-only test
```bash
python tests/test_readonly_api.py
```

## 🔒 Feature Flags

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

## 📊 Phase 4B-1 Endpoints

| Endpoint | Status | Description |
|----------|--------|-------------|
| `get_history` | ✅ Implemented | Get recent videos |
| `get_status` | ✅ Implemented | Check video status |
| `download_video` | ✅ Implemented | Download completed video |
| `create_video` | ⏸️ Shadow only | Disabled until Phase 4B-2 |

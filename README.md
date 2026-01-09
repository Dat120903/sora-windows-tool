# Sora Automation Tool - Phase 2

## 📁 Structure
```
sora_tool/
├── core/
│   ├── models.py              # Job & Account data
│   ├── persistence.py         # SQLite
│   ├── account_manager.py     # Selection logic
│   ├── state_machine.py       # Job lifecycle
│   ├── queue_engine.py        # FIFO queue
│   ├── scheduler.py           # Main loop
│   ├── mock_sora_client.py    # Phase 1 mock
│   ├── sora_client_interface.py  # [NEW] Abstract interface
│   ├── sora_api_adapter.py    # [NEW] Real API adapter
│   ├── client_factory.py      # [NEW] Mock/Real selector
│   ├── config.py              # [NEW] Feature flags
│   ├── auth_store.py          # [NEW] Secure credential storage
│   └── telemetry.py           # [NEW] Latency tracking
└── tests/
    ├── test_simulation.py     # E2E test (mock)
    ├── test_shadow_mode.py    # [NEW] Shadow mode test
    └── test_canary.py         # [NEW] Canary test
```

## 🔒 Feature Flags

Config file: `~/.sora_tool/config.json`

| Flag | Default | Description |
|------|---------|-------------|
| `use_real_api` | `false` | Enable real API adapter |
| `shadow_mode` | `true` | Read-only (no create_video) |
| `kill_switch` | `false` | Emergency stop all API calls |

## 🚀 How to Enable Real API

### Step 1: Shadow Mode Test (Safe)
```bash
python tests/test_shadow_mode.py
```
This tests auth/polling WITHOUT creating actual videos.

### Step 2: Canary Test (1 Job)
```bash
python tests/test_canary.py
```
Runs full flow with a single job.

### Step 3: Enable Programmatically
```python
from sora_tool.core.config import config

# Enable with shadow mode (safe)
config.enable_real_api(shadow_mode=True)

# Enable full mode (careful!)
config.enable_real_api(shadow_mode=False)

# Disable (back to mock)
config.disable_real_api()
```

## 🛑 Kill Switch

Emergency stop ALL real API calls:
```python
from sora_tool.core.config import config
config.activate_kill_switch()
```

Or manually edit `~/.sora_tool/config.json`:
```json
{"kill_switch": true}
```

## 🔐 Credential Storage

Credentials stored in: `~/.sora_tool/auth/`

```python
from sora_tool.core.auth_store import auth_store

# Save credentials
auth_store.save_credentials("account_1", 
    cookies={"session": "...", "token": "..."},
    access_token="...")

# Load
creds = auth_store.load_credentials("account_1")
```

## 📊 Telemetry
```python
from sora_tool.core.telemetry import telemetry
print(telemetry.get_stats())
# {"total_requests": 10, "success_rate": 0.9, "avg_latency_ms": 250}
```

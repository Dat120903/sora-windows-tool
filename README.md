# Sora Automation Tool - Core Engine (Phase 1)

## 📁 Structure
```
sora_tool/
├── core/
│   ├── models.py          # Job & Account dataclasses
│   ├── persistence.py     # SQLite (WAL mode)
│   ├── account_manager.py # Quota & selection logic
│   ├── state_machine.py   # Job lifecycle
│   ├── queue_engine.py    # Job queue
│   ├── scheduler.py       # Main loop
│   └── mock_sora_client.py # Test stub
└── tests/
    └── test_simulation.py # E2E test
```

## 🚀 Run Test
```bash
cd C:\Users\thanh\AIVideo
python sora_tool/tests/test_simulation.py
```

## ✅ Expected Output
```
>>> Starting Test Simulation...
   [Created Account acc_1]
   [Created Job ...]
   Tick 0: Status = ASSIGNED_ACCOUNT
   ...
   Tick 14: Status = DONE
>>> SUCCESS: Job finished!
>>> Test Complete.
```

## 🛠️ Key Features
- **Immediate Persistence**: Every state change is saved to SQLite.
- **Crash Recovery**: Jobs resume from last persisted state.
- **Account Management**: Rule-based selection, cooldown, soft-ban handling.
- **Mock API**: Simulates Sora video generation (3s delay).

---
description: Sora Windows Tool - Project Context & Memory
---

# 🎯 Project: Sora Windows Automation Tool

## Overview
Windows Desktop tool để tự động tạo video từ Sora AI bằng reverse-engineered API.
- **Repo**: https://github.com/Dat120903/sora-windows-tool.git
- **Location**: `C:\Users\thanh\AIVideo\sora_tool\`

## 🔒 Architectural Rules (BẮT BUỘC)
1. GUI KHÔNG chứa business logic
2. Queue Engine KHÔNG biết GUI
3. Sora API Client KHÔNG biết Queue
4. Core Engine chạy độc lập GUI
5. **Tất cả state PHẢI persist ra disk ngay lập tức**

## 📊 Current Status

### ✅ Phase 0: Architecture Design - COMPLETE
- Architecture document: `.agent/workflows/architecture.md`
- 4-layer structure: GUI → Controller → Core Engine → Sora Client

### ✅ Phase 1: Core Engine - COMPLETE
Files implemented:
- `core/models.py` - Job & Account dataclasses
- `core/persistence.py` - SQLite WAL mode
- `core/account_manager.py` - Rule-based selection, quota, cooldown
- `core/state_machine.py` - Full job lifecycle
- `core/queue_engine.py` - FIFO queue
- `core/scheduler.py` - Background tick loop
- `core/mock_sora_client.py` - Test stub

**Job States**: CREATED → QUEUED → WAITING_FOR_ACCOUNT → ASSIGNED_ACCOUNT → CREATING_VIDEO → POLLING_STATUS → RETRY_SCHEDULED → DOWNLOADING → DONE/FAILED

**Account States**: ACTIVE, WAITING_RECOVERY, SOFT_BANNED, COOLDOWN, INVALID

### 🔜 Phase 2: Sora API Client - NEXT
- [ ] Reverse engineer actual Sora endpoints
- [ ] Cookie/token authentication 
- [ ] Polling actual video status
- [ ] Download video without watermark

### ⏳ Phase 3: GUI & Controller - FUTURE
- [ ] PyQt/Electron GUI
- [ ] Controller/Orchestrator pattern

## 🧪 How to Test
```bash
cd C:\Users\thanh\AIVideo\sora_tool
python tests/test_simulation.py
```

## ⚠️ Key Constraints
- ❌ Không web service / SaaS / cloud
- ❌ Không auth user / payment  
- ❌ Không multi-tenant
- ✅ Tool chạy local trên Windows
- ✅ Mock API only until Phase 2

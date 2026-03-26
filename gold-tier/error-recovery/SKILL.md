# 🔄 Error Recovery Skill

**Type**: Utility / Cross-Cutting Concern  
**Purpose**: Retry logic and graceful degradation for all operations  
**Status**: 🚧 Development  

---

## Overview

The Error Recovery module provides robust error handling across all AI Employee operations:
- **Retry Logic**: Automatic retries with exponential backoff
- **Graceful Degradation**: Continue operating when components fail
- **Circuit Breaker**: Stop trying failed operations temporarily
- **Fallback Actions**: Alternative actions when primary fails

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR RECOVERY                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Retry Handler                           │  │
│  │  - Exponential Backoff                               │  │
│  │  - Max Attempts                                      │  │
│  │  - Jitter                                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Circuit Breaker                            │  │
│  │  - Open (failing) → Stop trying                      │  │
│  │  - Half-Open → Try once                              │  │
│  │  - Closed (working) → Normal operation               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Graceful Degradation                        │  │
│  │  - Queue actions locally                             │  │
│  │  - Skip non-critical features                        │  │
│  │  - Notify human of failures                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Error Categories

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| **Transient** | Network timeout, API rate limit | Exponential backoff retry |
| **Authentication** | Expired token, revoked access | Alert human, pause operations |
| **Logic** | Invalid parameters, misinterpretation | Human review queue |
| **Data** | Corrupted file, missing field | Quarantine + alert |
| **System** | Process crash, disk full | Watchdog + auto-restart |

---

## Usage

### Retry Decorator

```python
from error_recovery import with_retry

@with_retry(max_attempts=3, base_delay=1, max_delay=60)
def call_external_api(params):
    # May raise TransientError
    pass
```

### Circuit Breaker

```python
from error_recovery import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=300)

if breaker.can_execute():
    try:
        result = execute_operation()
        breaker.record_success()
    except Exception as e:
        breaker.record_failure()
        raise
else:
    # Circuit is open, skip operation
    logger.warning('Circuit breaker open, skipping operation')
```

### Graceful Degradation

```python
from error_recovery import DegradationMode

degradation = DegradationMode()

# If Odoo is down, queue locally
if not degradation.is_degraded('odoo'):
    try:
        post_to_odoo(data)
    except Exception:
        degradation.set_degraded('odoo')
        queue_locally(data)
else:
    queue_locally(data)
```

---

## Configuration

```json
{
  "retry": {
    "max_attempts": 3,
    "base_delay": 1,
    "max_delay": 60,
    "jitter": true
  },
  "circuit_breaker": {
    "failure_threshold": 5,
    "recovery_timeout": 300,
    "half_open_attempts": 1
  },
  "degradation": {
    "auto_recovery": true,
    "notify_human": true,
    "queue_actions": true
  }
}
```

---

## File Structure

```
error-recovery/
├── SKILL.md
└── scripts/
    ├── retry_handler.py       # Retry logic
    └── circuit_breaker.py     # Circuit breaker pattern
```

---

## Integration

All Gold Tier skills use error recovery:
- Odoo MCP
- Facebook/Instagram Poster
- Twitter Poster
- Email MCP
- Watchers

---

*Error Recovery v0.1 | AI Employee Hackathon 2026*

# 11 System Configuration

## 11.1 Introduction

This appendix centralizes all the Configuration settings of the league system. The settings are divided by component: Gatekeeper, clocks, timeouts, and log server.

## 11.2 Gatekeeper Configuration

### 11.2.1 Quota Settings (Quota)

Table 192: Quota settings

| Setting | Description | Default |
|---------|-------------|---------|
| daily_limit | Maximum daily quota | 500 |
| operational_limit | Operational limit (safety margin) | 400 |
| warning_threshold | Warning threshold (percentage) | 80% |
| reset_hour_utc | Reset time (UTC) | 00:00 |

### 11.2.2 DOS Detection Settings

Table 193: DOS detection settings

| Setting | Description | Default |
|---------|-------------|---------|
| max_requests_per_minute | Maximum requests per minute | 60 |
| max_requests_per_second | Maximum requests per second | 5 |
| block_duration_seconds | Block duration (seconds) | 300 |
| alert_admin | Send alert to administrator | true |

### 11.2.3 Rate Limiting Settings (Rate Limiting)

Table 194: Rate limiting settings

| Setting | Description | Default |
|---------|-------------|---------|
| min_interval_ms | Minimum interval between requests (milliseconds) | 200 |
| burst_size | Allowed burst size | 10 |
| backoff_multiplier | Backoff multiplier | 2.0 |
| max_backoff_seconds | Maximum backoff (seconds) | 60 |

### 11.2.4 Broadcast Consolidation Settings

Table 195: Broadcast consolidation settings

| Setting | Description | Default |
|---------|-------------|---------|
| consolidation_enabled | Broadcast consolidation enabled | true |
| max_recipients_per_email | Maximum recipients per message | 50 |
| subject_format | Subject format with broadcast_id | includes |

### 11.2.5 Full Configuration Example

Gatekeeper Configuration -- JSON

```json
{
  "gatekeeper": {
    "quota": {
      "daily_limit": 500,
      "operational_limit": 400,
      "warning_threshold": 0.8,
      "reset_hour_utc": 0
    },
    "dos_detection": {
      "max_requests_per_minute": 60,
      "max_requests_per_second": 5,
      "block_duration_seconds": 300,
      "alert_admin": true
    },
    "rate_limiting": {
      "min_interval_ms": 200,
      "burst_size": 10,
      "backoff_multiplier": 2.0,
      "max_backoff_seconds": 60
    },
    "broadcast_consolidation": {
      "enabled": true,
      "max_recipients_per_email": 50
    }
  }
}
```

## 11.3 Clocks Configuration

### 11.3.1 Season Settings (Season)

Table 196: Season settings

| Setting | Description | Default |
|---------|-------------|---------|
| total_rounds | Number of rounds in a season | 6 |
| games_per_round | Games per round | 10 |
| warmup_rounds | Warmup rounds before the league | 3 |

### 11.3.2 Registration Settings (Registration)

Table 197: Registration settings

| Setting | Description | Default |
|---------|-------------|---------|
| open_days_before_season | Days before season start | 14 |
| close_hours_before_start | Hours before round 1 start | 24 |
| late_registration_allowed | Allow late registration | false |

### 11.3.3 Round Settings (Round)

Table 198: Round settings

| Setting | Description | Default |
|---------|-------------|---------|
| duration_hours | Round duration (hours) | 3 |
| game_max_duration_minutes | Maximum game duration (minutes) | 30 |
| interval_between_rounds_days | Days between rounds | 7 |

### 11.3.4 Time Windows Settings (Calendar Windows)

Table 199: Time windows settings

| Setting | Description | Default |
|---------|-------------|---------|
| allowed_days | Allowed days | Tuesday, Thursday |
| start_time_gmt | Opening time (GMT) | 18:30 |
| end_time_gmt | Closing time (GMT) | 22:00 |
| grace_period_minutes | Grace period (minutes) | 15 |

### 11.3.5 Full Configuration Example

Clocks Configuration -- JSON

```json
{
  "clocks": {
    "season": {
      "total_rounds": 6,
      "games_per_round": 10,
      "warmup_rounds": 3
    },
    "registration": {
      "open_days_before_season": 14,
      "close_hours_before_start": 24,
      "late_registration_allowed": false
    },
    "round": {
      "duration_hours": 3.5,
      "game_max_duration_minutes": 30,
      "interval_between_rounds_days": 7
    },
    "calendar_windows": {
      "allowed_days": ["tuesday", "thursday"],
      "start_time_gmt": "18:30",
      "end_time_gmt": "22:00",
      "grace_period_minutes": 15
    }
  }
}
```

## 11.4 Timeouts Configuration (Timeouts)

### 11.4.1 Timeout Categories

For a description of the timeout categories and the messages associated with them, see Appendix B, Table 91.

### 11.4.2 Configuration Example

Timeouts Configuration -- JSON

```json
{
  "timeouts": {
    "keep_alive_seconds": 30,
    "critical_seconds": 120,
    "game_flow_seconds": 300,
    "registration_seconds": 600,
    "announcement_seconds": 86400,
    "default_seconds": 3600
  }
}
```

## 11.5 Log Server Configuration

### 11.5.1 Basic Settings

Table 200: Log server settings

| Setting | Description | Default |
|---------|-------------|---------|
| enabled | Log server enabled | true |
| email | Log server address | beit.halevi.700@gmail.com |
| cc_policy | CC policy | all_game_messages |

### 11.5.2 CC Policies

Table 201: CC policy options

| Option | Description |
|--------|-------------|
| all_messages | CC on all messages (including logging) |
| all_game_messages | CC only on game messages |
| critical_only | CC only on critical messages (failures, force majeure) |
| disabled | No CC (not recommended) |

### 11.5.3 Configuration Example

Log Server Configuration -- JSON

```json
{
  "log_server": {
    "enabled": true,
    "email": "beit.halevi.700@gmail.com",
    "cc_policy": "all_game_messages"
  }
}
```

## 11.6 Default Values Table

Table 202: Default values -- Summary

| Category | Setting | Value |
|----------|---------|-------|
| Quota | Operational limit | 400/day |
| Quota | Warning threshold | 80% |
| Rate | Minimum interval | 200 milliseconds |
| DOS | Block | 300 seconds |
| Season | Rounds | 6 |
| Season | Games per round | 10 |
| Round | Maximum duration | 30 minutes |
| Time window | Days | Tuesday, Thursday |
| Time window | Hours | 18:30-22:00 GMT |
| Timeout | game_flow | 5 minutes |
| Timeout | default | 60 minutes |
| Log | Address | beit.halevi.700@gmail.com |

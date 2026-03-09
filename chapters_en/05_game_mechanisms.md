# 5 Game Mechanisms

## 5.1 Introduction

This chapter details the technical mechanisms of the game system: the assignment table, game ID format, time windows, and handling technical failures.

### 5.1.1 Chapter Objectives

By the end of this chapter, you will understand:

- The structure of the assignment table and how it is created
- The composite game ID format (SSRRGGG)
- The time windows for games
- The types of technical failures and the 2-2-0 rule
- The Force Majeure protocol
- The lifecycle of a season and a round

## 5.2 Assignment Table

### 5.2.1 Table Structure

The assignment table (season_assignments) contains 180 rows per season:

- 60 games x 3 participants (referee + 2 players) = 180 rows
- 6 rounds x 10 games per round = 60 games

Table 50: Structure of the season_assignments table

| Field | Type |
|---|---|
| id | SERIAL PRIMARY KEY |
| season_id | VARCHAR(50) NOT NULL |
| round_number | INTEGER NOT NULL |
| game_number | INTEGER NOT NULL |
| group_id | VARCHAR(20) NOT NULL |
| participant_id | VARCHAR(100) NOT NULL |
| role | VARCHAR(20) NOT NULL |
| assignment_status | VARCHAR(20) DEFAULT 'PENDING' |
| assigned_at | TIMESTAMP DEFAULT NOW() |
| notified_at | TIMESTAMP |
| confirmed_at | TIMESTAMP |

**Constraint:** UNIQUE(season_id, round_number, game_number, role)

> **Normal Design**
>
> The table uses a normalized design: 3 rows per game (one row per participant). The game ID (SSRRGGG) is composed from the combination of season_id + round_number + game_number.

### 5.2.2 Table Creation

The table is created automatically when the registration window closes:

```
Registration Closes --> Generate 180 Rows --> Broadcast Assignment Table
```

Figure 13: Assignment table creation process

### 5.2.3 Assignment Broadcast Message (BROADCAST_ASSIGNMENT_TABLE)

The league manager sends a BROADCAST_ASSIGNMENT_TABLE message to all participants:

**Assignment Broadcast Message**

```json
{
  "version": "league.v2",
  "message_type": "BROADCAST_ASSIGNMENT_TABLE",
  "message_id": "assign-abc123",
  "timestamp": "2026-01-16T18:15:00+00:00",
  "sender_id": "LM001",
  "recipient_id": "BROADCAST",
  "payload": {
    "broadcast_id": "assign-20260116-001",
    "season_id": "S01",
    "league_id": "Q21G",
    "assignments": [
      {"round_number": 1, "game_number": 1, "group_id": "team1",
       "participant_id": "R-team1", "role": "REFEREE"},
      {"round_number": 1, "game_number": 1, "group_id": "team2",
       "participant_id": "P-team2", "role": "PLAYER_A"}
    ],
    "total_count": 180,
    "message_text": "Season S01 assignments are ready!"
  },
  "league_id": "Q21G",
  "season_id": "S01"
}
```

### 5.2.4 Repeat Delivery Request (REQUEST_ASSIGNMENT_TABLE)

A participant who did not receive the message can request repeat delivery:

**Assignment Table Request**

```json
{
  "version": "league.v2",
  "message_type": "REQUEST_ASSIGNMENT_TABLE",
  "message_id": "req-xyz789",
  "timestamp": "2026-01-16T19:00:00+00:00",
  "sender_id": "P-team3",
  "recipient_id": "LM001",
  "payload": {
    "season_id": "S01",
    "group_id": "team3"
  },
  "league_id": "Q21G",
  "season_id": "S01"
}
```

### 5.2.5 Assignment Response (RESPONSE_ASSIGNMENT_TABLE)

The league manager returns the specific assignments of the requester:

**Response with Assignments**

```json
{
  "version": "league.v2",
  "message_type": "RESPONSE_ASSIGNMENT_TABLE",
  "message_id": "resp-def456",
  "timestamp": "2026-01-16T19:00:05+00:00",
  "sender_id": "LM001",
  "recipient_id": "P-team3",
  "payload": {
    "season_id": "S01",
    "group_id": "team3",
    "assignments": [
      {"round_number": 1, "game_number": 2, "participant_id": "P-team3",
       "role": "PLAYER_A"},
      {"round_number": 2, "game_number": 5, "participant_id": "R-team3",
       "role": "REFEREE"}
    ],
    "total_count": 12
  },
  "league_id": "Q21G",
  "season_id": "S01"
}
```

> **Payload Fields**
>
> - **BROADCAST**: broadcast_id, season_id, league_id, assignments[], total_count, message_text
> - **REQUEST**: season_id, group_id (optional -- default: sender_id)
> - **RESPONSE**: season_id, group_id, assignments[], total_count

## 5.3 Composite Game ID (SSRRGGG)

The game ID is a string of 7 characters in SSRRGGG format. For the full ID structure, parsing examples, and implementation code, see Appendix V' section 10.

## 5.4 League Dates and Time Windows

### 5.4.1 Only Two League Dates

Unlike regular leagues, Q21G league takes place on **only two evenings** -- one evening per season. For the full schedule including warm-up sessions, see table 69 in chapter 7.

### 5.4.2 League Evening Structure

Each league evening is divided into the following stages. For the detailed schedule, see table 3 in chapter 1.

### 5.4.3 Grace Period

A game that started before 21:45 can continue until 22:00. From round 6 onward, it ends with the publication of season results.

### 5.4.4 League Date Check Logic

```python
from datetime import datetime, timezone

# League dates (UTC)
LEAGUE_DATES = [
    datetime(2026, 2, 17, tzinfo=timezone.utc),  # Season A
    datetime(2026, 3, 17, tzinfo=timezone.utc),  # Season B
]

def is_league_day(current_time: datetime) -> bool:
    """Check if today is a league day."""
    current_date = current_time.date()
    return any(d.date() == current_date for d in LEAGUE_DATES)

def can_start_new_round(current_time: datetime) -> bool:
    """Check if new round can start in current time window."""
    if not is_league_day(current_time):
        return False

    # Check time window (19:00-21:30 UTC for new rounds)
    hour, minute = current_time.hour, current_time.minute
    start_ok = (hour == 19 and minute >= 0) or hour > 19
    end_ok = hour < 21 or (hour == 21 and minute <= 30)

    return start_ok and end_ok
```

## 5.5 Handling Technical Failures

### 5.5.1 Failure Types and Events

The system uses a simple model with two failure types (failure_type) and three cancellation events:

Table 51: Failure types (failure_type)

| Type | Description | Usage |
|---|---|---|
| NO_RESPONSE | Referee did not respond | handle_no_response() -- referee did not respond by deadline |
| TECHNICAL_FAILURE | Technical failure | handle_technical_failure() -- reported failure |

Table 52: Cancellation events (MatchEvent)

| Event | Description |
|---|---|
| TIMEOUT | Time exceeded (generic for all timeout types) |
| FORFEIT | Participant withdrawal |
| CANCEL | Game cancellation |

> **Simple Model**
>
> Unlike a detailed model with 4 separate failure types, the code uses a simpler model:
> - No distinction between referee_no_show and player_no_show -- both are NO_RESPONSE
> - No distinction between non-arrival and mid-game abandonment -- both map to failure_reason
> - The detailed reason is stored in the failure_reason field as free text

### 5.5.2 The 2-2-0 Rule

For every technical failure, the system applies automatic scoring:

> **Scoring Method**
>
> **2-2-0 Rule:**
> - Player A receives **2 points**
> - Player B receives **2 points**
> - The referee receives **0 points**
>
> The rule applies whenever a game is not completed due to a technical failure, regardless of the cause of the failure.

### 5.5.3 Failure Handling Diagram

```
        Game Active
       /           \
  30min limit    no response
     /               \
Timeout          No-Show
Detected         Detected
     \               /
      Apply 2-2-0
        Scoring
          |
       Game End
```

Figure 14: Technical failure handling process with 2-2-0 scoring

### 5.5.4 Failure Documentation (Referee)

For the referee agent, it is recommended to document every action and failure. The current implementation uses log files (JSON Lines) and not a database table:

Table 53: Audit log fields (File-based)

| Field | Type | Description |
|---|---|---|
| timestamp | ISO8601 | Event time (UTC) |
| operation | string | Action type: CREATE, UPDATE, DELETE, ACCESS |
| entity_type | string | Entity type (generic string) |
| entity_id | string | Entity ID |
| user_id | string | User/agent ID |
| status | string | Status: SUCCESS, FAILED |
| details | object | Additional details (JSON) |
| error | string | Error message (if relevant) |

> **File-based Implementation**
>
> The current implementation saves logs to files at logs/audit/audit_YYYYMMDD.log in JSON Lines format. There is no database table for audit_trail.

**File-based Audit Logger**

```python
class AuditLogger:
    """Logs operations to file for debugging and compliance."""

    def log(self, operation: str, entity_type: str, entity_id: str,
            user_id: str, status: str, details: dict = None,
            error: str = None):
        """Log an operation to audit file."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operation": operation,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "status": status,
            "details": details or {},
            "error": error,
        }
        # Append to logs/audit/audit_YYYYMMDD.log
        self._write_to_file(entry)
```

```python
    # Helper methods
    def log_create(self, entity_type, entity_id, user_id, details): ...
    def log_update(self, entity_type, entity_id, user_id, details): ...
    def log_delete(self, entity_type, entity_id, user_id, details): ...
    def log_access(self, entity_type, entity_id, user_id, details): ...
    def log_error(self, entity_type, entity_id, user_id, error, details)
    : ...
```

> **Importance of Documentation**
>
> Detailed documentation in log files enables:
> - **Debug** -- identifying the root cause of failures
> - **Appeals** -- evidence to support Force Majeure requests
> - **Improvement** -- analysis of failure patterns to improve code

## 5.6 Force Majeure Protocol

### 5.6.1 What is Force Majeure?

Force Majeure is a situation where an external failure prevents the normal continuation of the game:

- General network failure
- Gmail server issue
- League manager system failure
- Other exceptional circumstances

### 5.6.2 Request Process

```
PENDING --Admin receives--> UNDER_REVIEW --Valid--> APPROVED
                                         --Invalid--> REJECTED
```

Figure 15: Force Majeure request state machine

### 5.6.3 Force Majeure Messages

For the full table of Force Majeure messages, see table 102 in Appendix B'.

> **Use Responsibly**
>
> Force Majeure requests are carefully reviewed. Malicious use of the mechanism (for example, to cover up a failure in code) may lead to rejection of future requests and grade reduction.

### 5.6.4 Force Majeure Request Format

The agent sends a Force Majeure request in the following format:

**Force Majeure Request**

```json
{
  "version": "league.v2",
  "message_type": "FORCE_MAJEURE_REQUEST",
  "message_id": "fm-req-001",
  "timestamp": "2026-01-16T10:30:00+00:00",
  "sender_id": "R-team1",
  "recipient_id": "LM001",
  "payload": {
    "game_id": "0103005",
    "reason": "Player hospitalized - medical emergency"
  },
  "league_id": "Q21G_2026",
  "season_id": "S01",
  "round_id": "03",
  "game_id": "0103005"
}
```

> **Payload Fields in Force Majeure Request**
>
> - **game_id** -- the relevant game ID (required)
> - **reason** -- description of the reason for the request (required) -- free text, should include specific details to enable understanding of the incident
>
> **Note:** The implementation uses the reason field as free text without predefined categories. The admin evaluates each request based on the description and circumstances.

### 5.6.5 Force Majeure Decision (FORCE_MAJEURE_DECISION)

The admin responds to the request with a decision message:

**Admin Decision**

```json
{
  "message_type": "FORCE_MAJEURE_DECISION",
  "payload": {
    "request_id": "fm-req-001",
    "decision": "APPROVED",
    "admin_notes": "Medical documentation verified",
    "new_start_time": "2026-01-20T14:00:00+00:00",
    "new_end_time": "2026-01-20T15:00:00+00:00"
  }
}
```

### 5.6.6 Force Majeure Result (FORCE_MAJEURE_RESULT)

After the decision, a result message is broadcast to all participants:

**Approval Result**

```json
{
  "message_type": "FORCE_MAJEURE_RESULT",
  "payload": {
    "request_id": "fm-req-001",
    "game_id": "0103005",
    "decision": "APPROVED",
    "new_start_time": "2026-01-20T14:00:00+00:00",
    "new_end_time": "2026-01-20T15:00:00+00:00",
    "admin_notes": "Game rescheduled"
  }
}
```

**Rejection Result**

```json
{
  "message_type": "FORCE_MAJEURE_RESULT",
  "payload": {
    "request_id": "fm-req-001",
    "game_id": "0103005",
    "decision": "REJECTED",
    "admin_notes": "Insufficient documentation",
    "scoring": "2-2-0 applied"
  }
}
```

Table 54: Possible outcomes of a Force Majeure request

| Decision | Outcome |
|---|---|
| APPROVED | The game is rescheduled with a new time window |
| REJECTED | 2-2-0 scoring applied (referee 0, each player 2) |

## 5.7 Extension Request Protocol

When an agent anticipates that it will not be able to meet the deadline, it can request an extension **from the league manager** before the time expires.

### 5.7.1 When to Request an Extension

- The required response time is about to expire
- The agent identifies that processing will take longer than expected
- A temporary failure prevents an immediate response

> **GTAI Protocol Flow**
>
> In the GTAI protocol, extension requests are sent **directly to the league manager** (not to the referee). The league manager handles the requests automatically.

> **Early Request**
>
> The extension request should be sent **before** the deadline expires. A request sent after the deadline will be automatically rejected.

### 5.7.2 Time Window Identification via Google Calendar

> **Backup Plan**
>
> In case the league manager is unavailable or experiences a technical failure, the agent can identify the time window through shared Google Calendar events. The calendar contains all critical events:

- REG_SEASON -- agent registration window (18:30-18:45)
- ROUND_1 through ROUND_6 -- game rounds
- FINAL_RESULTS -- results publication (21:45-22:00)

When the agent identifies a calendar event without receiving a message from the league manager, it should act proactively and send the appropriate message (registration/confirmation/joining, etc.).

### 5.7.3 Extension Request Format

**Extension Request**

```json
{
  "protocol": "league.v2",
  "messagetype": "EXTENSION_REQUEST",
  "sender": {"email": "player@gmail.com", "role": "PLAYER", "logical_id"
  : null},
  "timestamp": "2026-01-16T10:40:00+00:00",
  "conversationid": "ext-req-abc123def456",
  "leagueid": "LEAGUE001",
  "payload": {
    "correlation_id": "uuid-for-tracking",
    "reason": "Processing complex game state",
    "requested_extension": "120"
  }
}
```

> **Payload Fields in Extension Request**
>
> - **correlation_id** -- the ID of the original message for which the extension is being requested
> - **reason** -- description of the reason for the extension request
> - **requested_extension** -- the requested extension duration in seconds (as a string, not a number)

### 5.7.4 League Manager Response

The league manager responds with RESPONSE_EXTENSION:

**Extension Response**

```json
{
  "message_type": "RESPONSE_EXTENSION",
  "payload": {
    "message_id": "ext-dec-tx20260115",
    "correlation_id": "bc-ka-xyz789",
    "decision": "APPROVED",
    "message": "Extension granted - please resubmit your response",
    "new_deadline": "2026-01-15T11:00:00+00:00",
    "new_deadline_display": "2026-01-15 11:00:00 UTC"
  }
}
```

> **Response Status**
>
> The status field can be "APPROVED" (extension approved) or "DENIED" (extension rejected).

Table 55: Extension response handling

| Status | Required Action | Notes |
|---|---|---|
| APPROVED | Use the new deadline | Continue processing and send response |
| DENIED | Send immediate response | Or receive REJECTION_NOTIFICATION |

### 5.7.5 Recommended Implementation

**Extension Manager**

```python
class ExtensionManager:
    async def request_extension_if_needed(
        self,
        original_msg: dict,
        deadline: datetime,
        processing_estimate: float
    ) -> bool:
        """Request extension if we won't make deadline."""
        time_remaining = (deadline - datetime.now()).total_seconds()

        if time_remaining < processing_estimate + 30:
            response = await self.send_extension_request(
                original_msg,
                requested_seconds=120
            )
            return response.get("status") == "APPROVED"
        return True
```

## 5.8 Season Lifecycle

```
        SETUP
          | open
    REGISTRATION_OPEN
          | close
    REGISTRATION_CLOSED
          | start
        ACTIVE <--pause/resume--> PAUSED
        |  done                    | cancel
    COMPLETED              CANCELLED
```

Figure 16: Season state machine

### 5.8.1 Season States

Table 56: Season states

| State | Description | Transition Trigger |
|---|---|---|
| SETUP | Preparation for season | Opening registration |
| REGISTRATION_OPEN | Registration window open | Closing the registration window |
| REGISTRATION_CLOSED | Registration closed | Season start |
| ACTIVE | Season active | End / Pause / Cancellation |
| PAUSED | Season paused | Resume / Cancellation |
| COMPLETED | Season completed (final) | -- |
| CANCELLED | Season cancelled (final) | -- |

> **Gap Between enum and Database**
>
> The LeagueState enum in code contains only 4 states (SETUP, REGISTRATION_OPEN, ACTIVE, COMPLETED), but the database constraint supports 7 states. The additional states (REGISTRATION_CLOSED, PAUSED, CANCELLED) are available at the DB level for future use.

## 5.9 Game Round Lifecycle

### 5.9.1 Round States

Table 57: Game round states

| State | Description | Triggered Message |
|---|---|---|
| SCHEDULED | Round is scheduled | -- |
| IN_PROGRESS | Round is active | BROADCAST_NEW_LEAGUE_ROUND |
| COMPLETED | Round is completed | BROADCAST_END_LEAGUE_ROUND |

### 5.9.2 Round Messages

The league manager sends messages at the beginning and end of each round:

Table 58: Round messages

| Message | Content |
|---|---|
| BROADCAST_NEW_LEAGUE_ROUND | Meta-data about the round (number, whether last, start time) |
| BROADCAST_END_LEAGUE_ROUND | Statistical summary (games that were completed out of total) |
| BROADCAST_ROUND_RESULTS | Updated standings table with standings |

#### 5.9.2.1 Opening Message - BROADCAST_NEW_LEAGUE_ROUND

```json
{
  "message_type": "BROADCAST_NEW_LEAGUE_ROUND",
  "payload": {
    "league_id": "Q21G_2026",
    "round_id": "S01_R03",
    "round_number": 3,
    "round_starting": 3,
    "round_ended": 2,
    "total_rounds": 6,
    "is_final_round": false,
    "scheduled_start": "2026-01-16T19:00:00+00:00"
  }
}
```

> **Note**
>
> This message contains meta-data only about the round. The **game list** is sent separately via BROADCAST_ASSIGNMENT_TABLE.

#### 5.9.2.2 Closing Message - BROADCAST_END_LEAGUE_ROUND

```json
{
  "message_type": "BROADCAST_END_LEAGUE_ROUND",
  "payload": {
    "league_id": "Q21G_2026",
    "round_id": "S01_R03",
    "round_number": 3,
    "matches_completed": 5,
    "matches_total": 5
  }
}
```

#### 5.9.2.3 Results Message - BROADCAST_ROUND_RESULTS

```json
{
  "message_type": "BROADCAST_ROUND_RESULTS",
  "payload": {
    "broadcast_id": "results-20260116-001",
    "league_id": "Q21G_2026",
    "round_id": "S01_R03",
    "round_number": 3,
    "standings": [
      {"rank": 1, "player_id": "P-team1", "points": 15},
      {"rank": 2, "player_id": "P-team2", "points": 12}
    ]
  }
}
```

## 5.10 Summary

This chapter presented the main game mechanisms:

- **Assignment Table** -- 180 rows (60 games x 3 participants)
- **Game ID** -- SSRRGGG format (season-round-game)
- **Time Windows** -- Tuesday/Thursday 18:30-22:00 GMT
- **Technical Failures** -- 2 types with 2-2-0 scoring
- **Force Majeure** -- PENDING -> UNDER_REVIEW -> APPROVED/REJECTED
- **Season Lifecycle** -- SETUP -> REGISTRATION -> ACTIVE -> COMPLETED
- **Round Lifecycle** -- SCHEDULED -> IN_PROGRESS -> COMPLETED

The next chapter will deal with the practical implementation of the agents.

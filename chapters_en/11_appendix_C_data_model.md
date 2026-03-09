# Appendix C: System Data Model

## C.1 Overview

The database of the GmailAsServer system is based on PostgreSQL and organized into eight logical categories. The architecture was designed to support comprehensive tracking of all system operations, league and season management, personal communication documentation for each user, and integration with Google Calendar.

### C.1.1 Eight Table Categories

The system contains more than 25 fixed tables and one dynamic table per registered user, divided into the following categories:

1. **Core System tables** — users, email logging, transactions, attachments, and audit (5 tables)
2. **League Management tables** — leagues, players, referees, rounds, and matches (5 tables)
3. **Season & Registration tables** — seasons, rankings, registration, and assignments (4 tables)
4. **Broadcast tables** — broadcasts, responses, and broadcast queue (3 tables)
5. **Game State tables** — game state, pending timeouts, and state transitions (3 tables)
6. **Gatekeeper tables** — logging of API protection operations (1 table)
7. **Calendar tables** — integration with Google Calendar (1 table)
8. **Dynamic Per-User tables** — personal message tracking table per user (N tables)

## C.2 Schema Diagram

*Figure 19: GmailAsServer system data model — more than 25 tables in eight logical categories*

**Color Legend:**
- Blue — Core System tables
- Green — League Management tables
- Orange — Season & Registration tables
- Purple — Broadcast tables
- Yellow — Game State tables
- Gray — Gatekeeper tables
- Pink — Calendar tables
- Red — Dynamic tables
- Light yellow — Primary Key (PK)
- Light blue — Foreign Key (FK)

## C.3 Core System Tables

This category contains five tables that form the basic infrastructure of the system: user management, email logging, transactions, attachments, and audit.

### C.3.1 `users` Table

The users table stores all user accounts in the system.

**Table 103: `users` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Unique ID |
| `email` | VARCHAR(255) UNIQUE | Email |
| `display_name` | VARCHAR(255) | Display name |
| `role` | VARCHAR(50) | MANAGER/REFEREE/PLAYER |
| `logical_id` | VARCHAR(50) UNIQUE | Readable ID |
| `auth_token` | VARCHAR(255) | Authentication token |
| `status` | VARCHAR(50) | ACTIVE/INACTIVE/DELETED |
| `message_table_name` | VARCHAR(255) | Name of messages table |

### C.3.2 `email_log` Table

This table records all emails processed in the system.

**Table 104: `email_log` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `user_id` | INTEGER FK | Link to users table |
| `transaction_id` | VARCHAR(100) UNIQUE | Transaction ID |
| `message_id` | VARCHAR(255) | Gmail message ID |
| `thread_id` | VARCHAR(255) | Gmail thread ID |
| `direction` | VARCHAR(20) NOT NULL | `sent` or `received` |
| `subject` | TEXT | Message subject |
| `sent_received_date` | TIMESTAMP | Send/receive time |
| `processed_at` | TIMESTAMP | Processing time |
| `status` | VARCHAR(50) | Processing status |

### C.3.3 `transactions` Table

This table stores message transactions before processing.

**Table 105: `transactions` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `transaction_id` | VARCHAR(100) UNIQUE | Transaction ID |
| `user_email` | VARCHAR(255) | User email |
| `message_type` | VARCHAR(100) | Message type |
| `payload` | JSONB | Message content in JSON |
| `status` | VARCHAR(50) | Status: PENDING, PROCESSED |

### C.3.4 `attachments` Table

This table manages files attached to emails.

**Table 106: `attachments` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `transaction_id` | VARCHAR(100) UNIQUE | Transaction ID |
| `email_log_id` | INTEGER FK | Link to email_log |
| `user_email` | VARCHAR(255) NOT NULL | User email |
| `email_id` | VARCHAR(255) NOT NULL | Gmail message ID |
| `thread_id` | VARCHAR(255) | Gmail thread ID |
| `direction` | VARCHAR(20) NOT NULL | `sent` or `received` |
| `email_date` | TIMESTAMP | Email date |
| `subject` | TEXT | Message subject |
| `original_filename` | VARCHAR(500) NOT NULL | Original filename |
| `internal_filename` | VARCHAR(500) UNIQUE | Internal storage name |
| `file_path` | TEXT | Full file path |
| `file_size` | INTEGER | File size in bytes |
| `created_at` | TIMESTAMP | Creation time |

### C.3.5 `audit_trail` Table

The audit table records all significant operations in the system.

**Table 107: `audit_trail` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `timestamp` | TIMESTAMP | Operation time |
| `operation` | VARCHAR(50) NOT NULL | Operation type |
| `entity_type` | VARCHAR(100) NOT NULL | Type of affected entity |
| `entity_id` | VARCHAR(255) | Entity ID |
| `user_id` | VARCHAR(255) | ID of user who performed |
| `status` | VARCHAR(50) | SUCCESS or FAILURE |
| `details` | JSONB | Additional details |
| `error_message` | TEXT | Error message on failure |
| `transaction_id` | VARCHAR(100) | Related transaction ID |
| `duration_ms` | FLOAT | Operation duration in milliseconds |

### C.3.6 `broadcasts` Table

This table manages broadcast messages to all participants.

**Table 108: `broadcasts` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `broadcast_id` | VARCHAR(100) UNIQUE | Broadcast ID |
| `message_type` | VARCHAR(100) NOT NULL | Message type |
| `league_id` | VARCHAR(100) | Target league |
| `season_id` | VARCHAR(100) | Target season |
| `round_id` | VARCHAR(100) | Related round |
| `payload` | JSONB NOT NULL | Message content |
| `message_text` | VARCHAR(200) | Short display text |
| `requires_response` | BOOLEAN | Whether response required |
| `response_deadline` | TIMESTAMP | Deadline for response |
| `deadline_processed` | BOOLEAN | Chaining flag |
| `total_recipients` | INTEGER | Number of recipients |
| `responses_received` | INTEGER | Responses received |
| `status` | VARCHAR(50) | Broadcast status |
| `created_at` | TIMESTAMP | Creation time |
| `sent_at` | TIMESTAMP | Send time |
| `completed_at` | TIMESTAMP | Completion time |

### C.3.7 `broadcast_responses` Table

This table stores responses to broadcasts.

**Table 109: `broadcast_responses` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `broadcast_id` | VARCHAR(100) NOT NULL | Link to broadcast |
| `responder_email` | VARCHAR(255) NOT NULL | Responder email |
| `responder_id` | VARCHAR(50) | Responder logical ID |
| `responder_role` | VARCHAR(50) | Responder role |
| `response_type` | VARCHAR(100) NOT NULL | Response type |
| `payload` | JSONB NOT NULL | Response content |
| `message_text` | VARCHAR(400) | Response text |
| `received_at` | TIMESTAMP | Response receipt time |
| `email_id` | VARCHAR(255) | Gmail message ID |
| `thread_id` | VARCHAR(255) | Gmail thread ID |

### C.3.8 `broadcast_queue` Table

This table provides a thread-safe queue to separate timer events from Gmail API calls.

**Table 110: `broadcast_queue` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `queue_id` | VARCHAR(100) UNIQUE | Queue record ID |
| `broadcast_type` | VARCHAR(50) NOT NULL | Broadcast type |
| `payload` | JSONB NOT NULL | Broadcast parameters |
| `status` | VARCHAR(20) | pending, processing, sent, failed |
| `error_message` | VARCHAR(500) | Error details on failure |
| `retry_count` | INTEGER | Current attempt (default: 0) |
| `max_retries` | INTEGER | Maximum attempts (default: 3) |
| `created_at` | TIMESTAMP | Queue entry time |
| `processed_at` | TIMESTAMP | Send time |

**Queue Broadcast Types:**
- `registration_start` — registration transition from PENDING to ACTIVE
- `registration_complete` — registration completion
- `season_start` — season start
- `season_end` — season end
- `round_start` — round start
- `round_end` — round end

## C.4 Registration and Group Tables

This category contains tables for managing student registration and groups.

### C.4.1 `student_groups` Table

This table stores static information about student groups (data that does not change during the season).

**Table 111: `student_groups` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `group_id` | VARCHAR(10) UNIQUE | Group ID (G001–G030) |
| `student_a_name` | VARCHAR(255) | Student A name |
| `student_a_email` | VARCHAR(255) | Student A email |
| `student_b_name` | VARCHAR(255) | Student B name |
| `student_b_email` | VARCHAR(255) | Student B email |
| `github_repo` | VARCHAR(500) | GitHub repository URL |
| `created_at` | TIMESTAMP | Creation time |

> **Separation of Static and Dynamic Data**
>
> The `student_groups` table contains only static information (names, emails, GitHub). Dynamic data such as game state, score, and role are stored in the `players` and `referees` tables per season.

## C.5 Season Management Tables

This category contains tables for managing seasons and rankings.

### C.5.1 `seasons` Table

This table manages league seasons.

**Table 112: `seasons` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `season_id` | VARCHAR(100) UNIQUE | Season ID |
| `league_id` | VARCHAR(100) NOT NULL | League ID |
| `season_name` | VARCHAR(255) | Season name |
| `season_type` | VARCHAR(50) | WARMUP or REGULAR |
| `state` | VARCHAR(50) | PENDING, ACTIVE, COMPLETED |
| `registration_deadline` | TIMESTAMP | Registration closing deadline |
| `total_rounds` | INTEGER | Total rounds (default: 6) |
| `current_round` | INTEGER | Current active round |
| `registered_players` | INTEGER | Number of registered players |
| `registered_referees` | INTEGER | Number of registered referees |
| `start_time` | TIMESTAMP | Season start time |
| `end_time` | TIMESTAMP | Season end time |
| `config` | JSONB | Season configuration |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update time |

### C.5.2 `season_registrations` Table

This table manages participant registrations for each season with user linkage.

**Table 113: `season_registrations` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `season_id` | VARCHAR(50) NOT NULL | Season ID |
| `participant_email` | VARCHAR(255) NOT NULL | Participant email |
| `participant_id` | VARCHAR(100) | Participant logical ID |
| `participant_role` | VARCHAR(20) | PLAYER or REFEREE |
| `user_id` | VARCHAR(50) | User ID (links player + referee) |
| `registered_at` | TIMESTAMP | Registration time |
| `registration_status` | VARCHAR(20) | ACTIVE, WITHDRAWN, REJECTED |

> **"Complete User" Concept**
>
> A user is considered "complete" when they have two season registration records:
> - Registration as PLAYER with a specific `user_id`
> - Registration as REFEREE with the same `user_id`
>
> Query to get complete users:
> ```sql
> SELECT DISTINCT user_id FROM season_registrations
> WHERE season_id = 'S01' AND registration_status = 'ACTIVE'
> GROUP BY user_id HAVING COUNT(DISTINCT participant_role) = 2;
> ```

### C.5.3 `season_standings` Table

This table stores the standings table for each season.

**Table 114: `season_standings` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `season_id` | VARCHAR(100) NOT NULL | Season ID |
| `participant_id` | VARCHAR(100) NOT NULL | Player or referee ID |
| `participant_email` | VARCHAR(255) NOT NULL | Participant email |
| `participant_role` | VARCHAR(20) NOT NULL | PLAYER or REFEREE |
| `user_id` | VARCHAR(50) | User link |
| `rank` | INTEGER | Season ranking |
| `matches_played` | INTEGER | Matches played |
| `matches_won` | INTEGER | Wins |
| `matches_lost` | INTEGER | Losses |
| `matches_drawn` | INTEGER | Draws |
| `total_score` | FLOAT | Cumulative score |
| `matches_refereed` | INTEGER | Matches refereed |
| `referee_score` | FLOAT | Referee score |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update |

## C.6 League Management Tables

This category contains five tables for managing league competitions: leagues, players, referees, rounds, and matches.

### C.6.1 `leagues` Table

This table stores league definitions.

**Table 115: `leagues` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `league_id` | VARCHAR(100) UNIQUE | League ID |
| `name` | VARCHAR(255) | League name |
| `current_state` | VARCHAR(50) | League state |
| `min_players` | INTEGER | Minimum players |
| `registered_players_count` | INTEGER | Number of registered players |
| `registration_opened_at` | TIMESTAMP | Registration open time |
| `started_at` | TIMESTAMP | League start time |
| `completed_at` | TIMESTAMP | League completion time |
| `config` | JSONB | Configuration |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update time |

### C.6.2 `players` Table

This table manages player registrations and dynamic statistics per season.

**Table 116: `players` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `player_id` | VARCHAR(100) UNIQUE | Player ID |
| `league_id` | VARCHAR(100) NOT NULL | League ID |
| `group_id` | VARCHAR(50) | Link to student_groups |
| `user_id` | INTEGER FK | Link to users table |
| `email` | VARCHAR(255) NOT NULL | Player email |
| `display_name` | VARCHAR(255) | Display name |
| `current_state` | VARCHAR(50) | REGISTERED, ACTIVE, WAITING |
| `current_match_id` | VARCHAR(100) | Current game if active |
| `current_season_id` | VARCHAR(100) | Current season context |
| `current_round_id` | VARCHAR(100) | Current round context |
| `current_game_id` | VARCHAR(100) | Current game context |
| `season_status` | VARCHAR(50) | Season-specific status |
| `matches_played` | INTEGER | Total matches |
| `matches_won` | INTEGER | Wins |
| `matches_lost` | INTEGER | Losses |
| `matches_drawn` | INTEGER | Draws |
| `total_score` | FLOAT | Cumulative score |
| `seasons_participated` | INTEGER | Number of seasons |
| `list_of_seasons` | TEXT[] | List of season IDs |
| `registered_at` | TIMESTAMP | Registration time |
| `state_entered_at` | TIMESTAMP | State entry time |
| `last_active_at` | TIMESTAMP | Last activity |
| `updated_at` | TIMESTAMP | Last update |

### C.6.3 `referees` Table

This table manages referees in the league and dynamic statistics per season.

**Table 117: `referees` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `referee_id` | VARCHAR(100) UNIQUE | Referee ID |
| `league_id` | VARCHAR(100) NOT NULL | League ID |
| `group_id` | VARCHAR(50) | Link to student_groups |
| `user_id` | INTEGER FK | Link to users |
| `email` | VARCHAR(255) NOT NULL | Referee email |
| `display_name` | VARCHAR(255) | Display name |
| `current_state` | VARCHAR(50) | REGISTERED, AVAILABLE, REFEREEING |
| `current_match_id` | VARCHAR(100) | Current game if active |
| `current_season_id` | VARCHAR(100) | Current season context |
| `current_round_id` | VARCHAR(100) | Current round context |
| `current_game_id` | VARCHAR(100) | Current game context |
| `season_status` | VARCHAR(50) | Season-specific status |
| `matches_refereed` | INTEGER | Matches refereed |
| `seasons_participated` | INTEGER | Number of seasons |
| `list_of_seasons` | TEXT[] | List of season IDs |
| `registered_at` | TIMESTAMP | Registration time |
| `state_entered_at` | TIMESTAMP | State entry time |
| `last_active_at` | TIMESTAMP | Last activity |
| `updated_at` | TIMESTAMP | Last update |

### C.6.4 `rounds` Table

This table manages league rounds.

**Table 118: `rounds` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `round_id` | VARCHAR(100) UNIQUE | Round ID |
| `league_id` | VARCHAR(100) NOT NULL | League ID |
| `season_id` | VARCHAR(100) | Season ID |
| `round_number` | INTEGER NOT NULL | Sequential round number |
| `current_state` | VARCHAR(50) | SCHEDULED, IN_PROGRESS, COMPLETED |
| `total_matches` | INTEGER | Total matches in round |
| `completed_matches` | INTEGER | Completed matches |
| `scheduled_start` | TIMESTAMP | Planned start time |
| `started_at` | TIMESTAMP | Actual start time |
| `completed_at` | TIMESTAMP | Completion time |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update |

### C.6.5 `matches` Table

This table stores details of individual matches.

**Table 119: `matches` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `match_id` | VARCHAR(100) UNIQUE | Match ID |
| `round_id` | VARCHAR(100) NOT NULL | Round ID |
| `league_id` | VARCHAR(100) NOT NULL | League ID |
| `season_id` | VARCHAR(100) | Season ID |
| `game_type` | VARCHAR(50) | Game type (default: Q21) |
| `player_a_id` | VARCHAR(100) NOT NULL | Player A ID |
| `player_b_id` | VARCHAR(100) NOT NULL | Player B ID |
| `referee_id` | VARCHAR(100) | Referee ID |
| `current_state` | VARCHAR(50) | WAITING_PLAYERS, ACTIVE, COMPLETED, CANCELLED |
| `player_a_joined` | BOOLEAN | Whether player A joined |
| `player_b_joined` | BOOLEAN | Whether player B joined |
| `winner_id` | VARCHAR(100) | Winner ID |
| `is_draw` | BOOLEAN | Whether game ended in draw |
| `player_a_score` | FLOAT | Player A score |
| `player_b_score` | FLOAT | Player B score |
| `referee_score` | FLOAT | Referee score |
| `cancel_reason` | TEXT | Cancellation reason |
| `started_at` | TIMESTAMP | Start time |
| `finished_at` | TIMESTAMP | Finish time |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update |

## C.7 Game Assignment Table

This table manages the assignment of game groups (referee + two players) for each round. Contains 180 rows per season (60 matches × 3 participants).

### C.7.1 `season_assignments` Table

**Table 120: `season_assignments` Table Structure**

| Column | Type |
|---|---|
| `id` | SERIAL PRIMARY KEY |
| `season_id` | VARCHAR(50) NOT NULL |
| `round_number` | INTEGER NOT NULL |
| `game_number` | INTEGER NOT NULL |
| `group_id` | VARCHAR(20) NOT NULL |
| `participant_id` | VARCHAR(100) NOT NULL |
| `role` | VARCHAR(20) NOT NULL |
| `assignment_status` | CHAR(20) DEFAULT 'PENDING' |
| `assigned_at` | TIMESTAMP DEFAULT NOW() |
| `notified_at` | TIMESTAMP |
| `confirmed_at` | TIMESTAMP |

**Constraints:**
```sql
UNIQUE(season_id, round_number, game_number, role)
CHECK (role IN ('REFEREE', 'PLAYER_A', 'PLAYER_B'))
```

**Composite game_id:**

The game ID in SSRRGGG format consists of seven digits:
- `SS` — season number (01–99)
- `RR` — round number (01–06)
- `GGG` — game number in round (001–010)

Example: `0103005` = Season 1, Round 3, Game 5

### C.7.2 Recommended Indexes

```sql
CREATE INDEX idx_season_assign_season ON season_assignments(season_id);
CREATE INDEX idx_season_assign_round ON season_assignments(round_number);
CREATE INDEX idx_season_assign_game ON season_assignments(game_number);
CREATE INDEX idx_season_assign_status ON season_assignments(assignment_status);
CREATE INDEX idx_season_assign_role ON season_assignments(role);
-- UNIQUE constraint: (season_id, round_number, game_number, role)
```

## C.8 Gatekeeper Tables

This category contains one active table (`gatekeeper_log`) to support the Gatekeeper component that manages Gmail API communication and protects against overuse. Two additional tables (`broadcast_transaction_mapping` and `gatekeeper_state`) are marked as deprecated in version 0.4.

### C.8.1 `broadcast_transaction_mapping` Table (Deprecated)

> **Deprecated Table**
>
> This table is not in use in schema version 0.4. The functionality has been merged into the `gatekeeper_log` table with the `broadcast_id` and `original_message_id` columns. This table is retained for backwards compatibility only and may be deleted in future versions.

**Table 121: `broadcast_transaction_mapping` Table Structure (Deprecated)**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `broadcast_id` | VARCHAR(20) | Broadcast ID (BC001–BC999) |
| `original_recipient` | VARCHAR(255) | Original recipient |
| `message_type` | VARCHAR(100) | Message type |
| `sent_at` | TIMESTAMP | Send time |
| `response_received` | BOOLEAN | Whether response received |
| `response_at` | TIMESTAMP | Response receipt time |

### C.8.2 `gatekeeper_state` Table (Deprecated)

> **Deprecated Table**
>
> This table is not in use in schema version 0.4. Gatekeeper state management has moved to in-memory state with Redis backup. This table is retained for backwards compatibility only.

**Table 122: `gatekeeper_state` Table Structure (Deprecated)**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `daily_quota_used` | INTEGER | Daily quota consumed |
| `daily_quota_limit` | INTEGER | Daily quota limit (400) |
| `dos_detection_active` | BOOLEAN | Whether DoS detection active |
| `rate_limit_window_start` | TIMESTAMP | Rate limit window start |
| `requests_in_window` | INTEGER | Requests in current window |
| `last_reset` | TIMESTAMP | Last quota reset |

### C.8.3 `gatekeeper_log` Table

This table records Gatekeeper operations for auditing.

**Table 123: `gatekeeper_log` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `timestamp` | TIMESTAMP | Operation time |
| `action_name` | VARCHAR(100) NOT NULL | Operation type |
| `origin` | VARCHAR(255) | Operation source |
| `broadcast_id` | VARCHAR(100) | Broadcast ID for response matching |
| `sender_email` | VARCHAR(255) | Sender email |
| `recipient_email` | VARCHAR(255) | Recipient email |
| `message_id` | VARCHAR(100) | Consolidated message ID |
| `original_message_id` | VARCHAR(100) | Original message ID |
| `details` | JSONB | Operation details |
| `threshold_exceeded` | BOOLEAN | Whether DoS threshold exceeded |
| `tier_violated` | VARCHAR(50) | Which DoS tier was violated |

**Gatekeeper Action Names:**
- `QUOTA_CHECK` — daily quota check
- `DOS_CHECK` — DoS detection check
- `BROADCAST_CONSOLIDATE` — recipient consolidation
- `RESPONSE_MAP` — response-to-source mapping
- `ADMIN_ALERT` — manager alert
- `RATE_LIMIT` — rate limiting

**DoS Tiers:**

| Tier | Window | Threshold |
|---|---|---|
| `PER_MINUTE` | 1 minute | 7,500 |
| `PER_HOUR` | 1 hour | 60,000 |
| `PER_8_HOURS` | 8 hours | 144,000 |
| `PER_DAY` | 24 hours | 2 |

## C.9 Game State Tables

This category contains three tables for managing active game states: state saving, timeout management, and state transition logging.

### C.9.1 `game_state` Table

This table saves the game state between turns.

**Table 124: `game_state` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `match_id` | VARCHAR(100) UNIQUE | Game ID |
| `game_type` | VARCHAR(50) | Game type (Q21) |
| `phase` | VARCHAR(50) | Current game phase |
| `state_data` | JSONB | Full game state |

### C.9.2 `pending_timeouts` Table

This table manages active timeouts.

**Table 125: `pending_timeouts` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `timeout_id` | VARCHAR(100) UNIQUE | Timeout ID |
| `timeout_type` | VARCHAR(50) NOT NULL | Timeout type |
| `target_email` | VARCHAR(255) | Target email |
| `target_entity_id` | VARCHAR(100) | Scheduled entity ID |
| `started_at` | TIMESTAMP NOT NULL | Start time |
| `timeout_seconds` | INTEGER NOT NULL | Duration in seconds |
| `expires_at` | TIMESTAMP NOT NULL | Expiry time |
| `context` | JSONB | Additional context |
| `expired` | BOOLEAN | Whether expired |
| `created_at` | TIMESTAMP | Creation time |

**Timeout Types:**
- `MOVE` — player turn time
- `SUBMISSION` — response submission time
- `CONNECTIVITY_TEST` — connectivity check
- `GAME_JOIN_ACK` — game join confirmation
- `Q21_WARMUP` — Q21 warmup phase
- `Q21_QUESTIONS` — Q21 questions phase
- `Q21_GUESS` — Q21 guess phase

### C.9.3 `state_transitions` Table

This table records state transitions in the system.

**Table 126: `state_transitions` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `entity_type` | VARCHAR(50) | MATCH, LEAGUE, PLAYER, ROUND |
| `entity_id` | VARCHAR(100) | Entity ID |
| `from_state` | VARCHAR(50) | Previous state |
| `to_state` | VARCHAR(50) | New state |
| `event` | VARCHAR(50) | Event that caused transition |

## C.10 Calendar Tables

This category contains one table for integration with Google Calendar for scheduling and managing league events.

### C.10.1 `calendar_events` Table

This table maps season dates to Google Calendar events.

**Table 127: `calendar_events` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `season_date` | DATE NOT NULL | Date in season |
| `event_type` | VARCHAR(50) NOT NULL | Event type |
| `google_event_id` | VARCHAR(255) NOT NULL | Google Calendar event ID |
| `status` | VARCHAR(20) | PLACEHOLDER or UPDATED |
| `broadcast_id` | VARCHAR(100) | Link to related broadcast |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Calendar Event Types:**
- `ASSIGNMENT_TABLE` — assignment table broadcast
- `ROUND_RESULTS` — round results broadcast
- `ROUND_START` — round start
- `ROUND_END` — round end

**Status Values:**
- `PLACEHOLDER` — event created, waiting for content
- `UPDATED` — event updated with actual content

## C.11 Dynamic User Table

For each registered user, a personal table is created that records all their messages with the league manager.

### C.11.1 Naming Convention

The table name is derived from the email address:

- Template: `user_messages_{email_sanitized}`
- `@` is replaced by `_at_`
- Dots are replaced by underscores

Example: `user@example.com` → `user_messages_user_at_example_com`

### C.11.2 Table Structure

**Table 128: `user_messages_{email}` Table Structure**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Unique ID |
| `request_message_id` | VARCHAR(100) | Request message ID |
| `request_message_type` | VARCHAR(50) | Request type |
| `request_correlation_id` | VARCHAR(100) | ID for request-response linking |
| `request_payload` | JSONB | Request content |
| `response_message_id` | VARCHAR(100) | Response ID |
| `response_payload` | JSONB | Response content |
| `status` | VARCHAR(20) | OPEN, CLOSED, REJECTED |
| `response_deadline` | TIMESTAMP | Response deadline |
| `rejected_response_payload` | JSONB | Late response that was rejected |

## C.12 Table Relationships

### C.12.1 Explicit Foreign Keys

**Table 129: Explicit Foreign Keys (4)**

| Source Table | Column | Target Table | Column |
|---|---|---|---|
| `email_log` | `user_id` | `users` | `id` |
| `attachments` | `email_log_id` | `email_log` | `id` |
| `players` | `user_id` | `users` | `id` |
| `referees` | `user_id` | `users` | `id` |

> **Minimalist FK Approach**
>
> The GmailAsServer system uses a minimalist approach with only 4 explicit foreign keys. The rest of the relationships are enforced at the application level. This is because:
> - Flexibility in managing seasons and rounds
> - Better performance in bulk operations
> - Simplicity in managing dynamic user tables

### C.12.2 Logical Relationships

These relationships are enforced at the application level:

- `broadcasts.broadcast_id → broadcast_responses.broadcast_id`
- `rounds.round_id → matches.round_id`
- `players.player_id → matches.player_a_id`
- `players.player_id → matches.player_b_id`
- `referees.referee_id → matches.referee_id`
- `matches.match_id → game_state.match_id`

## C.13 Schema Architecture

### C.13.1 Schema File Organization

Schema definition files are located in the `src/infrastructure/database/` directory:

```
src/infrastructure/database/
├── manager.py                      # Database initialization
├── pool.py                         # Connection pooling
├── schema.py                       # Master schema orchestrator
├── schema_core.py                  # users, email_log, transactions
├── schema_league.py                # leagues, players, referees
├── schema_seasons.py               # seasons, standings, assignments
├── schema_season_registrations.py  # season_registrations
├── schema_broadcast.py             # broadcasts, responses
├── schema_broadcast_queue.py       # broadcast_queue
├── schema_game.py                  # game_state, timeouts
├── schema_gatekeeper.py            # gatekeeper_log
├── schema_calendar_events.py       # calendar_events
├── schema_groups.py                # student_groups
├── user_message_schema.py          # Dynamic user tables
└── migrations/                     # Upgrade scripts
```

### C.13.2 Repository Locations

**Table 130: Repository Locations**

| Repository | Path |
|---|---|
| UserRepository | `src/data/repositories/.../user_repository.py` |
| PlayerRepository | `src/data/repositories/.../player_repository.py` |
| RefereeRepository | `src/data/repositories/.../referee_repository.py` |
| SeasonRepository | `src/data/repositories/.../season_repository.py` |
| MatchRepository | `src/data/repositories/.../match_repository.py` |
| BroadcastRepository | `src/data/repositories/.../broadcast_repository.py` |
| StandingsRepository | `src/data/repositories/.../standings_repository.py` |
| AssignmentRepository | `src/data/repositories/.../assignment_repository.py` |

## C.14 Index Summary

### C.14.1 Primary Key Indexes

All tables contain an automatic primary key index on the `id` column.

### C.14.2 Uniqueness Constraint Indexes

**Table 131: Uniqueness Constraints**

| Table | Column/Columns |
|---|---|
| `users` | `email`, `logical_id` |
| `email_log` | `transaction_id` |
| `transactions` | `transaction_id` |
| `attachments` | `transaction_id`, `internal_filename` |
| `leagues` | `league_id` |
| `players` | `player_id`, `(league_id, email)` |
| `referees` | `referee_id`, `(league_id, email)` |
| `rounds` | `round_id`, `(league_id, round_number)` |
| `matches` | `match_id` |
| `seasons` | `season_id` |
| `season_registrations` | `(season_id, participant_email)` |
| `season_standings` | `(season_id, participant_id, participant_role)` |
| `season_assignments` | `(season_id, round_number, game_number, role)` |
| `broadcasts` | `broadcast_id` |
| `broadcast_responses` | `(broadcast_id, responder_email)` |
| `broadcast_queue` | `queue_id` |
| `game_state` | `match_id` |
| `pending_timeouts` | `timeout_id` |
| `calendar_events` | `(season_date, event_type)` |

### C.14.3 Performance Indexes

**Table 132: Key Performance Indexes**

| Table | Index Name | Columns | Purpose |
|---|---|---|---|
| `users` | `idx_users_email` | `email` | Email search |
| `users` | `idx_users_role` | `role` | Role filtering |
| `players` | `idx_players_league` | `league_id` | League queries |
| `players` | `idx_players_state` | `current_state` | State filtering |
| `matches` | `idx_matches_state` | `current_state` | Active matches |
| `matches` | `idx_matches_players` | `(player_a_id, player_b_id)` | Player search |
| `broadcasts` | `idx_broadcasts_deadline` | `response_deadline` | Deadline check |
| `broadcast_queue` | `idx_bq_status` | `status` | Pending items |
| `state_transitions` | `idx_transitions_timestamp` | `timestamp` | Recent transitions |
| `gatekeeper_log` | `idx_gk_log_timestamp` | `timestamp` | Log queries |

## C.15 SQL Query Guide

### C.15.1 Common Queries

**Get "complete" users for a season:**
```sql
SELECT DISTINCT user_id,
    array_agg(participant_email) as emails,
    array_agg(participant_role) as roles
FROM season_registrations
WHERE season_id = 'SEASON_001'
  AND registration_status = 'ACTIVE'
GROUP BY user_id
HAVING COUNT(DISTINCT participant_role) = 2;
```

**Get season standings:**
```sql
SELECT participant_id, participant_email, total_score, rank
FROM season_standings
WHERE season_id = 'SEASON_001' AND participant_role = 'PLAYER'
ORDER BY rank;
```

**Pending broadcasts with expired deadlines:**
```sql
SELECT broadcast_id, message_type, response_deadline
FROM broadcasts
WHERE status = 'SENT'
  AND response_deadline < NOW()
  AND deadline_processed = FALSE;
```

**User message history:**
```sql
SELECT request_message_type, status, response_deadline
FROM user_messages_user_at_example_com
ORDER BY created_at DESC
LIMIT 20;
```

## C.16 Schema Statistics

**Table 133: Database Statistics**

| Metric | Value |
|---|---|
| Fixed tables | 25+ |
| Dynamic tables | 1 per user |
| Explicit foreign keys | 4 |
| Total indexes | 50+ |
| JSONB columns | 18+ |
| Table categories | 8 |

## C.17 Diagram Generation Code

The diagram was created using a Python script generating a graphical diagram in LaTeX. The central part of the script:

```python
"""Generate LaTeX diagram of GmailAsServer database schema."""
import subprocess
import tempfile
from pathlib import Path

TIKZ_DOCUMENT = r"""
\documentclass[tikz,border=15pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{positioning,shapes.multipart,arrows.meta}

\definecolor{corecolor}{RGB}{66,133,244}
\definecolor{leaguecolor}{RGB}{52,168,83}
\definecolor{gamecolor}{RGB}{251,188,5}
\definecolor{dynamiccolor}{RGB}{234,67,53}
\tikzset{
  table/.style={
    rectangle split,
    rectangle split parts=#1,
    draw, anchor=north,
    font=\small\ttfamily,
    minimum width=3.5cm
  }
}
"""

def main():
    """Generate the database schema diagram."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "schema.tex"
        tex_file.write_text(TIKZ_DOCUMENT)
        subprocess.run(
            ["lualatex", tex_file.name],
            cwd=tmpdir
        )
```

The full script is available in: `scripts/generate_schema_diagram.py`

## C.18 Summary

The GmailAsServer database provides comprehensive infrastructure for managing an email-based league system. The modular architecture with more than 25 tables in eight categories enables:

- **Complete tracking** — every message and response is stored for auditing
- **Data isolation** — each user receives a personal table for message tracking
- **Flexibility** — using 18+ JSONB columns for changing data
- **Scalability** — support for multiple leagues, seasons, and matches in parallel
- **Integration** — connection to Google Calendar for event scheduling

---

*© Dr. Segal Yoram - All rights reserved*

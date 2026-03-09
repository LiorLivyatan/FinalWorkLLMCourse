# Appendix D: Player Agent Database Schema

## D.1 Introduction

This appendix describes the database schema of the player agent (GmailAsPlayer). The database is based on PostgreSQL 14+ and organized into six logical groups:

1. **Player and state tables** — saving player state and transition history
2. **Game tables** — sessions, questions, answers, guesses, and results
3. **Messages and files tables** — protocol message logging, file tracking, and correlations
4. **Broadcast tables** — tracking broadcast messages and pause/resume
5. **Season and league tables** — season registration, assignments, and standings
6. **System tables** — schema version and error logs

**Total tables: 20** (including `schema_version`)

**Schema version: 1.5.0**

## D.2 Schema Diagram

*Figure 20: Full database structure including foreign key relationships between tables.*

### D.2.1 Diagram Legend

- Yellow — Player and state tables
- Green — Game core tables
- Turquoise — Game data tables (questions, answers, guesses)
- Blue — Messages and files tables
- Purple — Broadcast tables
- Orange — Season and league tables
- Gray — System tables
- Blue arrows — Foreign key relationships

## D.3 Player and State Tables

### D.3.1 `player_states` Table

This is the central table for managing player state. Each row represents a registered player in the system.

**Table 134: `player_states` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `player_email` | VARCHAR(255) UNIQUE | Player email address |
| `player_name` | VARCHAR(255) | Display name |
| `current_state` | VARCHAR(50) | Current state in state machine |
| `current_game_id` | VARCHAR(100) | Active game ID |
| `current_book` | VARCHAR(255) | Current book name |
| `current_description` | TEXT | Book description |
| `current_domain` | VARCHAR(255) | Associative domain |
| `current_league_id` | VARCHAR(100) | Active league ID |
| `current_season_id` | VARCHAR(100) | Active season ID |
| `current_round_id` | VARCHAR(100) | Active round ID |
| `registration_id` | VARCHAR(100) | Registration transaction ID |
| `registered_at` | TIMESTAMP | Registration time |
| `last_activity` | TIMESTAMP | Last activity time |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Indexes:**
- `idx_player_states_email` on `player_email`

**Possible Player States:**
- `INIT_START_STATE` — initial state
- `REGISTERED` — registered in league
- `AWAITING_GAME` — waiting for game assignment
- `IN_GAME` — active in a game
- `GAME_COMPLETED` — game has ended

### D.3.2 `state_transitions` Table

History table for tracking state transitions. Used for debugging and analytics.

**Table 135: `state_transitions` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `player_email` | VARCHAR(255) | Player email address |
| `from_state` | VARCHAR(50) | Previous state |
| `to_state` | VARCHAR(50) | New state |
| `event` | VARCHAR(50) | Event that caused transition |
| `transition_metadata` | JSONB | Additional metadata |
| `created_at` | TIMESTAMP | Transition time |

**Indexes:**
- `idx_st_pe` on `player_email`
- `idx_st_ev` on `event`

**Common Transition Events:**
- `REGISTRATION_CONFIRMED` — registration confirmation
- `GAME_INVITATION_RECEIVED` — game invitation received
- `WARMUP_COMPLETED` — warmup completed
- `QUESTIONS_SUBMITTED` — questions submitted
- `GUESS_SUBMITTED` — guess submitted
- `GAME_COMPLETED` — game completed

## D.4 Game Core Tables

### D.4.1 `game_sessions` Table

Each row represents one game session. This is the parent table for questions, answers, and guesses.

**Table 136: `game_sessions` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `game_id` | VARCHAR(100) UNIQUE | Game session ID |
| `player_email` | VARCHAR(255) | Player email address |
| `book_name` | VARCHAR(255) | Book name to guess |
| `description` | TEXT | Book description |
| `domain` | VARCHAR(255) | Associative domain |
| `season_id` | VARCHAR(50) | Season ID |
| `round_id` | VARCHAR(50) | Round ID |
| `round_number` | INTEGER | Round number |
| `game_number` | INTEGER | Game number in round |
| `opponent_email` | VARCHAR(255) | Opponent email |
| `opponent_name` | VARCHAR(100) | Opponent name |
| `my_role` | VARCHAR(20) | Role: PLAYER1/PLAYER2 |
| `match_id` | VARCHAR(50) UNIQUE | Unique match ID |
| `referee_email` | VARCHAR(255) | Referee email |
| `invitation_status` | VARCHAR(20) | Invitation status |
| `invitation_deadline` | TIMESTAMP | Invitation deadline |
| `invitation_received_at` | TIMESTAMP | Invitation receipt time |
| `started_at` | TIMESTAMP | Game start time |
| `ended_at` | TIMESTAMP | Game end time |
| `is_completed` | BOOLEAN | Whether game completed |
| `is_abandoned` | BOOLEAN | Whether game abandoned |
| `result_correct` | BOOLEAN | Whether guess was correct |
| `result_score` | DECIMAL(5,2) | Final score |

**Indexes:**
- `idx_gs_gid` on `game_id`
- `idx_gs_pe` on `player_email`
- `idx_gs_sid` on `season_id`
- `idx_gs_mid` on `match_id`

### D.4.2 `game_state` Table

New table for managing the current game phase and detailed context.

**Table 137: `game_state` Table Columns**

| Column | Type | Description |
|---|---|---|
| `match_id` | VARCHAR(50) PK | Match ID (primary key) |
| `player_email` | VARCHAR(255) | Player email |
| `game_id` | VARCHAR(100) | Game ID |
| `current_phase` | VARCHAR(30) | Current game phase |
| `book_name` | VARCHAR(255) | Book name |
| `book_description` | TEXT | Book description |
| `associative_domain` | VARCHAR(50) | Associative domain |
| `warmup_question` | TEXT | Warmup question |
| `warmup_answer` | TEXT | Warmup answer |
| `warmup_deadline` | TIMESTAMP | Warmup deadline |
| `warmup_retry_count` | INTEGER | Warmup attempt count |
| `questions_deadline` | TIMESTAMP | Questions deadline |
| `guess_deadline` | TIMESTAMP | Guess deadline |
| `player_role` | VARCHAR(20) | Role: QUESTIONER/ANSWERER |
| `questions_required` | INTEGER | Required questions (20) |
| `time_limit_seconds` | INTEGER | Time limit in seconds |
| `created_at` | TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | Update time |

**Possible Game Phases (`current_phase`):**
- `AWAITING_WARMUP` — waiting for warmup question
- `WARMUP_IN_PROGRESS` — warmup in progress
- `AWAITING_HINTS` — waiting for hints
- `HINTS_RECEIVED` — hints received
- `AWAITING_QUESTIONS_CALL` — waiting for questions request
- `QUESTIONS_IN_PROGRESS` — generating questions
- `QUESTIONS_SUBMITTED` — questions submitted
- `AWAITING_ANSWERS` — waiting for answers
- `ANSWERS_RECEIVED` — answers received
- `AWAITING_GUESS_CALL` — waiting for guess request
- `GUESS_IN_PROGRESS` — generating guess
- `GUESS_SUBMITTED` — guess submitted
- `AWAITING_RESULT` — waiting for result
- `COMPLETED` — game completed

### D.4.3 `game_invitations` Table

Tracking game invitations.

**Table 138: `game_invitations` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `match_id` | VARCHAR(50) UNIQUE | Match ID |
| `player_email` | VARCHAR(255) | Player email |
| `referee_email` | VARCHAR(255) | Referee email |
| `opponent_email` | VARCHAR(255) | Opponent email |
| `book_name` | VARCHAR(255) | Book name |
| `deadline` | TIMESTAMP | Response deadline |
| `status` | VARCHAR(20) | Status: PENDING/ACCEPTED/REJECTED |
| `received_at` | TIMESTAMP | Receipt time |
| `responded_at` | TIMESTAMP | Response time |

### D.4.4 `game_results` Table

Saving results and detailed feedback for each game.

**Table 139: `game_results` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `match_id` | VARCHAR(50) UNIQUE | Match ID |
| `game_id` | VARCHAR(100) | Game ID |
| `season_id` | VARCHAR(50) | Season ID |
| `total_score` | DECIMAL(5,2) | Total score (0–100) |
| `opening_sentence_score` | DECIMAL(5,2) | Opening sentence score (50%) |
| `sentence_justification_score` | DECIMAL(5,2) | Sentence justification score (20%) |
| `associative_word_score` | DECIMAL(5,2) | Associative word score (20%) |
| `word_justification_score` | DECIMAL(5,2) | Word justification score (10%) |
| `opening_sentence_feedback` | TEXT | Opening sentence feedback |
| `word_feedback` | TEXT | Word feedback |
| `actual_opening_sentence` | TEXT | Correct opening sentence |
| `actual_associative_word` | VARCHAR(100) | Correct associative word |
| `received_at` | TIMESTAMP | Result receipt time |

> **Scoring Method**
>
> Score breakdown:
> - Opening sentence (50%) — exact or partial match
> - Sentence justification (20%) — explanation quality (30–50 words)
> - Associative word (20%) — exact match only
> - Word justification (10%) — explanation quality (20–30 words)

## D.5 Game Data Tables

### D.5.1 `questions` Table

Saves the 20 questions sent in each game.

**Table 140: `questions` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `game_id` | VARCHAR(100) FK | Foreign key to game_sessions |
| `question_number` | INTEGER | Question number (1–20) |
| `question_text` | TEXT | Question text |
| `options` | JSONB | Answer options |
| `created_at` | TIMESTAMP | Creation time |
| `answer_received` | VARCHAR(20) | Answer: YES/NO/UNKNOWN |
| `answer_received_at` | TIMESTAMP | Answer receipt time |

**Constraints:**
```sql
UNIQUE(game_id, question_number)
FOREIGN KEY(game_id) REFERENCES game_sessions(game_id)
```

### D.5.2 `answers` Table

Saves the referee's answers to each of the 20 questions.

**Table 141: `answers` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `game_id` | VARCHAR(100) FK | Foreign key to game_sessions |
| `question_number` | INTEGER | Question number |
| `selected_option` | VARCHAR(10) | Answer: YES/NO/UNKNOWN |
| `received_at` | TIMESTAMP | Receipt time |

**Constraints:**
```sql
UNIQUE(game_id, question_number)
FOREIGN KEY(game_id) REFERENCES game_sessions(game_id)
```

### D.5.3 `guesses` Table

Saves the player's final guess — opening sentence and associative word.

**Table 142: `guesses` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `game_id` | VARCHAR(100) FK UNIQUE | Foreign key to game_sessions |
| `opening_sentence` | TEXT | Guessed opening sentence |
| `sentence_justification` | TEXT | Sentence guess justification (30–50 words) |
| `associative_word` | VARCHAR(100) | Associative word |
| `word_justification` | TEXT | Word justification (20–30 words) |
| `confidence` | DECIMAL(5,2) | Confidence level (0–1) |
| `strategy_used` | VARCHAR(50) | Strategy: LLM/KEYWORD/RANDOM/DEMO |
| `created_at` | TIMESTAMP | Creation time |

**Constraints:**
```sql
UNIQUE(game_id)
FOREIGN KEY(game_id) REFERENCES game_sessions(game_id)
```

## D.6 Messages and Files Tables

### D.6.1 `message_logs` Table

Complete documentation of all protocol messages — incoming and outgoing.

**Table 143: `message_logs` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `gmail_id` | VARCHAR(100) UNIQUE | Gmail message ID |
| `thread_id` | VARCHAR(100) | Thread ID |
| `direction` | VARCHAR(10) | INBOUND/OUTBOUND |
| `message_type` | VARCHAR(100) | Protocol message type |
| `transaction_id` | VARCHAR(100) | Transaction ID |
| `sender_email` | VARCHAR(255) | Sender email |
| `recipient_email` | VARCHAR(255) | Recipient email |
| `subject` | TEXT | Email subject |
| `payload` | JSONB | Full message content |
| `game_id` | VARCHAR(100) | Associated game ID |
| `league_id` | VARCHAR(100) | League ID |
| `round_id` | VARCHAR(100) | Round ID |
| `processed` | BOOLEAN | Processing status |
| `error_message` | TEXT | Error message (if any) |
| `created_at` | TIMESTAMP | Log time |
| `processed_at` | TIMESTAMP | Processing time |

**Indexes:**
- `idx_ml_gid` on `gmail_id`
- `idx_ml_tid` on `thread_id`
- `idx_ml_mt` on `message_type`
- `idx_ml_txid` on `transaction_id`

### D.6.2 `attachments` Table

Tracking JSON files attached to protocol messages.

**Table 144: `attachments` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `internal_filename` | VARCHAR(255) UNIQUE | Internal filename |
| `original_filename` | VARCHAR(255) | Original filename |
| `message_id` | VARCHAR(100) | Gmail message ID |
| `mime_type` | VARCHAR(100) | MIME type |
| `size_bytes` | INTEGER | Size in bytes |
| `checksum` | VARCHAR(64) | SHA-256 for verification |
| `created_at` | TIMESTAMP | Creation time |

**Indexes:**
- `idx_att_int` on `internal_filename`
- `idx_att_msg` on `message_id`

### D.6.3 `message_correlations` Table

Linking request messages to responses.

**Table 145: `message_correlations` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `request_type` | VARCHAR(100) | Request message type |
| `request_id` | VARCHAR(100) | Request transaction ID |
| `request_gmail_id` | VARCHAR(100) | Gmail ID of request |
| `response_type` | VARCHAR(100) | Response message type |
| `response_id` | VARCHAR(100) | Response transaction ID |
| `response_gmail_id` | VARCHAR(100) | Gmail ID of response |
| `correlated_at` | TIMESTAMP | Correlation time |

**Indexes:**
- `idx_mc_req` on `request_id`
- `idx_mc_res` on `response_id`

## D.7 Broadcast Tables

### D.7.1 `broadcasts_received` Table

Tracking broadcast messages received from the league manager.

**Table 146: `broadcasts_received` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PRIMARY KEY | Auto ID |
| `broadcast_id` | VARCHAR(100) UNIQUE NOT NULL | Broadcast ID |
| `message_type` | VARCHAR(100) NOT NULL | Broadcast type |
| `message_text` | VARCHAR(200) | Human-readable text |
| `league_id` | VARCHAR(100) | League ID (optional) |
| `round_id` | VARCHAR(100) | Round ID (optional) |
| `season_id` | VARCHAR(100) | Season ID (optional) |
| `sender_email` | VARCHAR(255) NOT NULL | Sender email |
| `payload` | JSONB NOT NULL | Broadcast content |
| `requires_response` | BOOLEAN DEFAULT FALSE | Whether response required |
| `response_deadline` | TIMESTAMP | Response deadline |
| `response_sent` | BOOLEAN DEFAULT FALSE | Whether response sent |
| `response_sent_at` | TIMESTAMP | Response send time |
| `received_at` | TIMESTAMP DEFAULT NOW() | Receipt time |
| `processed_at` | TIMESTAMP | Processing time |
| `status` | VARCHAR(50) DEFAULT 'RECEIVED' | Status: RECEIVED, RESPONDED, RED |

**Indexes:**
- `idx_broadcasts_received_league` on `league_id`
- `idx_broadcasts_received_status` on `status`
- `idx_broadcasts_received_type` on `message_type`
- `idx_broadcasts_received_round` on `round_id`
- `idx_broadcasts_received_sender` on `sender_email`

**Common Broadcast Types:**
- `BROADCAST_KEEP_ALIVE` — availability check (requires response)
- `BROADCAST_PAUSE_LEAGUE` — league pause
- `BROADCAST_RESUME_LEAGUE` — league resume
- `BROADCAST_NEW_LEAGUE_ROUND` — new round start
- `BROADCAST_ROUND_RESULTS` — round results
- `BROADCAST_ASSIGNMENT_TABLE` — assignment table

### D.7.2 `pause_state` Table

Saving context when the agent is paused.

**Table 147: `pause_state` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `broadcast_id` | VARCHAR(100) | Pause broadcast ID |
| `previous_state` | VARCHAR(50) | State before pause |
| `previous_match_id` | VARCHAR(100) | Active game before pause |
| `saved_context` | JSONB | Full context snapshot |
| `paused_at` | TIMESTAMP | Pause time |
| `resumed_at` | TIMESTAMP | Resume time |
| `resume_broadcast_id` | VARCHAR(100) | Resume broadcast ID |

## D.8 Season and League Tables

### D.8.1 `season_registrations` Table

Tracking season registrations.

**Table 148: `season_registrations` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `season_id` | VARCHAR(50) UNIQUE | Season ID |
| `league_id` | VARCHAR(50) | League ID |
| `season_name` | VARCHAR(100) | Season name |
| `registration_status` | VARCHAR(20) | Registration status |
| `registered_at` | TIMESTAMP | Registration time |
| `confirmed_at` | TIMESTAMP | Confirmation time |
| `rejection_reason` | VARCHAR(255) | Rejection reason (if relevant) |

**Registration Statuses:**
- `PENDING` — waiting for confirmation
- `CONFIRMED` — registration confirmed
- `REJECTED` — registration rejected
- `WITHDRAWN` — player withdrew

### D.8.2 `my_assignments` Table

Game assignments for the player in each round.

**Table 149: `my_assignments` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `season_id` | VARCHAR(50) | Season ID |
| `round_number` | INTEGER | Round number |
| `game_number` | INTEGER | Game number |
| `role` | VARCHAR(20) | Role: PLAYER_A/PLAYER_B |
| `my_role` | VARCHAR(10) | PRD role: PLAYER1/PLAYER2 |
| `opponent_group_id` | VARCHAR(100) | Opponent group ID |
| `referee_group_id` | VARCHAR(100) | Referee group ID |
| `game_id` | VARCHAR(100) | Game ID (when starts) |
| `match_id` | VARCHAR(50) | Match ID |
| `assignment_status` | VARCHAR(20) | Assignment status |
| `received_at` | TIMESTAMP | Receipt time |
| `started_at` | TIMESTAMP | Start time |
| `completed_at` | TIMESTAMP | Completion time |

**Constraints:**
```sql
UNIQUE(season_id, round_number, game_number)
```

**Assignment Statuses:**
- `PENDING` — waiting to start
- `IN_PROGRESS` — active game
- `COMPLETED` — game completed
- `FAILED` — game failed/abandoned

### D.8.3 `season_standings` Table

League standings by round.

**Table 150: `season_standings` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `season_id` | VARCHAR(50) | Season ID |
| `round_number` | INTEGER | Round number |
| `group_id` | VARCHAR(100) | Group/player ID |
| `total_score` | DECIMAL(10,2) | Cumulative score |
| `games_played` | INTEGER | Number of games |
| `games_won` | INTEGER | Number of wins |
| `rank` | INTEGER | Ranking position |
| `received_at` | TIMESTAMP | Update time |

**Constraints:**
```sql
UNIQUE(season_id, round_number, group_id)
```

## D.9 System Tables

### D.9.1 `schema_version` Table

Tracking schema version for migrations.

**Table 151: `schema_version` Table Columns**

| Column | Type | Description |
|---|---|---|
| `version` | VARCHAR(20) PK | Version number |
| `applied_at` | TIMESTAMP | Version application time |

**Current version: 1.5.0**

### D.9.2 `error_logs` Table

Error documentation with context for debugging.

**Table 152: `error_logs` Table Columns**

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto ID |
| `error_type` | VARCHAR(50) | Error category |
| `error_code` | VARCHAR(50) | Specific error code |
| `error_message` | TEXT | Error description |
| `context` | JSONB | Additional context |
| `stack_trace` | TEXT | Call stack |
| `created_at` | TIMESTAMP | Error time |
| `resolved_at` | TIMESTAMP | Resolution time |
| `resolution_notes` | TEXT | Resolution notes |

**Error Categories:**
- `GMAIL_ERROR` — Gmail API errors
- `PROTOCOL_ERROR` — Invalid message format
- `STATE_ERROR` — Illegal state transition
- `STRATEGY_ERROR` — AI strategy failure
- `DATABASE_ERROR` — Database errors

## D.10 Foreign Key Relationships

**Table 153: Foreign Key Relationships in Schema**

| Source Table | Column | Target Table | Column | ON DELETE |
|---|---|---|---|---|
| `questions` | `game_id` | `game_sessions` | `game_id` | CASCADE |
| `answers` | `game_id` | `game_sessions` | `game_id` | CASCADE |
| `guesses` | `game_id` | `game_sessions` | `game_id` | CASCADE |

**Logical Relationships**

Several relationships in the schema are logical and not enforced by foreign keys:

- `game_sessions.game_id → player_states.current_game_id`
- `game_state.match_id → game_sessions.match_id`
- `game_results.match_id → game_sessions.match_id`
- `season_registrations.season_id → my_assignments.season_id`

This approach allows greater flexibility in data insertion order.

## D.11 Design Patterns

The schema implements several important design patterns:

1. **Cascade Delete**: Questions, answers, and guesses are automatically deleted when the game session is deleted
2. **Uniqueness Constraints**: Preventing duplicates in `match_id`, `game_id`, `player_email`, and compound combinations
3. **JSONB Storage**: Schema flexibility for:
   - Question options (`questions.options`)
   - Message content (`message_logs.payload`)
   - Broadcast content (`broadcasts_received.payload`)
   - Saved context (`pause_state.saved_context`)
   - Transition metadata (`state_transitions.transition_metadata`)
   - Error context (`error_logs.context`)
4. **Audit Trail**: All tables include timestamps, and `state_transitions` provides detailed history
5. **Phase Separation**: The `game_state` table enables precise tracking of game progress

## D.12 Schema Statistics

**Table 154: Database Schema Statistics**

| Metric | Value |
|---|---|
| Total tables | 20 |
| Logical groups | 6 |
| Foreign key constraints | 3 |
| Total indexes | 30+ |
| JSONB columns | 6 |
| Cascade deletes | 3 |
| Uniqueness constraints | 12 |
| Schema version | 1.5.0 |

## D.13 Table Summary by Group

**Table 155: Summary of 20 Tables by Group**

| Group | Tables | Count |
|---|---|---|
| Player and state | `player_states`, `state_transitions` | 2 |
| Game core | `game_sessions`, `game_state`, `game_invitations`, `game_results` | 4 |
| Game data | `questions`, `answers`, `guesses` | 3 |
| Messages and files | `message_logs`, `attachments`, `message_correlations` | 3 |
| Broadcast | `broadcasts_received`, `pause_state` | 2 |
| Season and league | `season_registrations`, `my_assignments`, `season_standings` | 3 |
| System | `schema_version`, `error_logs` | 2 |
| **Total** | | **20** |

---

*© Dr. Segal Yoram - All rights reserved*

# Appendix H: Architectural Principles of the League Manager

## H.1 Introduction

This appendix describes the architectural principles of the league manager server. This material is intended as background for understanding the overall system, and serves as a basis for comparison with the agents architecture (Chapter 2).

## H.2 Separation of Static and Dynamic Data

### H.2.1 The Guiding Principle

The league manager separates between two main types of data:

1. **Static data** -- information that does not change during the season
2. **Dynamic data** -- information that is updated in real time

### H.2.2 Student Groups Table (student_groups)

The student_groups table contains the static information for each group:

Table 203: Static data in the groups table

| Field | Type | Description |
|-------|------|-------------|
| group_id | VARCHAR | Unique group identifier (G001--G030) |
| group_name | VARCHAR(8) | Group name (8 characters) |
| student_emails | JSON | List of students' email addresses |
| player_github_repo | URL | Link to the player repository |
| referee_github_repo | URL | Link to the referee repository |
| registered_at | TIMESTAMP | Registration time in the system |

### H.2.3 Dynamic Data -- Players and Referees

The players tables (players) and referees (referees) contain dynamic data:

- **Current status** -- whether the agent is active, suspended, or disabled
- **Season statistics** -- games, wins, points
- **Current season identifier** -- which season the agent is registered for

## H.3 The Gatekeeper Pattern of the League Manager

### H.3.1 The Problem

Gmail API imposes strict limits on the volume of messages and reads. Exceeding the limits causes temporary blocking of the account.

### H.3.2 The Solution -- Protection Layer

The Gatekeeper of the league manager is a Facade pattern with three components:

Table 204: Components of the league manager's Gatekeeper

| Component | Role | Action on Violation |
|-----------|------|---------------------|
| QuotaManager | Tracking daily quota | Stopping sending until renewal |
| DOSDetector | Identifying suspicious patterns | Temporary blocking and alert |
| RateLimiter | Limiting sending rate | Automatic delay |

> **Operational Limit**
>
> The league manager defines an operational limit of 400 messages per day (out of a quota of 500) in order to preserve a safety margin.

### H.3.3 DoS Detection Layers

The DOSDetector component checks for violations at four time layers:

Table 205: DoS layers of the Gatekeeper

| Layer | Time Window | Maximum Threshold |
|-------|-------------|-------------------|
| PER_MINUTE | One minute | 2 messages |
| PER_HOUR | One hour | 7500 messages |
| PER_8_HOURS | 8 hours | 60000 messages |
| PER_DAY | 24 hours | 144000 messages |

> **Full Gatekeeper Schema**
>
> For a full breakdown of the Gatekeeper tables including gatekeeper_log and documented actions, see Appendix 9 (System Data Model), Section 9.

## H.4 The Clock System of the League Manager

The league manager manages five types of clocks:

Table 206: State machines of the league manager

| Component | Role | States |
|-----------|------|--------|
| LeagueState | Managing league lifecycle | SETUP, REGISTRATION_OPEN, ACTIVE, COMPLETED |
| RefereeState | Managing referee state | Including PAUSED for referee suspension |
| RoundClock | Game round | PENDING, ACTIVE, COMPLETED |
| MessageDeadlineClock | Message response deadline | Managing callbacks (no states) |
| GameWindow | Time window for games | dataclass (no states) |

> **State Architecture**
>
> **LeagueState** and **RoundClock** are the main state machines. PAUSED exists only in **RefereeState** for suspending an individual referee, not for suspending the overall season. In contrast:
> - **GameWindow** -- a dataclass for computing time windows, uses the functions is_active() and is_in_grace()
> - **MessageDeadlineClock** -- manages response deadlines via callbacks, without an explicit state machine

## H.5 Broadcast Consolidation

### H.5.1 The Problem

Sending a broadcast message to 30 participants as 30 separate emails requires 30 API reads.

### H.5.2 The Solution

Instead of sending separate messages, the league manager sends one message with all recipients in the TO field. This reduces API consumption by 97%.

### H.5.3 Broadcast Types in the GTAI Protocol

The system supports 12 broadcast types:

1. BROADCAST_KEEP_ALIVE -- availability check (30s)
2. BROADCAST_FREE_TEXT -- free text message (1h)
3. BROADCAST_CRITICAL_RESET -- system reset (2m)
4. BROADCAST_CRITICAL_PAUSE -- activity suspension (2m)
5. BROADCAST_CRITICAL_CONTINUE -- activity resumption (2m)
6. BROADCAST_NEW_LEAGUE_ROUND -- round start (24h)
7. BROADCAST_END_LEAGUE_ROUND -- round end
8. BROADCAST_END_GROUP_ASSIGNMENT -- group assignment end
9. BROADCAST_START_SEASON -- season start (1m)
10. BROADCAST_END_SEASON -- season end
11. BROADCAST_START_SEASON_REGISTRATION -- registration opening
12. BROADCAST_ROUND_RESULTS -- round results

### H.5.4 Response Mapping

When a recipient responds to a broadcast message, the system identifies the original message via:

1. **broadcast_id** -- unique identifier in the email subject
2. **gatekeeper_log table** -- broadcast_id and original_message_id columns
3. **In-Reply-To field** -- link to the original message header

> **Change in Version 4.0**
>
> In previous versions, the broadcast_transaction_mapping table was used to maintain the mapping. In version 4.0, the functionality was merged into the gatekeeper_log table for efficiency and schema simplification.

## H.6 Context Inheritance

Every message in the system carries context fields that identify its position in the hierarchy:

Table 207: Context fields

| Field | Example | Description |
|-------|---------|-------------|
| league_id | Q21G_2026 | League identifier |
| season_id | S01 | Season identifier |
| round_id | 01 | Round number |
| game_id | 0101001 | Composite game identifier |

> **Protocol Specification**
>
> **Inheritance rule:** A response to a message must include the same context fields that appeared in the original message.

## H.7 State Machines

The league manager uses consistent state patterns:

1. **Lifecycle pattern** -- PENDING -> ACTIVE -> COMPLETED
2. **Registration pattern** -- UNREGISTERED -> REGISTERED -> ACTIVE
3. **Game pattern** -- SCHEDULED -> IN_PROGRESS -> FINISHED
4. **Request pattern** -- PENDING -> APPROVED/REJECTED

### H.7.1 State Transition Principles

- **Unidirectionality** -- transitions advance forward only (except PAUSED)
- **Atomicity** -- a state transition is an atomic operation
- **Documentation** -- every state transition is logged with a timestamp
- **Triggers** -- every transition is activated by a defined event

## H.8 Summary

This appendix summarized the architectural principles of the league manager:

- **Data separation** -- static vs. dynamic
- **Gatekeeper pattern** -- protection over Gmail API
- **Five clocks** -- managing times and deadlines
- **Broadcast consolidation** -- reducing API reads
- **Context inheritance** -- passing context fields in responses
- **State machines** -- consistent patterns for state management

For details on implementing these principles in the player and referee agents, see Chapter 2.

# 3 The League System — Multi-Agent Architecture

## 3.1 Introduction

This chapter presents the modular architecture of the league system. The system is based on a clear separation between different operational layers, which allows for flexibility, easy maintenance, and the ability to replace game rules without changing the protocol.

### 3.1.1 Chapter Objectives

By the end of this chapter, you will understand:
- The principle of separation into three layers: league, refereeing, and game rules
- The three types of agents: league manager, referee, and player
- The state machines of each agent
- The identity (IDs) and tracking mechanism
- The detailed scoring system

## 3.2 Three-Layer Architecture

### 3.2.1 Design Principles

The system was designed according to several guiding principles:

1. **Programming language independence** — Each student can implement an agent in their language of choice
2. **Separation of responsibilities** — Each agent is responsible only for a defined role
3. **Open protocol** — Messages in JSON structure with required and optional fields
4. **Single source of truth** — The referee is the source of truth for game state

### 3.2.2 Three-Layer Diagram

Figure 5 presents the three-layer architecture.

```
┌─────────────────────────────────────────────────────────┐
│                    League Layer (Layer 1)                 │
│         Tournament management, registration, rankings     │
│                    Match assignments                      │
│                                            ┌───────────┐ │
│                                            │ Log Server │ │
│                                            │(CC all    │ │
│                                            │ messages) │ │
├─────────────────────────────────────────────────────────┤
│                    Referee Layer (Layer 2)                │
│      Match management, move validation, winner declaration│
│                     Move validation                      │
├─────────────────────────────────────────────────────────┤
│               Game Rules Layer (Q21G) (Layer 3)           │
│           Game-specific logic, scoring, validation       │
└─────────────────────────────────────────────────────────┘
```

*Figure 5: Three-layer architecture with the log server*

### 3.2.3 Layer 1: League Management

The League Layer is responsible for:
- **Player and referee registration** — Intake and assignment of unique identifiers
- **Game schedule creation** — Assignment of triplets for each round
- **Ranking management** — Calculation and publication of the ranking table
- **Broadcasts** — General messages to all participants

### 3.2.4 Layer 2: Game Refereeing

The Referee Layer manages individual games:
- **Arrival coordination** — Inviting players and receiving confirmation
- **Game phase management** — Transitioning between different phases
- **Score calculation** — Evaluating guesses and providing feedback
- **Reporting to the league** — Sending results to the league manager

### 3.2.5 Layer 3: Game Rules

The Game Rules Layer contains Q21G logic:
- **Paragraph selection** — Selection from lecture materials
- **Clue creation** — Title, description, association
- **Answer validation** — Checking questions and answers
- **Score calculation** — The four components

## 3.3 Agent Types

### 3.3.1 Interaction Diagram

Figure 6 presents the communication between agents, including broadcast flow.

```
                    ┌─────────────┐
                    │  Log Server │
                    │   (Audit)   │
                    └──────┬──────┘
                           │ CC
              ┌────────────┼────────────┐
              │      League Manager     │
              │  MatchResult | assign   │
              │     Broadcast           │
              └────┬────────────────────┘
                   │ Broadcast
            ┌──────┴──────┐
            │   Referee   │
            │             │
            │ Game msgs   │ Game msgs
            └──────┬──────┘
              ┌────┴─────┐
         ┌────┴──┐   ┌───┴───┐
         │Player │   │Player │
         │  A    │   │  B    │
         └───────┘   └───────┘

Purple = Broadcasts
Red = CC to Log
```

*Figure 6: Agent interaction diagram — including broadcasts and log server*

### 3.3.2 Main Communication Flows

**Table 33: Main Communication Flows**

| Flow | Sender | Recipients |
|---|---|---|
| Registration | Player/Referee | League Manager |
| Game assignment | League Manager | Referee and Players |
| Game invitation | Referee | Both Players |
| Game messages | Referee ↔ Player (bidirectional) | — |
| Broadcast | League Manager | All Participants |
| Result reporting | Referee | League Manager |
| Documentation (CC) | All Senders | Log Server |

### 3.3.3 League Agent (League Manager)

A Singleton agent that manages the entire tournament:

**Table 34: League Manager Responsibilities**

| Domain | Actions | Messages |
|---|---|---|
| Registration | Intake of players and referees | REGISTER_REQUEST/RESPONSE |
| Scheduling | Game schedule creation | ROUND_ANNOUNCEMENT |
| Assignment | Mapping games to triplets | MATCH_ASSIGNMENT |
| Ranking | Points and ranking calculation | STANDINGS_UPDATE |

### 3.3.4 Referee Agent

Each student implements a referee agent that manages a single game. The referee is the sole source of truth for the game state.

**Referee Responsibilities:**

1. League registration — The referee must register with the league manager before games start (see Chapter 7)
2. Paragraph selection and clue creation
3. Sending clues to players
4. Receiving questions and providing answers
5. Receiving guesses and calculating scores
6. Returning detailed feedback to players
7. Reporting results to the league manager

### 3.3.5 Player Agent

Each student implements a player agent that competes in games.

**Player Responsibilities:**

1. League registration and receiving an ID
2. Responding to game invitations
3. Receiving clues and creating 20 questions
4. Receiving answers and preparing the final guess
5. Sending the guess with reasoning

## 3.4 State Machines

### 3.4.1 Game State Machine (from the Referee's Perspective)

Figure 7 shows the state transitions of a single game as the referee manages it. The machine includes 12 states representing all game phases from the moment of assignment to completion or failure.

```
                         PENDING
                    (assignment received)
                           │
                        WARMUP
                  (players confirmed)
                           │
                    WARMUP_COMPLETE
                           │
                      ROUND_START
                     (hints sent)
                           │
                       QUESTIONS
                  (waiting for questions)  ─────────► FAILED
                           │                         (timeout/error)
                   QUESTIONS_COMPLETE
                           │
                      ANSWERS_SENT
                   (waiting for guesses)
                           │
                        GUESSING
                (all guesses received)
                           │
                  GUESSING_COMPLETE
                  (calculate scores)
                           │
                        SCORING
                  (results reported)
                           │
                       COMPLETE
```

*Figure 7: Single game state machine — 12 states from the referee's perspective*

### 3.4.2 Game State Descriptions

Table 35 describes all 12 game states:

**Table 35: Game State Descriptions**

| State | Description | Referee Action |
|---|---|---|
| PENDING | Waiting for assignment | Receiving MATCH_ASSIGNMENT |
| WARMUP | Warmup phase | Sending Q21_WARMUP_CALL, waiting for confirmations |
| WARMUP_COMPLETE | Warmup completed | All players confirmed, preparing clues |
| ROUND_START | Round start | Sending Q21_ROUND_START to players |
| QUESTIONS | Questions phase | Waiting to receive 20 questions from each player |
| QUESTIONS_COMPLETE | Questions received | Processing and providing answers |
| ANSWERS_SENT | Answers sent | Sending answers to players |
| GUESSING | Guessing phase | Waiting for final guesses |
| GUESSING_COMPLETE | Guesses received | All guesses received |
| SCORING | Score calculation | Calculating scores and sending feedback |
| COMPLETE | Game ended | Reporting results to league manager |
| FAILED | Game failed | Reporting failure to league manager |

### 3.4.3 Player Agent State Machine

The player agent transitions between defined states. Each state determines which actions are allowed:

**Table 36: Player Agent States — Registration**

| State | Description | Allowed Actions |
|---|---|---|
| INIT_START_STATE | Agent not yet registered | Sending registration request |
| REGISTERING | Waiting for registration confirmation | Waiting for response |
| REGISTERED | Registered in the league | Waiting for assignments |
| AWAITING_ASSIGNMENT | Waiting for assignment table | Receiving assignments |
| INVITED | Received game invitation | Confirming invitation |
| PAUSED | Suspended (PAUSE broadcast) | Waiting for CONTINUE |
| ERROR | An error occurred | Recovery attempt |

**Table 37: Player Agent States — In-Game**

| State | Description | Allowed Actions |
|---|---|---|
| IN_MATCH | Game started | Receiving warmup call |
| WARMUP | Warmup phase | Answering warmup question |
| QUESTIONING | Questions phase | Creating and sending questions |
| AWAITING_ANSWERS | Waiting for answers | Receiving answer batches |
| GUESSING | Guessing phase | Creating and sending guess |
| MATCH_COMPLETE | Game ended | Receiving results, next game |

```
INIT_START_STATE → (REGISTER_REQ) → REGISTERING → (SUCCESS) → REGISTERED
→ (SEASON_START) → AWAITING_ASSIGNMENT → (INVITATION) → INVITED
→ (ACCEPTED) → IN_MATCH → (WARMUP_CALL) → WARMUP → (RESPONSE) → QUESTIONING
→ (ANSWERS) → GUESSING → (RESULT) → [back to AWAITING_ASSIGNMENT]
```

*Figure 8: Event-based player agent state machine*

### 3.4.4 Referee Agent State Machine

The referee agent uses a two-level architecture: the referee state machine (high level) and the game state machine (detailed game phases). The referee state machine manages 6 states:

**Table 38: Referee Agent States (RefereeState)**

| State | Description | Allowed Actions |
|---|---|---|
| INIT_START_STATE | Initial state after initialization | Sending registration request |
| WAITING_FOR_CONFIRMATION | Waiting for registration confirmation | Waiting for response |
| RUNNING | Active and waiting (registered) | Receiving game assignment |
| WAITING_FOR_ASSIGNMENT | Waiting for assignment | Receiving MATCH_ASSIGNMENT |
| IN_GAME | Managing active game | Managing game phases |
| PAUSED | Suspended by league manager | Waiting for CONTINUE |

> **Separation of Responsibilities**
>
> SCORING and REPORTING phases are not part of the referee states — they are managed by the game state machine (Table 35).
>
> When the referee is in IN_GAME state, the game state machine tracks the specific phase (WARMUP, QUESTIONS, SCORING, etc.).

```
INIT_START_STATE → (register) → WAITING_FOR_CONFIRMATION → (confirmed) → RUNNING
→ (assignment) → WAITING_FOR_ASSIGNMENT → (match start) → IN_GAME
↕ PAUSE/CONTINUE ↕ PAUSED
→ (game complete) → [back to RUNNING]
```

*Figure 9: Referee agent state machine — 6 states*

## 3.5 Game Group Assignment Table

### 3.5.1 Table Schema

Table 39 presents the structure of the season_assignments table. The implementation uses a normalized design: 3 rows per game (one row per participant), instead of one row with separate columns per participant.

**Table 39: season_assignments Table Schema (Normalized)**

| Field | Type |
|---|---|
| id | SERIAL PRIMARY KEY |
| season_id | VARCHAR(50) NOT NULL |
| round_number | INTEGER NOT NULL |
| game_number | INTEGER NOT NULL |
| group_id | VARCHAR(20) NOT NULL |
| participant_id | VARCHAR(100) NOT NULL |
| role | VARCHAR(20) NOT NULL |
| assignment_status | CHAR(20) DEFAULT 'PENDING' |
| assigned_at | TIMESTAMP DEFAULT NOW() |
| notified_at | TIMESTAMP |
| confirmed_at | TIMESTAMP |

Constraints:
```sql
UNIQUE(season_id, round_number, game_number, role)
CHECK (role IN ('REFEREE', 'PLAYER_A', 'PLAYER_B'))
```

> **Normalized Design**
>
> - Each game is represented by 3 rows — one row per participant (referee, Player A, Player B)
> - The game ID (SSRRGGG) is composed of the combination: season_id + round_number + game_number
> - This design enables separate tracking of each participant (notified_at, confirmed_at)

### 3.5.2 Game States (game_status)

Figure 10 shows the game status state machine. For a description of the possible game states see Table 5 in Chapter 1.

```
                    assigned_and_waiting
                   /         |          \
        all 3 responded  timeout    referee reports issue
              │               │              │
    referee_responsibility  no_response   malfunction
              │
        results reported
              │
           game_end

        Force Majeure restart (from malfunction or no_response)
```

*Figure 10: Game status state machine — five possible states*

### 3.5.3 Important Distinction

**malfunction** — The referee reported a technical malfunction during the game (system problem, network failure, etc.). In this case, a force majeure request can be made.

**no_response** — The referee did not respond at all until the end of the round. In this case, the referee receives 0 points and both players receive 2 points each.

## 3.6 Identity Model

### 3.6.1 ID Types

The system defines several ID types for unambiguous tracking. Some IDs are validated using regex patterns:

**Table 40: ID Types in the System**

| ID | Format/Pattern | Example | Description |
|---|---|---|---|
| league_id | Fixed string | Q21G | League ID (hardcoded) |
| season_id | ^[SW]\d{2}$ | S01, W01 | Season ID (summer/winter) |
| round_id | ^\d{2}$ | 01–06 | Round number |
| game_id | ^\d{7}$ (SSRRGGG) | 0101003 | Composite game ID |
| player_id | String (no validation) | P-Q21G-001 | Player ID |
| referee_id | String (no validation) | R-Q21G-001 | Referee ID |
| message_id | UUID v4 | 550e8400-... | Unique message ID |

> **ID Validation**
>
> - season_id, round_id, game_id are validated using regex in context.py
> - player_id and referee_id are not validated in code — used as free strings
> - league_id is hardcoded ("Q21G") and not dynamically validated

## 3.7 Detailed Scoring System

### 3.7.1 The Four Score Components

Each player's guess is evaluated on four components:

**1. Opening Sentence Accuracy (50%):**
- Linguistic match — words, order, structure
- Conceptual match — idea, role of the opening
- High score for good match, medium for partial match

**2. Sentence Reasoning (20%):**
- Intelligent use of the answers received
- Logical connection to the general description
- Depth of understanding of the opening sentence's role

**3. Associative Word Accuracy (20%):**
- Match to the word or close variations
- Distant association or from the wrong domain — low score

**4. Association Reasoning (10%):**
- Intelligent connection between the word and the paragraph's topic
- Shallow or incidental reasoning — low score

### 3.7.2 Feedback Requirement

The referee is obligated to return to each player:
- The total numerical score (0–100)
- Breakdown for each of the four components
- Verbal explanation of 30–50 words for each component, justifying the score given

> **Verbal Explanation Requirement**
>
> The referee must provide a verbal explanation of 30–50 words for each of the four score components. The explanation should justify why the specific score was given, with reference to the quality of the guess relative to the correct answer. An explanation that is too short or too long will be considered a reporting defect.

### 3.7.3 Reporting to the League Manager

At the end of the game, the referee is obligated to send a result report (MATCH_RESULT_REPORT) to the league manager including:
- League scores (0–3) of both players
- Private scores (0–100) of both players
- Verbal summary of 30–50 words describing the game course and overall performance

## 3.8 Error Handling

### 3.8.1 Error Codes

**Table 41: Main Error Codes**

| Code | Name | Description | Retryable |
|---|---|---|---|
| E001 | TIMEOUT_ERROR | Response not received on time | Yes |
| E005 | NOT_REGISTERED | Agent not registered | No |
| E009 | CONNECTION_ERROR | Network failure | Yes |
| E011 | AUTH_MISSING | Authentication token missing | No |
| E012 | AUTH_INVALID | Invalid token | No |
| E020 | MALFUNCTION_REPORTED | Referee reported a malfunction | No |
| E021 | NO_RESPONSE | No response until end of round | No |
| E022 | FORCE_MAJEURE | Force majeure — game cancelled | No |

### 3.8.2 Retry Policy

The retry policy in the system varies according to the game phase. Below is a table describing actual retry behavior:

**Table 42: Retry Policy by Game Phase**

| Phase | Retries | Delay | Failure Result |
|---|---|---|---|
| WARMUP | 1 | Exponential backoff | Technical loss (0 points) |
| QUESTIONS | 0 | — | 0 points for questions |
| GUESS | 0 | — | 0 points for guess |

#### 3.8.2.1 General Retry Definition

The system uses retry configuration with exponential backoff:

```python
# RetryConfig configuration
class RetryConfig:
    max_attempts: int = 3      # Maximum number of attempts
    base_delay: float = 1.0    # Initial delay in seconds
    max_delay: float = 60.0    # Maximum delay in seconds
    exponential_base: float = 2.0  # Exponential multiplier
```

The delay between attempts grows exponentially: 1 second, 2 seconds, 4 seconds, and so on up to a maximum of 60 seconds. This approach allows for a quick first attempt while protecting the system from overload.

**Table 43: Failure Results by Phase**

| Phase | Failure Behavior |
|---|---|
| WARMUP | If no response after one attempt — technical loss (forfeit) with 0 points |
| QUESTIONS | No retry — timeout results in 0 points in the questions phase |
| GUESS | No retry — timeout results in 0 points in the guessing phase |

> **Difference from Original Specification**
>
> The original specification defined 3 attempts for each phase with a fixed delay of 60 seconds. The actual implementation differs:
> - Warmup: One attempt only (not 3)
> - Questions and guess: No retry at all
> - Delay: Exponential backoff (not fixed)

#### 3.8.2.2 League Manager Messages

Note that the league manager can approve a blanket assessment. Your agents need to know how to receive the league manager's message and adjust schedules according to the league manager's message. For example, the league manager can announce that a specific game or game round receives a new time window, in which case the games that received a time window from the league manager are reset and take place again. Prepare the agents accordingly. During warmup time windows, you will be able to practice this topic with the league manager.

## 3.9 Summary

This chapter presented the league system architecture:

- Three-layer architecture: league, refereeing, and game rules
- Three types of agents: league manager, referee, and player
- The log server receives CC of all game messages (quantitative analysis in Appendix E)
- Defined state machines for the game and for each agent
- Game group assignment table with five possible states
- Distinction between malfunction (reported failure) and no_response (non-response)
- Identity model with unique IDs for tracking
- Detailed scoring system with four components

In the next chapter, we will delve into the detailed communication protocol between agents.

---

*© Dr. Segal Yoram - All rights reserved*

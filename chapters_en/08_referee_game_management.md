# 8 Referee Game Management

## 8.1 Introduction

This chapter describes the complete game management process from the perspective of the referee agent. After the league manager sends a game assignment (`MATCH_ASSIGNMENT`), the referee is responsible for managing the game from start to finish.

This chapter details all communication phases: from sending the warmup question to reporting results to the league manager.

### 8.1.1 Chapter Objectives

By the end of this chapter, you will understand:

- The season registration process and receiving the assignment table
- The process of receiving a game assignment from the manager
- The complete message flow in a Q21G game
- The scoring calculation and results reporting process
- Handling errors and deadlines

## 8.2 Season Registration and Assignment Table

Before the referee can manage a game, they must register for the season and receive the assignment table. This process is identical for player agents and referee agents — each one registers separately.

### 8.2.1 Registration Process

1. **Opening registration**: The league manager sends `BROADCAST_START_SEASON_REGISTRATION` to all participants.
2. **Sending registration request**: Each agent (player or referee) sends `SEASON_REGISTRATION_REQUEST` with their details.
3. **Registration confirmation**: The league manager sends `RESPONSE_SEASON_REGISTRATION` with the registration status.

**SEASON_REGISTRATION_REQUEST — Season Registration Request**

```json
{
  "protocol": "1.0",
  "messagetype": "SEASONREGISTRATIONREQUEST",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "leagueid": "Q21G",
  "payload": {
    "season_id": "SEASON_2026_A",
    "user_id": "ghost002",
    "display_name": "GTAI League Referee"
  }
}
```

### 8.2.2 The Assignment Table

After all participants have registered, the league manager sends the assignment table (`BROADCAST_ASSIGNMENT_TABLE`) to all participants. The table contains all the games in all rounds and specifies who plays against whom and who is the referee in each game.

> **Important — Filtering Assignments**
>
> Each agent filters from the table only the assignments relevant to them:
> - **Player agent**: filters assignments with `role = "player1"` or `role = "player2"` where their email appears.
> - **Referee agent**: filters assignments with `role = "referee"` where their email appears.

**BROADCAST_ASSIGNMENT_TABLE — Assignment Table**

```json
{
  "protocol": "1.0",
  "messagetype": "BROADCAST_ASSIGNMENT_TABLE",
  "sender": {
    "email": "league.manager@gmail.com",
    "role": "LEAGUEMANAGER"
  },
  "payload": {
    "season_id": "SEASON_2026_A",
    "broadcast_id": "ASSIGN-2026-02-01-001",
    "assignments": [
      {
        "game_id": "GAME001",
        "role": "referee",
        "email": "referee@gmail.com",
        "group_id": "ghost002"
      },
      {
        "game_id": "GAME001",
        "role": "player1",
        "email": "alice@gmail.com",
        "group_id": "alpha001"
      },
      {
        "game_id": "GAME001",
        "role": "player2",
        "email": "bob@gmail.com",
        "group_id": "beta002"
      }
    ]
  }
}
```

After receiving the table, each agent sends an acknowledgment (`RESPONSE_GROUP_ASSIGNMENT`):

**RESPONSE_GROUP_ASSIGNMENT — Assignment Acknowledgment**

```json
{
  "protocol": "1.0",
  "messagetype": "RESPONSE_GROUP_ASSIGNMENT",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "payload": {
    "season_id": "SEASON_2026_A",
    "group_id": "ghost002",
    "assignments_received": 2,
    "status": "ACKNOWLEDGED"
  }
}
```

### 8.2.3 Season and Round Start

After all participants have received the assignments, the league manager sends:

1. `BROADCAST_START_SEASON` — message about the start of the season.
2. `BROADCAST_NEW_LEAGUE_ROUND` — message about the start of a new round.

> **Game Rules — When Does the Referee's Responsibility Begin?**
>
> When the referee receives a `BROADCAST_NEW_LEAGUE_ROUND` message, they check their assignment table. If they have an assignment for the current round, they begin managing the game by sending (or receiving, in a centralized architecture) a `MATCH_ASSIGNMENT` message.
>
> From this moment on — the referee is responsible for the entire game flow as described in this chapter.
>
> **Important Note — Simple Flow**
>
> In the current protocol, the referee does NOT send a game invitation (`GAME_INVITATION`). Instead, the referee sends directly the warmup message (`Q21_WARMUP_CALL`) immediately after receiving the game assignment. The warmup response serves as the player's readiness confirmation.

## 8.3 Protocol Message Formats

### 8.3.1 Email Subject Format

Every message is sent as an email with a subject in the following format:

```
{protocol}::{role}::{sender_email}::{transaction_id}::{message_type}
```

**Table 74: Email Subject Components**

| Component | Description |
|---|---|
| `protocol` | Protocol version: `league.v2` or `Q21G.v1` |
| `role` | Sender's role: `REFEREE`, `PLAYER`, `LEAGUEMANAGER` |
| `sender_email` | Sender's email address |
| `transaction_id` | Unique transaction ID (e.g., `tx-abc123`) |
| `message_type` | Message type (without underscores) |

### 8.3.2 Protocol Versions

**Table 75: Protocol Versions**

| Protocol | Usage | Attachment Filename |
|---|---|---|
| `league.v2` | General league messages | `message.json` |
| `Q21G.v1` | Q21G game messages | `payload.json` |

### 8.3.3 Q21G.v1 JSON Envelope Structure

```json
{
  "protocol": "1.0",
  "messagetype": "Q21ROUNDSTART",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "timestamp": "2026-02-01T10:30:00Z",
  "conversationid": "conv-match-001",
  "leagueid": "LEAGUE001",
  "seasonid": "SEASON_2026",
  "roundid": "SEASON_2026_R1",
  "gameid": "GAME001",
  "recipientid": "player@gmail.com",
  "payload": { ... }
}
```

## 8.4 Complete Game Message Flow

### 8.4.1 Game Flow Diagram

```
LGM          Referee         Player A        Player B
 │                │                │                │
 │─MATCH_ASSIGN──>│                │                │
 │                │                │                │
 │                │──Q21_WARMUP───>│                │
 │                │──Q21_WARMUP────────────────────>│
 │                │<──WARMUP_RESP──│                │
 │                │<──WARMUP_RESP──────────────────|│
 │                │                │                │
 │                │──Q21_ROUND────>│                │
 │                │──Q21_ROUND─────────────────────>│
 │                │<──QUESTIONS────│                │
 │                │<──QUESTIONS────────────────────|│
 │                │──ANSWERS──────>│                │
 │                │──ANSWERS───────────────────────>│
 │                │<──GUESS────────│                │
 │                │<──GUESS────────────────────────|│
 │                │──SCORE────────>│                │
 │                │──SCORE─────────────────────────>│
 │<─RESULT────────│                │                │
```

*Figure 18: Complete Q21G game message flow*

> **Game Rules — Unimplemented Messages**
>
> The current protocol does NOT use the following messages (even though they are mentioned in older documentation):
> - `GAME_INVITATION` — the referee sends `Q21_WARMUP_CALL` directly
> - `GAME_JOIN_ACK` — the warmup response serves as readiness confirmation
> - `Q21_QUESTIONS_CALL` — merged into `Q21_ROUND_START`
> - `Q21_GUESS_CALL` — not required, `Q21_ANSWERS_BATCH` includes `guess_deadline`

## 8.5 Receiving the Game Assignment

### 8.5.1 MATCH_ASSIGNMENT Message

When a new round begins, the league manager sends the referee the specific game details:

**MATCH_ASSIGNMENT Message — League Manager to Referee**

```json
{
  "protocol": "1.0",
  "messagetype": "MATCHASSIGNMENT",
  "sender": {
    "email": "league.manager@gmail.com",
    "role": "LEAGUEMANAGER"
  },
  "payload": {
    "match_id": "MATCH001",
    "season_id": "SEASON_2026",
    "round_id": "SEASON_2026_R1",
    "round_number": 1,
    "game_number": 1,
    "player_a": {
      "email": "player1@gmail.com",
      "name": "Player One",
      "user_id": "alpha001"
    },
    "player_b": {
      "email": "player2@gmail.com",
      "name": "Player Two",
      "user_id": "beta002"
    },
    "book": {
      "name": "The Little Prince",
      "description": "A philosophical tale about love and loss",
      "associative_domain": "animal",
      "opening_sentence": "All grown-ups were once children...",
      "associative_word": "fox"
    }
  }
}
```

> **Game Rules — Book Information**
>
> The referee receives the complete book information including:
> - `opening_sentence` — the opening sentence (the correct answer)
> - `associative_word` — the associative word (the correct answer)
> - `description` — a general hint for the players
> - `associative_domain` — the associative domain
>
> The referee uses this information to compare players' answers and calculate scores. The referee **never** reveals the correct answers to the players.

## 8.6 Warmup Phase

### 8.6.1 Sending the Warmup Question

Immediately after receiving the game assignment, the referee sends a warmup question to both players:

**Q21_WARMUP_CALL Message — Referee to Player**

```json
{
  "protocol": "1.0",
  "messagetype": "Q21WARMUPCALL",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "payload": {
    "match_id": "MATCH001",
    "book_description": "A philosophical tale about love and loss",
    "associative_domain": "animal",
    "warmup_question": "What is 2 + 2?"
  }
}
```

**Table 76: Warmup Message Fields**

| Field | Description |
|---|---|
| `match_id` | Unique game ID |
| `book_description` | General book description (hint for player) |
| `associative_domain` | The associative domain |
| `warmup_question` | The warmup question (usually a math calculation) |

### 8.6.2 Warmup Response from Player

**Q21_WARMUP_RESPONSE Message — Player to Referee**

```json
{
  "protocol": "1.0",
  "messagetype": "Q21WARMUPRESPONSE",
  "sender": {
    "email": "player1@gmail.com",
    "role": "PLAYER"
  },
  "payload": {
    "match_id": "MATCH001",
    "answer": "4"
  }
}
```

> **Implementation Tip**
>
> Warmup questions are usually a simple math calculation like "2+2=?". The player calculates the answer ("4") and returns it. If it's not a math question, the default is "42". The warmup response serves as confirmation that the player is ready and active.

**Table 77: Warmup Phase Details**

| Parameter | Value | Notes |
|---|---|---|
| Response deadline | 300 seconds (5 minutes) | |
| Number of attempts | 1 | One additional attempt allowed |
| Failure | 0 points | Player loses technically |

## 8.7 Round Start Phase

### 8.7.1 Round Start Message

After receiving warmup responses from both players, the referee sends the book details and request for questions:

**Q21_ROUND_START Message — Referee to Player**

```json
{
  "protocol": "1.0",
  "messagetype": "Q21ROUNDSTART",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "payload": {
    "match_id": "MATCH001",
    "round_number": 1,
    "book_name": "The Little Prince",
    "description": "A philosophical tale about love and loss",
    "associative_domain": "animal",
    "your_role": "QUESTIONER",
    "questions_required": 20,
    "time_limit_minutes": 10,
    "instruction": "Submit exactly 20 multiple-choice questions",
    "question_count": 20,
    "response_deadline": "2026-02-01T10:40:00Z"
  }
}
```

> **Game Rules — Information Disclosure**
>
> Note: The referee does **not** reveal the opening sentence or the associative word to the players. They receive only:
> - Book name (`book_name`)
> - General description (`description`)
> - Associative domain (`associative_domain`)
> - Instructions for question submission (`instruction`)
>
> This message replaces `Q21_QUESTIONS_CALL` — there is no separate message for questions request.

## 8.8 Questions and Answers Phase

### 8.8.1 Receiving Questions from the Player

The player sends 20 questions:

**Q21_QUESTIONS_BATCH Message — Player to Referee**

```json
{
  "protocol": "1.0",
  "messagetype": "Q21QUESTIONSBATCH",
  "sender": {
    "email": "player1@gmail.com",
    "role": "PLAYER"
  },
  "payload": {
    "match_id": "MATCH001",
    "questions": [
      {
        "number": 1,
        "text": "Does the opening sentence mention a person?",
        "choices": {"A": "Yes", "B": "No", "C": "Partially", "D": "Unknown"}
      },
      {
        "number": 2,
        "text": "Is the associative word a mammal?",
        "choices": {"A": "Yes", "B": "No"}
      }
    ],
    "strategy_used": "llm"
  }
}
```

### 8.8.2 Sending Answers to the Player

The referee answers all questions and sends the answers with the guess deadline:

**Q21_ANSWERS_BATCH Message — Referee to Player**

```json
{
  "protocol": "1.0",
  "messagetype": "Q21ANSWERSBATCH",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "payload": {
    "match_id": "MATCH001",
    "answers": [
      {"question_number": 1, "answer": "A"},
      {"question_number": 2, "answer": "A"},
      {"question_number": 3, "answer": "B"},
      {"question_number": 4, "answer": "NOT_RELEVANT"}
    ],
    "guess_deadline": "2026-02-01T10:50:00Z"
  }
}
```

> **Implementation Tip**
>
> `guess_deadline` field: The answers message includes the final deadline for submitting the guess. There is no need for a separate `Q21_GUESS_CALL` message. The player knows when to submit the guess from this message.

**Table 78: Possible Answer Values**

| Value | Meaning |
|---|---|
| `A` | Yes / Positive |
| `B` | No / Negative |
| `C` | Partial / Sometimes |
| `D` | Unknown / Cannot determine |
| `NOT_RELEVANT` | The question is not relevant |

**Table 79: Questions Phase Deadlines**

| Phase | Deadline | Notes |
|---|---|---|
| Sending questions | 600 seconds (10 minutes) | From round start |
| Sending guess | 300 seconds (5 minutes) | From receiving answers |

## 8.9 Final Guess Phase

### 8.9.1 Receiving Guess from the Player

The player sends the final guess with justifications. The guess is sent automatically immediately after receiving the answers:

**Q21_GUESS_SUBMISSION Message — Player to Referee**

```json
{
  "protocol": "1.0",
  "messagetype": "Q21GUESSSUBMISSION",
  "sender": {
    "email": "player1@gmail.com",
    "role": "PLAYER"
  },
  "payload": {
    "match_id": "MATCH001",
    "opening_sentence_guess": "All grown-ups were once children...",
    "sentence_justification": "Based on answers indicating past tense...",
    "associative_word_guess": "fox",
    "word_justification": "The answers confirmed mammal, clever...",
    "confidence": 0.85,
    "strategy_used": "llm"
  }
}
```

> **Scoring Method — Justification Limits**
>
> - Opening sentence justification: 30–50 words
> - Associative word justification: 20–30 words

## 8.10 Scoring and Feedback Phase

### 8.10.1 The Dual Scoring System

The system uses two types of scoring:

**Table 80: Score Types**

| Type | Range | Usage |
|---|---|---|
| `league_score` | 0–3 | League ranking (public) |
| `private_score` | 0–100 | Detailed score (private) |

**Table 81: League Score Values**

| Score | Meaning |
|---|---|
| 3 | Win |
| 1 | Draw |
| 1 | Loss |
| 0 | Technical loss / Disqualification |

### 8.10.2 Private Score Components

**Table 82: Private Score Components**

| Component | Range | Weight |
|---|---|---|
| Opening sentence guess | 0–50 | High |
| Sentence justification | 0–20 | Medium |
| Associative word guess | 0–20 | Medium |
| Word justification | 0–10 | Low |
| **Total** | **0–100** | — |

### 8.10.3 Sending Feedback to the Player

**Q21_SCORE_FEEDBACK Message — Referee to Player**

```json
{
  "protocol": "1.0",
  "messagetype": "Q21SCOREFEEDBACK",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "recipientid": "player1@gmail.com",
  "payload": {
    "match_id": "MATCH001",
    "league_score": 3,
    "private_score": 85.5,
    "breakdown": {
      "opening_sentence_score": 45.0,
      "sentence_justification_score": 18.0,
      "associative_word_score": 15.0,
      "word_justification_score": 7.5
    },
    "feedback": {
      "opening_sentence": "Very close match!",
      "associative_word": "Correct!"
    },
    "match_league_scores": [
      {"email": "player1@gmail.com", "user_id": "alpha001", "league_score": 3},
      {"email": "player2@gmail.com", "user_id": "beta002", "league_score": 1},
      {"email": "referee@gmail.com", "user_id": "ghost002", "league_score": 3}
    ]
  }
}
```

> **Game Rules — Information Security**
>
> The referee **never** reveals:
> - `actual_opening_sentence` — the real opening sentence
> - `actual_associative_word` — the real associative word
>
> Players receive only feedback and scoring, not the correct answers.
>
> **Referee Scoring**: If there is a winner, the referee receives 2 points. In a draw (no winner), the referee receives 0 points. The referee's private score is always 0.
>
> **Referee Failure**: If a failure occurs in the referee agent (technical failure), the referee receives 0 points, while both players (who did not experience a failure) each receive 2 points.

## 8.11 Reporting Results to the League Manager

### 8.11.1 Game Results Message

After sending feedback to both players, the referee reports the results to the league manager:

**MATCH_RESULT_REPORT Message — Referee to League Manager**

```json
{
  "protocol": "1.0",
  "messagetype": "MATCHRESULTREPORT",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "recipientid": "league.manager@gmail.com",
  "payload": {
    "match_id": "MATCH001",
    "winner_id": "alpha001",
    "is_draw": false,
    "scores": [
      {
        "email": "player1@gmail.com",
        "user_id": "alpha001",
        "league_score": 3,
        "private_score": 85.5
      },
      {
        "email": "player2@gmail.com",
        "user_id": "beta002",
        "league_score": 1,
        "private_score": 45.0
      },
      {
        "email": "referee@gmail.com",
        "user_id": "ghost002",
        "league_score": 3,
        "private_score": 0
      }
    ]
  }
}
```

**Table 83: Game Results Fields**

| Field | Description |
|---|---|
| `match_id` | Unique game ID |
| `winner_id` | Winner ID, or `null` in a draw |
| `is_draw` | `true` if the game ended in a draw |
| `scores` | List of scores for all participants |

## 8.12 Error Handling and Deadlines

### 8.12.1 Deadline Table

**Table 84: Deadlines Summary**

| Phase | Deadline | Attempts | Action on Failure |
|---|---|---|---|
| Connectivity check | 60 seconds | 1 | Report error |
| Warmup | 300 seconds | 1 | Technical loss |
| Questions | 600 seconds | 0 | Technical loss |
| Guess | 300 seconds | 0 | Technical loss |
| Game results | 300 seconds | 1 | Log report |

### 8.12.2 Game Error Message

When a failure occurs, the referee sends an error message to the league manager:

**GAME_ERROR Message — Referee to League Manager**

```json
{
  "protocol": "1.0",
  "messagetype": "GAMEERROR",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE"
  },
  "payload": {
    "match_id": "MATCH001",
    "error_code": "PLAYER_TIMEOUT",
    "error_message": "Player failed to respond within deadline",
    "affected_player": "player1@gmail.com",
    "phase": "QUESTIONS"
  }
}
```

**Table 85: Error Codes**

| Code | Description |
|---|---|
| `PLAYER_TIMEOUT` | Player did not respond in time |
| `INVALID_RESPONSE` | Incorrect response format |
| `DUPLICATE_SUBMISSION` | Player sent twice |
| `OUT_OF_ORDER` | Message in wrong phase |
| `MATCH_NOT_FOUND` | Unrecognized game ID |

## 8.13 Handling Broadcast Messages

### 8.13.1 Broadcast Messages the Referee Handles

During game management, the referee may receive broadcast messages from the league manager:

**Table 86: Broadcast Messages for the Referee**

| Message | Response Required | Deadline |
|---|---|---|
| `BROADCAST_KEEP_ALIVE` | `RESPONSE_KEEP_ALIVE` | 300 seconds |
| `BROADCAST_CRITICAL_PAUSE` | `RESPONSE_CRITICAL_PAUSE` | 120 seconds |
| `BROADCAST_CRITICAL_CONTINUE` | `RESPONSE_CRITICAL_CONTINUE` | 120 seconds |
| `BROADCAST_CRITICAL_RESET` | `RESPONSE_CRITICAL_RESET` | 120 seconds |
| `BROADCAST_START_SEASON` | `SEASON_REGISTRATION_REQUEST` | — |
| `BROADCAST_ASSIGNMENT_TABLE` | `RESPONSE_GROUP_ASSIGNMENT` | — |
| `BROADCAST_NEW_LEAGUE_ROUND` | Start games | — |

### 8.13.2 Example — KEEP_ALIVE Response

**RESPONSE_KEEP_ALIVE Message — Referee to League Manager**

```json
{
  "protocol": "1.0",
  "messagetype": "RESPONSEKEEPALIVE",
  "sender": {
    "email": "referee@gmail.com",
    "role": "REFEREE",
    "logical_id": "ghost002"
  },
  "payload": {
    "machine_state": "IN_GAME",
    "state_detail": "managing_match_MATCH001",
    "message_text": "Referee managing active match"
  }
}
```

**Table 87: Referee State Machine States (RefereeState)**

| State | Description |
|---|---|
| `INIT_START_STATE` | Initial state after initialization |
| `WAITING_FOR_CONFIRMATION` | Waiting for registration confirmation |
| `RUNNING` | Active and ready for assignments |
| `WAITING_FOR_ASSIGNMENT` | Waiting for game assignment |
| `IN_GAME` | Managing an active game |
| `PAUSED` | Paused by league manager |

## 8.14 Game Phases in the State Machine

**Table 88: Game Phases**

| Phase | Description |
|---|---|
| `PENDING` | Waiting to start |
| `WARMUP` | In warmup phase |
| `WARMUP_COMPLETE` | Warmup completed |
| `QUESTIONS` | Waiting for questions |
| `QUESTIONS_COMPLETE` | Questions received |
| `ANSWERS_SENT` | Answers sent |
| `GUESSING` | Waiting for guess |
| `GUESSING_COMPLETE` | Guess received |
| `SCORING` | Calculating score |
| `COMPLETE` | Game completed |
| `FAILED` | Game failed |

## 8.15 Summary

This chapter described the complete game management process by the referee:

- **Receiving assignment** — receiving `MATCH_ASSIGNMENT` with player and book details
- **Warmup phase** — sending `Q21_WARMUP_CALL` directly (without `GAME_INVITATION`)
- **Round start** — `Q21_ROUND_START` includes questions request
- **Questions and answers** — receiving `Q21_QUESTIONS_BATCH`, sending `Q21_ANSWERS_BATCH`
- **Guess** — receiving `Q21_GUESS_SUBMISSION` (automatic)
- **Scoring and feedback** — sending `Q21_SCORE_FEEDBACK` to each player
- **Reporting** — sending `MATCH_RESULT_REPORT` to the league manager
- **Error handling** — `GAME_ERROR` and deadlines

**Key Points:**

1. The referee sends `Q21_WARMUP_CALL` directly — no `GAME_INVITATION`
2. `Q21_ROUND_START` replaces `Q21_QUESTIONS_CALL`
3. `Q21_ANSWERS_BATCH` includes `guess_deadline` — no `Q21_GUESS_CALL`
4. The referee **never** reveals the correct answers to players
5. Dual scoring system: `league_score` (public) and `private_score` (private)

For additional details:
- Protocol messages — see Chapter 4 (Inter-Agent Communication Protocol)
- Game mechanisms — see Chapter 5 (assignment table, technical failures, deadlines)
- Multi-agent architecture — see Chapter 3 (state machines, system layers)

---

*© Dr. Segal Yoram - All rights reserved*

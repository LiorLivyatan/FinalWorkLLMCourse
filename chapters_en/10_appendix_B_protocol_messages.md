# Appendix B: Protocol Message Repository

## B.1 Introduction

This appendix centralizes all types of messages in the league.v2 protocol, including response deadline categories defined in the system. The tables are based on three official documentation sources: protocol-reference.md (League Manager), PROTOCOL_MESSAGES.md (Referee), and MESSAGE-TYPES.md (Player).

## B.2 Response Deadline Categories

The system defines six response deadline categories, tailored for email-based communication. Table 91 summarizes the categories and their meanings.

Table 91: Response Deadline Categories

| Deadline | Category | Description |
|---|---|---|
| 30 seconds | broadcast_keep_alive | Availability checks (BROADCAST_KEEP_ALIVE) |
| 1 minute | connectivity_test | Connectivity checks (CONNECTIVITY_TEST_CALL) |
| 2 minutes | broadcast_critical | Critical notifications (reset, pause, continue) |
| 5 minutes | q21_warmup / game_flow | Q21 game actions, invitation and joining |
| 20 minutes | registration / assignment | League registration, assignment table |
| 30 minutes | broadcast_round | Start of round (BROADCAST_NEW_LEAGUE_ROUND) |
| 1 hour | default / free_text | Default, free messages |

## B.3 Full Protocol Message Table

The tables in this appendix present all types of messages in the protocol, including sender, receiver, expected response, and response deadline.

### B.3.1 Registration and Connectivity Messages

Table 92: Registration and Connectivity Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| LEAGUE_REGISTER_REQUEST | Player | League Manager | 20m |
| RESPONSE_LEAGUE_REGISTER | League Manager | Player | N/A |
| REFEREE_REGISTER_REQUEST | Referee | League Manager | 20m |
| RESPONSE_REFEREE_REGISTER | League Manager | Referee | N/A |
| SEASON_REGISTRATION_REQUEST | Player/Referee | League Manager | 20m |
| RESPONSE_SEASON_REGISTRATION | League Manager | Player/Referee | N/A |
| CONNECTIVITY_TEST_CALL | Player/Referee | League Manager | 5m |
| RESPONSE_CONNECTIVITY_TEST | League Manager | Player/Referee | N/A |
| CONNECTIVITY_TEST_ECHO | League Manager | Player/Referee | N/A |
| REQUEST_USER_TABLE | Player/Referee | League Manager | 1h |
| RESPONSE_USER_TABLE | League Manager | Player/Referee | N/A |

### B.3.2 JSON Examples for Registration Messages

**LEAGUE_REGISTER_REQUEST**

```json
{
  "message_type": "LEAGUE_REGISTER_REQUEST",
  "payload": {
    "user_id": "U001",
    "display_name": "bibi0707",
    "player_email": "bibi0707.player@gmail.com",
    "player_meta": {
      "display_name": "bibi0707",
      "contact_endpoint": "bibi0707.player@gmail.com",
      "game_types": ["Q21"]
    }
  },
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-02-01T10:00:00Z"
}
```

**RESPONSE_LEAGUE_REGISTER**

```json
{
  "message_type": "RESPONSE_LEAGUE_REGISTER",
  "payload": {
    "status": "accepted",
    "player_id": "P001",
    "message": "Welcome bibi0707!",
    "participant_state": {
      "player_id": "P001",
      "league_id": "LEAGUE001",
      "email": "bibi0707.player@gmail.com",
      "display_name": "bibi0707",
      "current_state": "REGISTERED",
      "matches_played": 0,
      "total_score": 0.0
    }
  },
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### B.3.3 Game Flow Messages

Table 93: Game Flow Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| ROUND_ANNOUNCEMENT | League Manager | All Players | N/A |
| MATCH_ASSIGNMENT | League Manager | Referee | N/A |
| GAME_INVITATION | League Manager | Player | 2m |
| GAME_JOIN_ACK | Player | League Manager | N/A |
| GAME_OVER | League Manager | Player | N/A |
| ROUND_COMPLETED | League Manager | All Players | N/A |
| LEAGUE_COMPLETED | League Manager | All Players | N/A |
| LEAGUE_ERROR | League Manager | Player/Referee | N/A |
| GAME_ERROR | League Manager | Player | N/A |

### B.3.4 Q21 Game Messages

Table 94 presents all Q21 game messages in the GTAI protocol, including exact response deadlines.

Table 94: Q21 Game Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| Q21_ROUND_START | League Manager | Player | N/A |
| Q21_WARMUP_CALL | League Manager | Player | 2m |
| RESPONSE_Q21_WARMUP | Player | League Manager | N/A |
| Q21_QUESTIONS_CALL | League Manager | Player | 5m |
| Q21_QUESTIONS_BATCH | League Manager | Player | N/A |
| Q21_ANSWERS_BATCH | Player | League Manager | N/A |
| Q21_GUESS_CALL | League Manager | Player | 5m |
| Q21_GUESS_SUBMISSION | Player | League Manager | N/A |
| Q21_GUESS_RESULT | League Manager | Player | N/A |

> **Changes from Previous Protocol**
>
> Messages Q21_HINTS and Q21_SCORE_FEEDBACK were replaced with Q21_ROUND_START and Q21_GUESS_RESULT respectively. Message Q21_WARMUP_RESPONSE was renamed to RESPONSE_Q21_WARMUP.

### B.3.5 Q21 Message Descriptions

**Q21_ROUND_START** -- This message is sent by the League Manager to each player at the beginning of a round for Q21. The message contains:

- Book name (book_name)
- General description (general_description)
- Association domain (associative_domain)
- Round number (round_number)

**Q21_GUESS_RESULT** -- This message is sent by the League Manager to each player individually at the end of the game. The message contains:

- Total score (total_score)
- Score breakdown (breakdown): opening sentence, associative word, efficiency bonus
- Original opening sentence (actual_opening_sentence)
- Original associative word (actual_associative_word)

### B.3.6 JSON Examples for Q21 Messages

**Q21_ROUND_START -- Round Start**

```json
{
  "message_type": "Q21_ROUND_START",
  "payload": {
    "match_id": "M001-R1",
    "book_name": "The Secret Garden",
    "general_description": "A classic children's novel about nature",
    "associative_domain": "animal",
    "round_number": 1,
    "round_id": "ROUND_1"
  },
  "message_id": "round-550e8400-e29b-41d4-a716",
  "timestamp": "2026-02-17T19:05:00Z"
}
```

**Q21_GUESS_RESULT -- Results from LGM to Player**

```json
{
  "message_type": "Q21_GUESS_RESULT",
  "payload": {
    "match_id": "M001-R1",
    "total_score": 85.5,
    "breakdown": {
      "opening_sentence_score": 45.0,
      "sentence_justification_score": 18.0,
      "associative_word_score": 15.0,
      "word_justification_score": 7.5,
      "efficiency_bonus": 0.0
    },
    "actual_opening_sentence": "The garden was hidden behind...",
    "actual_associative_word": "fox"
  },
  "message_id": "result-550e8400-e29b-41d4-a716",
  "timestamp": "2026-02-17T19:18:00Z"
}
```

> **Difference Between Perspectives**
>
> **LGM Perspective:** The Q21_GUESS_RESULT message includes the actual answers (actual_associative_word, actual_opening_sentence) for the purpose of full transparency to the player after the game ends.
>
> **Referee Perspective:** The Q21_SCORE_FEEDBACK message does not include the answers in practice, to prevent the referee (student agent) from accessing the answers. The answers are revealed only through the League Manager (LGM) after the game ends.

**Q21_SCORE_FEEDBACK -- Feedback from Referee (Referee Perspective)**

```json
{
  "message_type": "Q21_SCORE_FEEDBACK",
  "payload": {
    "match_id": "M001-R1",
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
      "associative_word": "Correct guess!"
    },
    "match_league_scores": [
      {"email": "player1@gmail.com", "user_id": "alpha001", "league_score": 3},
      {"email": "player2@gmail.com", "user_id": "beta002", "league_score": 1}
    ]
  },
  "message_id": "result-550e8400-e29b-41d4-a716",
  "timestamp": "2026-02-17T19:18:00Z"
}
```

> **Note Regarding Answer Hiding**
>
> **Referee Perspective:** The Q21_SCORE_FEEDBACK message does not include the answers in practice, to prevent the referee (student agent) from accessing the answers. The answers are revealed only through the League Manager (LGM) after the game ends.

**MATCH_RESULT_REPORT -- Report to League Manager**

```json
{
  "message_type": "MATCH_RESULT_REPORT",
  "payload": {
    "match_id": "M001-R1",
    "winner_id": "alpha001",
    "is_draw": false,
    "scores": [
      {"email": "player1@gmail.com", "user_id": "alpha001",
       "league_score": 3, "private_score": 85.5},
      {"email": "player2@gmail.com", "user_id": "beta002",
       "league_score": 1, "private_score": 60.0},
      {"email": "referee@gmail.com", "user_id": "ghost002",
       "league_score": 3, "private_score": 0}
    ]
  },
  "message_id": "result-550e8400-e29b-41d4-a716",
  "timestamp": "2026-02-17T19:18:30Z"
}
```

### B.3.7 Broadcast Messages (12 Types)

The system defines 12 broadcast types. Some require a response (with a deadline) and some are informational messages only.

Table 95: Broadcast Messages Requiring Response

| Message Type | Scope | Deadline | Required Response |
|---|---|---|---|
| BROADCAST_KEEP_ALIVE | League | 30s | RESPONSE_KEEP_ALIVE |
| BROADCAST_CRITICAL_RESET | League | 2m | RESPONSE_CRITICAL_RESET |
| BROADCAST_CRITICAL_PAUSE | League | 2m | RESPONSE_CRITICAL_PAUSE |
| BROADCAST_CRITICAL_CONTINUE | League | 2m | RESPONSE_CRITICAL_CONTINUE |
| BROADCAST_FREE_TEXT | League | 1h | RESPONSE_FREE_TEXT (optional) |

Table 96: Broadcast Messages Not Requiring Response

| Message Type | Scope | Description |
|---|---|---|
| BROADCAST_START_SEASON | Season | Season opening |
| BROADCAST_END_SEASON | Season | Season end |
| BROADCAST_NEW_LEAGUE_ROUND | Round | Round start |
| BROADCAST_END_LEAGUE_ROUND | Round | Round end |
| BROADCAST_ASSIGNMENT_TABLE | Season | Assignment table (180 rows) |
| BROADCAST_ROUND_RESULTS | Round | Round results |
| BROADCAST_END_GROUP_ASSIGNMENT | Round | Group assignment end |
| BROADCAST_START_SEASON_REGISTRATION | Season | Registration window opening |

> **Broadcast Sending Mechanism**
>
> Broadcast messages are sent as a single message to all participants with the TO field. The scope field in the message indicates the context: LEAGUE, SEASON, or ROUND.

> **Response Requirement**
>
> Broadcasts of type KEEP_ALIVE, CRITICAL_RESET, CRITICAL_PAUSE, and CRITICAL_CONTINUE **require a response** within a defined deadline. Non-response will lead to a REJECTION_NOTIFICATION.

### B.3.8 Lifecycle Messages

Table 97: Lifecycle Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| BROADCAST_NEW_LEAGUE_ROUND | League Manager | All | 24h |
| BROADCAST_END_LEAGUE_ROUND | League Manager | All | N/A |
| BROADCAST_ROUND_RESULTS | League Manager | All | N/A |
| BROADCAST_START_SEASON | League Manager | All | 1m |
| BROADCAST_END_SEASON | League Manager | All | N/A |
| BROADCAST_START_SEASON_REGISTRATION | League Manager | All | N/A |

### B.3.9 Assignment Table Messages

Table 98: Assignment Table Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| BROADCAST_ASSIGNMENT_TABLE | League Manager | All | N/A |
| REQUEST_ASSIGNMENT_TABLE | Participant | League Manager | 1h |
| RESPONSE_ASSIGNMENT_TABLE | League Manager | Participant | N/A |

> **Assignment Table Mechanism**
>
> The Assignment Table is created automatically at the close of registration and contains 180 rows (60 players x 3 participants). The BROADCAST_ASSIGNMENT_TABLE message is sent automatically to all participants. A participant who did not receive the table can request it using REQUEST_ASSIGNMENT_TABLE.

### B.3.10 Query and Error Messages

Table 99: Query and Error Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| QUERY_STANDINGS_REQUEST | Player | League Manager | 1h |
| RESPONSE_QUERY_STANDINGS | League Manager | Player | N/A |
| LEAGUE_QUERY | Referee | League Manager | 1h |
| RESPONSE_LEAGUE_QUERY | League Manager | Referee | N/A |
| LEAGUE_STANDINGS_UPDATE | League Manager | All Players | N/A |
| MATCH_RESULT_REPORT | Referee | League Manager | 5m |
| LEAGUE_ERROR | League Manager | Player/Referee | N/A |
| GAME_ERROR | League Manager | Player | N/A |

### B.3.11 Extension Request Messages

Table 100: Extension Request Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| EXTENSION_REQUEST | Participant | League Manager | N/A |
| RESPONSE_EXTENSION | League Manager | Participant | N/A |
| REJECTION_NOTIFICATION | League Manager | Participant | N/A |
| ALREADY_REJECTED_NOTIFICATION | League Manager | Participant | N/A |

> **Extension Request Flow**
>
> In the GTAI protocol, extension requests are sent directly to the League Manager, and not to the referee. The League Manager handles requests automatically and decides on approval or rejection.

### B.3.12 Admin Intervention Messages

Table 101: Admin Intervention Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| ADMIN_BROADCAST_REQUEST | Admin | League Manager | N/A |
| ADMIN_BROADCAST_CONFIRMATION | League Manager | Admin | N/A |

**ADMIN_BROADCAST_REQUEST**

```json
{
  "message_type": "ADMIN_BROADCAST_REQUEST",
  "payload": {
    "broadcast_type": "BROADCAST_KEEP_ALIVE",
    "season_id": "SEASON_2026",
    "round_id": "ROUND_5"
  }
}
```

**ADMIN_BROADCAST_CONFIRMATION**

```json
{
  "message_type": "ADMIN_BROADCAST_CONFIRMATION",
  "payload": {
    "status": "SUCCESS",
    "original_request_id": "admin-req-20260119-001",
    "broadcast_type": "BROADCAST_KEEP_ALIVE",
    "broadcast_id": "bc-ka-20260119-001",
    "recipients_count": 42,
    "scope": "LEAGUE",
    "message": "Broadcast sent successfully to 42 recipients"
  }
}
```

> **Handling Technical Failures**
>
> In the GTAI protocol, technical failures are handled using a Force Majeure mechanism only. See Table 102 for force majeure messages.

### B.3.13 Force Majeure Messages

Table 102: Force Majeure Messages

| Message Type | From | To | Deadline |
|---|---|---|---|
| FORCE_MAJEURE_REQUEST | Referee | League Manager | N/A |
| FORCE_MAJEURE_DECISION | Admin | League Manager | N/A |
| FORCE_MAJEURE_RESULT | League Manager | All Participants | N/A |

> **Force Majeure Process**
>
> A force majeure request allows a referee to request cancellation or postponement of a game due to exceptional circumstances. The process: (1) Referee sends FORCE_MAJEURE_REQUEST to the League Manager, (2) the system manager reviews and sends FORCE_MAJEURE_DECISION, (3) the League Manager sends FORCE_MAJEURE_RESULT to all participants (approval = rescheduling, rejection = all receive 0-2-0).

## B.4 Summary

This appendix serves as a comprehensive reference for all protocol messages. The full CSV file (protocol_messages.csv) is available in the appendix folder for technical use.

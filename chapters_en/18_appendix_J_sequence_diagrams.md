# Appendix J: Message Sequence Diagrams

## J.1 Introduction

This appendix presents Sequence Diagrams for the main scenarios in the system. The diagrams illustrate the order of messages between agents and the league manager.

## J.2 League Registration Sequence

```
Player                        League Manager
  |                                |
  |-- LEAGUE_REGISTER_REQUEST ---->|
  |<-- RESPONSE_LEAGUE_REGISTER ---|
  |    (includes participant_state)|
  |                                |
  |<-- BROADCAST_START_SEASON -----|
  |                                |
  |-- SEASON_REGISTRATION_REQUEST->|
  |<-- RESPONSE_SEASON_REGISTRATION|
  |                                |
  |<-- BROADCAST_ASSIGNMENT_TABLE--|
  |    (includes 180 rows)         |
```

*Figure 21: Player registration sequence for the league and season*

## J.3 Season Start Sequence

```
Player          LGM           Referee
  |              |               |
  |<-- BROADCAST_START_SEASON ---|
  |              |               |
  |<-- BROADCAST_ASSIGNMENT_TABLE|
  |              |               |
  |<-- BROADCAST_NEW_LEAGUE_ROUND|
  |              |               |
  Season begins                  |
  Games can start                |
```

*Figure 22: Season start sequence*

## J.4 Full Game Sequence

```
Player                    LGM
  |                        |
  |<-- Q21_ROUND_START -----|
  |                        |
  |<-- GAME_INVITATION -----|
  |-- GAME_JOIN_ACK (120s)->|
  |                        |
  |<-- Q21_WARMUP_CALL -----|
  |-- RESPONSE_Q21_WARMUP ->|
  |                        |
  |<-- Q21_QUESTIONS_CALL --|
  |-- Q21_QUESTIONS_BATCH ->|
  |   (20 Qs, 300s)        |
  |                        |
  |<-- Q21_ANSWERS_BATCH ---|
  |                        |
  |<-- Q21_GUESS_CALL ------|
  |-- Q21_GUESS_SUBMISSION->|
  |                        |
  |<-- Q21_GUESS_RESULT ----|
```

*Figure 23: Full Q21 game sequence (GTAI protocol)*

## J.5 Broadcast Response Sequence

```
Agent                    LGM
  |                       |
  |<-- BROADCAST_KEEP_ALIVE|
  |-- RESPONSE_KEEP_ALIVE->|
  |   (30s)               |
  |                       |
  If no response:         |
  |<-- REJECTION_NOTIFICATION
```

*Figure 24: Broadcast response sequence (with deadline)*

## J.6 Extension Request Sequence

```
Agent                              LGM
  |                                 |
  |<-- Original message (deadline) -|
  |                                 |
  |-- EXTENSION_REQUEST ----------->|
  |<-- RESPONSE_EXTENSION (APPROVED)|
  |                                 |
  |-- Original response ----------->|
  |   (with new deadline)          |
  Extension granted:
  new deadline applies
```

*Figure 25: Successful extension request sequence*

## J.7 Force Majeure Sequence

```
Referee         LGM           All
  |              |              |
  |-- FORCE_MAJEURE_REQUEST --->|
  |<-- FORCE_MAJEURE_DECISION --|
  |   Admin reviews (24h)      |
  |<-- FORCE_MAJEURE_RESULT ----| --> All
  |                            |
  Game cancelled or rescheduled
```

*Figure 26: Force majeure request sequence*

## J.8 Response Deadline Summary

**Table 210: Response Deadlines by Message**

| Original Message | Response Message | Deadline |
|---|---|---|
| GAME_INVITATION | GAME_JOIN_ACK | 2 minutes |
| Q21_WARMUP_CALL | RESPONSE_Q21_WARMUP | 2 minutes |
| Q21_QUESTIONS_CALL | Q21_QUESTIONS_BATCH | 5 minutes |
| Q21_GUESS_CALL | Q21_GUESS_SUBMISSION | 5 minutes |
| CONNECTIVITY_TEST_CALL | RESPONSE_CONNECTIVITY_TEST | 5 minutes |
| BROADCAST_KEEP_ALIVE | RESPONSE_KEEP_ALIVE | 30 seconds |
| BROADCAST_CRITICAL_* | RESPONSE_CRITICAL_* | 2 minutes |

> **Non-compliance with Deadline**
>
> Non-response within a deadline will trigger a REJECTION_NOTIFICATION message and the response will not be accepted. Request an extension before the deadline expires.

---

*© Dr. Segal Yoram - All rights reserved*

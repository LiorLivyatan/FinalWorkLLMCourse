# 4 Inter-Agent Communication Protocol

## 4.1 Introduction

This chapter focuses on the `league.v2` communication protocol that enables agents to communicate with each other in a reliable and structured manner. The protocol is based on the principles of open agent communication: well-framed messages, mandatory and optional fields, conversation identification, and unambiguous status.

### 4.1.1 Chapter Objectives

By the end of this chapter, you will understand:

- The Gmail API-based transport layer
- The Envelope structure with the Shared Header
- The different message types
- The CC obligation to the log server
- The deadline management system

## 4.2 Transport Layer — Gmail API

### 4.2.1 The Core Concept

Unlike traditional architectures that use HTTP servers, the league system uses the Gmail API as its transport layer.

**Advantages of this choice:**

- No server required — agents operate as independent processes
- Asynchronous communication — messages are stored until processed
- Simple debugging — every message is stored in the inbox
- "Slow gear" — easy to track and understand what is happening
- Built-in reliability — Gmail provides high reliability

> **Gmail API Limitations**
>
> It is important to be familiar with Gmail API limitations before implementation: a free account is limited to 500 messages per day, with rate limits of 250 quota units per second. For a detailed analysis of limitations and their adaptation to league traffic, see Appendix E.

### 4.2.2 Comparison to HTTP

**Table 44: HTTP vs. Gmail Comparison**

| Action | HTTP | Gmail |
|---|---|---|
| Sending a message | `POST /endpoint` | Sending an email |
| Receiving a message | `GET /endpoint` | Reading an email |
| Message body | `JSON in body` | `JSON attachment` |
| Target address | `URL` | Email address |

### 4.2.3 Gmail Message Structure

Every message is sent with the following structure:

- `From` — the sender agent's address
- `To` — the recipient agent's address
- `CC` — mandatory: the log server
- `Subject` — protocol and message identifier
- `Attachment` — a JSON file with the message content

## 4.3 Email Subject Format

### 4.3.1 Subject Structure

Every email in the protocol includes a Subject in a defined format:

```
league.v2::<ROLE>::<EMAIL>::<TXID>::<MESSAGETYPE>
Q21G.v1::<ROLE>::<EMAIL>::<GAMEID>::<MESSAGETYPE>
```

**Table 45: Email Subject Components**

| Component | Description | Example |
|---|---|---|
| `protocol` | Protocol version | `league.v2`, `Q21G.v1` |
| `ROLE` | Sender's role | `PLAYER`, `REFEREE`, `LEAGUEMANAGER` |
| `EMAIL` | Sender's address | `mygroup.player@gmail.com` |
| `TXID` | Transaction ID | `tx-20260113-abc123` (league.v2) |
| `GAMEID` | Game ID | `0101003` (Q21G.v1) |
| `MESSAGETYPE` | Message type | `LEAGUEREGISTERREQUEST` |

**Two Protocol Versions:**

- `league.v2` — general protocol for communication between the league manager, players, and referees (registration, broadcasts, assignments)
- `Q21G.v1` — game protocol for communication between the referee and players during the game (warmup, questions, answers, guess)

### 4.3.2 Email Subject Examples

```python
# Player registration request
league.v2::PLAYER::mygroup.player@gmail.com::tx-20260113-abc::LEAGUEREGISTERREQUEST

# Referee registration request
league.v2::REFEREE::mygroup.referee@gmail.com::tx-20260113-def::REFEREEREGISTERREQUEST

# Broadcast from League Manager
league.v2::LEAGUEMANAGER::bitalevi100@gmail.com::bc-550e8400::BROADCAST_KEEP_ALIVE

# Game invitation from referee
league.v2::REFEREE::mygroup.referee@gmail.com::tx-20260117-ghi::GAMEINVITATION
```

> **Implementation Tip**
>
> Parsing the email subject in code:
> ```python
> def parse_subject(subject: str) -> dict:
>     parts = subject.split("::")
>     return {
>         "protocol": parts[0],       # "league.v2"
>         "role": parts[1],           # "PLAYER" / "REFEREE" / "LEAGUEMANAGER"
>         "email": parts[2],          # sender email
>         "txid": parts[3],           # transaction ID
>         "message_type": parts[4]    # message type
>     }
> ```

## 4.4 Envelope — Shared Header Structure

### 4.4.1 Shared Header Fields

> **Message Format — JSON File**
>
> Remember: every message in the protocol is sent as a JSON file attached to the email. The email body itself may be empty or contain a human-readable summary, but the binding content is always in the attached JSON file. Agents must read and process the attached file and not rely on the email body.

Every message in the protocol contains a Shared Header (Envelope) with the following fields:

**Table 46: Message Envelope Fields**

| Field | Type | Required | Description |
|---|---|---|---|
| `version` | string | Yes | Protocol version ("league.v2", "Q21G.v1") |
| `message_id` | UUID | Yes | Unique message identifier |
| `message_type` | string | Yes | Message type (MessageType enum) |
| `timestamp` | ISO8601 | Yes | Sending time |
| `sender_id` | string | Yes | Sender ID (`P-Q21G-xxx` or `R-Q21G-xxx`) |
| `recipient_id` | string | No | Recipient ID |
| `correlation_id` | UUID | No | ID for linking responses |
| `payload` | object | Yes | Message content (JSON) |
| `league_id` | string | No | League ID (Q21G) |
| `season_id` | string | No | Season ID (S01, W01) |
| `round_id` | string | No | Round number (01–06) |
| `game_id` | string | No | Composite game ID (SSRRGGG) |

**Table 47: Additional Fields at Message Level (not in Envelope)**

| Field | Location | Description |
|---|---|---|
| `sender_email` | IncomingMessage | Sender's email address |
| `recipient_email` | OutgoingMessage | Recipient's email address |

> **Separation Between Envelope and Message**
>
> The email fields (`sender_email`, `recipient_email`) are not part of the message Envelope but are added at the Message level:
> - `IncomingMessage` — contains `sender_email` (read from email headers)
> - `OutgoingMessage` — contains `recipient_email` (destination address for sending)

### 4.4.2 Message Envelope Example (Flat Structure)

> **Protocol Specification**
>
> **Flat structure**: All header fields are at the top level of the JSON, without a `header` wrapper. Only the `payload` field remains as a nested object.

```json
{
  "version": "league.v2",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_type": "Q21_ROUND_START",
  "timestamp": "2026-01-16T10:30:00Z",
  "sender_id": "R-Q21G-001",
  "sender_email": "mygroup.referee@gmail.com",
  "recipient_id": "P-Q21G-002",
  "recipient_email": "mygroup.player@gmail.com",
  "correlation_id": "abc123-def456-...",
  "league_id": "Q21G",
  "season_id": "S01",
  "round_id": "01",
  "game_id": "0101003",
  "payload": {
    // Game-specific content
  }
}
```

### 4.4.3 Context Fields Explanation

Context fields identify the message's position in the hierarchy:

- `league_id` — league ID, constant for all messages
- `season_id` — current season ID (S01 for season A, S02 for season B)
- `round_id` — current round number (01–06)
- `game_id` — composite game ID in SSRRGGG format (see Appendix F)

## 4.5 Context Fields (MessageContext)

### 4.5.1 Full Context Fields

Every message in the protocol can include context fields. The available fields depend on the message type:

**Table 48: Context Fields by Message Type**

| Message Type | league_id | season_id | game_id |
|---|---|---|---|
| Registration (REGISTER) | Required | — | — |
| Season broadcast (SEASON) | Required | Required | — |
| Round broadcast (ROUND) | Required | Required | — |
| Game (GAME) | Required | Required | Required |

### 4.5.2 Field Format Validation

**Table 49: Context Field Format**

| Field | Format | Examples |
|---|---|---|
| `league_id` | Free string | `Q21G_2026` |
| `season_id` | `[SW]\d{2}` | `S01`, `W02` |
| `round_id` | `\d{2}` | `01`, `06` |
| `game_id` | `\d{7}` | `0101001` |

> **Implementation Tip**
>
> Extracting context from `game_id`:
>
> You can extract all context fields from the game ID:
> - `"S" + game_id[0:2] = season_id` (example: "S01")
> - `game_id[2:4] = round_id` (example: "01")
> - `game_id[4:7] = game_number` (example: "001")

## 4.6 Message Types

The protocol defines several message categories. For complete tables of all message types, see Appendix B:

- Registration and connectivity messages — Table 92
- Game flow messages — Table 93
- Q21 game messages — Table 94
- Broadcast messages — Tables 95 and 96

> **Broadcast Sending Mechanism**
>
> Note that central broadcast messages cannot be confirmed as separate messages. Broadcast messages are sent as a single message with all participants in the CC field, not as separate messages to each participant. This assumption significantly reduces the sending load on the league manager.

## 4.7 CC Obligation to the Log Server

### 4.7.1 The Requirement

> **Protocol Specification**
>
> Every message sent during a game (from the referee to players or from players to the referee) must include the log server in the CC field.

**Log server address:** `beit.halevi.700@gmail.com`

### 4.7.2 CC Purposes

1. **Audit** — complete documentation of all correspondence
2. **Dispute resolution** — evidence for claims
3. **Performance analysis** — tracking response times
4. **Protocol enforcement** — identifying violations

### 4.7.3 Message Flow Diagram with CC

```
Referee ──Q21_HINTS/Q21_QUESTIONS──> Player A
    │                                     (CC to Log Server)
    └──Q21_HINTS/Q21_QUESTIONS──> Player B
                                         (CC to Log Server)
                          ↑
                     Log Server
```

*Figure 11: Message flow with CC to the log server*

## 4.8 Spam Folder Scanning

### 4.8.1 The Requirement

> **Protocol Specification**
>
> Every referee agent, player agent, and league manager must scan the Spam folder at the initial stages of communication. This requirement applies to all parties in the system without exception.

### 4.8.2 When to Scan for Spam?

1. **At the registration stage** — immediately after sending the registration message, check if the response arrived in spam
2. **At the start of each game** — before the Warmup phase begins
3. **While waiting for a response** — if no response was received within the expected time
4. **After sending the first message** — in every first communication with a new party

### 4.8.3 Reasons for Spam Filtering

The Gmail system may filter messages as spam in the following cases:

- A new account sending messages for the first time
- Messages with attachments (JSON attachments)
- Addresses not in the contact list
- Automated message templates (sent by code)

For detailed prevention strategies and recommendations for dealing with spam and blocking risks, see Appendix E, section E.10.

> **Warning**
>
> A message that arrived in the spam folder and was not read in time will be considered an undelivered message. The agent may receive a technical loss if it does not respond in time due to not scanning the spam folder.

> **Implementation Tip**
>
> In the agent code, include logic to scan the spam folder in addition to the Inbox. In the Gmail API, you can access the spam folder using the `SPAM` label.

## 4.9 Inter-Group Communication

### 4.9.1 Inter-Group Communication Rules

In certain cases, groups can communicate with each other (e.g., for clarifications or technical collaboration). Communication rules:

1. **Use the agent account** — send messages only from the agent address, not a personal email
2. **CC obligation to the log server** — every inter-group message requires CC to the log server
3. **Message validity** — a message sent without CC to the log server is not valid
4. **Response from agent account** — only a response from the agent account is considered valid

> **Important Warning**
>
> Inter-group messages sent without CC to the log server will not be recognized as valid in case of dispute or audit need.

## 4.10 Extension and Error Messages

### 4.10.1 Extension Request (EXTENSION_REQUEST)

A participant can request a time extension from the league manager. For the complete extension messages table see Table 100 in Appendix B.

> **Extension Request Flow in GTAI Protocol**
>
> In the GTAI protocol, extension requests are sent directly to the league manager, not to the referee. The league manager handles requests automatically and returns `RESPONSE_EXTENSION` with a decision (APPROVED or DENIED).

### 4.10.2 Extension Request Example

```json
{
  "version": "league.v2",
  "message_id": "ext-req-001",
  "message_type": "EXTENSION_REQUEST",
  "timestamp": "2026-01-16T10:30:00+00:00",
  "sender_id": "P-Q21G-001",
  "recipient_id": "LEAGUE_MANAGER",
  "correlation_id": null,
  "payload": {
    "correlation_id": "bc-ka-xyz789",
    "reason": "Network issues prevented timely response"
  },
  "league_id": "Q21G",
  "season_id": "S01",
  "round_id": "01",
  "game_id": "0101003"
}
```

**`correlation_id` Structure:**
- The `correlation_id` of the original message (for which extension is requested) is inside the `payload`
- The `correlation_id` at the envelope level is `null` (this is a new message, not a response)
- Extension duration is determined by the admin in the response (options: 30s, 5m, 1h, 24h, 7d)

### 4.10.3 Force Majeure

In case of a serious technical failure, the referee can send a Force Majeure request (`FORCE_MAJEURE_REQUEST`) to the league manager. For details see Table 102 in Appendix B.

### 4.10.4 Extension Request Flow Diagram

```
Participant ──EXTENSION_REQUEST──> League Manager
Participant <──RESPONSE_EXTENSION (APPROVED)── League Manager
Participant <──RESPONSE_EXTENSION (DENIED)── League Manager
                             LM processes requests automatically
```

*Figure 12: Extension request flow — Participant → League Manager*

## 4.11 Deadline Management

### 4.11.1 Deadline Categories

The system defines six deadline response categories. For the complete table see Appendix B Table 91.

### 4.11.2 Deadline Enforcement Process

1. Every message requiring a response includes a `response_deadline` field
2. The system monitors open messages (status = 'OPEN')
3. When the deadline passes without a response, the status changes to `REJECTED`
4. A technical loss is imposed if there is no timely response

## 4.12 Handling Late Responses

### 4.12.1 REJECTION_NOTIFICATION Message

There are two variants of the `REJECTION_NOTIFICATION` message:

#### Variant A: Late Response

When a response arrives after the deadline, the participant receives a rejection notification:

```json
{
  "message_type": "REJECTION_NOTIFICATION",
  "payload": {
    "message_id": "rej-tx20260115abc",
    "correlation_id": "bc-ka-xyz789",
    "deadline": "2026-01-15T10:30:00+00:00",
    "received_at": "2026-01-15T10:35:00+00:00",
    "reason": "Response received after deadline",
    "can_request_extension": true
  }
}
```

#### Variant B: Expired Without Response

When the deadline expired and no response was received at all:

```json
{
  "message_type": "REJECTION_NOTIFICATION",
  "payload": {
    "message_id": "rej-exp-abc123",
    "correlation_id": "bc-ka-xyz789",
    "deadline": "2026-01-15T10:30:00+00:00",
    "reason": "Response deadline expired - no response received",
    "original_message_type": "BROADCAST_KEEP_ALIVE",
    "can_request_extension": true
  }
}
```

**Difference Between Variants:**

In the first variant (late response) there is a `received_at` field indicating when the response was received. In the second variant (expired) there is no such field since no response was received at all, but an `original_message_type` field is added indicating the type of the original unanswered message.

### 4.12.2 Options After Rejection

When a response is rejected, there are two options:

1. **Extension request (EXTENSION_REQUEST)** — if the reason is justified
2. **Accept the rejection** — the message will not be counted and the game will continue

> **Warning**
>
> Repeated late responses may lead to disqualification from the game. If three responses in the same game were rejected, the agent is marked as `MALFUNCTION` and the game ends with a score of 0-2-2.

### 4.12.3 ALREADY_REJECTED_NOTIFICATION Message

If a response is sent for a message that was already previously rejected:

```json
{
  "version": "league.v2",
  "message_id": "alr-abc123def456",
  "message_type": "ALREADY_REJECTED_NOTIFICATION",
  "timestamp": "2026-01-17T10:40:00+00:00",
  "sender_id": "LEAGUE_MANAGER",
  "recipient_id": "P-Q21G-001",
  "correlation_id": null,
  "payload": {
    "message_id": "alr-abc123def456",
    "correlation_id": "original-message-id",
    "reason": "Message was already rejected due to late response",
    "action_required": "Submit EXTENSION_REQUEST if you need to appeal"
  },
  "league_id": "Q21G",
  "season_id": "S01"
}
```

**Message Structure:**
- The `correlation_id` of the original message is inside the `payload`
- The `action_required` field indicates the available action (extension request)
- The message ID starts with `alr-` (abbreviation of already-rejected)

## 4.13 Message Examples

### 4.13.1 Round Start Message (Q21_ROUND_START)

```json
{
  "version": "league.v2",
  "message_type": "Q21_ROUND_START",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-16T10:30:00+00:00",
  "sender_id": "LM001",
  "recipient_id": "P-Q21G-002",
  "correlation_id": null,
  "league_id": "Q21G",
  "season_id": "S01",
  "round_id": "01",
  "game_id": "0101001",
  "payload": {
    "match_id": "0101001",
    "book_name": "The Secret Garden",
    "general_description": "A classic children's novel about nature",
    "associative_domain": "animal",
    "round_number": 1,
    "round_id": "01"
  }
}
```

### 4.13.2 Questions Message (Q21_QUESTIONS_BATCH)

```json
{
  "version": "league.v2",
  "message_type": "Q21_QUESTIONS_BATCH",
  "message_id": "q21-batch-550e8400...",
  "timestamp": "2026-01-16T10:32:00+00:00",
  "sender_id": "P-Q21G-002",
  "recipient_id": "R-Q21G-001",
  "correlation_id": "game-start-abc123",
  "league_id": "Q21G",
  "season_id": "S01",
  "round_id": "01",
  "game_id": "0101003",
  "payload": {
    "questions": [
      {
        "number": 1,
        "text": "Does the protocol address time management?",
        "choices": {"A": "Yes", "B": "No", "C": "Unknown", "D": "Not relevant"}
      }
      // ... 19 more questions (total 20 required)
    ]
  }
}
```

**Question Structure:**
- Exactly 20 questions required per message
- Question identifier: `number` (or `question_number`) — number 1–20
- `choices`: answer options as a dictionary with keys A, B, C, D
- Valid answers: A, B, C, D, or `NOT_RELEVANT`

### 4.13.3 Final Guess Message (Q21_GUESS_SUBMISSION)

The final guess message is sent from the player to the referee (not the league manager) and includes the guess with justifications:

```json
{
  "protocol": "league.v2",
  "messagetype": "Q21_GUESS_SUBMISSION",
  "sender": {"email": "player@gmail.com", "role": "PLAYER", "logical_id": null},
  "timestamp": "2026-01-16T10:40:00+00:00",
  "conversationid": "conv-123",
  "leagueid": "LEAGUE001",
  "payload": {
    "game_id": "M001-R1",
    "match_id": "M001-R1",
    "auth_token": "token123",
    "guess": {
      "opening_sentence": "When Mary Lennox was sent to the manor...",
      "sentence_justification": "Based on answers indicating past tense narration and English setting, this appears to be the opening of The Secret Garden.",
      "associative_word": "robin",
      "word_variations": ["robins"],
      "word_justification": "The answers confirmed the word is a small bird, common in English gardens, and plays a key role in the story."
    },
    "confidence": 0.85
  }
}
```

**Mandatory Fields in Guess Message:**

- `opening_sentence` — the guessed opening sentence
- `sentence_justification` — justification for the sentence guess (30–50 words)
- `associative_word` — the guessed associative word
- `word_justification` — justification for the word guess (20–30 words)
- `confidence` — confidence level in the guess (value between 0 and 1)

## 4.14 Summary

This chapter presented the communication protocol:

- **Gmail API-based transport layer** — simple and reliable
- **Message envelope with Shared Header**
- **Message types** for registration, league flow, and game
- **CC obligation to the log server** in every game message and inter-group communication
- **Spam folder scanning obligation** at the initial stages of communication — applies to all agents and the league manager
- **Inter-group communication rules** — using agent account with mandatory CC
- **Extension messages**: `EXTENSION_REQUEST` → `RESPONSE_EXTENSION` (to league manager)
- **Force Majeure**: `FORCE_MAJEURE_REQUEST` for handling technical failures
- **Five deadline categories** with enforcement

In the next chapter we will deal with the practical implementation of the agents.

---

*© Dr. Segal Yoram - All rights reserved*

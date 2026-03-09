# 6 Final Project Implementation

## 6.1 Introduction: From Theory to Practice

Throughout this book we have journeyed through the world of AI agents and the Q21G League. The time has now come to consolidate all the knowledge into a practical implementation. This chapter provides detailed guidelines for implementing a player agent and a referee agent.

### 6.1.1 Chapter Objectives

By the end of this chapter, you will understand:

- The required development environment setup
- The player agent structure and responsibilities
- The referee agent structure and responsibilities
- The required configuration files
- Recommended testing strategies

## 6.2 Development Environment

### 6.2.1 System Requirements

**Table 59: Environment Requirements**

| Component | Requirement |
|---|---|
| Programming language | Python recommended, but any other language is allowed |
| Gmail API | 2 Gmail accounts with OAuth 2.0 permissions (see Appendix A and E) |
| Anthropic CLI | Terminal or Gemini recommended, but any other LLM CLI is possible |
| Git | For version control |
| PostgreSQL | Set up 2 databases, one for each AI agent |

### 6.2.2 Library Installation

```python
# requirements.txt
google-api-python-client>=2.100.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
anthropic>=0.20.0  # or openai>=1.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
psycopg2-binary>=2.9.0  # optional, for PostgreSQL
```

### 6.2.3 Recommended Project Structure

```
q21g-agents/
├── src/
│   ├── player/
│   │   ├── __init__.py
│   │   ├── player_agent.py      # Main player logic
│   │   ├── question_generator.py # Question generation
│   │   └── guess_strategy.py    # Guessing strategy
│   ├── referee/
│   │   ├── __init__.py
│   │   ├── referee_agent.py     # Main referee logic
│   │   ├── paragraph_selector.py # Paragraph selection
│   │   └── scorer.py            # Scoring logic
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── gmail_client.py      # Gmail API wrapper
│   │   ├── protocol.py          # Message types
│   │   └── config.py            # Configuration
│   └── main.py                  # Entry point
├── config/
│   ├── credentials.json         # Gmail OAuth credentials
│   ├── player.env               # Player configuration
│   └── referee.env              # Referee configuration
├── data/
│   └── course_materials/        # Course materials PDFs
├── tests/
│   ├── test_player.py
│   ├── test_referee.py
│   └── test_protocol.py
└── requirements.txt
    README.md
```

## 6.3 Player Agent Implementation

### 6.3.1 Player Lifecycle

1. **Initialization** — loading configuration and connecting to Gmail API
2. **Registration** — sending `LEAGUE_REGISTER_REQUEST`
3. **Waiting** — tracking incoming messages
4. **Game** — responding to invitations and managing game phases
5. **Completion** — closing connections and saving logs

### 6.3.2 Full Player Message Sequence

**Table 60: Player Messages — Registration and Season**

| Direction | Message Type | Description |
|---|---|---|
| Send | `LEAGUE_REGISTER_REQUEST` | Register with league |
| Receive | `RESPONSE_LEAGUE_REGISTER` | Registration confirmation + user table |
| Receive | `BROADCAST_START_SEASON` | Season start |
| Send | `SEASON_REGISTRATION_REQUEST` | Register for season |
| Receive | `RESPONSE_SEASON_REGISTRATION` | Season registration confirmation |
| Receive | `BROADCAST_ASSIGNMENT_TABLE` | Assignment table |

**Table 61: Player Messages — Game**

| Direction | Message Type | Description |
|---|---|---|
| Receive | `GAME_INVITATION` | Game invitation |
| Send | `GAME_JOIN_ACK` | Join confirmation (manual, not automatic) |
| Receive | `Q21_WARMUP_CALL` | Warmup question |
| Send | `Q21_WARMUP_RESPONSE` | Warmup answer |
| Receive | `Q21_ROUND_START` | Round start + book info |
| Receive | `Q21_QUESTIONS_CALL` | Questions request |
| Send | `Q21_QUESTIONS_BATCH` | 20 questions (within 300s) |
| Receive | `Q21_ANSWERS_BATCH` | Answers to questions |
| Send | `Q21_GUESS_SUBMISSION` | Final guess |
| Receive | `Q21_HINTS` | Additional hints |
| Receive | `Q21_GUESS_RESULT` | Guess results |
| Receive | `Q21_SCORE_FEEDBACK` | Score feedback |
| Receive | `GAME_OVER` | Game over |

### 6.3.3 Question Generation Module

```python
from anthropic import Anthropic

class QuestionGenerator:
    """Generates 20 multiple-choice questions based on hint."""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic()
        self.model = model

    async def generate_questions(
        self,
        description: str,
        association_topic: str
    ) -> list[dict]:
        """Generate 20 questions based on hint."""
        prompt = f"""
        Based on this description: "{description}"
        And association topic: "{association_topic}"

        Generate 20 strategic multiple-choice questions
        to identify the source paragraph.

        Each question should have 4 options.
        """

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_questions(response.content[0].text)
```

### 6.3.4 Guessing Strategy

> **Implementation Tips**
>
> Tips for guessing strategy:
> - Analyze the answers to identify patterns
> - Search course materials for matching paragraphs
> - Weight the confidence in each guess
> - Remember: the associative word is worth 30% of the score!

## 6.4 Referee Agent Implementation

### 6.4.1 Referee Lifecycle

1. **Initialization** — loading course materials
2. **Registration** — sending `REFEREE_REGISTER_REQUEST`
3. **Assignment** — receiving assignment table
4. **Game management** — invitation, hints, answers, scores
5. **Reporting** — sending `GAME_RESULT`

### 6.4.2 Full Referee Message Sequence

**Table 62: Referee Messages — Registration**

| Direction | Message Type | Description |
|---|---|---|
| Send | `REFEREE_REGISTER_REQUEST` | Register as referee |
| Receive | `RESPONSE_REFEREE_REGISTER` | Registration confirmation |
| Receive | `BROADCAST_ASSIGNMENT_TABLE` | Assigned games |

**Table 63: Referee Messages — Game Management**

| Direction | Message Type | Description |
|---|---|---|
| Send | `Q21_WARMUP_CALL` | Send warmup question |
| Receive | `Q21_WARMUP_RESPONSE` | Warmup answer from player |
| Send | `Q21_ROUND_START` | Round start (includes book info) |
| Receive | `Q21_QUESTIONS_BATCH` | 20 questions from player |
| Send | `Q21_ANSWERS_BATCH` | Answers + deadline for guess |
| Receive | `Q21_GUESS_SUBMISSION` | Final guess from player |
| Send | `Q21_SCORE_FEEDBACK` | Results for player |
| Send | `MATCH_RESULT_REPORT` | Report to league manager |

> **Differences from Original Specification**
>
> The actual code differs from the specification:
> - `GAME_INVITATION` / `GAME_JOIN_ACK` — defined but not in use (warmup starts directly)
> - `Q21_QUESTIONS_CALL` — merged into `Q21_ROUND_START`
> - `GAME_OVER` — replaced by `Q21_SCORE_FEEDBACK`
> - `GAME_RESULT` — changed to `MATCH_RESULT_REPORT`

### 6.4.3 Paragraph Selection and Hint Creation

```python
import random

class ParagraphSelector:
    """Selects paragraph and creates hints."""

    def __init__(self, materials_path: str):
        self.materials = self._load_materials(materials_path)

    def select_paragraph(self) -> dict:
        """Select a random paragraph from course materials."""
        lecture = random.choice(self.materials)
        paragraph = random.choice(lecture["paragraphs"])
        return {
            "lecture_id": lecture["id"],
            "paragraph_id": paragraph["id"],
            "text": paragraph["text"],
            "opening_sentence": paragraph["text"].split(".")[0] + "."
        }

    def create_hints(self, paragraph: dict) -> dict:
        """Create description and association for paragraph."""
        # Use LLM to generate hints
        # IMPORTANT: description must NOT contain words from paragraph!
        return {
            "secret_title": "...",    # Max 5 words
            "description": "...",     # Max 15 words, no overlap
            "association_word": "...",
            "association_topic": "..."
        }
```

### 6.4.4 Score Calculation

```python
class Scorer:
    """Scores player guesses against original paragraph."""

    def score_guess(
        self,
        original: dict,
        guess: dict
    ) -> dict:
        """Calculate score (0-100) with breakdown."""

        # 50% - Opening sentence accuracy
        sentence_score = self._compare_sentences(
            original["opening_sentence"],
            guess["opening_sentence"]
        )

        # 20% - Sentence reasoning quality
        reasoning_score = self._evaluate_reasoning(
            guess["sentence_reasoning"]
        )

        # 20% - Association word accuracy
        association_score = self._compare_association(
            original["association_word"],
            guess["association_word"],
            guess["association_variations"]
        )

        # 10% - Association reasoning quality
        assoc_reasoning_score = self._evaluate_reasoning(
            guess["association_reasoning"]
        )

        total = (
            sentence_score * 0.5 +
            reasoning_score * 0.2 +
            association_score * 0.2 +
            assoc_reasoning_score * 0.1
        )

        return {
            "total": round(total, 2),
            "breakdown": {
                "opening_sentence": sentence_score,
                "sentence_reasoning": reasoning_score,
                "association_word": association_score,
                "association_reasoning": assoc_reasoning_score
            }
        }
```

### 6.4.5 Converting Private Score to League Score

After calculating the private score (0–100), the referee converts it to a league score (0–3):

**Table 64: Converting Private Score to League Score**

| Private Score Range | League Score | Performance Level |
|---|---|---|
| 85–100 | 3 points | Excellent |
| 70–84 | 2 points | Good |
| 50–69 | 1 point | Average |
| 0–49 | 0 points | Weak |

**ScoreCalculator — Full Implementation**

```python
class ScoreCalculator:
    """Complete scoring implementation for Q21 referee."""

    WEIGHTS = {
        "opening_sentence": 0.50,
        "sentence_justification": 0.20,
        "associative_word": 0.20,
        "word_justification": 0.10
    }

    def calculate_scores(self, original: dict, guess: dict) -> dict:
        """Calculate complete scores with feedback."""

        # Calculate component scores (0-100 each)
        components = {
            "opening_sentence_score": self._score_sentence(
                original["opening_sentence"], guess["opening_sentence"]),
            "sentence_justification_score": self._score_justification(
                guess["sentence_reasoning"]),
            "associative_word_score": self._score_word(
                original["association_word"], guess["association_word"]),
            "word_justification_score": self._score_justification(
                guess["association_reasoning"])
        }

        # Calculate weighted private score (0-100)
        private_score = sum(
            components[f"{k}_score"] * v
            for k, v in self.WEIGHTS.items()
        )

        # Convert to league score (0-3)
        league_score = self._convert_to_league_score(private_score)

        # Generate 30-50 word feedback for each component
        feedback = self._generate_feedback(original, guess, components)

        return {
            **components,
            "private_score": round(private_score, 2),
            "league_score": league_score,
            "opening_sentence_feedback": feedback["sentence"],
            "word_feedback": feedback["word"]
        }

    def _convert_to_league_score(self, private_score: float) -> int:
        """Convert private score (0-100) to league score (0-3)."""
        if private_score >= 85:
            return 3
        elif private_score >= 70:
            return 2
        elif private_score >= 50:
            return 1
        return 0

    def _generate_feedback(self, original: dict, guess: dict,
                           components: dict) -> dict:
        """Generate 30-50 word feedback for each component."""
        # Use LLM to generate meaningful feedback
        return {
            "sentence": self._generate_component_feedback(
                "opening_sentence", original, guess, components),
            "word": self._generate_component_feedback(
                "associative_word", original, guess, components)
        }
```

> **Verbal Explanation Requirement**
>
> The referee must provide a verbal explanation of 30–50 words for each score component. The explanation should justify the score given and address the quality of the guess relative to the correct answer.

## 6.5 Configuration Files

### 6.5.1 Player Configuration

```bash
# player.env
# Player Configuration
PLAYER_EMAIL=MyGroup.player@gmail.com
PLAYER_NAME=MyGroup Player
LEAGUE_MANAGER_EMAIL=bitalevi100@gmail.com
LOG_SERVER_EMAIL=beit.halevi.700@gmail.com

# LLM Configuration
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
LLM_API_KEY=sk-ant-...

# Gmail API
GMAIL_CREDENTIALS_PATH=./config/credentials.json
GMAIL_TOKEN_PATH=./config/token.json

# Polling interval (seconds)
POLL_INTERVAL=30
```

### 6.5.2 Referee Configuration

```bash
# referee.env
# Referee Configuration
REFEREE_EMAIL=MyGroup.referee@gmail.com
REFEREE_NAME=MyGroup Referee
LEAGUE_MANAGER_EMAIL=bitalevi100@gmail.com
LOG_SERVER_EMAIL=beit.halevi.700@gmail.com

# Course Materials
MATERIALS_PATH=./data/course_materials/

# LLM Configuration
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
LLM_API_KEY=sk-ant-...

# Gmail API
GMAIL_CREDENTIALS_PATH=./config/credentials.json
GMAIL_TOKEN_PATH=./config/token.json

# Polling interval (seconds)
POLL_INTERVAL=30
```

### 6.5.3 Detailed Settings File for Referee (config.json)

The full configuration file includes all tunable parameters:

```json
{
  "version": "1.0.0",
  "protocol_version": "league.v2",
  "gmail": {
    "poll_interval_seconds": 30,
    "max_emails_per_minute": 10,
    "batch_size": 10
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "q21_referee",
    "pool_size": 5
  },
  "timeouts": {
    "warmup_seconds": 300,
    "warmup_retries": 1,
    "questions_seconds": 600,
    "guess_seconds": 600,
    "default_seconds": 900
  },
  "q21": {
    "max_questions": 20,
    "demo_ai_mode": false,
    "scoring_weights": {
      "opening_sentence": 0.50,
      "sentence_justification": 0.20,
      "associative_word": 0.20,
      "word_justification": 0.10
    },
    "league_score_thresholds": {
      "excellent": 85,
      "good": 70,
      "average": 50
    },
    "feedback_word_count": {
      "min": 30,
      "max": 50
    }
  },
  "logging": {
    "level": "INFO",
    "sensitive_patterns": ["password", "token", "secret"]
  }
}
```

**Table 65: Important Parameters in config.json**

| Parameter | Default Value | Description |
|---|---|---|
| `timeouts.warmup_seconds` | 300 | Warmup phase timeout |
| `timeouts.questions_seconds` | 600 | Questions phase timeout |
| `timeouts.guess_seconds` | 300 | Guess phase timeout |
| `q21.max_questions` | 20 | Maximum question count |
| `q21.demo_ai_mode` | false | Demo mode (pre-made answers) |
| `q21.feedback_word_count.min` | 30 | Minimum words in explanation |
| `q21.feedback_word_count.max` | 50 | Maximum words in explanation |

## 6.6 Testing

### 6.6.1 Testing Strategies

1. **Unit tests** — testing individual functions
2. **Integration tests** — testing communication with Gmail API
3. **End-to-end tests** — full game between agents
4. **Self-play tests** — play against your own referee

### 6.6.2 Mandatory Test List

**Table 66: Mandatory Test List**

| Test | Description |
|---|---|
| Registration | Agent registers successfully and receives an ID |
| Invitation response | Player responds to game invitation in time |
| Question generation | Player generates 20 valid questions |
| Final guess | Player sends guess with all components |
| Score calculation | Referee returns valid score with breakdown |
| CC to log server | Every message includes CC |
| Meeting deadlines | Responses within time windows |
| GateKeeper | Rate limits and quotas are enforced |
| Broadcast handling | Response to broadcasts requiring response |
| Extension request | Ability to request extension before deadline |
| Message tracking | Tracking table with statuses |

### 6.6.3 Referee-Specific Tests

The referee agent requires additional tests beyond the general tests:

**Table 67: Referee-Specific Tests**

| Test | Description |
|---|---|
| State machine | Valid transition between 12 game states |
| Timeout management | Alerts and actions on timeout |
| Score calculation | Correct calculation of 4 score components |
| League score conversion | Correct conversion from private (0–100) to league (0–3) |
| Verbal feedback | Explanation length 30–50 words per component |
| Manager reporting | Sending valid `MATCH_RESULT_REPORT` |
| Crash recovery | Continue game from saved state |
| Warmup with retry | Handle timeout with one additional attempt |

```python
# tests/referee/
# ├── unit/
# │   ├── test_score_calculator.py      # Scoring logic
# │   ├── test_state_machine.py         # State transitions
# │   └── test_timeout_manager.py       # Timeout handling
# ├── integration/
# │   ├── test_gmail_handler.py         # Email processing
# │   └── test_database_ops.py          # DB operations
# └── e2e/
#     └── test_full_game.py             # Complete game flow

import pytest

class TestScoreCalculator:
    """Unit tests for referee scoring."""

    def test_league_score_conversion_excellent(self):
        """Score 85+ should give 3 league points."""
        calc = ScoreCalculator()
        assert calc._convert_to_league_score(85) == 3
        assert calc._convert_to_league_score(100) == 3

    def test_league_score_conversion_boundaries(self):
        """Test boundary conditions."""
        calc = ScoreCalculator()
        assert calc._convert_to_league_score(84.99) == 2
        assert calc._convert_to_league_score(69.99) == 1
        assert calc._convert_to_league_score(49.99) == 0

    def test_feedback_word_count(self):
        """Feedback must be 30-50 words."""
        calc = ScoreCalculator()
        feedback = calc._generate_feedback(original, guess, components)
        word_count = len(feedback["sentence"].split())
        assert 30 <= word_count <= 50
```

## 6.7 Message Tracking Table Implementation

The agent must track every message sent and received. The table enables identifying missing responses and preventing duplicate sending.

### 6.7.1 Table Structure

**Table 68: `message_logs` Table Structure**

| Field | Type | Description |
|---|---|---|
| `id` | INTEGER (PK) | Auto ID |
| `gmail_id` | VARCHAR(100) | Unique message ID (Gmail ID) |
| `thread_id` | VARCHAR(100) | Thread ID |
| `direction` | VARCHAR(10) | "IN" (receive) or "OUT" (send) |
| `message_type` | VARCHAR(100) | Message type |
| `transaction_id` | VARCHAR(100) | Transaction ID |
| `sender_email` | VARCHAR(255) | Sender address |
| `recipient_email` | VARCHAR(255) | Recipient address |
| `subject` | TEXT | Message subject |
| `payload` | JSON | Message content |
| `game_id` | VARCHAR(100) | Game ID |
| `league_id` | VARCHAR(100) | League ID |
| `round_id` | VARCHAR(100) | Round ID |
| `processed` | BOOLEAN | Whether processed |
| `error_message` | TEXT | Error message (if any) |
| `created_at` | TIMESTAMP | Creation time |
| `processed_at` | TIMESTAMP | Processing time |

> **Message Correlation**
>
> Request-response linking is done in a separate `message_correlations` table with fields: `request_type`, `request_id`, `response_type`, `response_id`, `correlated_at`.

### 6.7.2 Message Tracking Class

```python
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class MessageStatus(Enum):
    OPEN = "OPEN"       # Waiting for response
    CLOSED = "CLOSED"   # Response received
    REJECTED = "REJECTED"  # Deadline passed

@dataclass
class TrackedMessage:
    message_id: str
    correlation_id: str
    message_type: str
    deadline: Optional[datetime]
    status: MessageStatus = MessageStatus.OPEN

class MessageTracker:
    def __init__(self):
        self.messages: dict[str, TrackedMessage] = {}

    def track_sent(self, msg: dict, deadline_seconds: int = None):
        """Track outgoing message with optional deadline."""
        deadline = None
        if deadline_seconds:
            deadline = datetime.now() + timedelta(seconds=deadline_seconds)

        tracked = TrackedMessage(
            message_id=msg["message_id"],
            correlation_id=msg.get("correlation_id"),
            message_type=msg["message_type"],
            deadline=deadline
        )
        self.messages[msg["correlation_id"]] = tracked

    def close_by_correlation(self, correlation_id: str):
        """Mark message as closed when response received."""
        if correlation_id in self.messages:
            self.messages[correlation_id].status = MessageStatus.CLOSED
```

## 6.8 Broadcast Handler Implementation

The server sends 11 different broadcast types. Some require a response and have a deadline.

### 6.8.1 Identifying Broadcasts

```python
# Broadcast types that require response
RESPONSE_REQUIRED = {
    "BROADCAST_CONNECTIVITY_TEST": 60,    # 60 seconds
    "BROADCAST_KEEP_ALIVE": 300,          # 5 minutes
    "BROADCAST_CRITICAL_SYSTEM": 120,     # 2 minutes
    "BROADCAST_CRITICAL_SECURITY": 120,   # 2 minutes
}

# Broadcast types - no response needed
NO_RESPONSE_NEEDED = {
    "BROADCAST_SEASON_START",
    "BROADCAST_ROUND_START",
    "BROADCAST_ROUND_END",
    "BROADCAST_SEASON_END",
    "BROADCAST_ASSIGNMENT_TABLE",
    "BROADCAST_STANDINGS_UPDATE",
    "BROADCAST_MAINTENANCE_NOTICE",
}

def get_response_deadline(message_type: str) -> int | None:
    """Get deadline in seconds, or None if no response needed."""
    return RESPONSE_REQUIRED.get(message_type)
```

### 6.8.2 Broadcast Handling

```python
class BroadcastHandler:
    def __init__(self, email_client, tracker: MessageTracker):
        self.email_client = email_client
        self.tracker = tracker

    async def handle_broadcast(self, msg: dict):
        """Process incoming broadcast message."""
        msg_type = msg["message_type"]
        deadline_seconds = get_response_deadline(msg_type)

        if deadline_seconds:
            # Response required - track and respond
            self.tracker.track_sent(msg, deadline_seconds)
            await self._send_broadcast_response(msg, deadline_seconds)
        else:
            # Informational only - log and process
            self._process_informational(msg)

    async def _send_broadcast_response(self, msg: dict, deadline: int):
        """Send acknowledgment response to broadcast."""
        response = {
            "message_type": f"RESPONSE_{msg['message_type']}",
            "correlation_id": msg["message_id"],
            "payload": {"status": "ACKNOWLEDGED"}
        }
        await self.email_client.send(response)
```

## 6.9 Extension Request Implementation

When the agent anticipates it will not meet the deadline, it can request an extension.

### 6.9.1 When to Request an Extension

> **Golden Rule**
>
> An extension request must be sent before the deadline expires! A late request will be rejected.

### 6.9.2 Extension Manager Implementation

```python
class ExtensionManager:
    def __init__(self, email_client, tracker: MessageTracker):
        self.email_client = email_client
        self.tracker = tracker
        self.pending_extensions: dict[str, bool] = {}

    async def request_if_needed(
        self,
        original_msg: dict,
        deadline: datetime,
        estimated_processing: float
    ) -> bool:
        """Request extension if we won't make deadline."""
        time_remaining = (deadline - datetime.now()).total_seconds()
        buffer = 30  # Safety margin

        if time_remaining < estimated_processing + buffer:
            return await self._send_extension_request(original_msg)
        return True  # No extension needed

    async def _send_extension_request(self, original_msg: dict) -> bool:
        """Send extension request and wait for response."""
        request = {
            "message_type": "EXTENSION_REQUEST",
            "payload": {
                "original_message_id": original_msg["message_id"],
                "original_message_type": original_msg["message_type"],
                "reason": "Processing requires additional time",
                "requested_extension_seconds": 120
            }
        }
        correlation_id = request.get("correlation_id")
        self.pending_extensions[correlation_id] = None
        await self.email_client.send(request)

        # Wait for RESPONSE_EXTENSION...
        return await self._wait_for_response(correlation_id)

    def handle_extension_response(self, response: dict):
        """Process extension response from server."""
        correlation_id = response.get("correlation_id")
        if correlation_id in self.pending_extensions:
            status = response["payload"]["status"]
            self.pending_extensions[correlation_id] = (status == "APPROVED")
```

## 6.10 Running the League

### 6.10.1 Startup Steps

1. Define the configuration files
2. Start the referee agent: `python main.py referee`
3. Start the player agent: `python main.py player`
4. The agents will register automatically and wait for messages
5. Perform self-play tests before the official league

### 6.10.2 Success Tips

> **Implementation Tips**
>
> Tips for league success:
> - **Logs** — document every incoming and outgoing message
> - **Deadlines** — add a safety buffer (don't wait until the last second)
> - **Error handling** — handle every exception, including error 429 (Rate Limit)
> - **Stable state** — save state in case of restart
> - **Practice** — play against yourself repeatedly
> - **API limits** — know the Gmail API limits (see Appendix E)

## 6.11 Summary

This chapter provided practical implementation guidelines:

- Development environment setup with Python 3.10+ and Gmail API
- Recommended project structure with player/referee separation
- Player agent implementation with question generation and guessing strategy
- Referee agent implementation with paragraph selection and score calculation
- Configuration files for both agents
- Testing strategies and mandatory test list

Good luck with the final project!

---

*© Dr. Segal Yoram - All rights reserved*

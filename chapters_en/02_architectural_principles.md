# 2 Architectural Principles for the Agent

## 2.1 Introduction

This chapter presents the architectural principles that students must implement in their player and referee agents. The principles are based on the same patterns used by the league manager (see Appendix H), but adapted to the unique needs of a single agent.

> **Key Difference**
>
> The league manager manages 30 groups and 60 games simultaneously. Your agent manages one player or one referee. This changes scale but not principles.

## 2.2 The Orchestrator Pattern (Gateway)

### 2.2.1 Core Concept

The Orchestrator is the central component that coordinates all agent activity. It serves as the single entry point for all interactions with the outside world.

**Table 17: Orchestrator Roles**

| Role | Description | Example |
|---|---|---|
| Initialization | Set up all subsystems | Create Gmail API connection |
| Coordination | Manage information flow | Forward message to Router |
| Monitoring | Track health | Watchdog check |
| Shutdown | Orderly shutdown | Release resources |

### 2.2.2 Recommended Structure

```python
# PlayerOrchestrator — Basic Structure
class PlayerOrchestrator:
    """Central coordinator for the player agent."""
    def __init__(self, config: Config):
        self.config = config
        self.state_machine = PlayerStateMachine()
        self.rate_limiter = TokenBucketRateLimiter(
            capacity=5, refill_rate=1.0
        )
        self.message_router = MessageRouter()
        self.gmail_client = None
        self._running = False

    def start(self) -> None:
        """Initialize and start the agent."""
        self._setup_gmail_client()
        self._register_handlers()
        self._running = True
        self._run_main_loop()

    def stop(self) -> None:
        """Graceful shutdown."""
        self._running = False
        self._cleanup_resources()
```

### 2.2.3 Separation Principle

The Orchestrator does not perform business logic itself — it only coordinates between components:
- Sending message → forward through RateLimiter
- State change → forward to StateMachine
- Receiving message → forward to MessageRouter

## 2.3 State Machine for the Agent

### 2.3.1 Player States

The agent transitions between well-defined states. Each state determines which actions are allowed.

**Table 18: Player Agent States — Registration & Assignments**

| State | Description | Transition Event |
|---|---|---|
| INIT_START_STATE | Initial state | REGISTER_REQUEST |
| REGISTERING | Registration in progress | REGISTER_SUCCESS |
| REGISTERED | Registered in league | SEASON_START_RECEIVED |
| AWAITING_ASSIGNMENT | Waiting for game invitation | GAME_INVITATION_RECEIVED |

**Table 19: Player Agent States — Game**

| State | Description | Transition Event |
|---|---|---|
| INVITED | Received game invitation | GAME_ACCEPTED |
| IN_MATCH | Game started | WARMUP_CALL_RECEIVED |
| WARMUP | Warmup phase | WARMUP_RESPONSE_SENT |
| QUESTIONING | Creating questions | QUESTIONS_SUBMITTED |
| AWAITING_ANSWERS | Waiting for answers | ANSWERS_RECEIVED |
| GUESSING | Creating guess | GUESS_SUBMITTED |
| MATCH_COMPLETE | Game ended | GAME_RESULT_RECEIVED |
| PAUSED | System paused | CONTINUE_RECEIVED |
| ERROR | Error | RESET or RECOVER |

### 2.3.2 Transition Diagram

The diagram shows the main flow with event names (in blue).

Additional states include: AWAITING_ANSWERS, PAUSED, and ERROR. After a game ends (MATCH_COMPLETE), the agent returns to REGISTERED, waiting for the next game.

### 2.3.3 State Machine Implementation

```python
# Player State Machine — Event-Based
from enum import Enum, auto
from typing import Dict, Tuple, Callable

class PlayerState(Enum):
    # Registration states
    INIT_START_STATE = auto()
    REGISTERING = auto()
    REGISTERED = auto()
    AWAITING_ASSIGNMENT = auto()
    # Match states
    INVITED = auto()
    IN_MATCH = auto()
    WARMUP = auto()
    QUESTIONING = auto()
    AWAITING_ANSWERS = auto()
    GUESSING = auto()
    MATCH_COMPLETE = auto()
    # System states
    PAUSED = auto()
    ERROR = auto()

class TransitionEvent(Enum):
    REGISTER_REQUEST = auto()
    REGISTER_SUCCESS = auto()
    SEASON_START_RECEIVED = auto()
    GAME_INVITATION_RECEIVED = auto()
    GAME_ACCEPTED = auto()
    WARMUP_CALL_RECEIVED = auto()
    WARMUP_RESPONSE_SENT = auto()
    QUESTIONS_SUBMITTED = auto()
    ANSWERS_RECEIVED = auto()
    GUESS_SUBMITTED = auto()
    GAME_RESULT_RECEIVED = auto()

class PlayerStateMachine:
    # Event-based transitions: (from_state, event) -> to_state
    TRANSITIONS: Dict[Tuple[PlayerState, TransitionEvent], PlayerState] = {
        (PlayerState.INIT_START_STATE, TransitionEvent.REGISTER_REQUEST):
            PlayerState.REGISTERING,
        (PlayerState.REGISTERING, TransitionEvent.REGISTER_SUCCESS):
            PlayerState.REGISTERED,
        (PlayerState.REGISTERED, TransitionEvent.SEASON_START_RECEIVED):
            PlayerState.AWAITING_ASSIGNMENT,
        (PlayerState.AWAITING_ASSIGNMENT, TransitionEvent.GAME_INVITATION_RECEIVED):
            PlayerState.INVITED,
        (PlayerState.INVITED, TransitionEvent.GAME_ACCEPTED):
            PlayerState.IN_MATCH,
        (PlayerState.IN_MATCH, TransitionEvent.WARMUP_CALL_RECEIVED):
            PlayerState.WARMUP,
        (PlayerState.WARMUP, TransitionEvent.WARMUP_RESPONSE_SENT):
            PlayerState.QUESTIONING,
        (PlayerState.QUESTIONING, TransitionEvent.QUESTIONS_SUBMITTED):
            PlayerState.AWAITING_ANSWERS,
        (PlayerState.AWAITING_ANSWERS, TransitionEvent.ANSWERS_RECEIVED):
            PlayerState.GUESSING,
        (PlayerState.GUESSING, TransitionEvent.GUESS_SUBMITTED):
            PlayerState.MATCH_COMPLETE,
        (PlayerState.MATCH_COMPLETE, TransitionEvent.GAME_RESULT_RECEIVED):
            PlayerState.REGISTERED,
    }

    def __init__(self):
        self._state = PlayerState.INIT_START_STATE
        self._callbacks: Dict[PlayerState, Callable] = {}

    def transition(self, event: TransitionEvent) -> bool:
        """Attempt event-based state transition."""
        key = (self._state, event)
        if key not in self.TRANSITIONS:
            return False
        self._state = self.TRANSITIONS[key]
        if callback := self._callbacks.get(self._state):
            callback()
        return True

    @property
    def current_state(self) -> PlayerState:
        return self._state
```

> **Event-Based Transitions**
>
> The real implementation uses event-based transitions, not direct state transitions. Each transition is triggered by a specific event (such as REGISTER_REQUEST or GAME_ACCEPTED). This approach allows more precise control over state flow.

### 2.3.4 Persistent State Machine

For the referee agent, it is recommended to save the state machine state in a database to allow crash recovery. The implementation uses a modular architecture:

- **Repository Pattern** — abstract database access through `IStateMachineRepository`
- **Mixin Pattern** — `PersistentStateMachineMixin` adds persistence to any state machine
- **Event-based transitions** — use `transition(event)` instead of direct state assignment
- **Factory methods** — `restore_from_db()` and `get_or_create()` for loading state

**Table 20: state_machine_state Table**

| Field | Type | Description |
|---|---|---|
| id | SERIAL PRIMARY KEY | Auto primary key |
| entity_id | VARCHAR(100) NOT NULL | Entity identifier (e.g., ch_id) |
| machine_type | VARCHAR(50) NOT NULL | Machine type: MATCH, ND |
| current_state | VARCHAR(50) NOT NULL | Current state |
| state_data | JSONB NOT NULL | Accompanying state data |
| parent_id | VARCHAR(100) | Parent entity identifier (optional) |
| is_terminal | BOOLEAN DEFAULT FALSE | Whether this is a terminal state |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP DEFAULT NOW() | Last update time |

Constraint: UNIQUE(entity_id, machine_type)

```python
# PersistentStateMachine — Mixin + Repository Pattern

# Repository interface for database abstraction
class IStateMachineRepository(ABC):
    @abstractmethod
    def get_state(self, entity_id: str, machine_type: str) -> Optional[dict]: ...
    @abstractmethod
    def save_state(self, entity_id: str, machine_type: str,
                   state: str, state_data: dict) -> None: ...

# Mixin adds persistence to any state machine
class PersistentStateMachineMixin:
    """Mixin that adds database persistence to state machines."""
    def __init__(self, repository: IStateMachineRepository,
                 entity_id: str, machine_type: str):
        self._repository = repository
        self.entity_id = entity_id
        self.machine_type = machine_type
        # Note: Does NOT auto-load state in constructor

    @classmethod
    def restore_from_db(cls, repository, entity_id: str,
                        machine_type: str) -> Optional['Self']:
        """Factory method to restore state machine from database."""
        row = repository.get_state(entity_id, machine_type)
        if row is None:
            return None  # No default state - returns None if not found
        instance = cls(repository, entity_id, machine_type)
        instance._state = row['current_state']
        instance._state_data = row['state_data']
        return instance

    def transition(self, event: str) -> None:
        """Event-based transition with automatic persistence."""
        old_state = self._state
        super().transition(event)  # Delegate to base state machine
        self._persist_state()

    def _persist_state(self) -> None:
        """Persist current state using repository (upsert pattern)."""
        self._repository.save_state(
            self.entity_id, self.machine_type,
            self._state, self._state_data
        )

# History recording is separate concern
class StateHistoryMixin:
    """Separate mixin for recording state transition history."""
    def record_transition(self, from_state, event, to_state): ...
```

### 2.3.5 State Transition History

For audit and debug purposes, it is recommended to document every state transition. History documentation is implemented as a separate Mixin (StateHistoryMixin) for separation of concerns:

**Table 21: state_history Table**

| Field | Type | Description |
|---|---|---|
| entity_id | VARCHAR | Entity identifier |
| machine_type | VARCHAR | Machine type |
| from_state | VARCHAR | Source state |
| event | VARCHAR | Event that caused the transition |
| to_state | VARCHAR | Target state |
| timestamp | TIMESTAMP | Transition time |
| is_initial_entry | BOOLEAN | Whether this is the initial entry |

```python
# StateHistoryMixin — Separate History Recording
class StateHistoryMixin:
    """Mixin for recording state transition history (separate concern)."""
    def __init__(self, history_repository: IStateHistoryRepository, **kwargs):
        super().__init__(**kwargs)
        self._history_repo = history_repository

    def record_transition(self, from_state: str, event: str, to_state: str) -> None:
        """Record state transition for audit trail."""
        self._history_repo.insert(
            entity_id=self.entity_id,
            machine_type=self.machine_type,
            from_state=from_state,
            event=event,
            to_state=to_state,
            is_initial_entry=(from_state is None)
        )

# Combining persistence and history via multiple inheritance
class FullStateMachine(PersistentStateMachineMixin, StateHistoryMixin, BaseStateMachine):
    """State machine with both persistence and history recording."""
    pass
```

> **Persistence Advantage**
>
> A persistent state machine enables:
> - Crash recovery — the agent can continue from the last state
> - Debugging — ability to track transition history
> - Audit — complete documentation for appeals

## 2.4 The GateKeeper Pattern (Email Protection)

> **Critical Requirement**
>
> Every agent (player and referee) must implement a GateKeeper mechanism to protect Gmail API quotas. An agent without protection may exhaust the entire daily quota and stop functioning.

### 2.4.1 Three GateKeeper Components

Your agent needs to implement three protection mechanisms:

**Table 22: GateKeeper Components**

| Component | Role | Recommended Values |
|---|---|---|
| Quota Manager | Track daily quota | 400 messages/day, warning at 80% |
| Rate Limiter | Limit send rate | 5 tokens, refill 1/second |
| DOS Detector | Detect infinite loops | Maximum 2 messages/minute to same recipient |

### 2.4.2 Quota Manager

Gmail API limits free accounts to 500 messages per day. Leave a safety buffer:

```python
# QuotaManager — Daily Email Limit
class QuotaManager:
    """Track daily email quota."""
    def __init__(self, daily_limit: int = 400, warning_threshold: float = 0.8):
        self.daily_limit = daily_limit
        self.warning_threshold = warning_threshold
        self._count = 0
        self._last_reset = datetime.now(timezone.utc).date()

    def can_send(self) -> bool:
        """Check if we can send more emails today."""
        self._maybe_reset()
        return self._count < self.daily_limit

    def record_send(self) -> None:
        """Record an outgoing email."""
        self._maybe_reset()
        self._count += 1
        if self._count >= self.daily_limit * self.warning_threshold:
            logger.warning(f"Quota warning: {self._count}/{self.daily_limit}")

    def _maybe_reset(self) -> None:
        """Reset counter at midnight GMT."""
        today = datetime.now(timezone.utc).date()
        if today > self._last_reset:
            self._count = 0
            self._last_reset = today
```

### 2.4.3 Loop Detection (DOS Self-Protection)

The agent may enter an infinite loop of sending messages. Add protection:

```python
# DOS Detector — Prevent Runaway Loops
class DOSDetector:
    """Detect runaway message loops."""
    def __init__(self, max_per_minute: int = 2):
        self.max_per_minute = max_per_minute
        self._recent_sends: dict[str, list[datetime]] = {}

    def is_safe_to_send(self, recipient: str) -> bool:
        """Check if sending to this recipient is safe."""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        # Clean old entries
        if recipient in self._recent_sends:
            self._recent_sends[recipient] = [
                t for t in self._recent_sends[recipient] if t > cutoff
            ]
        # Check rate
        recent = self._recent_sends.get(recipient, [])
        return len(recent) < self.max_per_minute

    def record_send(self, recipient: str) -> None:
        """Record a send to recipient."""
        if recipient not in self._recent_sends:
            self._recent_sends[recipient] = []
        self._recent_sends[recipient].append(datetime.now(timezone.utc))
```

> **Why This Matters**
>
> A bug in your code can cause sending hundreds of messages in minutes. This will cause:
> - Exhausting the daily email quota
> - Temporary blocking by Gmail
> - Technical losses in all remaining games

## 2.5 Token Bucket Rate Limiter

### 2.5.1 The Problem

Gmail API limits the number of calls. Exceeding causes a 429 Too Many Requests error and temporary blocking.

### 2.5.2 The Solution

Token Bucket algorithm allows smooth rate control:
1. Token bucket — holds up to N tokens (e.g., 5)
2. Refill — new token every T seconds (e.g., every second)
3. Consumption — every API call consumes one token
4. Waiting — if no tokens, wait for refill

```python
# TokenBucketRateLimiter Implementation
import time
import threading

class TokenBucketRateLimiter:
    """Thread-safe token bucket rate limiter."""
    def __init__(self, capacity: int = 5, refill_rate: float = 1.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, timeout: float = 30.0) -> bool:
        """Acquire a token. Blocks until available or timeout."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            time.sleep(0.1)
        return False

    def _refill(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
```

> **Recommendation**
>
> Start with a capacity of 5 tokens and a refill rate of one token per second. Adjust as needed.

## 2.6 Periodic Scheduling System

### 2.6.1 Two Main Loops

The agent needs to perform periodic operations:

**Table 23: Scheduling Loops**

| Loop | Frequency | Role |
|---|---|---|
| Poll Loop | Every 30 seconds | Check for new messages |
| Heartbeat Loop | Every 5 minutes | Send keep-alive signal |

### 2.6.2 Implementation

```python
# PeriodicHandler with Event
import threading
from typing import Callable

class PeriodicHandler:
    """Manages periodic tasks with graceful shutdown."""
    def __init__(self):
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

    def add_task(self, func: Callable, interval: float, name: str):
        """Add a periodic task."""
        def runner():
            while not self._stop_event.wait(interval):
                try:
                    func()
                except Exception as e:
                    print(f"Error in {name}: {e}")
        thread = threading.Thread(target=runner, name=name, daemon=True)
        self._threads.append(thread)

    def start(self):
        """Start all periodic tasks."""
        for thread in self._threads:
            thread.start()

    def stop(self, timeout: float = 5.0):
        """Signal all tasks to stop and wait."""
        self._stop_event.set()
        for thread in self._threads:
            thread.join(timeout=timeout)
```

> **Important Principle**
>
> Use `Event.wait()` instead of `time.sleep()` — this allows fast and orderly shutdown.

## 2.7 Message Routing

### 2.7.1 Registration Pattern

Instead of a long `if-else` chain for handling message types, use the registration pattern:

```python
# MessageRouter with Handler Registration
from typing import Dict, Callable, Any
from enum import Enum

class MessageType(Enum):
    REGISTRATION_CONFIRMED = "REGISTRATION_CONFIRMED"
    MATCH_ASSIGNMENT = "MATCH_ASSIGNMENT"
    GAME_INVITATION = "GAME_INVITATION"
    GAME_JOIN_ACK = "GAME_JOIN_ACK"
    Q21_WARMUP_CALL = "Q21_WARMUP_CALL"
    GAME_RESULT = "GAME_RESULT"
    BROADCAST_KEEP_ALIVE = "BROADCAST_KEEP_ALIVE"

class MessageRouter:
    """Routes messages to registered handlers."""
    def __init__(self):
        self._handlers: Dict[MessageType, Callable] = {}

    def register(self, msg_type: MessageType, handler: Callable):
        """Register a handler for a message type."""
        self._handlers[msg_type] = handler

    def route(self, message: Dict[str, Any]) -> bool:
        """Route message to appropriate handler."""
        msg_type_str = message.get("message_type")
        try:
            msg_type = MessageType(msg_type_str)
        except ValueError:
            return False  # Unknown message type
        handler = self._handlers.get(msg_type)
        if handler:
            handler(message)
            return True
        return False
```

### 2.7.2 Pattern Advantages

- Easy extension — adding a new message type = registering a new handler
- Testing — easy to test each handler separately
- Readability — clear who handles what

### 2.7.3 Dedicated Q21 Handlers (Referee)

For the referee agent, dedicated handlers must be defined for each game phase:

**Table 24: Q21 Handlers for Referee**

| Handler | Message Type | Role |
|---|---|---|
| MatchAssignmentHandler | MATCH_ASSIGNMENT | Receive game assignment |
| Q21WarmupResponseHandler | Q21_WARMUP_RESPONSE | Player readiness confirmation |
| Q21QuestionsBatchHandler | Q21_QUESTIONS_BATCH | Receive 20 questions |
| Q21GuessSubmissionHandler | Q21_GUESS_SUBMISSION | Receive final guess |
| ScoreCalculator | (internal) | Calculate scores |
| BroadcastHandler | BROADCAST_* | Handle broadcasts |

```python
# Q21 Referee Handler Registration
class Q21RefereeOrchestrator:
    """Orchestrator for Q21 referee agent."""

    def _register_handlers(self) -> None:
        """Register all Q21-specific handlers."""
        # Match lifecycle - warmup response confirms player readiness
        self.router.register("MATCH_ASSIGNMENT",
            MatchAssignmentHandler(self.state_machine, self.db))
        # Q21 game flow - warmup serves as readiness confirmation
        self.router.register("Q21_WARMUP_RESPONSE",
            Q21WarmupResponseHandler(self.state_machine))
        self.router.register("Q21_QUESTIONS_BATCH",
            Q21QuestionsBatchHandler(self.state_machine, self.question_repo))
        self.router.register("Q21_GUESS_SUBMISSION",
            Q21GuessSubmissionHandler(self.state_machine, self.scorer))
        # Broadcasts
        for broadcast_type in BROADCAST_TYPES:
            self.router.register(broadcast_type,
                BroadcastHandler(self.state_machine, self.db))

    def handle_incoming(self, message: dict) -> None:
        """Route incoming message to appropriate handler."""
        msg_type = message.get("message_type")
        handler = self.router.get(msg_type)
        if handler:
            handler.handle(message)
        else:
            self.logger.warning(f"Unknown message type: {msg_type}")
```

> **Important Principle**
>
> Every handler should:
> - Update the state machine accordingly
> - Cancel/start relevant timeouts
> - Log the action in the database
> - Return a response if required

## 2.8 Message Consolidation via CC

### 2.8.1 The Principle

Instead of sending multiple separate messages, use the CC field for consolidation:

**Table 25: Using Recipient Fields**

| Recipient Field | Role |
|---|---|
| TO | Main recipient — League Manager |
| CC | Automatic documentation — Log Server |
| CC | Group member transparency |

```python
# Sending with CC
def send_move(self, game_id: str, move: str) -> None:
    """Send move to LGM with CC to log server and group."""
    message = self._build_move_message(game_id, move)
    recipients = {
        "to": [self.config.lgm_email],
        "cc": [
            self.config.log_server_email,
            *self._get_group_emails()
        ]
    }
    self.gmail_client.send(
        to=recipients["to"],
        cc=recipients["cc"],
        subject=self._build_subject(game_id),
        body=json.dumps(message)
    )
```

### 2.8.2 API Savings

A single send with CC consumes one API call, instead of three separate calls.

## 2.9 Watchdog Mechanism

### 2.9.1 The Problem

The scan loop may stall due to:
- Network failure
- Unhandled exception
- Deadlock

### 2.9.2 The Solution

```python
# Watchdog Implementation
import time
import threading

class Watchdog:
    """Detects stalled operations."""
    def __init__(self, timeout: float = 120.0, callback: Callable = None):
        self.timeout = timeout
        self.callback = callback
        self._last_ping = time.monotonic()
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._monitor, daemon=True)

    def ping(self):
        """Call this regularly to indicate activity."""
        with self._lock:
            self._last_ping = time.monotonic()

    def _monitor(self):
        """Background monitor thread."""
        while self._running:
            time.sleep(10)  # Check every 10 seconds
            with self._lock:
                elapsed = time.monotonic() - self._last_ping
                if elapsed > self.timeout and self.callback:
                    self.callback()

    def start(self):
        self._thread.start()

    def stop(self):
        self._running = False
```

### 2.9.3 Usage

```python
# Watchdog in Main Loop
def _run_main_loop(self):
    watchdog = Watchdog(
        timeout=120.0,
        callback=self._handle_stall
    )
    watchdog.start()
    while self._running:
        watchdog.ping()  # Signal activity
        messages = self._poll_for_messages()
        for msg in messages:
            self.message_router.route(msg)
        time.sleep(30)
```

## 2.10 Deadline Tracking Pattern

### 2.10.1 The Problem

If the agent does not respond in time, the response will be rejected and it will receive a REJECTION_NOTIFICATION. You must track response deadlines.

```python
# DeadlineTracker — Track Response Deadlines
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class PendingResponse:
    message_id: str
    message_type: str
    deadline: datetime
    correlation_id: str

class DeadlineTracker:
    """Track pending responses and their deadlines."""
    def __init__(self):
        self._pending: dict[str, PendingResponse] = {}

    def add_pending(self, message_id: str, message_type: str,
                    deadline: datetime, correlation_id: str) -> None:
        """Track a message requiring response."""
        self._pending[message_id] = PendingResponse(
            message_id=message_id,
            message_type=message_type,
            deadline=deadline,
            correlation_id=correlation_id
        )

    def get_urgent(self) -> list[PendingResponse]:
        """Get messages with deadline in next 30 seconds."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(seconds=30)
        return [p for p in self._pending.values() if p.deadline <= cutoff]

    def mark_responded(self, correlation_id: str) -> None:
        """Remove message after responding."""
        to_remove = [k for k, v in self._pending.items()
                     if v.correlation_id == correlation_id]
        for k in to_remove:
            del self._pending[k]
```

### 2.10.2 Persistent Timeout Manager

For the referee agent, it is recommended to manage timeouts in a database to allow crash recovery:

**Table 26: pending_timeouts Table**

| Field | Type | Description |
|---|---|---|
| id | SERIAL PRIMARY KEY | Auto primary key |
| timeout_id | VARCHAR(100) UNIQUE NOT NULL | Unique identifier (UUID) |
| timeout_type | VARCHAR(50) NOT NULL | Type: WARMUP, QUESTIONS, GUESS |
| target_email | VARCHAR(255) NOT NULL | Waiting player address |
| started_at | TIMESTAMP NOT NULL | Countdown start time |
| timeout_seconds | FLOAT NOT NULL | Duration in seconds (supports fractions) |
| expires_at | TIMESTAMP NOT NULL | Expiry time (calculated) |
| context | JSONB | Additional context (match_id, phase, attempt) |
| created_at | TIMESTAMP | Record creation time |

Implementation notes:
- match_id is stored inside the context field, not as a separate column
- Timeout cancellation is done by deleting the record (not marking is_active=FALSE)
- timeout_id is UUID, not a serial number

**Table 27: Timeout Values in Referee Implementation**

| Phase | Time (seconds) | Notes |
|---|---|---|
| WARMUP | 300 | One retry allowed |
| QUESTIONS | 600 | No retry |
| GUESS | 600 | No retry |
| Default | 900 | For general operations |

```python
# PersistentTimeoutManager — Database-Backed Timeouts
class PersistentTimeoutManager:
    """Manages game timeouts with database persistence."""
    TIMEOUT_VALUES = {
        "WARMUP": 300.0,    # 5 minutes (float)
        "QUESTIONS": 600.0, # 10 minutes
        "GUESS": 300.0,     # 5 minutes
        "DEFAULT": 900.0,   # 15 minutes
    }

    def __init__(self, db_connection):
        self.db = db_connection

    def start_timeout(self, timeout_type: str, target_email: str,
                      match_id: str = None, context: dict = None) -> str:
        """Start a new timeout and persist to database."""
        timeout_id = str(uuid.uuid4())  # UUID string, not SERIAL
        timeout_seconds = self.TIMEOUT_VALUES.get(timeout_type, self.TIMEOUT_VALUES["DEFAULT"])
        # match_id stored inside context JSONB, not separate column
        full_context = {"match_id": match_id, **(context or {})}
        self.db.execute("""
            INSERT INTO pending_timeouts
            (timeout_id, timeout_type, target_email, started_at,
             timeout_seconds, expires_at, context)
            VALUES (%s, %s, %s, NOW(), %s,
                    NOW() + INTERVAL '%s seconds', %s)
        """, (timeout_id, timeout_type, target_email, timeout_seconds,
              timeout_seconds, json.dumps(full_context)))
        return timeout_id  # Returns UUID string

    def cancel_timeout(self, timeout_id: str) -> None:
        """Cancel timeout by DELETING (not marking inactive)."""
        self.db.execute("""
            DELETE FROM pending_timeouts WHERE timeout_id = %s
        """, (timeout_id,))

    def get_expired_timeouts(self) -> list[dict]:
        """Get all expired timeouts (existence = active)."""
        return self.db.execute("""
            SELECT * FROM pending_timeouts WHERE expires_at <= NOW()
        """).fetchall()
```

## 2.11 Message Correlation Pattern

### 2.11.1 Using correlation_id

Every message in the system includes a correlation_id field that links request to response:

```python
# MessageCorrelator — Match Requests and Responses
class MessageCorrelator:
    """Match outgoing requests with incoming responses."""
    def __init__(self):
        self._open_requests: dict[str, dict] = {}

    def track_request(self, correlation_id: str, request: dict) -> None:
        """Track an outgoing request."""
        self._open_requests[correlation_id] = {
            "request": request,
            "sent_at": datetime.now(timezone.utc),
            "status": "OPEN"
        }

    def match_response(self, correlation_id: str, response: dict) -> dict:
        """Match response to original request."""
        if correlation_id not in self._open_requests:
            return None
        entry = self._open_requests[correlation_id]
        entry["response"] = response
        entry["received_at"] = datetime.now(timezone.utc)
        entry["status"] = "CLOSED"
        return entry["request"]

    def get_open_requests(self) -> list[str]:
        """Get all open correlation IDs."""
        return [k for k, v in self._open_requests.items()
                if v["status"] == "OPEN"]
```

## 2.12 Broadcast Handling

### 2.12.1 11 Broadcast Types

The league manager sends broadcast messages to all participants. Some require a response:

**Table 28: Broadcast Types and Required Response**

| Type | Description | Response? | Deadline |
|---|---|---|---|
| BROADCAST_KEEP_ALIVE | Availability check | Yes | 30s |
| BROADCAST_CRITICAL_RESET | System reset | Yes | 2m |
| BROADCAST_CRITICAL_PAUSE | Pause activity | Yes | 2m |
| BROADCAST_CRITICAL_CONTINUE | Resume activity | Yes | 2m |
| BROADCAST_FREE_TEXT | Free message | Optional | 1h |
| BROADCAST_NEW_LEAGUE_ROUND | Round start | No | — |
| BROADCAST_END_LEAGUE_ROUND | Round end | No | — |
| BROADCAST_START_SEASON | Season start | No | — |
| BROADCAST_END_SEASON | Season end | No | — |
| BROADCAST_ASSIGNMENT_TABLE | Assignment table | No | — |
| BROADCAST_ROUND_RESULTS | Round results | No | — |

### 2.12.2 Broadcast Handler Implementation

```python
# BroadcastHandler — Complete Implementation
class BroadcastHandler:
    """Handles league-wide broadcast messages."""
    # Broadcasts that require response
    RESPONSE_REQUIRED = {
        "BROADCAST_KEEP_ALIVE": ("RESPONSE_KEEP_ALIVE", 30),
        "BROADCAST_CRITICAL_RESET": ("RESPONSE_CRITICAL_RESET", 120),
        "BROADCAST_CRITICAL_PAUSE": ("RESPONSE_CRITICAL_PAUSE", 120),
        "BROADCAST_CRITICAL_CONTINUE": ("RESPONSE_CRITICAL_CONTINUE", 120),
    }

    def __init__(self, state_machine: PlayerStateMachine):
        self.state_machine = state_machine
        self._previous_state = None

    def handle(self, message: dict) -> dict | None:
        """Route broadcast to appropriate handler."""
        msg_type = message.get("message_type")
        if msg_type == "BROADCAST_KEEP_ALIVE":
            return self._handle_keep_alive(message)
        elif msg_type == "BROADCAST_CRITICAL_PAUSE":
            return self._handle_pause(message)
        elif msg_type == "BROADCAST_CRITICAL_CONTINUE":
            return self._handle_continue(message)
        elif msg_type in ("BROADCAST_NEW_LEAGUE_ROUND", "BROADCAST_END_LEAGUE_ROUND"):
            self._update_round_state(message)
            return None  # No response required
        return None

    def _handle_keep_alive(self, message: dict) -> dict:
        """Respond to keep-alive with current state."""
        return {
            "message_type": "RESPONSE_KEEP_ALIVE",
            "broadcast_id": message.get("broadcast_id"),
            "machine_state": self.state_machine.current_state.name
        }
```

> **Broadcast Identification**
>
> A broadcast message can be identified by:
> - Message type starts with `BROADCAST_`
> - `broadcast_id` field exists in message content
> - Sent from league manager address

### 2.12.3 Broadcast Logging in Database (Referee)

For the referee agent, it is recommended to log received broadcasts and sent responses:

**Table 29: broadcasts_received Table**

| Field | Type | Description |
|---|---|---|
| id | SERIAL PRIMARY KEY | Auto primary key |
| broadcast_id | VARCHAR(100) UNIQUE NOT NULL | Broadcast identifier |
| message_type | VARCHAR(100) NOT NULL | Broadcast type |
| message_text | VARCHAR(200) | Short text content |
| league_id | VARCHAR(100) | League identifier (optional) |
| round_id | VARCHAR(100) | Round identifier (optional) |
| season_id | VARCHAR(100) | Season identifier (optional) |
| sender_email | VARCHAR(255) NOT NULL | Sender address |
| payload | JSONB NOT NULL | Broadcast content |
| requires_response | BOOLEAN DEFAULT FALSE | Whether response is required |
| response_deadline | TIMESTAMP | Response deadline (optional) |
| response_sent | BOOLEAN DEFAULT FALSE | Whether response was sent |
| response_sent_at | TIMESTAMP | When response was sent |
| received_at | TIMESTAMP DEFAULT NOW() | Receive time |
| processed_at | TIMESTAMP | When broadcast was processed |
| status | VARCHAR(50) DEFAULT 'RECEIVED' | Status: RECEIVED, RESPONDED, RED |

**Table 30: broadcast_responses_sent Table**

| Field | Type | Description |
|---|---|---|
| broadcast_id | VARCHAR | Link to original broadcast (foreign key) |
| response_message_id | VARCHAR(100) | Response message identifier |
| response_type | VARCHAR | Response type |
| payload | JSONB | Response content |
| sent_at | TIMESTAMP | Send time |
| status | VARCHAR | Status: SENT, FAILED |
| context_season_id | VARCHAR | Season context |
| context_round_id | VARCHAR | Round context |

## 2.13 Timezone Policy

### 2.13.1 Guiding Principle

> **Iron Rule**
>
> All internal system clocks operate in UTC. User display will be in Israel winter time (UTC+2).

This principle ensures:
- Consistency — all agents use the same time base
- Simplicity — no need to deal with summer/winter time in internal logic
- Documentation — all logs and databases use UTC
- Compatibility — conversion to local time only in display layer

### 2.13.2 Israel Winter Time

Israel Winter Time is UTC+2 (two hours ahead of UTC). For example:

**Table 31: Time Conversion**

| UTC | Israel Winter Time | Note |
|---|---|---|
| 00:00 | 02:00 | Midnight UTC = 02:00 in Israel |
| 10:00 | 12:00 | Morning UTC = Noon in Israel |
| 22:00 | 00:00 (+1) | Evening UTC = Midnight next day in Israel |

### 2.13.3 Code Implementation

```python
# Timezone Handling — UTC Internal
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+

# Israel Winter Time = UTC+2
ISRAEL_WINTER_TZ = ZoneInfo("Asia/Jerusalem")

def get_current_utc() -> datetime:
    """Get current time in UTC (for internal use)."""
    return datetime.now(timezone.utc)

def utc_to_israel_display(utc_time: datetime) -> str:
    """Convert UTC to Israel time for display."""
    israel_time = utc_time.astimezone(ISRAEL_WINTER_TZ)
    return israel_time.strftime("%d/%m/%Y %H:%M:%S")

def format_deadline_for_user(deadline_utc: datetime) -> str:
    """Format deadline for user-facing messages."""
    israel_time = deadline_utc.astimezone(ISRAEL_WINTER_TZ)
    return f"Deadline: {israel_time.strftime('%H:%M:%S')} (Israel time)"

# Example usage
deadline_utc = datetime(2026, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
print(utc_to_israel_display(deadline_utc))  # "15/01/2026 12:30:00"
```

### 2.13.4 Important Points

1. **Database storage** — all timestamps saved in UTC
2. **Logs** — all logs use UTC for consistency
3. **Communication protocol** — all times in JSON messages are in UTC
4. **User display** — conversion to UTC+2 only in user interface
5. **Quota resets** — Gmail API quota resets at midnight UTC (02:00 in Israel)

> **Why Not Summer Time?**
>
> The league operates in winter months (January-February), so Israel Winter Time (UTC+2) is used. If the league is held in summer, use UTC+3.

## 2.14 Configuration Management

### 2.14.1 Separating Secrets from Settings

**Table 32: Configuration File Separation**

| File | Content | In Git? |
|---|---|---|
| .env | Secrets (passwords, keys) | No |
| config.json | Settings (addresses, parameters) | Yes |

### 2.14.2 Secrets File

```
# .env File
# Gmail API credentials
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REFRESH_TOKEN=your-refresh-token
# Database
DATABASE_URL=postgresql://user:pass@localhost/league
```

### 2.14.3 Settings File

```json
{
  "agent": {
    "player_id": "P-Q21G-001",
    "group_id": "G001"
  },
  "gmail": {
    "poll_interval_seconds": 30,
    "rate_limit_capacity": 5,
    "rate_limit_refill_rate": 1.0
  },
  "lgm": {
    "email": "league.manager.q21g@gmail.com",
    "log_server_email": "beit.halevi.700@gmail.com"
  },
  "watchdog": {
    "timeout_seconds": 120
  }
}
```

## 2.15 Summary

This chapter presented the architectural principles for implementing a player or referee agent:

- **Orchestrator** — single entry point for coordinating all activity
- **State machine** — managing transitions between defined states
- **Token Bucket** — control over API call rate
- **Periodic Handler** — executing periodic operations with orderly shutdown
- **Message Router** — routing messages to registered handlers
- **CC consolidation** — saving API calls and transparency
- **Watchdog** — detecting and recovering from stalls
- **Broadcast handling** — responding to system messages
- **Timezone policy** — internal clocks in UTC, display in Israel time (UTC+2)
- **Configuration separation** — secrets in .env, settings in config.json

> **Recommendation:** Start with a simple implementation of each component, and improve gradually. Don't try to build everything perfectly from the start.
>
> For background on the league manager's parallel architecture, see Appendix H.

---

*© Dr. Segal Yoram - All rights reserved*

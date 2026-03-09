# 10 ID Conventions

## 10.1 Introduction

This appendix consolidates all ID formats (IDs) used in the league system. Understanding the ID structure is essential for message parsing, database queries, and debugging.

## 10.2 Group and User IDs

### 10.2.1 Group ID (group_id)

**Table 178: Group ID Format**

| Component | Description | Example |
|---|---|---|
| G | Fixed prefix | G |
| ### | Serial number (3 digits) 001–030 | G001, G015, G030 |

Total: 4 characters

### 10.2.2 User ID (user_id)

**Table 179: User ID Format**

| Component | Description | Example |
|---|---|---|
| U-Q21G- | Fixed prefix | U-Q21G- |
| ### | Serial number (3 digits) 001–060 | U-Q21G-001 |

Total: 10 characters

## 10.3 Player and Referee IDs

### 10.3.1 Player ID (player_id)

**Table 180: Player ID Format**

| Component | Description | Example |
|---|---|---|
| P-Q21G- | Fixed prefix | P-Q21G- |
| ### | Serial number (3 digits) 001–030 | P-Q21G-001 |

Total: 10 characters

### 10.3.2 Referee ID (referee_id)

**Table 181: Referee ID Format**

| Component | Description | Example |
|---|---|---|
| R-Q21G- | Fixed prefix | R-Q21G- |
| ### | Serial number (3 digits) 001–030 | R-Q21G-001 |

Total: 10 characters

## 10.4 Season and Round IDs

### 10.4.1 Season ID (season_id)

**Table 182: Season ID Format**

| Component | Description | Example |
|---|---|---|
| S or W | Season type (S=regular, W=winter) | S |
| ## | Season number (2 digits) | 01, 02 |

Total: 3 characters. Examples: S01, S02, W01

### 10.4.2 Round ID (round_id)

**Table 183: Round ID Format**

| Component | Description | Example |
|---|---|---|
| ## | Round number (2 digits) 01–06 | 01, 03, 06 |

Total: 2 digits

## 10.5 Composite Game ID (SSRRGGG)

### 10.5.1 ID Structure

The game ID is a string of 7 digits containing all hierarchical information:

**Table 184: Composite Game ID Structure**

| Field | Position | Description |
|---|---|---|
| SS | 1-2 | Season number (01–99) |
| RR | 3-4 | Round number (01–06) |
| GGG | 5-7 | Game number in round (001–010) |

### 10.5.2 Full Examples

**Table 185: Game ID Decomposition Examples**

| ID | Season | Round | Game | Meaning |
|---|---|---|---|---|
| 0101001 | S01 | 01 | 001 | Season A, Round 1, Game 1 |
| 0103007 | S01 | 03 | 007 | Season A, Round 3, Game 7 |
| 0206010 | S02 | 06 | 010 | Season B, Round 6, Game 10 |

### 10.5.3 Parse Code

```python
def parse_game_id(game_id: str) -> dict:
    """Parse SSRRGGG format into components."""
    if len(game_id) != 7 or not game_id.isdigit():
        raise ValueError(f"Invalid game_id: {game_id}")
    return {
        "season_id": f"S{game_id[0:2]}",
        "round_id": int(game_id[2:4]),
        "game_num": int(game_id[4:7])
    }

def build_game_id(season: int, round: int, game: int) -> str:
    """Build SSRRGGG from components."""
    return f"{season:02d}{round:02d}{game:03d}"

# Examples:
# parse_game_id("0103007") -> {"season_id": "S01", "round_id": 3, "game_num": 7}
# build_game_id(1, 3, 7) -> "0103007"
```

### 10.5.4 Assignment Statistics

The total number of assignments in a season depends on the number of participants:

**Table 186: Assignment Statistics by Number of Participants**

| Users | Games/Round | Total Games | Total Assignments |
|---|---|---|---|
| 3 | 1 | 6 | 18 |
| 6 | 2 | 12 | 36 |
| 9 | 3 | 18 | 54 |
| 15 | 5 | 30 | 90 |
| 30 | 10 | 60 | 180 |

**Assignment Formula:**

```
Assignments = (Users / 3) × 6 rounds × 3 roles
```

Each game requires 3 assignments: one referee and two players.

## 10.6 Broadcast and Message IDs

### 10.6.1 Broadcast ID (broadcast_id)

**Table 187: Broadcast ID Format**

| Component | Description | Example |
|---|---|---|
| BC | Fixed prefix | BC |
| ### | Serial number (3 digits) 001–999 | BC001, BC123 |

Total: 5 characters

### 10.6.2 Message ID (message_id)

The message ID is a UUID in standard format:

**Table 188: Message ID Format**

| Component | Format | Length | Example |
|---|---|---|---|
| UUID v4 | Standard | 36 characters | 550e8400-e29b-41d4-a716-446655440000 |

### 10.6.3 Conversation ID (conversation_id)

The conversation ID links messages related to the same game or interaction:

**Table 189: Conversation ID Format**

| Component | Description | Example |
|---|---|---|
| CONV- | Fixed prefix | CONV- |
| game_id | Game ID | 0101001 |
| - | Separator | - |
| UUID[:8] | Part of UUID | 550e8400 |

Total: 21 characters. Example: `CONV-0101001-550e8400`

**Using conversation_id:**
The referee uses the conversation_id to link all messages of a specific game:
- Invitation and player responses
- Questions and answers
- Guesses and scores

### 10.6.4 Calendar Channel ID (channel_id)

A channel ID is used for receiving notifications from Google Calendar:

**Table 190: Calendar Channel ID Format**

| Component | Format | Length | Example |
|---|---|---|---|
| UUID v4 | Standard | 36 characters | ch-550e8400-e29b-41d4-a716- |

The channel is created when subscribing to Google Calendar push notifications and serves as a backup for league manager messages.

## 10.7 Consolidated Reference Table

**Table 191: Full Reference Table — All ID Types**

| ID Type | Format | Length | Example |
|---|---|---|---|
| group_id | G### | 4 | G001 |
| user_id | U-Q21G-### | 10 | U-Q21G-001 |
| player_id | P-Q21G-### | 10 | P-Q21G-001 |
| referee_id | R-Q21G-### | 10 | R-Q21G-001 |
| season_id | S## or W## | 3 | S01 |
| round_id | ## | 2 | 01 |
| game_id | SSRRGGG | 7 | 0101001 |
| broadcast_id | BC### | 5 | BC001 |
| message_id | UUID v4 | 36 | 550e8400-... |
| conversation_id | CONV-#######-######## | 21 | CONV-0101001-550e8400 |
| channel_id | UUID v4 | 36 | ch-550e8400-... |

## 10.8 Regular Expressions for Validation

```python
import re

ID_PATTERNS = {
    "group_id": r"^G\d{3}$",
    "user_id": r"^U-Q21G-\d{3}$",
    "player_id": r"^P-Q21G-\d{3}$",
    "referee_id": r"^R-Q21G-\d{3}$",
    "season_id": r"^[SW]\d{2}$",
    "round_id": r"^\d{2}$",
    "game_id": r"^\d{7}$",
    "broadcast_id": r"^BC\d{3}$",
    "message_id": r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    # Referee-specific IDs
    "conversation_id": r"^CONV-\d{7}-[0-9a-f]{8}$",
    "channel_id": r"^ch-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}$"
}

def validate_id(id_type: str, value: str) -> bool:
    """Validate ID against its pattern."""
    pattern = ID_PATTERNS.get(id_type)
    if not pattern:
        raise ValueError(f"Unknown ID type: {id_type}")
    return bool(re.match(pattern, value, re.IGNORECASE))
```

---

*© Dr. Segal Yoram - All rights reserved*

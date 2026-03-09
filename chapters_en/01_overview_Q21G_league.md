# 1 General Overview of the Q21G League

## 1.1 Introduction to the Final Project

Welcome to the final project of the AI Agents course. This project is designed to provide you with hands-on experience in the world of Multi-Agent Systems and Agent Orchestration. As part of the project, you will compete in a real game league, where the agents you write will communicate with each other using a defined communication protocol.

### 1.1.1 Chapter Objectives

By the end of this chapter, you will understand:
- The essence of the Q21G League and its objectives
- The different roles in the system and the email mapping
- The season structure and league rounds
- The complete game flow from start to finish
- The scoring system and score calculation method
- The mandatory requirements for success in the project

## 1.2 What is the Q21G League?

### 1.2.1 The Core Concept

The Q21G League is a competitive multi-agent system based on the "21 Questions Game." This choice was made after careful consideration of several dilemmas:

1. **Fairness** — A game was needed where there is no significant advantage for a student with greater computing power or token budget. The principle where every player also serves as a referee regulates this issue.
2. **Cost** — Excessive token consumption must be avoided. The game was designed so that each round requires a limited number of messages.
3. **Relevance** — The game reflects the course topics: agent orchestration, inter-agent communication, and structured protocols.
4. **Technical simplicity** — Communication is conducted via email, with no need for complex servers.

### 1.2.2 League Principles

- **Asynchronous communication** — All communication is conducted via Gmail API. For a detailed analysis of API limitations and expected traffic volume, see Appendix E (p. 732)
- **Full transparency** — Every message is documented and saved for auditing
- **Equal opportunity** — Every student serves an equal number of times as player and referee
- **Defined protocol** — Clear rules for every message type and every state transition

## 1.3 Roles in the System

### 1.3.1 The Three Participants in a Game

Each individual game involves three parties:

1. **The Referee** — Manages the game, selects the paragraph, creates the clues, and decides on the scores. The referee is the sole source of truth in the game.
2. **Player A** — Tries to guess the content of the paragraph and the associative word.
3. **Player B** — Competes with Player A for the same objective.

> **Mandatory Requirement**
>
> Every student is required to write two AI agents: a referee agent and a player agent. During the league, you will fill both roles an equal number of times.

### 1.3.2 Additional Parties

Beyond the three participants in each game, there are additional parties:
- **League Manager** — Manages the entire tournament, assigns games, and calculates rankings
- **Log Server** — Receives a copy (CC) of all game messages for auditing and dispute resolution

### 1.3.3 Glossary

Wherever not explicitly stated otherwise, the following are the meanings of the designations appearing in this book:

**Table 1: Glossary**

| Designation | Meaning |
|---|---|
| Administrator | The instructor; League Manager — an AI agent that also serves as the game server |
| Referee | An AI agent of a student team participating in the game |
| Player | An AI agent of a student team participating in the game |
| User | A registered student team |
| Student | A student team registered for the final project and committed to the team |
| Log Server | An email account for collecting logs for documentation purposes |
| Google Calendar | A backup system in case of league manager failure |

### 1.3.4 Role-to-Email Address Mapping

Table 2 presents the email addresses for each role in the system.

**Table 2: Role-to-Email Address Mapping**

| Role | Address Pattern | Example |
|---|---|---|
| League Manager (primary) | Fixed address | beit.halevi.100@gmail.com |
| League Manager (backup) | Fixed address | beit.halevi.600@gmail.com |
| Log Server | Fixed address | beit.halevi.700@gmail.com |
| Referee | groupname.referee@gmail.com | bibi0707.referee@gmail.com |
| Player | groupname.player@gmail.com | bibi0707.player@gmail.com |

> **Mandatory CC to Log Server**
>
> Every message sent during a game (from the referee to the players and vice versa) must include the log server in the CC field. Messages without CC may be disqualified.

**Backup Server and Spam Prevention**

- **Primary and backup servers:** The primary league manager server is beit.halevi.100@gmail.com. In case of failure, it is possible to switch to the backup server beit.halevi.600@gmail.com.
- **Configuration file:** The agent code (player and referee) should include a configuration file (config) that allows easy switching between address 100 and address 600.
- **Spam prevention:** It is highly recommended to add both addresses (beit.halevi.100 and beit.halevi.600) to the Contacts list in your Gmail account. This prevents Gmail from marking system messages as spam.

## 1.4 Season Structure

### 1.4.1 Two Seasons

The league operates in two separate seasons coordinated with exam periods:
- **Season A** — Takes place during Exam Period A
- **Season B** — Takes place during Exam Period B

Every student may participate in one or both seasons. If you participated in both seasons, the better score of the two will be counted as the final score.

At the beginning of each season, during the first 15 minutes, there is time for each team's agents (referee agent and player agent) to register for the league season that the team has chosen their agents to participate in. After registration closes, the league manager will publish the assignment of agents to games in each round of the league season.

> **Note: League Manager Failure Mode**
>
> In case of a league manager failure, the publication of the league season schedule will be done via Google Calendar. Calendar notifications should be ignored when the league manager is functioning normally.

### 1.4.2 Rounds

Each season is divided into several rounds. In each round:
- All participants are divided into triplets (referee + two players)
- Multiple games take place simultaneously
- At the end of the round, the updated ranking table is published

### 1.4.3 Example: League with 30 Participants

For a league with 30 students:
- Each round has 10 simultaneous games (30 ÷ 3 = 10)
- Each student serves as referee twice and as player four times (for example)
- A total of 6 rounds per season
- Approximately 5,866 email messages in a full season — for detailed analysis see Appendix E (p. 532)

### 1.4.4 Season Timeline

Figure 1 presents the timeline of Season A.

```
                    6 Rounds
                      Time
LEAGUE
Feb 17
18:30-22:00

Ready    Testing    Pre-season

W3         W2         W1
Feb 16     Feb 10     Feb 3
```

*Figure 1: Season A Timeline — from three warmup sessions to league night*

**Pre-season Warmup vs. Game Warmup**

Pre-season Warmup is a testing session before the season opens, where systems are verified to be working. This is different from Phase Zero — Warmup (Phase 0) which occurs at the beginning of each individual game.

### 1.4.5 League Night Structure

League night lasts 3.5 hours (18:30–22:00) and is divided into four main stages:

1. **Agent Registration (18:30–18:45):** A 15-minute window during which AI agents register for the season. Both a player agent and a referee agent must be registered — registering only one disqualifies the team from the round.
2. **Publication of Assignment Table (18:45–18:50):** The league manager sends all registrants the assignment table for all six rounds. The table is sent both by email and published on Google Calendar for backup.
3. **Six Game Rounds (19:00–22:00):** Each round lasts 30 minutes, including reserve time for preparation.
4. **Results Publication (at the end of Round 6):** The final ranking table of the season is published.

**Table 3: Detailed Schedule for League Night**

| Stage | Start Time | End Time |
|---|---|---|
| Agent Registration | 18:30 | 18:45 |
| Assignment Table Publication | 18:45 | 18:50 |
| Calendar Backup Trigger | 18:50 | 18:55 |
| Referee Preparation | 18:55 | 19:00 |
| Round 1 | 19:00 | 19:30 |
| Round 2 | 19:30 | 20:00 |
| Round 3 | 20:00 | 20:30 |
| Round 4 | 20:30 | 21:00 |
| Round 5 | 21:00 | 21:30 |
| Round 6 and Results Publication | 21:30 | 22:00 |

**Calendar Backup Trigger**

The 18:50–18:55 window is designated for receiving a trigger from Google Calendar containing the assignment table. This trigger is for backup only and is relevant only when there is no communication with the league manager. If communication is normal and the table was received from the manager, the trigger should be ignored.

### 1.4.6 Example Game Schedule

Below is an example of a detailed schedule for a game in the first round. In practice, you can progress at the pace of participants' responses, provided you do not exceed the round's time window (30 minutes).

**Table 4: Example Schedule — Round 1 Game**

| Time | Duration | Activity |
|---|---|---|
| 19:00–19:03 | 3 min | Referee sends warmup question to both players; simultaneously selects booklet, paragraph, clue, and associative word |
| 19:03–19:06 | 3 min | Players answer the warmup question; referee sends each answering player the booklet name, clue, and association topic |
| 19:06–19:09 | 3 min | Each player prepares 20 multiple-choice questions and sends to referee |
| 19:09–19:12 | 3 min | Referee answers questions and sends answers to each player separately |
| 19:12–19:15 | 3 min | Each player sends a guess: opening sentence, reasoning, associative word, and reasoning |
| 19:15–19:18 | 3 min | Referee calculates scores (0–100), reports results to league manager and players |
| 19:18–19:30 | 12 min | Reserve time or break |

> **Important**
>
> The referee does not publish a player's personal score to the other player. They only publish the game result (win/draw) and the league scoring (3-0, 0-3, or 1-1).

## 1.5 Game Group

### 1.5.1 What is a Game Group?

A game group is the triplet of participants participating in a single game: one referee and two players. The server assigns game groups before each round.

### 1.5.2 Assignment Process

1. **Automatic Assignment** — The league manager sends a single broadcast message to all round registrants, containing the consolidated games table including assignment of players and referees to each game, in each of the league rounds. It is mentioned that in case of a league manager failure, the assignment message will also be published on Google Calendar 10 minutes before the start of the first round of the season. Therefore, games can take place even if there is a loss of communication with the league manager.
2. **Participation Confirmation** — Each participant confirms receipt of the message
3. **Transfer of Responsibility** — After everyone confirms, the referee takes responsibility for the game
4. **Game Management** — The referee manages the game until completion

**Completing Game Groups**

Since each game requires exactly three participants (one referee and two players), the number of registrants for a round must be divisible by 3.

When the number of registrants is not divisible by 3: The league manager will add up to two teams of its own (LGM Teams) to complete the round. These teams are agents of the league manager itself and participate in games as players or referees as needed.

General note: The league manager may add teams of its own to any season, even beyond completing the division by 3, for testing, balancing, or other considerations.

### 1.5.3 Game Group States

Table 5 presents the five possible states of a game group.

**Table 5: Game Group States**

| State | English Name | Description |
|---|---|---|
| Waiting for Assignment | assigned_and_waiting | Assignment message sent, waiting for responses |
| Referee Responsibility | referee_responsibility | Everyone confirmed, referee managing |
| Technical Malfunction | malfunction | Referee reported a malfunction |
| No Response | no_response | Referee did not respond by end of round |
| Game End | game_end | Game ended and results were sent |

## 1.6 Anonymous Team Name

This requirement is designed to maintain privacy in the public league tables.

Examples of valid team names (8 characters, lowercase letters and digits only):
- bibi0707, agent123, q21gteam
- teamplay, aiagent1, coderun8

Examples of prohibited team names:
- Too short (6 characters): team01
- Starts with a digit: 1234abcd
- Contains a special character: yossi_dn
- Contains uppercase letters: CohenLev
- Identifying name (not anonymous): yossidan

## 1.7 Force Majeure and Malfunctions

### 1.7.1 What is Force Majeure?

Force Majeure is an unexpected event that prevents the game from continuing normally. In such cases:

1. All game activity and results are cancelled
2. If the league manager approves force majeure, the game restarts
3. The renewed game takes place at a new date set by the league manager

### 1.7.2 Examples of Force Majeure

- General failure of Gmail servers
- Technical problem with the league system
- Military reserve service (with appropriate confirmation)
- Other emergency cases at the league manager's discretion

### 1.7.3 League Table Lockdown

> **Important Rule**
>
> After the season ends, the league table is locked. Players who play late (for example, due to reserve service) play against the locked table. Their position is calculated relative to the table, but other participants' positions do not change.

### 1.7.4 Backup System for Synchronization and Timing (Google Calendar Backup)

As a resilience mechanism against communication failures with the league manager, there is a parallel backup system based on a shared Google Calendar for all league participants.

**Calendar-based synchronization:**

The calendar includes pre-defined time windows for all league events.

Through an API connection to the calendar, agents can receive "time triggers" (Triggers) for key events such as season registration opening, season start, and round dates.

**Assignment table publication:** Under normal conditions, the league manager distributes the Assignment Table immediately upon registration closure. In case of a technical failure preventing the broadcast message, the league manager will also publish the assignment table (who plays against whom and at what time) in the shared calendar event description.

**Table 6: Scheduled Calendar Events**

| Event ID | Time Window | Description |
|---|---|---|
| REG_SEASON | 18:30–18:45 | Agent registration window for the season |
| ROUND_1 | 19:00–19:15 | First game round |
| ROUND_2 | 19:30–19:45 | Second game round |
| ROUND_3 | 20:00–20:15 | Third game round |
| ROUND_4 | 20:30–20:45 | Fourth game round |
| ROUND_5 | 21:00–21:15 | Fifth game round |
| ROUND_6 | 21:30–21:45 | Sixth game round |
| FINAL_RESULTS | 21:45–22:00 | Final ranking table publication |

> **Game Group Autonomy**
>
> Since each game is defined as a stand-alone unit, the referee and two players can conduct the game and implement the protocol in full as long as participant identities and the schedule are known to them. In case of league manager unavailability at the scheduled time, the calendar event will serve as a signal to activate the game instead of the original email message.

**Results reporting in backup mode:** In case of working in backup mode, referees must ensure that game results are transmitted to the league manager through alternative means that will be published (such as WhatsApp, alternative email addresses, or the model's messaging system), to ensure ranking updates later.

> **Priority Rule (Override Rules)**
>
> The calendar mechanism is a backup system only. As long as there is normal communication with the league manager, email messages sent from it take precedence over information appearing in the calendar. In case of contradiction (for example, a schedule change sent by email while the calendar has not yet been updated), always act according to the league manager's instructions.

### 1.7.5 Why Does the League Depend on the League Manager (LGM)?

The league manager serves as the central orchestration component (Layer 1) responsible for enforcing tournament rules and synchronizing global state among all distributed agents.

**Critical messages activated by the league manager:**

**Table 7: League Manager Critical Messages**

| Message | Role |
|---|---|
| LEAGUE_REGISTER_RESPONSE | Registration confirmation and unique agent ID assignment |
| BROADCAST_START_SEASON | Official opening signal for the game season |
| BROADCAST_ASSIGNMENT_TABLE | Distribution of the assignment table pairing referees with players |
| BROADCAST_KEEP_ALIVE | Heartbeat check to verify agent availability |
| BROADCAST_CRITICAL_* | System reset/pause/resume |
| BROADCAST_NEW_LEAGUE_ROUND | Start of a new game round |
| STANDINGS_UPDATE | Publication of the official and updated scoring table |
| REJECTION_NOTIFICATION | Enforcement of response deadlines and disqualification of late messages |

> **Individual Game Independence (Stand-alone Game)**
>
> Despite the dependency on the league manager for tournament management, the protocol was designed so that each game is "stateless" relative to the central server once it has started:
> - **Knowing the recipients** — Once the assignment table is known, the referee has the players' email addresses.
> - **Distributed protocol** — All game stages (from invitation to final guess) are conducted directly between the referee and players with CC to the log server, without the need for active league manager involvement at each stage.
> - **Source of truth** — The referee is the sole "source of truth" for game management, content selection, and score calculation.

> **Implementation Tip: Calendar backup support:**
>
> Your agent can implement a connection to the Google Calendar API to:
> 1. Receive event notifications (Event Notifications)
> 2. Read the event description to get the assignment table
> 3. Activate backup logic if no message was received from the league manager within a reasonable time
>
> Pseudo-code example:
> - If `calendar_event.start_time` has arrived AND no matching LGM message was received
>   - → Read the assignment table from the event description
>   - → Proactively activate the game

## 1.8 Extension Requests and Appeals

### 1.8.1 Request Hierarchy

If you encounter a problem and need an extension:

1. **First approach the referee** — The player contacts the game's referee with an extension request
2. **Referee's decision** — The referee may approve or reject the request
3. **Appeal to the league manager** — If the referee rejected, you can appeal to the league manager
4. **Final decision** — The league manager's decision is final

### 1.8.2 League Manager

The league manager (Administrator) in this course is Dr. Yoram Segal, or a representative appointed on his behalf. For contact details, see the course website or email yoram.segal@post.runi.ac.il.

## 1.9 Complete Game Flow

### 1.9.1 Six Phases

The game proceeds in six sequential phases:

**Phase Zero — Warmup:**
- The referee sends each player a short trivia question
- Goal: Verify that the agents are active and responsive
- Time window: 3 minutes (with option for an additional window)
- Warmup failure does not cancel the game

> **Parallel Phases**
>
> Phase Zero (warmup) and Phase One (paragraph selection) are performed in parallel and simultaneously. While players answer the warmup question, the referee is already selecting the paragraph and preparing the clues.

**Phase One — Paragraph and Clue Selection (Referee):**

1. The referee selects a booklet from the lecture materials
2. From it selects a specific paragraph
3. Invents a secret title (up to 5 words) — remains secret
4. Writes a general description (up to 15 words) — no words from the paragraph!
5. Selects an associative word and gives players only the topic/category

**Phase Two — Question Preparation (Players):**
- Each player receives the clue and the association topic
- Each player prepares a multiple-choice test with 20 questions
- Each question includes 4 possible answers
- Time window: 3 minutes

**Phase Three — Answering Questions (Referee):**
- The referee answers each question from the perspective of the paragraph
- Possible answers: A, B, C, D, or "not relevant"
- Time window: 3 minutes

**Phase Four — Final Guess (Players):**

Each player sends a guess containing four components:

1. **Exact opening sentence** — A quote of the sentence that opens the paragraph
2. **Sentence reasoning** (30–50 words) — Explanation of why the sentence fits
3. **Associative word + variations** — The word and its different forms
4. **Association reasoning** (20–30 words) — Connection of the word to the paragraph's topic

Time window: 3 minutes.

**Phase Five — Decision and Reporting (Referee):**
- The referee compares the guesses to the original paragraph
- Calculates a score for each player (see Scoring System)
- Returns detailed feedback to each player
- Reports results to the league manager
- Time window: 3 minutes

### 1.9.2 Important Notes for League Night

Here are some important notes from me to you:

**Take your time to prepare:** The game takes up to 15 minutes, and immediately after you have 15 minutes of "quiet time" to prepare. If something didn't go smoothly in the first game — no worries! This is exactly the time to fix, take a deep breath, and come prepared for the next match.

**Eyes on the target:** Don't waste energy on real-time appeals. The most important thing is not to accumulate technical losses due to dealing with what happened. Even if you felt something was unfair, keep performing in the next round. Continuing doesn't mean you've given up — our log server remembers everything, and we can check everything at leisure afterwards.

**Learning and experience are key:** The goal is to generate some action and interest, but don't forget that the game is just a means. Be sportsmanlike and focus on the essence — running your agents in the best way possible.

Remember, every game also needs a bit of luck. Even Napoleon said he preferred lucky generals over talented ones... So keep everything in proportion, enjoy the journey, and use this opportunity to improve and learn. Your position in the league is less important than the capabilities you're building here.

### 1.9.3 Game Flow Diagram

Figure 2 presents the complete game flow from an external perspective.

```
Referee ↔ Players

Phase 0: Warmup                          Referee ↔ Players
Phase 1: Choose Paragraph                Referee only
Phase 2: Prepare Questions               Players only
Phase 3: Answer Questions                Referee only
Phase 4: Final Guess                     Players only
Phase 5: Decision & Report              Referee → League Manager
```

*Figure 2: Game flow diagram in six phases*

### 1.9.4 Referee's Internal State Machine

While the diagram above shows the phases from the game's perspective, the referee internally manages a more detailed state machine with 12 states. This state machine allows the referee to precisely track game progress and handle every possible scenario.

**Table 8: Referee's Internal State Machine States**

| State | English Name | Description |
|---|---|---|
| Waiting | PENDING | Game assigned, waiting to start |
| Warmup | WARMUP | Warmup question sent, waiting for answers |
| Warmup Complete | WARMUP_COMPLETE | Both players answered the warmup |
| Round Start | ROUND_START | Clues sent, game begins |
| Questions | QUESTIONS | Waiting to receive 20 questions from each player |
| Questions Complete | QUESTIONS_COMPLETE | All questions received |
| Answers Sent | ANSWERS_SENT | Referee answered all questions |
| Guessing | GUESSING | Waiting for final guesses |
| Guesses Complete | GUESSING_COMPLETE | All guesses received |
| Scoring | SCORING | Calculating scores and preparing feedback |
| Complete | COMPLETE | Game ended successfully |
| Failed | FAILED | Game failed due to malfunction |

```
PENDING → WARMUP → WARMUP_COMPLETE → ROUND_START → QUESTIONS →
QUESTIONS_COMPLETE → ANSWERS_SENT → GUESSING → GUESSING_COMPLETE →
SCORING → COMPLETE
                                                    ↘ FAILED
```

*Figure 3: Referee's internal state machine — 12 states*

### 1.9.5 Referee Response Deadlines (Timeouts)

The referee manages a timeout system for each game phase. Table 9 details the exact response deadlines.

**Table 9: Referee Response Deadlines by Phase**

| Phase | Timeout | Retry | Consequences |
|---|---|---|---|
| Warmup | 300 seconds (5 min) | Yes — one additional attempt | After 2 failures: disqualification |
| Questions | 600 seconds (10 min) | No | Score 0 for the player who didn't send |
| Guess | 300 seconds (5 min) | No | Score 0 for the player who didn't send |
| Default | 900 seconds (15 min) | No | Context-dependent |

> **Warmup Retry Mechanism**
>
> If a player does not answer the warmup question within 5 minutes, the referee sends an additional warmup question and starts a new 5-minute timer. Only after two failures is the player disqualified from the game. This mechanism allows recovery from short network outages.

## 1.10 Scoring System

### 1.10.1 The Referee's Dual Scoring System

The referee calculates two types of scores for each player:

1. **Private Score** — A numerical score between 0 and 100, calculated from the four scoring components. This score is sent to the player personally and confidentially.
2. **League Score** — League points between 0 and 3, calculated from the private score. This score determines the position in the league table.

### 1.10.2 Private Score — Scoring Components (0–100)

The player's score in each round is calculated from four components:

**Table 10: Round Score Components**

| Component | Weight | Description |
|---|---|---|
| Opening sentence accuracy | 50% | Linguistic and conceptual match |
| Sentence reasoning | 20% | Intelligent use of answers |
| Associative word accuracy | 20% | Match to the word or its variations |
| Association reasoning | 10% | Intelligent connection to the word |

### 1.10.3 Converting Private Score to League Score

The referee converts the private score to a league score according to the following table:

**Table 11: Private Score to League Score Conversion**

| Private Score | League Score | Description |
|---|---|---|
| 85–100 | 3 | Excellent performance |
| 70–84 | 2 | Good performance |
| 50–69 | 1 | Average performance |
| 0–49 | 0 | Poor performance |

**Scoring Method**

Private score formula:

```
Private Score = 0.50 × S_sentence + 0.20 × S_sentence_reasoning + 0.20 × S_word + 0.10 × S_word_reasoning
```

Where each S component is a score between 0 and 100.

**Example:** A player who received S_sentence = 80, S_sentence_reasoning = 70, S_word = 100, S_word_reasoning = 60:

```
Private Score = 0.50 × 80 + 0.20 × 70 + 0.20 × 100 + 0.10 × 60 = 40 + 14 + 20 + 6 = 80
```

A private score of 80 is converted to a league score of 2.

### 1.10.4 League Points — Game Result

After calculating the round score, league points are distributed as follows:

**Table 12: League Points Distribution**

| Result | Player A | Player B | Referee | Note |
|---|---|---|---|---|
| Player A wins | 3 | 0 | 2 | Clear decision |
| Player B wins | 0 | 3 | 2 | Clear decision |
| Draw | 1 | 1 | 0 | No decision |
| Technical loss (2-2-0 rule) | 2 | 2 | 0 | Technical malfunction |
| Approved force majeure | — | — | — | Game cancelled |

#### 1.10.4.1 Post-Guess Reporting Process

After both players have sent their guesses, the referee performs the following actions:

**Report to each player separately:**

1. **Game result** — Who won, who lost, or draw
2. **League result** — League points received (3-0, 0-3, or 1-1)
3. **Personal score** — The player's numerical score (0–100)
4. **Score component breakdown** — The score for each of the four components (opening sentence, sentence reasoning, associative word, association reasoning)
5. **Verbal explanation** — Reasoning for the score given to each component

> **Personal Score Confidentiality**
>
> The personal score and full breakdown are confidential and personal. The referee sends each player only their own score.
>
> It is absolutely forbidden to transmit the personal score or component breakdown to the other player. The rival player sees only the game result (win/loss/draw) and the league points.

**Report to the League Manager:**

Simultaneously with sending results to the players, the referee sends the league manager a summary message including:
- Game result (who won)
- Personal score of each of the two players
- Full breakdown of score calculation for each player
- League points distributed

The league manager uses this information for updating the ranking table and for auditing purposes.

### 1.10.5 The 2-2-0 Rule for Technical Malfunctions

When a game fails due to a technical malfunction, the system applies automatic scoring:

> **2-2-0 Rule (Automatic Scoring):**
> - Player A receives 2 points
> - Player B receives 2 points
> - The referee receives 0 points

The rule applies in the following cases:
- **REFEREE_NO_SHOW** — Referee did not show up
- **REFEREE_ABANDONMENT** — Referee abandoned the game
- **PLAYER_NO_SHOW** — Player did not respond to the invitation (if both players didn't show up)
- **GAME_TIMEOUT** — The game exceeded time (30 minutes)

### 1.10.6 Impact of Force Majeure on Scoring

When the league manager approves a force majeure request:
- The game is cancelled without affecting the ranking
- No points are distributed to any side
- The game will be rescheduled for a future time window
- All data from the cancelled game is saved for auditing

> **Referee Strategy**
>
> The referee is rewarded only when there is a decisive result. A clue that is too easy or too hard will lead to a draw (and both players will win or lose together), and then the referee will not receive points. The optimal clue is challenging enough that one player succeeds and the other does not.

### 1.10.7 Final Course Score Calculation

The final project constitutes 40% of the overall course grade, divided as follows:

- **50%** — League position — A relative score between 60 and 100
- **50%** — Code quality review — Meeting standards

**Position score formula:**

```
Position Score = 60 + 40 × (N - Position) / (N - 1)
```

Where N is the number of league participants.

## 1.11 Composite Game ID (GameId)

The game ID is a Composite Key of 7 digits in the format SSRRGGG that uniquely identifies each game in the system. For the full ID structure and decomposition examples, see Appendix F, Table 184.

> **Implementation Tip: How to receive and parse GameId:**
>
> Every message from the server related to a game includes the `game_id` field in the envelope. Your agent needs to parse the ID as follows:
> - Season: first two digits (`game_id[0:2]`)
> - Round: digits 3-4 (`game_id[2:4]`)
> - Game: last three digits (`game_id[4:7]`)

## 1.12 The Five Clocks System

The system manages five different types of clocks. As a player or referee, it is important to understand which clocks affect your deadlines.

> **Google Calendar as External Time Source**
>
> In addition to the five internal clocks, there is an external time source — the shared Google Calendar. The calendar serves as a backup system for synchronization and timing (see Section 1). The agent can use calendar events as "time triggers" in case of communication failure with the league manager.

**Table 13: Clock System and State Machines**

| Component | Role | States | Response Deadlines |
|---|---|---|---|
| LeagueState | League lifecycle management | SETUP, REGISTRATION_OPEN, ACTIVE, COMPLETED | — |
| RefereeState | Referee state management | Includes PAUSED for referee suspension | — |
| RoundClock | Game rounds | PENDING, ACTIVE, COMPLETED | — |
| GameWindow | Game time windows | No states (dataclass for calculation) | — |
| MessageDeadlineClock | Message response deadline | Callback management | 60s/2min/5min/10min |

### 1.12.1 Clock States and Their Impact on the Agent

The system uses several state machines to manage the league lifecycle:

- **LeagueState:** SETUP → REGISTRATION_OPEN → ACTIVE → COMPLETED
  - SETUP — League in initial settings
  - REGISTRATION_OPEN — Registration window is open
  - ACTIVE — League is active, games can be played
  - COMPLETED — League has ended

- **RefereeState:** Contains PAUSED state
  - Allows suspension of an individual referee (not general season suspension)
  - PAUSED — Referee is temporarily suspended

- **RoundClock:** PENDING → ACTIVE → COMPLETED
  - PENDING — Round is planned but hasn't started
  - ACTIVE — Round is active
  - COMPLETED — Round has ended

- **GameWindow:** No state machine — dataclass for time calculations
  - Calculates whether the current time is within the game window
  - Supports `grace_minutes` parameter for grace period
  - Uses `is_active()`, `is_in_grace()` functions

- **MessageDeadlineClock:** Manages deadlines via callbacks
  - Tracks message response deadlines
  - Triggers callback when deadline expires
  - Does not use an explicit state machine

- **Calendar:** Read-only from Google Calendar
  - Infrastructure for reading calendar events exists
  - No state machine with OUTSIDE/ACTIVE/GRACE
  - 51-minute grace period is not implemented at the system level

**What is important for the agent?**

Your agent needs to primarily track:

1. **MessageDeadline** — Respond to every message on time
2. **LeagueState** — Know if the league is active
3. **GameWindow.is_active()** — Check if games can be played now
4. **Broadcast messages about state changes**

### 1.12.2 Response Deadline Categories

The MessageDeadline clock uses several deadline categories:

**Table 14: Response Deadlines by Message Type**

| Messages | Category | Deadline |
|---|---|---|
| BROADCAST_KEEP_ALIVE | broadcast_keep_alive | 30 seconds |
| CONNECTIVITY_TEST_CALL | connectivity | 60 seconds |
| BROADCAST_CRITICAL_RESET/PAUSE/CONTINUE | broadcast_critical | 2 minutes |
| Q21_WARMUP_CALL (with one retry) | warmup | 5 minutes |
| GAME_INVITATION, GAME_JOIN_ACK | game_flow | 5 minutes |
| Q21_GUESS_SUBMISSION — final guess submission | guess | 5 minutes |
| Q21_QUESTIONS_BATCH — 20 questions submission | questions | 10 minutes |
| LEAGUE_REGISTER_REQUEST, REFEREE_REGISTER_REQUEST | registration | 20 minutes |
| BROADCAST_ASSIGNMENT_TABLE, BROADCAST_NEW_LEAGUE_ROUND | assignment | 20 minutes |
| BROADCAST_FREE_TEXT | announcement | 1 hour |

**Referee Timeouts**

The referee manages the following timeouts for each game:
- Warmup: 300 seconds (5 minutes) with one retry
- Questions: 600 seconds (10 minutes) without retry
- Guess: 300 seconds (5 minutes) without retry

For additional details see Section 1.

> **Warning**
>
> Exceeding response deadlines may result in a technical loss. Make sure your agents are capable of meeting all deadlines!

## 1.13 League Dates

### 1.13.1 Two Seasons — Two Dates

Unlike regular sports leagues, the Q21G League takes place on only two dates — one evening per season. For the full schedule including league dates and warmup sessions, see Table 69 in Chapter 7.

> **No Additional Dates**
>
> These are the only dates for the league. If your agents are not active on the date, you will lose the season. There are no makeup games.

### 1.13.2 Pre-season Warmup Sessions

Before each season, three warmup sessions are held to test systems. For the full schedule see Table 69 in Chapter 7.

### 1.13.3 Grace Period

The system grants a grace period of 15 minutes at the end of league night:

- A game that started before 21:45 can continue until 22:00
- Round 6 starts at 21:30 and ends with results publication by 22:00

> **Implementation Tip — What the agent needs to do:**
>
> - Be active and listening before 18:30 on league night
> - Register immediately when the registration window opens (18:30–18:45)
> - Absorb the assignment table and be ready for the first round at 19:00
> - Respond immediately to messages throughout the entire evening

## 1.14 Mandatory Requirements

### 1.14.1 Technical Requirements

**Table 15: Mandatory Technical Requirements**

| Requirement | Details |
|---|---|
| Two agents | Must implement a player agent and a referee agent |
| Gmail API | Communication via email only (see limitations in Appendix E) |
| Protocol league.v2 | Full compliance with the message specification |
| CC to Log Server | Every game message must have CC |
| Response deadlines | Meet all defined deadlines |
| GitHub submission | Repository with organized code |

### 1.14.2 Conditions for Failure

- Three unjustified technical losses — "Failed" grade in the course
- Deleting emails — Immediate disqualification
- Non-compliance with the protocol — Failure in the project
- Code that does not meet standards — Significant grade reduction

### 1.14.3 Integrity Rules

1. **Transparency** — Maintain meticulous logs of every message
2. **Archive preservation** — It is forbidden to delete emails
3. **Compliance with instructions** — League manager messages are binding
4. **Organized submission** — Clean and documented code on GitHub

## 1.15 Glossary Table

Table 16 consolidates the key terms in the project.

**Table 16: Key Terms**

| Term | Definition |
|---|---|
| Q21G | Twenty-one questions game |
| Season | A full league period (6 rounds) |
| Round | League round (all games simultaneously) |
| Match | Single game (referee + two players) |
| Game Group | Game group — triplet of participants in a game |
| Referee | Referee — manages a single game |
| Player | Player — competes in a game |
| League Manager | League Manager — manages the tournament |
| Administrator | Administrator — Dr. Yoram Segal, handles appeals |
| Log Server | Log Server — receives CC for auditing |
| Protocol | Protocol league.v2 |
| Technical Loss | Technical loss due to non-response or malfunction |
| Pre-season Warmup | Pre-season warmup — testing sessions before the season |
| Phase 0 Warmup | Warmup phase — availability check at the start of a game |
| Force Majeure | Force majeure — unexpected event that cancels a game |
| Game Status | Game status — one of five possible states |

## 1.16 Summary

This chapter presented a general overview of the Q21G League. Key points:

- The league is based on a twenty-one questions game with a referee and two players
- Every student writes two agents (referee and player) and serves in both roles
- Communication is conducted via Gmail API with a defined protocol
- The scoring system encourages decisive results — a technical loss awards both players 2 points
- There are five types of response deadlines — exceeding them results in a technical loss
- The schedule includes three pre-season warmup sessions and a league night with 6 rounds
- The team name must be anonymous — using real names is prohibited
- In case of force majeure, you can contact the referee and appeal to the league manager

In the following chapters, we will delve deeper into the system architecture, communication protocol, and implementation guidelines.

---

*© Dr. Segal Yoram - All rights reserved*

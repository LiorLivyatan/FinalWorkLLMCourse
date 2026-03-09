# 7 Administration and Management

## 7.1 Introduction — The Three Registration Levels

The registration process for the final project takes place on three separate levels: the student level, the group level, and the AI agent level. Understanding the differences between these levels is essential for completing the registration process successfully.

> **IMPORTANT NOTE!**
>
> As part of project operations during the project, and especially the evening or even the day of the league round, the administrator may send specification updates or protocol updates in the form of PRD files in MARKDOWN format that you will need to update in your project. The message will be sent via the group WhatsApp and also through the model's messaging mechanism. The purpose of these messages will be to verify the flexibility of your architecture and code.

### 7.1.1 Chapter Objectives

By the end of this chapter, you will know:
- The complete registration process from the team selection stage to agent activation
- The team name selection rules and format requirements
- How to set up Gmail accounts for AI agents
- How to set up private code repositories on GitHub
- The email addresses of the league manager and log server
- How to register in the model and submit the PDF file

### 7.1.2 The Three Registration Levels

1. **Student Level** — Each student personally registers in the model via a PDF file
2. **Group Level** — The group fills out a shared electronic form (one group member is enough)
3. **Agent Level** — Two AI agents (player and referee) register automatically via code

Figure 17 presents the complete registration process.

```
Student:  Choose Name → Moodle PDF
Group:    Electronic Form → Create Gmail → Create GitHub  (One member performs for entire group)
Agent:    Email LGM → Email Log Server
```

*Figure 17: Registration process — from team selection to submission in the model*

## 7.2 Detailed Schedule

Table 69 presents the full schedule for the current academic year.

**Table 69: Schedule — League Seasons**

| Event | Date | Hours | Season |
|---|---|---|---|
| Season A Reception Hours 1 | Feb 3, 2026 | 18:30–21:00 | Season A |
| Season A Reception Hours 2 | Feb 10, 2026 | 18:30–21:00 | Season A |
| Season A Reception Hours 3 | Feb 16, 2026 | 18:30–21:00 | Season A |
| Season A League | Feb 17, 2026 | 18:30–22:00 | Season A |
| Season B Reception Hours 1 | Feb 24, 2026 | 18:30–21:00 | Season B |
| Season B Reception Hours 2 | Mar 3, 2026 | 18:30–21:00 | Season B |
| Season B Reception Hours 3 | Mar 16, 2026 | 18:30–21:00 | Season B |
| Season B League | Mar 17, 2026 | 18:30–22:00 | Season B |

> **Open Training Server**
>
> Instead of pre-season warmup windows, the windows will be much wider and we'll try to keep the league server open for you all the time, subject to load limits and technical constraints. The server holds two idle teams that will allow you to practice against a "dumb" player and "dumb" referee at times convenient for you.
>
> **Note:**
> - Game pace will be accelerated, not at the league pace
> - Training rounds will be in quarter-hour increments
> - You cannot join a warmup game mid-way — only at each quarter hour (for load management)

**Closing the Warmup Server Before League Day**

On the Friday before the Tuesday of the league itself, the warmup server will be closed for maintenance ahead of league day. Therefore, make sure to practice before the last Friday before the league date!

> **Schedule Planning**
>
> Write these dates in your personal calendar. Make sure you are available for every league round time window. Absence may result in automatic loss.

> **Continuous Agent Operation**
>
> In every season where you want your agents to participate, they need to run continuously. The agents need to scan their Gmail account and be ready to respond or send emails at any time. For example, during league Season A, the agent needs to be active for 3.5 hours continuously.

## 7.3 Setting Up a Team

### 7.3.1 Choosing Team Members

- **Standard composition** — A pair of students per team
- **Special cases** — With department head, secretariat, and instructor approval:
  - Single student in a team
  - Three students in a team (with additional assignments)

> **Recommendation**
>
> It is highly recommended to appoint one of the team members as administrator responsible for all bureaucratic processes. This will ensure all stages are completed in an orderly manner.

> **No Interference During League**
>
> No presence and/or active participation is allowed during the league season. Should a malfunction occur with an agent during the league round — the agent exits the game.
>
> During the pre-season period, a league manager and a "dumb" player and referee will be available for training.

### 7.3.2 Team Name Selection Rules

The team name must meet all of the following requirements:

1. **Length** — Exactly 8 characters
2. **Allowed characters** — Lowercase English letters (a-z) and digits (0-9) only
3. **Opening character** — Must start with a letter (not a digit)
4. **No spaces** — No spaces or special characters allowed
5. **Anonymity** — Students must not be identifiable from the name
6. **Uniqueness** — The name must be unique in the system

> **Anonymity Requirement**
>
> The team name must be anonymous. The name may not include your real names, last names, or any other identifying information. This requirement is designed to maintain privacy in the public league tables. For additional examples see Section 1 in Chapter 1.

**Table 70: Examples of Team Names**

| Type | Example | Explanation |
|---|---|---|
| Valid | bibi0707 | 8 characters, starts with letter |
| Valid | agent123 | 8 characters, letters and digits |
| Valid | q21gteam | 8 characters, letters only |
| Invalid | team01 | Only 6 characters |
| Invalid | 1234abcd | Starts with a digit |
| Invalid | yossi_dan | Contains special character |
| Invalid | CohenLev | Contains uppercase letters |

## 7.4 Setting Up AI Agent Accounts

### 7.4.1 Creating Gmail Accounts

Each team is required to open two new, free Gmail accounts:

1. **Player agent account** — For the player agent's communication
2. **Referee agent account** — For the referee agent's communication

> **Gmail Mandatory**
>
> Use of Gmail is mandatory. Do not use other email providers. All system communication is conducted via Gmail API. It is important to be familiar with API limitations before implementation — see Appendix E for a detailed analysis of sending limits and API quotas.

### 7.4.2 Email Address Format

The agents' email addresses must follow this format:

- Player agent: `groupname.player@gmail.com`
- Referee agent: `groupname.referee@gmail.com`

> **Note on Domain**
>
> Pay attention to the domain. Your actual email addresses should follow the standard gmail.com pattern. Do not use unconventional domains.

**Table 71: Email Address Format for Agents**

| Agent Type | Format | Example |
|---|---|---|
| Player | groupname.player@gmail.com | bibi0707.player@gmail.com |
| Referee | groupname.referee@gmail.com | bibi0707.referee@gmail.com |

### 7.4.3 Sending Email to League Manager

Immediately after opening the Gmail accounts, send a manual email to the league manager:

1. Send an email from the player account to the league manager's address
2. Send an email from the referee account to the league manager's address
3. Wait for a reply from the league manager for each of the messages

> **Implementation Tip**
>
> League manager address: bitalevi100@gmail.com
>
> Registration will be ready only after you receive a reply from the league manager for each of the emails you sent.

### 7.4.4 Programmatic League Registration

After manual registration, the agent performs automatic registration in JSON format:

```json
// LEAGUE_REGISTER_REQUEST
{
  "message_type": "LEAGUE_REGISTER_REQUEST",
  "payload": {
    "agent_name": "bibi0707.player",
    "agent_type": "PLAYER",
    "email": "bibi0707.player@gmail.com",
    "group_name": "bibi0707",
    "version": "1.0"
  },
  "message_id": "uuid-v4",
  "timestamp": "2026-02-01T10:00:00Z"
}
```

The server returns RESPONSE_LEAGUE_REGISTER with the user table:

```json
// RESPONSE_LEAGUE_REGISTER
{
  "message_type": "RESPONSE_LEAGUE_REGISTER",
  "payload": {
    "status": "REGISTERED",
    "agent_id": "P-bibi0707",
    "user_table": [
      {"agent_id": "P-bibi0707", "email": "bibi0707.player@..."},
      {"agent_id": "R-bibi0707", "email": "bibi0707.referee@..."},
      // ... more users
    ]
  },
  "correlation_id": "uuid-from-request"
}
```

### 7.4.5 Season Registration

After receiving `BROADCAST_SEASON_START`, the agent registers for the season:

```json
// SEASON_REGISTRATION_REQUEST
{
  "message_type": "SEASON_REGISTRATION_REQUEST",
  "payload": {
    "agent_id": "P-bibi0707",
    "season_id": "S01"
  },
  "message_id": "uuid-v4",
  "timestamp": "2026-02-01T12:00:00Z"
}
```

> **Agent Registration Window**
>
> Agent season registration is performed autonomously at the start of league night:
> - Registration window: 18:30–18:45 (15 minutes)
> - Trigger: BROADCAST_START_SEASON message or REG_SEASON calendar event in the shared calendar
> - Result: Agent automatically registers for the current season
>
> After 18:45, the registration window closes and it is no longer possible to register for the current season.

**Distinction Between Registration Types**

- **Group/User Registration (Manual Registration):** Performed once by students via an electronic form and PDF in the model.
- **Agent Season Registration (Autonomous Registration):** Performed autonomously by agents at the start of each league night.

### 7.4.6 Spam Prevention

To prevent spam issues from both directions, perform the following actions:

1. In each agent's Gmail account, go to the Contacts list
2. Add the league manager's address: `bitalevi100@gmail.com`
3. Add the log server's address: `beit.halevi.700@gmail.com`
4. Save the contacts

> **Very Important**
>
> Without adding the league manager to the contacts list, the system's broadcast messages may be blocked as spam. Additionally, messages you send may be considered spam by Google. For additional prevention strategies and implementation recommendations, see Appendix E, Section 10.

### 7.4.7 Mandatory Spam Folder Scanning

> **Protocol Specification**
>
> In addition to adding contacts, every agent (player and referee) must scan the spam folder during the initial stages of communication. This requirement also applies to the league manager.

**When to Scan?**

- Immediately after sending the manual registration email — check if the reply arrived in spam
- At the start of each game — before the warmup phase
- Every time an expected response is not received on time

For full details on the spam scanning requirement and implementation recommendations, see Section 4 in Chapter 4.

## 7.5 Setting Up Code Repositories on GitHub

### 7.5.1 Creating a Private Repository

Unlike homework assignments, final project code repositories must be private:

1. Create a private repository for the player agent
2. Create a private repository for the referee agent
3. In the initial stage, creating just a README file is sufficient

> **Code Privacy**
>
> The repository must be Private and not Public. This is because your code is part of the submission and should not be accessible to other teams.

### 7.5.2 Adding a Collaborator

For the league manager to be able to review the code and give a grade, add them as a collaborator:

> **Implementation Tip — Steps to Add a Collaborator on GitHub:**
>
> 1. Go to the repository on GitHub
> 2. Click Settings (top right corner)
> 3. In the side menu, select Collaborators under Access
> 4. Click Add people
> 5. Enter the address: bitalevi100@gmail.com
> 6. Send the invitation
> 7. The league manager will accept the invitation
>
> Repeat the process for both repositories (player and referee).

## 7.6 Log Server Registration

In addition to sending an email to the league manager, send an email to the log server as well:

1. Send a manual email from the player account to the log server
2. Send a manual email from the referee account to the log server
3. Add the log server to the contacts list in both accounts

> **Implementation Tip**
>
> Log server address: beit.halevi.700@gmail.com
>
> The log server receives a copy (CC) of all messages during games. This enables documentation, auditing, and dispute resolution when needed.

## 7.7 Model Registration

### 7.7.1 Registration Principles

Here are the registration guidelines for the final project in the AI Agents Orchestration course:

1. Every student, personally, must register through the final project assignment in the model
2. Every student is a member of a team
3. Every student registers to their team by submitting a PDF file containing all required fields

### 7.7.2 Filling Out the Electronic Form for Agent Registration

After completing all the previous steps, fill out the electronic form to register the team's AI agents in the league:

1. Go to the model and open the final project assignment
2. Find the link to the AI agent registration form for the league (link appears in the model assignment)
3. Fill in all required fields (team name, agent email addresses, repository links)
4. Confirm you sent emails to the league manager and log server
5. Submit the form

> **One Form per Team**
>
> One team member filling out the electronic form to register the AI agents for the league is sufficient. The form represents the registration of the entire team's agents.

### 7.7.3 Personal PDF File Submission

Unlike the electronic form, each student must register in the model personally by submitting a PDF file.

**Required fields in the PDF file:**

1. **Team name** — The 8-character team name you chose
2. **Team member details** — For each member specify:
   - (a) First name
   - (b) Last name
   - (c) ID number
3. **Referee Agent details:**
   - (a) Agent email address (in format groupname.referee@gmail.com)
   - (b) Link to the agent's GitHub repository
4. **Player Agent details:**
   - (a) Agent email address (in format groupname.player@gmail.com)
   - (b) Link to the agent's GitHub repository

**Table 72: PDF Registration File Fields**

| Category | Required Fields |
|---|---|
| Team details | Team name (8 characters) |
| Each member details | First name, last name, ID number |
| Referee agent | Email address, GitHub link |
| Player agent | Email address, GitHub link |

> **Mandatory Personal Submission**
>
> Submission in the model is personal, not group-based. Every student must submit separately in order to receive a grade. A student who does not submit will not be able to receive a grade for the final project.

## 7.8 Complete Email Address Guide

Table 73 consolidates all email addresses appearing in this book, including system addresses, agent address patterns, and contact addresses.

**Table 73: Addresses by Role**

| Role | Address | When to Use |
|---|---|---|
| Course Instructor | yoram.segal@post.runi.ac.il | Academic questions, appeals |
| League Manager (primary) | beit.halevi.100@gmail.com | Registration, games, scores |
| League Manager (backup) | beit.halevi.600@gmail.com | When primary server fails |
| Log Server | beit.halevi.700@gmail.com | CC in every message |
| Player Agent | groupname.player@gmail.com | Game communication |
| Referee Agent | groupname.referee@gmail.com | Game communication |

> **Important Clarification**
>
> - **Fixed addresses:** beit.halevi.100@gmail.com and beit.halevi.700@gmail.com are the actual addresses to use.
> - **Backup server:** The address beit.halevi.600@gmail.com serves as a backup server for the league manager. In case of a primary server failure (100), the system switches to the backup server (600).
> - **Agent names:** Agent names are derived from the team name — groupname.player and groupname.referee (for example: MyGroup.player).
> - **Address patterns:** Replace `groupname` with your team name (for example: bibi0707.player@gmail.com).
> - **Generic addresses in code:** If you use symbolic addresses like league.manager@gmail.com or log.server@gmail.com in code or configuration files, replace them with the actual addresses from the table.
> - **Contacting the instructor:** For academic and administrative questions, contact Dr. Yoram Segal at yoram.segal@post.runi.ac.il.

**Configuration File and Server Switching**

The agent code (player and referee) must include a configuration file (config.json or .env) with the league manager address setting. Recommended structure:

```json
{
  "lgm_server": "beit.halevi.100@gmail.com",
  "lgm_backup": "beit.halevi.600@gmail.com"
}
```

In case of failure, changing just one line in the configuration file is enough to switch to the backup server.

**Preventing Spam Marking**

Add both league manager addresses to the Contacts list (Google Contacts) in the agent's Gmail account:

- beit.halevi.100@gmail.com
- beit.halevi.600@gmail.com

This action prevents Gmail from marking system messages as spam and ensures proper receipt of all messages.

## 7.9 Student Checklist

Below is the complete checklist for the registration process. Check each step after completing it:

- [ ] **Team selection** — Found partner(s) for the team
- [ ] **Name selection** — Chose an 8-character, anonymous, unique team name
- [ ] **Player account** — Opened a new Gmail account for the player agent in format groupname.player@gmail.com
- [ ] **Referee account** — Opened a new Gmail account for the referee agent in format groupname.referee@gmail.com
- [ ] **Email to manager (player)** — Sent email to league manager from the player account
- [ ] **Email to manager (referee)** — Sent email to league manager from the referee account
- [ ] **Reply from manager** — Received reply from league manager for both emails
- [ ] **Contacts** — Added league manager and log server to contacts in both accounts
- [ ] **Player repository** — Created a private empty repository for the player agent, with at least a README file
- [ ] **Referee repository** — Created a private empty repository for the referee agent, with at least a README file
- [ ] **Collaborator** — Added league manager as collaborator to both repositories
- [ ] **Email to log (player)** — Sent email to log server from the player account
- [ ] **Email to log (referee)** — Sent email to log server from the referee account
- [ ] **Spam scan** — Checked spam folder in both accounts to verify no messages arrived there
- [ ] **Electronic form** — Filled (or team member filled) the electronic form to register 2 AI agents for the Q21G league
- [ ] **Calendar entry** — Entered time windows for agent training and league round dates in personal calendar
- [ ] **Model submission** — Submitted the personal PDF file in the model including team member details and AI agents. **Mandatory: each student registers separately in the model**

> **Registration Completion**
>
> After completing all steps on the checklist, you are ready to start developing the agents. Remember that when the league opens, agents register automatically via the code you write — everything you did here is one-time manual preparation.

---

*© Dr. Segal Yoram - All rights reserved*

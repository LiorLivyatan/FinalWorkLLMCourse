# Appendix E: Email Traffic Volume Analysis and Gmail API Limitations

## E.1 Introduction

The Q21G League is based on communication via Gmail API, so understanding service limitations and adapting the architecture to them is critical to the project's success. This appendix presents a comprehensive analysis of the expected traffic volume during a full league season, alongside an in-depth review of Gmail API limitations and their implications for system design.

### E.1.1 Importance of the Topic

Designing an email-based system requires addressing three dimensions:

1. **Quota Limits** — The number of messages allowed per day
2. **Rate Limiting** — The number of requests per minute
3. **Spam Policy** — Risk of blocking due to unusual sending patterns

This analysis is based on official Google documentation and detailed calculations of league traffic in various scenarios.

## E.2 Design Assumptions

Table 156 presents the league parameters used for traffic volume calculation.

**Table 156: League Parameters for Traffic Calculation**

| Parameter | Value |
|---|---|
| Number of teams in league | 30 |
| Teams per single game | 3 (one referee + two players) |
| Games per round | 10 |
| Rounds per season | 6 |
| Total games per season | 60 |
| Questions per game (Q21) | 21 |

> **Key Assumption**
>
> Broadcast messages are sent as a single message with all participants in the CC field, not as separate messages. This assumption significantly reduces the sending load on the league manager.

## E.3 League Manager Traffic Analysis

### E.3.1 Season Lifecycle Messages

Table 157 details the broadcast messages during a full season.

**Table 157: Season Lifecycle Messages — Full Season**

| Message Type | Quantity per Season |
|---|---|
| Registration opening | 1 |
| Registration closing | 1 |
| Season start | 1 |
| Season end + final scoring table | 1 |
| **Total** | **4** |

### E.3.2 Round Lifecycle Messages

**Table 158: Round Messages — Full Season**

| Message Type | Per Round | Rounds | Total |
|---|---|---|---|
| Round start + assignments | 1 | 6 | 6 |
| Round end + scoring table | 1 | 6 | 6 |
| **Total** | | | **12** |

### E.3.3 Game-Level Messages

**Table 159: Messages to Referees — All Games**

| Message Type | Per Game | Games | Total |
|---|---|---|---|
| Game assignment confirmation | 1 | 60 | 60 |
| Results receipt confirmation | 1 | 60 | 60 |
| **Total** | | | **120** |

### E.3.4 League Manager Traffic Summary

**Table 160: League Manager Messages Summary**

| Category | Quantity |
|---|---|
| Season broadcasts | 4 |
| Round broadcasts | 12 |
| Messages to referees | 120 |
| **Total sent** | **136** |

## E.4 Participant Traffic Analysis

### E.4.1 Registration Messages

**Table 161: Registration Messages**

| Message Type | Senders | Total |
|---|---|---|
| Registration confirmation | 30 | 30 |

### E.4.2 Game Result Reports

**Table 162: Result Reports from Referees**

| Message Type | Per Game | Games | Total |
|---|---|---|---|
| Game result report | 1 | 60 | 60 |

### E.4.3 Traffic to League Manager Summary

**Table 163: Messages Received by League Manager**

| Category | Quantity |
|---|---|
| Registration confirmations | 30 |
| Result reports | 60 |
| **Total received** | **90** |

## E.5 In-Game Traffic Analysis

This section analyzes the internal traffic between the referee and players during the games themselves.

### E.5.1 Role Distribution Over the Season

**Table 164: Role Distribution per Single Participant**

| Role | Games per Season |
|---|---|
| Referee | 2 |
| Player | 4 |
| **Total** | **6** |

### E.5.2 Referee Messages — Single Game

**Table 165: Referee Messages for a Single Game**

| Message Type | Recipient | Quantity |
|---|---|---|
| Assignment confirmation | League Manager | 1 |
| Result report | League Manager | 1 |
| **Subtotal to Manager** | | **2** |
| Game invitation | Player A | 1 |
| Questions (Q21) | Player A | 21 |
| Result message | Player A | 1 |
| **Subtotal to Player A** | | **23** |
| Game invitation | Player B | 1 |
| Questions (Q21) | Player B | 21 |
| Result message | Player B | 1 |
| **Subtotal to Player B** | | **23** |
| **Total per Game** | | **48** |

### E.5.3 Player Messages — Single Game

**Table 166: Player Messages for a Single Game**

| Message Type | Recipient | Quantity |
|---|---|---|
| Assignment confirmation | League Manager | 1 |
| **Subtotal to Manager** | | **1** |
| Join confirmation | Referee | 1 |
| Answers (Q21) | Referee | 21 |
| **Subtotal to Referee** | | **22** |
| **Total per Game** | | **23** |

### E.5.4 Summary of Traffic per Single Participant per Season

**Table 167: Single Participant Messages Summary**

| Role | Games | Messages per Game | Total per Season |
|---|---|---|---|
| As referee | 2 | 48 | 96 |
| As player | 4 | 23 | 92 |
| **Total** | **6** | | **188** |

### E.5.5 Validation — All Participants

**Table 168: Total Traffic Validation**

| Metric | Per Participant | Participants | Total |
|---|---|---|---|
| Messages sent | 188 | 30 | 5,640 |

## E.6 Total Traffic Summary

**Table 169: Total Traffic Summary — Full Season**

| Direction | Message Count | Percentage |
|---|---|---|
| League Manager → Participants | 136 | 2.4% |
| Participants → League Manager | 90 | 1.6% |
| In-game traffic | 5,640 | 96.0% |
| **Total** | **5,866** | **100%** |

> **Key Insight**
>
> 96% of traffic is in-game — between referees and players. The league manager handles only 226 messages throughout the entire season, while each participant sends an average of 188 messages.

## E.7 Broadcast Consolidation Savings

The Broadcast Consolidation component in Gatekeeper consolidates broadcast messages to multiple recipients into a single message with all recipients in the TO field. This saving is critical for meeting Gmail API limits.

### E.7.1 Saving Calculation

**Table 170: Before and After Broadcast Consolidation Comparison**

| Metric | Without Consolidation | With Consolidation |
|---|---|---|
| BROADCAST_KEEP_ALIVE message | 30 calls | 1 call |
| BROADCAST_ROUND_START message | 30 calls | 1 call |
| Season broadcasts (16 types) | 480 calls | 16 calls |
| Savings per single broadcast | — | **97%** |

### E.7.2 Impact on Daily Quota

**Table 171: Daily Quota Consumption — Peak Day**

| Action | Without Consolidation | With Consolidation |
|---|---|---|
| Keep Alive broadcasts (every 30 min) | 1,440 | 48 |
| Round broadcasts (start + end) | 60 | 2 |
| Messages to referees | 10 | 10 |
| **Total API calls** | **1,510** | **60** |
| Savings percentage | — | **96%** |

> **Importance of Consolidation**
>
> Without broadcast consolidation, the system would exceed Gmail's 500 daily message limit within just 8 hours. With consolidation, the system consumes only 60 calls on a peak day — 15% of the operational quota (400).

## E.8 Gmail API Limitations

### E.8.1 Limits by Account Type

Table 172 summarizes the sending limits by Gmail account type.

**Table 172: Gmail Sending Limits by Account Type**

| Account Type | Daily Limit | Notes |
|---|---|---|
| Free Gmail | 500 messages | 100 via automated SMTP |
| Google Workspace | 2,000 messages | Up to 10,000 recipients |
| SMTP Relay (business) | 10,000 messages | Requires special configuration |

> **Operational Limit**
>
> Although Gmail's limit is 500 messages per day, the Gatekeeper system sets an operational limit of 400 messages per day (80%) to leave a safety buffer. When 400 is reached, the system switches to "reduced" mode and pauses non-critical broadcasts.

### E.8.2 Rate Limiting

**Table 173: Gmail API Rate Limits**

| Parameter | Value |
|---|---|
| Requests per second (per user) | 250 quota units |
| Requests per second (per project) | 25,000 quota units |
| Recommended Batch size | Up to 50 requests |
| Response Timeout | 429 Too Many Requests |

### E.8.3 Quota Units for Common Operations

**Table 174: Quota Unit Cost per Operation**

| Operation | Quota Units |
|---|---|
| messages.send | 100 |
| messages.get | 5 |
| messages.list | 5 |
| messages.modify | 5 |
| labels.list | 1 |

> **Implementation Tip**
>
> - Use Exponential Backoff when receiving a 429 error
> - Limit message sending to 20 per hour with a free account
> - Maintain a gap of at least 3 seconds between messages
> - Avoid sending more than 50 requests in a single Batch

## E.9 Compliance Analysis

### E.9.1 League Manager Scenario

**Table 175: Limits Analysis — League Manager**

| Metric | Value | Limit |
|---|---|---|
| Messages per season | 136 | — |
| Messages on peak day (round) | ~30 | 2,000/500 |
| Safety buffer | > 90% | OK |

### E.9.2 Single Participant Scenario

**Table 176: Limits Analysis — Single Participant**

| Metric | Value | Limit |
|---|---|---|
| Messages per season | 188 | — |
| Messages per game (as referee) | 48 | 500/day |
| Messages per game (as player) | 23 | 500/day |
| Safety buffer | > 80% | OK |

> **Conclusion**
>
> With a standard free Gmail account (500 messages per day), a participant can play up to 10 games per day as a referee or 21 games per day as a player without exceeding the quota. In practice, the league allows at most one game per day, so the system operates within safe boundaries.

## E.10 Spam and Blocking Risks

### E.10.1 Risk Factors

1. **Automated sending patterns** — Google identifies automated sending and may restrict the account
2. **New accounts** — Accounts less than 30 days old are limited to 100 messages per day
3. **Sending to unfamiliar recipients** — May trigger spam filtering
4. **Repeated content** — Identical messages to different recipients are flagged as potential spam

### E.10.2 Mitigation Strategies

**Table 177: Strategies for Preventing Blocking**

| Risk | Mitigation Strategy |
|---|---|
| New account | Open accounts 30+ days before the league starts |
| Sending patterns | Add random delays between messages |
| Unfamiliar recipients | Add to contacts before first send |
| Repeated content | Use templates with slight variations |

## E.11 Architectural Recommendations

> **Implementation Tip — Recommendations for Resilient System Design:**
>
> 1. **Message Queue** — Use an internal queue with controlled sending rate
> 2. **Quota monitoring** — Track daily quota consumption and stop sending when approaching the limit
> 3. **Graceful Degradation** — In case of blocking, switch to "read-only" mode and alert the operator
> 4. **Detailed logs** — Document every API request for problem analysis
> 5. **Backup account** — Consider preparing an alternative account for emergencies

## E.12 Summary

This appendix presented a comprehensive analysis of email traffic in the Q21G League:

- **Total volume** — ~5,866 messages in a full season with 30 teams
- **Traffic breakdown** — 96% in-game, 4% administrative
- **Broadcast consolidation** — 96% savings in API calls on peak day
- **Operational limit** — 400 messages per day (80% of quota) for safety buffer
- **Compliance** — The system operates within safe boundaries with free Gmail accounts
- **Main risks** — New accounts and automated sending patterns
- **Recommendations** — Use message queue, quota monitoring, and delays between messages

Understanding these limitations is essential for designing AI agents that will operate reliably throughout the entire league season without interruptions.

## E.13 Sources

1. Gmail API Usage Limits — Google Developers
   https://developers.google.com/workspace/gmail/api/reference/quota
2. Gmail Sending Limits — Google Workspace Admin Help
   https://support.google.com/a/answer/166852
3. Gmail API Error Handling — Google Developers
   https://developers.google.com/workspace/gmail/api/guides/handle-errors

---

*© Dr. Segal Yoram - All rights reserved*

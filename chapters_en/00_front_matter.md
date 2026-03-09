# Q21G League -- Final Project

**Q21G League - Final Project**

A comprehensive guide to the league system and communication protocol

**Dr. Yoram Segal**

All rights reserved - (c) Dr. Yoram Segal

January 2026

Version 4.00

In case of a contradiction between this booklet and the model -- the model prevails.

---

## Abstract

### Q21G League -- Final Project

This booklet serves as a comprehensive guide to the final project of the course "Artificial Intelligence Agents." The project demonstrates multi-agent communication through a competitive game league based on the game "Twenty-One Questions" (Q21G).

The guide presents the three-layer architecture of the system -- league, judging, and game rules -- and the league.v2 communication protocol that enables autonomous AI agents to communicate via Gmail API. The book includes detailed guidelines for implementing a player agent and a referee agent, including code examples, architecture diagrams, and database schemas.

---

## Personal Note

I am addressing you, the future generation of technology leaders, those who are about to harness the power of AI agents and transform them into "force multipliers" in the modern job market. We are not here just to learn theory; we are here to build empires of distributed intelligence.

This project is your entry ticket to a league of the greats. My goal is to bring each and every one of you to a capability multiplier of 16x. You are the spark I saw in my eyes throughout the semester, and I believe with all my heart that this group will produce the next "unicorn." To ensure your victory, we must operate according to the rules of iron. These are not just technical requirements, but the foundation for excellence and your integrity.

This project was built with care to provide you with an experience that will leverage you to the level of a diploma of recognition. These requirements were designed for you -- to protect your hard work and ensure your credentials. Remember always: at the heart of it stands the positive and optimistic approach to your project. I recognize your skills, and I know you are capable of leading. I have seen the knowledge you have encountered, and I know you are capable of leading.

In the spirit of victory, success awaits you just around the corner!

Go and show the world what a well-managed AI agent can do!

Yoram

---

## Table of Contents

**Abstract** ..... iv

**Personal Note** ..... iv

### 1 General Overview of the Q21G League ..... 1
- 1.1 Introduction to the Final Project ..... 1
- 1.2 What is the Q21G League? ..... 1
- 1.3 Roles in the System ..... 2
- 1.4 Season Structure ..... 4
- 1.5 Game Group ..... 7
- 1.6 Anonymous Group Name ..... 8
- 1.7 Force Majeure and Failures ..... 9
- 1.8 Extension Requests and Appeals ..... 12
- 1.9 Full Game Flow ..... 12
- 1.10 Scoring System ..... 16
- 1.11 Composite Game Identifier (GameId) ..... 19
- 1.12 Five-Clock System ..... 20
- 1.13 League Dates ..... 22
- 1.14 Mandatory Requirements ..... 23
- 1.15 Glossary ..... 25
- 1.16 Summary ..... 25

### 2 Architectural Principles for the Agent ..... 27
- 2.1 Introduction ..... 27
- 2.2 The Orchestrator Pattern (Entry Gate) ..... 27
- 2.3 Agent State Machine ..... 28
- 2.4 The GateKeeper Pattern (Email Protection) ..... 36
- 2.5 Token Bucket Rate Limiter ..... 38
- 2.6 Periodic Handler (Timing System) ..... 40
- 2.7 Message Router ..... 41
- 2.8 Message Consolidation via CC ..... 43
- 2.9 Watchdog Mechanism ..... 45
- 2.10 Deadline Tracker Pattern ..... 46
- 2.11 Correlation Matching Pattern ..... 49
- 2.12 Broadcast Handling ..... 50
- 2.13 Time Zone Policies ..... 55
- 2.14 Configuration Management ..... 57
- 2.15 Summary ..... 58

### 3 League System -- Multi-Agent Architecture ..... 59
- 3.1 Introduction ..... 59
- 3.2 Three-Layer Architecture ..... 59
- 3.3 Agent Types ..... 61
- 3.4 State Machines ..... 62
- 3.5 Game Group Allocation Table ..... 66
- 3.6 Identity Model ..... 68
- 3.7 Detailed Scoring System ..... 69
- 3.8 Error Handling ..... 70
- 3.9 Summary ..... 72

### 4 Inter-Agent Communication Protocol ..... 73
- 4.1 Introduction ..... 73
- 4.2 Transport Layer -- Gmail API ..... 73
- 4.3 Email Subject Format ..... 74
- 4.4 Envelope Structure -- Shared Header ..... 76
- 4.5 Context Structure (MessageContext) ..... 78
- 4.6 Message Types ..... 79
- 4.7 CC Obligation to the Log Server ..... 80
- 4.8 Spam Inbox Scanning ..... 81
- 4.9 Inter-Group Communication ..... 82
- 4.10 Extension and Failure Messages ..... 82
- 4.11 Deadline Management ..... 84
- 4.12 Handling Late Responses ..... 84
- 4.13 Message Examples ..... 86
- 4.14 Summary ..... 89

### 5 Game Mechanisms ..... 91
- 5.1 Introduction ..... 91
- 5.2 Assignment Table ..... 92
- 5.3 Composite Game Identifier (SSRRGGG) ..... 95
- 5.4 League Dates and Time Windows ..... 95
- 5.5 Technical Failure Handling ..... 96
- 5.6 Force Majeure Protocol ..... 99
- 5.7 Extension Request Protocol ..... 102
- 5.8 Season Life Cycle ..... 104
- 5.9 Game Round Life Cycle ..... 105
- 5.10 Summary ..... 107

### 6 Final Project Implementation ..... 109
- 6.1 Introduction: From Theory to Practice ..... 109
- 6.2 Development Environment ..... 109
- 6.3 Player Agent Implementation ..... 111
- 6.4 Referee Agent Implementation ..... 113
- 6.5 Configuration Files ..... 118
- 6.6 Tests ..... 121
- 6.7 Message Tracking Table Implementation ..... 123
- 6.8 Broadcast Handler Implementation ..... 126
- 6.9 Extension Request Implementation ..... 127
- 6.10 Running the League ..... 128
- 6.11 Summary ..... 129

### 7 Management and Administration ..... 131
- 7.1 Introduction -- Three Levels of Registration ..... 131
- 7.2 Detailed Timeline ..... 132
- 7.3 Group Setup ..... 133
- 7.4 Setting Up AI Agent Accounts ..... 135
- 7.5 Setting Up Code Repositories on GitHub ..... 138
- 7.6 Registration to the Log Server ..... 139
- 7.7 Registration in the Model ..... 139
- 7.8 Complete Email Address Guide ..... 142
- 7.9 Student Checklist ..... 143

### 8 Game Management by the Referee ..... 145
- 8.1 Introduction ..... 145
- 8.2 Season Registration and Assignment Table ..... 145
- 8.3 Protocol Message Format ..... 148
- 8.4 Full Game Message Flow ..... 149
- 8.5 Receiving the Game Assignment ..... 151
- 8.6 Warm-Up Phase ..... 152
- 8.7 Round Start Phase ..... 154
- 8.8 Questions and Answers Phase ..... 155
- 8.9 Final Guess Phase ..... 157
- 8.10 Scoring and Calculation Phase ..... 157
- 8.11 Results Report to the League Manager ..... 159
- 8.12 Failure and Deadline Handling ..... 161
- 8.13 Handling Broadcast Messages ..... 162
- 8.14 Game Phases in the State Machine ..... 164
- 8.15 Summary ..... 164

### Appendix A: Setting Up Permissions to Connect to a Gmail Account via Code ..... 167
- A.1 Introduction ..... 167
- A.2 Step 1: Start the Project ..... 167
- A.3 Step 2: Setting Up OAuth Consent Screen ..... 168
- A.4 Step 3: Creating Desktop Credentials ..... 168
- A.5 Step 4: Adding Test Users ..... 169
- A.6 Summary of Steps ..... 170

### Appendix B: Protocol Message Repository ..... 171
- B.1 Introduction ..... 171
- B.2 Response Deadline Categories ..... 171
- B.3 Full Protocol Messages Table ..... 171
- B.4 Summary ..... 181

### 9 Appendix C: System Data Model ..... 183
- 9.1 General Overview ..... 183
- 9.2 Schema Diagram ..... 185
- 9.3 System Core Tables ..... 185
- 9.4 Registration and Group Tables ..... 190
- 9.5 Season Management Tables ..... 190
- 9.6 League Management Tables ..... 193
- 9.7 Game Group Allocation Table ..... 197
- 9.8 Gatekeeper Tables ..... 199
- 9.9 Game State Tables ..... 201
- 9.10 Year Schedule Tables ..... 203
- 9.11 Dynamic User Table ..... 204
- 9.12 Relationships Between Tables ..... 204
- 9.13 Schema Architecture ..... 205
- 9.14 Index Summary ..... 206
- 9.15 SQL Query Guide ..... 208
- 9.16 Schema Statistics ..... 209
- 9.17 Diagram Generation Code ..... 209
- 9.18 Summary ..... 210

### Appendix D: Player Agent Database Schema ..... 211
- D.1 Introduction ..... 211
- D.2 Schema Diagram ..... 211
- D.3 Player and State Tables ..... 213
- D.4 Game Core Tables ..... 215
- D.5 Game Data Tables ..... 219
- D.6 Message and File Tables ..... 221
- D.7 Broadcast Tables ..... 223
- D.8 Season and League Tables ..... 224
- D.9 System Tables ..... 226
- D.10 Foreign Key Relationships ..... 227
- D.11 Design Patterns ..... 228
- D.12 Schema Statistics ..... 229
- D.13 Table Summary by Group ..... 229

### Appendix E: Email Transport Volume Analysis and Gmail API Limitations ..... 231
- E.1 Introduction ..... 231
- E.2 Design Assumptions ..... 231
- E.3 League Manager Transport Analysis ..... 232
- E.4 Participant Transport Analysis ..... 233
- E.5 Intra-Game Transport Analysis ..... 234
- E.6 Overall Transport Summary ..... 235
- E.7 Broadcast Consolidation Savings ..... 236
- E.8 Gmail API Limitations ..... 237
- E.9 Adaptation Analysis for Limitations ..... 238
- E.10 Spam and Blocking Risks ..... 238
- E.11 Architectural Recommendations ..... 239
- E.21 Summary ..... 239
- E.31 Sources ..... 240

### 10 Identifying Conventions ..... 241
- 10.1 Introduction ..... 241
- 10.2 Group and User Identifiers ..... 241
- 10.3 Player and Referee Identifiers ..... 241
- 10.4 Season and Round Identifiers ..... 242
- 10.5 Composite Game Identifier (SSRRGGG) ..... 243
- 10.6 Broadcast and Message Identifiers ..... 244
- 10.7 Centralized Reference Table ..... 246
- 10.8 Regular Expressions for Validation ..... 246

### 11 System Configuration ..... 249
- 11.1 Introduction ..... 249
- 11.2 Gatekeeper Configuration ..... 249
- 11.3 Clock Configuration ..... 251
- 11.4 Timeout Configuration ..... 253
- 11.5 Log Server Configuration ..... 253
- 11.6 Default Values Table ..... 254

### Appendix H: Architectural Principles of the League Manager ..... 255
- H.1 Introduction ..... 255
- H.2 Separation of Static and Dynamic Data ..... 255
- H.3 League Manager Gatekeeper Pattern ..... 256
- H.4 League Manager Clock System ..... 257
- H.5 Broadcast Consolidation ..... 257
- H.6 Context Inheritance ..... 258
- H.7 State Machines ..... 259
- H.8 Summary ..... 259

### Appendix I: GateKeeper Implementation Guide ..... 261
- I.1 Introduction ..... 261
- I.2 GateKeeper Components ..... 261
- I.3 QuotaManager Implementation ..... 261
- I.4 RateLimiter (Token Bucket) Implementation ..... 263
- I.5 DOSDetector Implementation ..... 264
- I.6 Integrated GateKeeper Implementation ..... 266
- I.7 Integration with the Player Agent ..... 267
- I.8 Implementation Checklist ..... 268

### Appendix J: Message Sequence Diagrams ..... 269
- J.1 Introduction ..... 269
- J.2 League Registration Sequence ..... 269
- J.3 Season Start Sequence ..... 269
- J.4 Full Game Sequence ..... 270
- J.5 Broadcast Response Sequence ..... 270
- J.6 Extension Request Sequence ..... 270
- J.7 Force Majeure Sequence ..... 270
- J.8 Response Deadline Summary ..... 270

---

## List of Figures

1. Season A Timeline -- From Three Warm-Up Meetings to League Evening ..... 5
2. Game Flow Diagram in Six Phases ..... 14
3. Internal State Machine of the Referee -- 12 States ..... 15
4. Event-Based State Transitions in the Player Agent ..... 30
5. Three-Layer Architecture with Log Server ..... 60
6. Agent Interaction Diagram -- Including Broadcasts and Log Server ..... 61
7. Single Game State Machine -- 12 Scored States from Referee Perspective ..... 63
8. Event-Based State Machine of the Player Agent ..... 65
9. Referee Agent State Machine -- 6 States ..... 66
10. Game Status State Machine -- Five Possible States ..... 68
11. Message Flow with CC to Log Server ..... 80
12. Extension Request Flow -- Participant -> League Manager ..... 84
13. Assignment Table Creation Process ..... 92
14. Technical Failure Handling Process with 0-2-2 Scoring ..... 97
15. Force Majeure Request State Machine ..... 99
16. Season State Machine ..... 105
17. Registration Process -- From Group Selection to Model Submission ..... 132
18. Full Q21G Game Message Flow ..... 150
20. Player Agent Database Schema -- 20 Tables in Six Logical Groups ..... 212

---

## List of Tables

1. Glossary ..... 3
2. Role Mapping to Email Addresses ..... 3
3. Detailed Timeline for League Evening ..... 6
4. Example Timeline -- Game in Round 1 ..... 7
5. Game Group States ..... 8
6. Scheduled Journal Events ..... 10
7. Critical League Manager Messages ..... 11
8. Internal Referee State Machine States ..... 15
9. Referee Response Deadlines by Phase ..... 16
10. Round Score Components ..... 16
11. Individual Score to League Score Conversion ..... 17
12. League Points Distribution ..... 17
13. Clock System and State Machines ..... 20
14. Response Deadlines by Message Type ..... 22
15. Mandatory Technical Requirements ..... 24
16. Key Terms ..... 25
17. Orchestrator Roles ..... 27
18. Player Agent States -- Registration and Assignments ..... 29
19. Player Agent States -- Game ..... 29
20. state_machine_state Table ..... 33
21. state_history Table ..... 35
22. GateKeeper Components ..... 36
23. Timing Loops ..... 40
24. Q21 Handlers for Referee ..... 42
25. Recipient Field Usage ..... 44
26. pending_timeouts Table ..... 48
27. Timeout Values in Referee Implementation ..... 48
28. Broadcast Types and Required Response ..... 51
29. broadcasts_received Table ..... 53
30. broadcast_responses_sent Table ..... 54
31. Time Conversions ..... 55
32. Configuration File Separation ..... 57
33. Key Communication Flows ..... 61
34. League Manager Responsibilities ..... 62
35. Game State Descriptions ..... 64
36. Player Agent States -- Registration ..... 65
37. Player Agent States -- Game ..... 65
38. Referee Agent States (RefereeState) ..... 66
39. season_assignments Table Schema (Normalized) ..... 67
40. System Identifier Types ..... 68
41. Main Error Codes ..... 70
42. Retry Policy by Game Phase ..... 70
43. Failure Results by Phase ..... 71
44. HTTP to Gmail Comparison ..... 74
45. Email Subject Components ..... 75
46. Message Envelope Fields ..... 77
47. Additional Message-Level Fields (Not in Envelope) ..... 77
48. Context Fields by Message Type ..... 79
49. Context Fields Format ..... 79
50. season_assignments Table Structure ..... 92
51. Failure Types (failure_type) ..... 96
52. Cancellation Events (MatchEvent) ..... 96
53. Audit Log Fields (File-based) ..... 98
54. Possible Force Majeure Request Outcomes ..... 102
55. Extension Response Handling ..... 104
56. Season States and Transitions ..... 105
57. Game Round States ..... 106
58. Round Messages ..... 106
59. Environment Requirements ..... 109
60. Player Messages - Registration and Season ..... 111
61. Player Messages - Game ..... 112
62. Referee Messages - Registration ..... 113
63. Referee Messages - Game Management ..... 114
64. Individual Score to League Score Conversion ..... 116
65. Important Parameters in config.json ..... 121
66. Mandatory Test List ..... 121
67. Referee-Specific Tests ..... 122
68. message_logs Table Structure ..... 123
69. Timeline -- League Seasons ..... 132
70. Group Name Examples ..... 134
71. Email Address Format for Agents ..... 135
72. PDF File Fields for Registration ..... 141
73. Addresses by Role ..... 142
74. Email Subject Components ..... 148
75. Protocol Versions ..... 149
76. Warm-Up Message Fields ..... 153
77. Warm-Up Phase Details ..... 153
78. Possible Response Values ..... 156
79. Questions Phase Deadlines ..... 156
80. Scoring Types ..... 158
81. League Scoring Values ..... 158
82. Individual Scoring Components ..... 158
83. Game Result Fields ..... 161
84. Deadline Summary ..... 161
85. Error Codes ..... 162
86. Broadcast Messages to Referee ..... 162
87. Referee State Machine States (RefereeState) ..... 163
88. Game Phases ..... 164
89. Branding Screen Settings ..... 168
90. Tag List for Gmail API Setup ..... 170
91. Protocol Response Deadline Categories ..... 171
92. Registration and Link Messages ..... 172
93. Game Flow Messages ..... 173
94. Q21 Game Messages ..... 174
95. Broadcast Messages Requiring Response ..... 177
96. Broadcast Messages Not Requiring Response ..... 178
97. Life Cycle Messages ..... 178
98. Assignment Table Messages ..... 179
99. Query and Error Messages ..... 179
100. Deadline Extension Messages ..... 179
101. League Manager Intervention Messages ..... 180
102. Force Majeure Messages ..... 181
103. users Table Structure ..... 185
104. email_log Table Structure ..... 186
105. transactions Table Structure ..... 186
106. attachments Table Structure ..... 187
107. audit_trail Table Structure ..... 187
108. broadcasts Table Structure ..... 188
109. broadcast_responses Table Structure ..... 189
110. broadcast_queue Table Structure ..... 189
111. student_groups Table Structure ..... 190
112. seasons Table Structure ..... 191
113. season_registrations Table Structure ..... 191
114. season_standings Table Structure ..... 192
115. leagues Table Structure ..... 193
116. players Table Structure ..... 194
117. referees Table Structure ..... 195
118. rounds Table Structure ..... 196
119. matches Table Structure ..... 197
120. season_assignments Table Structure ..... 198
121. broadcast_transaction_mapping Table Structure (Deprecated) ..... 199
122. gatekeeper_state Table Structure (Deprecated) ..... 200
123. gatekeeper_log Table Structure ..... 200
124. game_state Table Structure ..... 201
125. pending_timeouts Table Structure ..... 202
126. state_transitions Table Structure ..... 203
127. calendar_events Table Structure ..... 203
128. user_messages_{email} Table Structure ..... 204
129. Interpreted Foreign Keys (4) ..... 205
130. Repository Locations ..... 206
131. Unique Constraints ..... 207
132. Key Performance Indices ..... 208
133. Database Statistics ..... 209
134. player_states Table Columns ..... 213
135. state_transitions Table Columns ..... 214
136. game_sessions Table Columns ..... 215
137. game_state Table Columns ..... 216
138. game_invitations Table Columns ..... 217
139. game_results Table Columns ..... 218
140. questions Table Columns ..... 219
141. answers Table Columns ..... 219
142. guesses Table Columns ..... 220
143. message_logs Table Columns ..... 221
144. attachments Table Columns ..... 222
145. message_correlations Table Columns ..... 222
146. broadcasts_received Table Columns ..... 223
147. pause_state Table Columns ..... 224
148. season_registrations Table Columns ..... 224
149. my_assignments Table Columns ..... 225
150. season_standings Table Columns ..... 226
151. schema_version Table Columns ..... 226
152. error_logs Table Columns ..... 227
153. Foreign Key Relationships in Schema ..... 227
154. Database Schema Statistics ..... 229
155. 20 Tables Summary by Group ..... 229
156. League Parameters for Transport Calculation ..... 231
157. Life Cycle Messages -- Complete Season ..... 232
158. Round Messages -- Complete Season ..... 232
159. Messages to Referees -- All Games ..... 232
160. League Manager Message Summary ..... 233
161. Registration Messages ..... 233
162. Referee Result Reports ..... 233
163. Messages Received at League Manager ..... 233
164. Role Assignment for a Single Participant ..... 234
165. Referee Messages for a Single Game ..... 234
166. Player Messages for a Single Game ..... 235
167. Single Participant Message Summary ..... 235
168. Overall Transport Verification ..... 235
169. Total Transport Summary -- Complete Season ..... 235
170. Before and After Broadcast Consolidation Comparison ..... 236
171. Daily Quota Coverage -- Peak Day ..... 236
172. Gmail Sending Limits by Account Type ..... 237
173. Gmail API Rate Limits ..... 237
174. Quota Unit Costs per Action ..... 237
175. Limitation Analysis -- League Manager ..... 238
176. Limitation Analysis -- Single Participant ..... 238
177. Strategies for Preventing Blocking ..... 239
178. Group Identifier Format ..... 241
179. User Identifier Format ..... 241
180. Player Identifier Format ..... 242
181. Referee Identifier Format ..... 242
182. Season Identifier Format ..... 242
183. Round Identifier Format ..... 242
184. Composite Game Identifier Structure ..... 243
185. Examples for Parsing Game Identifier ..... 243
186. Assignment Statistics by Number of Participants ..... 244
187. Broadcast Identifier Format ..... 244
188. Message Identifier Format ..... 245
189. Conversation Identifier Format ..... 245
190. Journal Channel Identifier Format ..... 245
191. Full Reference Table -- All Identifier Types ..... 246
192. Quota Settings ..... 249
193. DOS Detection Settings ..... 249
194. Rate Limit Settings ..... 250
195. Broadcast Consolidation Settings ..... 250
196. Season Settings ..... 251
197. Registration Settings ..... 251
198. Round Settings ..... 251
199. Time Window Settings ..... 252
200. Log Server Settings ..... 253
201. CC Policy Options ..... 253
202. Default Values -- Summary ..... 254
203. Static Data in Group Tables ..... 255
204. League Manager Gatekeeper Components ..... 256
205. DoS Layers of the Gatekeeper ..... 256
206. League Manager State Machines ..... 257
207. Context Fields ..... 258
208. GateKeeper Components ..... 261
209. Recommended Token Bucket Parameters ..... 264
210. Response Deadlines by Message ..... 270

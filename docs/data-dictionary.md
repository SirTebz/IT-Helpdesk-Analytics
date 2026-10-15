# Data dictionary

| Column | Type | Nullable | Business meaning |
|---|---|---:|---|
| TicketID | text | No | Unique service desk identifier |
| CreatedDate | datetime | No | Ticket creation timestamp |
| ResolvedDate | datetime | Yes | Resolution timestamp |
| Department | text | No | Requesting business unit |
| Category | text | No | Issue category |
| Priority | text | No | Low, Medium, High, or Critical |
| Status | text | No | Workflow status |
| ResolutionHours | decimal | Yes | Created-to-resolved duration |
| SLAStatus | text | No | Within SLA, Breached, or Not Applicable |

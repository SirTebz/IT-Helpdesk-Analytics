# Example DAX measures

```DAX
Total Tickets = COUNTROWS(Tickets)
Resolved Tickets = CALCULATE([Total Tickets], NOT(ISBLANK(Tickets[ResolvedDate])))
Open Tickets = CALCULATE([Total Tickets], Tickets[Status] IN {"Open", "In Progress", "Pending"})
Resolution Rate = DIVIDE([Resolved Tickets], [Total Tickets])
SLA Compliance = DIVIDE(CALCULATE([Resolved Tickets], Tickets[SLAStatus] = "Within SLA"), [Resolved Tickets])
Average Resolution Time = AVERAGE(Tickets[ResolutionHours])
Average Satisfaction = AVERAGE(Tickets[CustomerSatisfactionScore])
```

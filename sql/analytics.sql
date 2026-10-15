-- Ticket demand by department
SELECT d.DepartmentName, COUNT(*) AS TicketCount FROM Tickets t JOIN Departments d ON t.DepartmentID=d.DepartmentID GROUP BY d.DepartmentName ORDER BY TicketCount DESC;
-- Monthly trend and running total (SQL Server)
WITH Monthly AS (SELECT DATETRUNC(month, CreatedDate) AS MonthStart, COUNT(*) AS Tickets FROM Tickets GROUP BY DATETRUNC(month, CreatedDate)) SELECT MonthStart, Tickets, SUM(Tickets) OVER (ORDER BY MonthStart) AS RunningTickets FROM Monthly;
-- SLA compliance by priority
SELECT t.Priority, COUNT(*) AS ResolvedTickets, AVG(CASE WHEN DATEDIFF(minute,t.CreatedDate,t.ResolvedDate)/60.0 <= s.TargetResolutionHours THEN 1.0 ELSE 0 END) AS SLACompliance FROM Tickets t JOIN SLA s ON t.SLAID=s.SLAID WHERE t.ResolvedDate IS NOT NULL GROUP BY t.Priority;
-- Workload ranking
SELECT TechnicianID, COUNT(*) AS AssignedTickets, RANK() OVER (ORDER BY COUNT(*) DESC) AS WorkloadRank FROM Tickets GROUP BY TechnicianID;

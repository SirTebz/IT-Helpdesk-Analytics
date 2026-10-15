import pandas as pd

def filtered(df,start,end,filters):
    out=df[(df.CreatedDate.dt.date>=start)&(df.CreatedDate.dt.date<=end)].copy()
    for col,values in filters.items():
        if values: out=out[out[col].isin(values)]
    return out

def kpis(df):
    resolved=df[df.ResolvedDate.notna()]; applicable=resolved[resolved.SLAStatus!="Not Applicable"]
    return {"Total Tickets":len(df),"Open Tickets":int(df.Status.isin(["Open","In Progress","Pending"]).sum()),"Resolved Tickets":len(resolved),"Resolution Rate":len(resolved)/len(df) if len(df) else 0,"Avg Resolution Time":resolved.ResolutionHours.mean(),"Median Resolution Time":resolved.ResolutionHours.median(),"SLA Compliance":(applicable.SLAStatus=="Within SLA").mean() if len(applicable) else 0,"SLA Breach Rate":(applicable.SLAStatus=="Breached").mean() if len(applicable) else 0,"Avg First Response":df.FirstResponseHours.mean(),"Customer Satisfaction":df.CustomerSatisfactionScore.mean(),"Reopened Ticket Rate":df.Reopened.mean()}

def grouped(df,by):
    return df[df.ResolvedDate.notna()].groupby(by).agg(Tickets=("TicketID","count"),Avg_Resolution_Hours=("ResolutionHours","mean"),SLA_Compliance=("SLAStatus",lambda x:(x=="Within SLA").mean()),Satisfaction=("CustomerSatisfactionScore","mean")).reset_index()

def insights(df):
    if df.empty:return []
    c=df.Category.value_counts(); d=df.Department.value_counts(); k=kpis(df); output=[("Observed finding",f"{c.index[0]} is the largest category with {c.iloc[0]:,} tickets.","Investigate recurring issues within this category."),("Observed finding",f"{d.index[0]} generated the highest support demand ({d.iloc[0]:,} tickets).","Review incident patterns and training opportunities in this department.")]
    if k["SLA Compliance"]<.85: output.append(("Observed finding",f"SLA compliance is {k['SLA Compliance']:.1%}.","Review workload distribution and SLA targets for this segment."))
    return output

"""Synthetic data, validation, cleaning and local storage."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from app.config import RAW, PROCESSED, database_url

DEPARTMENTS=["Finance","Human Resources","IT","Operations","Marketing","Procurement","Student Services","Facilities","Administration","Management"]
CATEGORIES=["Hardware","Software","Network","Access","Email","Microsoft 365","Printer","Security","Application","Account","Other"]
PRIORITIES=["Low","Medium","High","Critical"]
STATUSES=["Open","In Progress","Pending","Resolved","Closed","Cancelled"]
SLA={"Low":(24,120),"Medium":(8,48),"High":(2,16),"Critical":(.5,4)}

def generate_tickets(n=10000,seed=42):
    rng=np.random.default_rng(seed); start=pd.Timestamp("2024-09-01"); span=(pd.Timestamp("2026-09-30")-start).days
    created=start+pd.to_timedelta(rng.integers(0,span,n),unit="D")+pd.to_timedelta(rng.integers(7,19,n),unit="h")
    dept=rng.choice(DEPARTMENTS,n,p=[.12,.07,.15,.18,.07,.06,.12,.08,.1,.05]); cat=rng.choice(CATEGORIES,n,p=[.1,.12,.12,.11,.1,.1,.05,.08,.12,.06,.04])
    priority=rng.choice(PRIORITIES,n,p=[.22,.49,.23,.06]); status=rng.choice(STATUSES,n,p=[.07,.08,.05,.46,.28,.06]); unresolved=np.isin(status,["Open","In Progress","Pending"])
    targets=np.array([SLA[p][1] for p in priority]); responses=np.array([SLA[p][0] for p in priority])*rng.lognormal(-.05,.65,n); duration=targets*rng.lognormal(-.12,.7,n)
    resolved=pd.Series(created+pd.to_timedelta(np.maximum(.5,duration),unit="h")).where(~unresolved,pd.NaT)
    satisfaction=pd.Series(np.clip(np.round(4.7-duration/targets*.9+rng.normal(0,.55,n)),1,5)).where(~unresolved & (rng.random(n)>.17),np.nan)
    return pd.DataFrame({"TicketID":[f"HD-{i:06d}" for i in range(1,n+1)],"CreatedDate":created,"FirstResponseDate":created+pd.to_timedelta(np.maximum(.1,responses),unit="h"),"ResolvedDate":resolved,"ClosedDate":resolved+pd.to_timedelta(rng.integers(0,5,n),unit="D"),"Department":dept,"Category":cat,"SubCategory":[f"{x} Support" for x in cat],"Technician":rng.choice([f"Technician {i:02d}" for i in range(1,21)],n),"Priority":priority,"Status":status,"Subject":[f"{c} request - {d}" for c,d in zip(cat,dept)],"Description":"Synthetic service desk request.","SLAID":[f"SLA-{x}" for x in priority],"ResolutionCode":rng.choice(["Password Reset","Software Installation","Hardware Replacement","Network Configuration","Account Unlock","Permission Change","Application Fix","User Training","Configuration Change","Vendor Escalation","Other"],n),"CustomerSatisfactionScore":satisfaction,"Reopened":rng.random(n)<.055})

def validate(df):
    required=["TicketID","CreatedDate","Priority","Status","Department","Category"]
    missing=[x for x in required if x not in df]
    if missing: raise ValueError("Required columns missing: "+", ".join(missing))
    bad=pd.Series(False,index=df.index); issues=[]
    for col,allowed in [("Priority",PRIORITIES),("Status",STATUSES),("Department",DEPARTMENTS),("Category",CATEGORIES)]:
        x=~df[col].isin(allowed)|df[col].isna(); bad|=x
        if x.any(): issues.append({"Issue":f"Invalid {col}","Count":int(x.sum())})
    duplicate=df.duplicated("TicketID",keep=False); bad|=duplicate
    if duplicate.any(): issues.append({"Issue":"Duplicate TicketID","Count":int(duplicate.sum())})
    created=pd.to_datetime(df.CreatedDate,errors="coerce"); invalid=created.isna()
    for col in ["FirstResponseDate","ResolvedDate","ClosedDate"]:
        d=pd.to_datetime(df[col],errors="coerce"); invalid|=d.notna()&(d<created)
    bad|=invalid
    if invalid.any(): issues.append({"Issue":"Invalid date sequence","Count":int(invalid.sum())})
    report=pd.DataFrame(issues or [{"Issue":"No validation issues","Count":0}]); report.attrs["summary"]={"Total Records":len(df),"Valid Records":int((~bad).sum()),"Invalid Records":int(bad.sum()),"Duplicate Records":int(duplicate.sum()),"Missing Values":int(df.isna().sum().sum()),"Invalid Dates":int(invalid.sum()),"Invalid Categories":int((~df.Category.isin(CATEGORIES)).sum())}
    return ~bad,report

def clean(df):
    out=df.drop_duplicates("TicketID").copy()
    for c in ["Department","Category","Priority","Status","Technician"]: out[c]=out[c].astype(str).str.strip().str.title()
    for c in ["CreatedDate","FirstResponseDate","ResolvedDate","ClosedDate"]: out[c]=pd.to_datetime(out[c],errors="coerce")
    out["ResolutionHours"]=(out.ResolvedDate-out.CreatedDate).dt.total_seconds()/3600; out["FirstResponseHours"]=(out.FirstResponseDate-out.CreatedDate).dt.total_seconds()/3600; out["SLATargetHours"]=out.Priority.map({p:x[1] for p,x in SLA.items()}); out["SLAStatus"]=np.where(out.ResolvedDate.notna(),np.where(out.ResolutionHours<=out.SLATargetHours,"Within SLA","Breached"),"Not Applicable"); out["Month"]=out.CreatedDate.dt.to_period("M").astype(str)
    return out.sort_values("CreatedDate")

def ensure_data():
    RAW.mkdir(parents=True,exist_ok=True); PROCESSED.mkdir(parents=True,exist_ok=True); cleaned_path=PROCESSED/"tickets_cleaned.csv"
    if cleaned_path.exists(): return pd.read_csv(cleaned_path,parse_dates=["CreatedDate","FirstResponseDate","ResolvedDate","ClosedDate"])
    raw=generate_tickets(); raw.to_csv(RAW/"tickets.csv",index=False); good,_=validate(raw); clean_df=clean(raw.loc[good]); clean_df.to_csv(cleaned_path,index=False); clean_df.to_excel(PROCESSED/"sample_analysis.xlsx",index=False); clean_df.to_sql("Tickets",create_engine(database_url()),if_exists="replace",index=False); return clean_df

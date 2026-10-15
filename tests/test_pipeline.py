import pandas as pd
from app.data import generate_tickets,validate,clean
from app.analytics import kpis

def test_generated_data_and_kpis():
    raw=generate_tickets(100,1); good,report=validate(raw); cleaned=clean(raw[good]); result=kpis(cleaned)
    assert len(cleaned)==100
    assert result["Total Tickets"]==100
    assert 0 <= result["SLA Compliance"] <= 1
    assert report.attrs["summary"]["Invalid Records"]==0

def test_duplicate_and_invalid_priority_detected():
    raw=generate_tickets(10,2); raw.loc[1,"TicketID"]=raw.loc[0,"TicketID"]; raw.loc[2,"Priority"]="Urgent"
    good,report=validate(raw)
    assert not good.all()
    assert report.attrs["summary"]["Duplicate Records"]==2

def test_clean_adds_analytics_columns():
    raw=generate_tickets(10,3); cleaned=clean(raw)
    assert {"ResolutionHours","FirstResponseHours","SLAStatus","Month"}.issubset(cleaned.columns)

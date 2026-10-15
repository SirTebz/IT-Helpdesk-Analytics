import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import plotly.express as px
import streamlit as st
from app.data import ensure_data,validate
from app.analytics import filtered,kpis,grouped,insights

st.set_page_config(page_title="IT Helpdesk Analytics",page_icon="🎫",layout="wide")
st.markdown("<style>.block-container{padding-top:1.5rem}.stMetric{background:#f5f7fb;padding:12px;border-radius:8px}</style>",unsafe_allow_html=True)
@st.cache_data
def load_data(): return ensure_data()
df=load_data(); st.sidebar.title("IT Helpdesk Analytics")
pages=["Dashboard","Tickets","Trends","SLA Analysis","Technician Analysis","Department Analysis","Category Analysis","Customer Satisfaction","Data Quality","Data Explorer","Reporting","About"]
page=st.sidebar.radio("Navigation",pages); st.sidebar.caption("Global filters")
start,end=st.sidebar.date_input("Date range",(df.CreatedDate.min().date(),df.CreatedDate.max().date()))
filters={c:st.sidebar.multiselect(c,sorted(df[c].dropna().unique())) for c in ["Department","Category","Priority","Status","Technician"]}
if st.sidebar.button("Reset filters"): st.rerun()
data=filtered(df,start,end,filters)
def plot(x,y,title,line=False):
    if data.empty: return st.info("No records match current filters.")
    fig=px.line(x,x=x,y=y,title=title,markers=True) if line else px.bar(x,x=x,y=y,title=title); st.plotly_chart(fig,use_container_width=True)
def cards(d):
    k=kpis(d); vals=[("Total Tickets",f"{k['Total Tickets']:,}"),("Open Tickets",f"{k['Open Tickets']:,}"),("Resolved Tickets",f"{k['Resolved Tickets']:,}"),("SLA Compliance",f"{k['SLA Compliance']:.1%}"),("Avg Resolution",f"{k['Avg Resolution Time']:.1f} h"),("Satisfaction",f"{k['Customer Satisfaction']:.1f} / 5")]
    for col,(name,val) in zip(st.columns(6),vals): col.metric(name,val)
if page=="Dashboard":
    st.title("IT Helpdesk Analytics Dashboard"); st.caption("Turn helpdesk ticket data into actionable operational insights."); cards(data)
    a,b=st.columns(2)
    with a: plot(data.groupby("Month").size().reset_index(name="Tickets"),"Month","Tickets","Ticket volume trend",True)
    with b: plot(data.groupby("Priority").size().reset_index(name="Tickets"),"Priority","Tickets","Tickets by priority")
    a,b=st.columns(2)
    with a: plot(data.Category.value_counts().head(8).sort_values().reset_index(name="Tickets"),"Category","Tickets","Tickets by category")
    with b: plot(data.Department.value_counts().reset_index(name="Tickets"),"Department","Tickets","Tickets by department")
    st.subheader("Recent active tickets"); st.dataframe(data[data.Status.isin(["Open","In Progress","Pending"])].sort_values("CreatedDate",ascending=False).head(15),use_container_width=True)
    st.subheader("Evidence-based insights")
    for _,finding,recommendation in insights(data): st.info(f"**Observed finding:** {finding} **Recommended investigation:** {recommendation}")
elif page=="Tickets":
    st.title("Ticket explorer"); term=st.text_input("Search Ticket ID or subject"); shown=data if not term else data[data.TicketID.str.contains(term,case=False)|data.Subject.str.contains(term,case=False)]
    columns=["TicketID","CreatedDate","Department","Category","Priority","Technician","Status","ResolutionHours","SLAStatus","CustomerSatisfactionScore"]
    st.dataframe(shown[columns].sort_values("CreatedDate",ascending=False).head(500),use_container_width=True); st.download_button("Export filtered tickets CSV",shown.to_csv(index=False),"filtered_tickets.csv","text/csv")
elif page=="Trends":
    st.title("Trends"); trend=data[data.ResolvedDate.notna()].groupby("Month").agg(Tickets=("TicketID","count"),Average_Resolution_Hours=("ResolutionHours","mean"),SLA_Compliance=("SLAStatus",lambda x:(x=="Within SLA").mean()),Satisfaction=("CustomerSatisfactionScore","mean")).reset_index()
    for col in trend.columns[1:]: plot(trend,"Month",col,f"Monthly {col.replace('_',' ').title()}",True)
elif page in ["SLA Analysis","Technician Analysis","Department Analysis","Category Analysis","Customer Satisfaction"]:
    by={"SLA Analysis":"Priority","Technician Analysis":"Technician","Department Analysis":"Department","Category Analysis":"Category","Customer Satisfaction":"Category"}[page]
    st.title(page); cards(data); table=grouped(data,by); st.dataframe(table.style.format({"Avg_Resolution_Hours":"{:.1f}","SLA_Compliance":"{:.1%}","Satisfaction":"{:.1f}"}),use_container_width=True); plot(table.sort_values("Tickets",ascending=False),by,"Tickets",f"Tickets by {by}")
    if page=="Customer Satisfaction": plot(data.dropna(subset=["CustomerSatisfactionScore"]).groupby("CustomerSatisfactionScore").size().reset_index(name="Tickets"),"CustomerSatisfactionScore","Tickets","Rating distribution")
elif page=="Data Quality":
    st.title("Data quality"); _,report=validate(df)
    for c,(name,value) in zip(st.columns(4),report.attrs["summary"].items()): c.metric(name,value)
    st.dataframe(report,use_container_width=True); st.download_button("Download validation report",report.to_csv(index=False),"data_quality_report.csv")
elif page=="Data Explorer":
    st.title("Data explorer"); st.dataframe(data.head(st.slider("Preview rows",10,500,100)),use_container_width=True); st.dataframe(pd.DataFrame({"Column":data.columns,"Data type":data.dtypes.astype(str)}),use_container_width=True); st.download_button("Download filtered data",data.to_csv(index=False),"helpdesk_export.csv")
elif page=="Reporting":
    st.title("Management report"); k=kpis(data); st.subheader("Executive summary"); st.write(f"The selected period contains **{k['Total Tickets']:,}** tickets. Resolution rate is **{k['Resolution Rate']:.1%}** and SLA compliance is **{k['SLA Compliance']:.1%}**."); report=pd.DataFrame(insights(data),columns=["Type","Finding","Recommended investigation"]); st.dataframe(report,use_container_width=True); st.download_button("Download analytical summary",report.to_csv(index=False),"analytical_summary.csv"); st.download_button("Download KPI summary",pd.DataFrame([k]).to_csv(index=False),"kpi_summary.csv")
else: st.title("About"); st.write("A reproducible portfolio project demonstrating helpdesk data generation, validation, cleaning, database loading, analysis, visualisation, and reporting.")

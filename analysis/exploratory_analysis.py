"""Reproducible Pandas/NumPy/Matplotlib/Seaborn exploration."""
from app.data import ensure_data
import matplotlib.pyplot as plt
import seaborn as sns

df=ensure_data()
print(df.info()); print(df.describe(include="all"))
print("Missing values:\n",df.isna().sum()); print("Duplicates:",df.TicketID.duplicated().sum())
monthly=df.groupby("Month").size(); sns.lineplot(x=monthly.index,y=monthly.values); plt.title("Monthly ticket volume"); plt.xticks(rotation=45); plt.tight_layout(); plt.show()

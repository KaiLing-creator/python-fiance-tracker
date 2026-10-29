"""Ledgerly: a shareable personal finance demo built with Streamlit and Pandas."""
from datetime import date, timedelta
from io import BytesIO
import uuid

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Ledgerly | Python Finance Tracker", page_icon="💸", layout="wide")

COLUMNS = ["id", "date", "type", "category", "description", "amount"]
EXPENSE_CATEGORIES = ["Food", "Shopping", "Transport", "Housing", "Bills", "Entertainment", "Health", "Education", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Investments", "Gifts", "Other"]


def demo_data():
    today = date.today()
    entries = [
        (-23, "Income", "Salary", "Part-time paycheck", 1450),
        (-20, "Expense", "Housing", "Rent contribution", 550),
        (-18, "Expense", "Food", "Groceries", 82.35),
        (-15, "Expense", "Transport", "Transit pass", 56),
        (-12, "Expense", "Shopping", "Books and supplies", 76.40),
        (-9, "Expense", "Food", "Coffee and lunch", 25.75),
        (-6, "Income", "Freelance", "Tutoring", 180),
        (-4, "Expense", "Entertainment", "Movie night", 19.50),
        (-2, "Expense", "Food", "Groceries", 47.90),
    ]
    return pd.DataFrame([{
        "id": str(uuid.uuid4()), "date": today + timedelta(days=offset),
        "type": kind, "category": cat, "description": desc, "amount": amount,
    } for offset, kind, cat, desc, amount in entries], columns=COLUMNS)


def normalize_upload(upload):
    df = pd.read_csv(upload)
    required = {"date", "type", "category", "description", "amount"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must contain date, type, category, description and amount columns.")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.date
    df["amount"] = pd.to_numeric(df["amount"], errors="raise")
    if df["amount"].isna().any() or (df["amount"] <= 0).any() or (df["amount"] > 1e9).any():
        raise ValueError("Amounts must be positive numbers below one billion.")
    if not df["type"].isin(["Income", "Expense"]).all():
        raise ValueError("Type must be Income or Expense.")
    for col in ("category", "description"):
        df[col] = df[col].fillna("").astype(str).str.slice(0, 100)
    df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    return df[COLUMNS]


if "transactions" not in st.session_state:
    st.session_state.transactions = demo_data()

st.markdown("""<style>
.block-container{padding-top:2rem;max-width:1150px}
h1,h2,h3{letter-spacing:-.035em}
[data-testid="stMetric"]{background:#f3f8f7;padding:18px;border-radius:14px;border:1px solid #e1eeeb}
</style>""", unsafe_allow_html=True)

st.title("💸 Ledgerly")
st.caption("Personal Finance Tracker · Built with Python, Streamlit & Pandas")
st.info("Demo mode: example data is preloaded. Your changes belong to your current session and are not shared with other visitors. Download CSV to save your work.")

df = st.session_state.transactions.copy()
df["date"] = pd.to_datetime(df["date"]).dt.date

with st.sidebar:
    st.header("⚙️ Controls")
    months = sorted(set(df["date"].map(lambda d: d.strftime("%Y-%m"))), reverse=True)
    this_month = date.today().strftime("%Y-%m")
    selected_month = st.selectbox("Report month", list(dict.fromkeys([this_month] + months)))
    st.divider()
    if st.button("↺ Reset demo data", use_container_width=True):
        st.session_state.transactions = demo_data()
        st.rerun()
    uploaded = st.file_uploader("Import transactions CSV", type="csv")
    if uploaded and st.button("Import CSV", use_container_width=True):
        try:
            imported = normalize_upload(uploaded)
            st.session_state.transactions = imported
            st.success(f"Imported {len(imported)} transactions.")
            st.rerun()
        except (ValueError, pd.errors.ParserError, KeyError) as exc:
            st.error(str(exc))

monthly = df[df["date"].map(lambda d: d.strftime("%Y-%m")) == selected_month]
income = monthly.loc[monthly["type"] == "Income", "amount"].sum()
expense = monthly.loc[monthly["type"] == "Expense", "amount"].sum()
balance = df.loc[df["type"] == "Income", "amount"].sum() - df.loc[df["type"] == "Expense", "amount"].sum()

a, b, c = st.columns(3)
a.metric("All-time balance", f"${balance:,.2f} CAD")
b.metric("Monthly income", f"${income:,.2f}")
c.metric("Monthly spending", f"${expense:,.2f}")

left, right = st.columns([1.25, 1])
with left:
    st.subheader("➕ Add a transaction")
    with st.form("add", clear_on_submit=True):
        kind = st.radio("Type", ["Expense", "Income"], horizontal=True)
        description = st.text_input("Description", placeholder="e.g. Groceries")
        amount = st.number_input("Amount (CAD)", min_value=0.01, max_value=999999999.0, value=10.0, step=1.0)
        category = st.selectbox("Category", EXPENSE_CATEGORIES if kind == "Expense" else INCOME_CATEGORIES)
        transaction_date = st.date_input("Date", value=date.today())
        add = st.form_submit_button("Add transaction", use_container_width=True, type="primary")
        if add:
            if not description.strip():
                st.error("Please enter a description.")
            else:
                item = pd.DataFrame([{"id": str(uuid.uuid4()), "date": transaction_date, "type": kind, "category": category, "description": description.strip()[:100], "amount": round(float(amount), 2)}])
                st.session_state.transactions = pd.concat([st.session_state.transactions, item], ignore_index=True)
                st.rerun()

with right:
    st.subheader("🥧 Spending by category")
    spending = monthly[monthly["type"] == "Expense"].groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    if spending.empty:
        st.caption("No spending this month yet.")
    else:
        st.bar_chart(spending.set_index("category"), x_label="Category", y_label="CAD")

st.subheader("📈 Monthly cash flow")
if df.empty:
    st.caption("Add a transaction to see your trend.")
else:
    trend = df.assign(month=df["date"].map(lambda d: d.strftime("%Y-%m")))
    trend = trend.pivot_table(index="month", columns="type", values="amount", aggfunc="sum", fill_value=0).sort_index()
    st.line_chart(trend, x_label="Month", y_label="CAD")

st.subheader("📋 Transaction history")
history = monthly.sort_values("date", ascending=False)
if history.empty:
    st.caption("No transactions in the selected month.")
else:
    st.dataframe(history.drop(columns="id"), hide_index=True, use_container_width=True, column_config={"amount": st.column_config.NumberColumn("Amount (CAD)", format="$%.2f")})
    remove_options = {f"{row.date} · {row.description} · ${row.amount:.2f} · {str(row.id)[:8]}": row.id for row in history.itertuples()}
    chosen = st.selectbox("Remove a transaction", options=list(remove_options), index=None, placeholder="Select a transaction to remove")
    if st.button("Delete selected", disabled=chosen is None):
        st.session_state.transactions = df[df["id"] != remove_options[chosen]].copy()
        st.rerun()

export = df.drop(columns="id").sort_values("date", ascending=False).to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Download all transactions (CSV)", data=export, file_name="ledgerly_transactions.csv", mime="text/csv", use_container_width=True)
st.caption("Built as a student portfolio project. Do not upload sensitive financial information to a public demo.")

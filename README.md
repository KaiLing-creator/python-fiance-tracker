# Ledgerly — Python Finance Tracker

A portfolio-ready financial tracker written in **Python**, **Streamlit**, and **Pandas**.

## Features

- Add and delete transactions
- Monthly income, spending, and running balance
- Spending by category and monthly trend charts
- Import and export CSV
- Preloaded demo data for interviews
- Session-isolated demo data (not a persistent personal finance service)

## Run locally on macOS

1. Install Python 3.11 or newer from https://www.python.org/downloads/.
2. In Terminal, go to this project folder.
3. Create an environment: `python3 -m venv .venv`
4. Activate it: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Start the app: `streamlit run app.py`

Open the local URL printed by Streamlit (usually http://localhost:8501).

## Deploy online (Streamlit Community Cloud)

1. Create a GitHub repository, e.g. `python-finance-tracker`.
2. Upload `app.py`, `requirements.txt`, and `README.md` into the repository root. Do not upload real financial records.
3. Sign in at https://share.streamlit.io/ with GitHub and select **Create app**.
4. Choose the repository and `main` branch. Set the main file path to `app.py`.
5. Choose an available app URL and deploy. Share the resulting `https://...streamlit.app` link.

The free cloud runtime is ephemeral: this project deliberately stores user edits per session, not in a shared SQLite file. For persistent private accounts, implement authentication and a managed database later.

## Resume wording (after you have tested and understood your contributions)

**Personal Finance Tracker | Python, Pandas, Streamlit**

- Built and tested an interactive expense-tracking dashboard with AI-assisted development tools.
- Implemented income/expense summaries, category charts, CSV import/export, and transaction management.
- Used Pandas to organize transaction data and calculate monthly financial trends.

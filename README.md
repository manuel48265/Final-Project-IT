# Final-Project-IT: AI-assisted accounting dashboard

Desktop application for managing the finances of a company organised by projects. It tracks income
and expenses per project, shows them in charts and tables in any of 13 currencies, answers questions
about the data through a Gemini chatbot, writes PDF financial reports with generative AI, and sends
upcoming-payment reminders through a Telegram bot.

Team project (December 2024 – January 2025).

## Features

- **Project and expense tracking.** Each project keeps its income and expenses in SQLite; general
  company expenses are tracked separately. Transactions can be searched and filtered by project,
  type, date range and amount range.
- **Dashboard and charts.** Income and expense breakdowns by type and over time (matplotlib embedded
  in Tkinter), with balances and upcoming payments.
- **Multi-currency.** Amounts are converted in real time between 13 currencies (USD, EUR, GBP, PLN,
  JPY, CNY…) using the exchangerate-api.com rates.
- **AI chatbot.** A chat panel sends the selected project's data to Gemini and renders the answer
  as formatted Markdown.
- **Generated reports.** Gemini drafts monthly/yearly, per-project and forecasting reports, which are
  rendered to PDF with WeasyPrint. Examples are in [`docs/`](docs/).
- **Telegram notifications.** A bot (`/start`, `/notify`, `/hours`, `/days`, `/weeks`) sends
  reminders of upcoming payments. It runs in its own process and asks the GUI for fresh data through
  a shared, lock-protected channel.

## Tech stack

Python · Tkinter · SQLite · pandas · matplotlib · Google Gemini (`google-genai`) · WeasyPrint ·
python-telegram-bot · exchangerate-api.com

## Getting started

```bash
git clone https://github.com/manuel48265/Final-Project-IT.git
cd Final-Project-IT
pip install -r requirements.txt
```

Create a `keys.env` file in the repository root (it is git-ignored):

```env
GOOGLE_API_KEY=your-gemini-api-key
TOKEN=your-telegram-bot-token
```

Run the application from the repository root:

```bash
PYTHONPATH=.:src python -m src.Main
```

Run the tests:

```bash
python -m unittest discover test
```

## Repository structure

```text
src/
├── Main.py                # entry point: starts the GUI and the Telegram bot
├── MainDashBoard.py       # main window and navigation
├── Project.py             # per-project income/expense model and charts
├── GeneralExpenses.py     # company-wide expenses
├── TotalExpenses.py       # searchable transaction table
├── InterfazData.py        # charts and upcoming dates
├── Currency.py            # currency conversion
├── ChatBot.py             # Gemini chat panel
├── FinancialReport.py     # Gemini-written reports rendered to PDF
├── DocumentationBoard.py  # report generation screen
└── TelegramBot.py         # payment reminders
test/                      # unit tests (currency conversion)
docs/                      # sample generated reports
*.py (root)                # early prototypes: task-time estimator with Gantt charts,
                           # PDF question answering, Kanban board
```

## Team

Manuel González Santana, Alejandro Martínez, Leandro Jorge Fernández Vega, Gonzalo Díaz Ruiz and
Jorge García Gámiz.

# FreelancerDotCom Assistant

Welcome to **FreelancerDotCom Assistant** – your automated, AI-powered solution for searching, evaluating, and bidding on freelance projects via Freelancer.com, with smart notification and proposal generation.

## Features

- **Automated Bidding:** Scans, filters, and bids on projects based on custom job types and budgets.
- **AI-Powered Proposals:** Generates friendly, tailored proposals in the project’s language using state-of-the-art AI models.
- **Semi-Automatic Mode:** Alerts for projects that need manual review or have missing information.
- **Telegram Integration:** Sends real-time notifications, proposals, and error alerts to your Telegram chat.
- **Web API:** Lightweight web server for status checks and to trigger proposal/bid generation.
- **Persistent Storage:** Tracks project IDs and details using SQLite and JSON for robust bid management.

## How It Works

1. **Project Search:** The bot regularly queries Freelancer.com’s API for new projects matching your criteria.
2. **Filtering:** Projects are filtered for relevance, currency, status, and budget.
3. **Language Detection:** The bot uses AI to detect the language of each project’s description.
4. **Proposal Generation:** Custom proposals are written using AI, adhering to professional, friendly guidelines.
5. **Bidding:** Automatically places bids with proposals; handles NDA, bid limits, and errors gracefully.
6. **Notifications:** All actions, including bids, errors, and manual alerts, are sent to your Telegram for review.
7. **Command Control:** Start, stop, and check status of auto/semi-auto modes via Telegram commands.

## Requirements

- Python 3.8+
- [Freelancer SDK](https://github.com/freelancer/freelancer-sdk)
- `python-telegram-bot`
- `quart`
- `g4f` (AI provider library)
- `sqlite3`, `dotenv`, `requests`, etc.

## Security & Control

- Only authorized Telegram user IDs can control or receive notifications from the bot.
- Sensitive access credentials are stored in `.env` and loaded at runtime.

---

# Running & Using FreelancerDotCom Assistant

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/TheKingAde/FreelancerDotCom-Assistant.git
   cd FreelancerDotCom-Assistant
   ```

2. **Install Python & Requirements**
   - Make sure you have Python 3.8 or higher installed.
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Configure Environment Variables**
   - Copy the example env file and fill in your secrets:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and set:
     - Freelancer.com API credentials
     - Telegram Bot token
     - Telegram User IDs (who can control the bot)
     - Other settings as needed

4. **Edit Bot Filters & Templates (Optional)**
   - Open `config.py` to adjust:
     - Job types, keywords, budget filters
     - AI proposal templates

5. **Initialize the Database**
   - The bot auto-creates its SQLite DB on first run. No manual setup needed.

6. **Run the Bot**
   ```bash
   python main.py
   ```

   The web server, Telegram bot, and bidding engine all start together.

## Telegram Commands

Send these to your bot on Telegram (must be an authorized user):

- `/start` — Start all bot services
- `/start_auto` — Start automatic bidding
- `/start_semi` — Start semi-automatic mode (alerts for manual review)
- `/stop` — Pause all services
- `/stop_auto` — Pause automatic bidding only
- `/stop_semi` — Pause semi-automatic mode only
- `/status` — Get current bot status and statistics

## Web API Usage

- `GET /` — Health check. Returns bot status.
- `GET /gen_proposal?project_id=...` — Generate proposal for a project.
- `GET /place_bid?project_id=...` — Place a bid on a project (auto proposal).

Access these endpoints via browser or HTTP client (e.g. curl, Postman).

## Troubleshooting

- **Missing dependencies:** Ensure Python version and pip packages match requirements.
- **Bot not responding on Telegram:** Check your Bot token and authorized user IDs in `.env`.
- **API errors:** See logs printed in terminal. Most errors are reported to Telegram.

## Tips

- For best results, tune job filters and AI templates in `config.py` to match your freelance preferences.
- Only authorized Telegram users (IDs listed in `.env`) can control the bot or receive notifications.

## API Endpoints

- `/` — Health check
- `/gen_proposal?project_id=...` — Generate a proposal for a specified project
- `/place_bid?project_id=...` — Place a bid on a specified project

## 👤 Author

**Adegoke M.**  
Automating Freelancer success since 2025.

---

> *Let the bot do the bidding, so you can focus on winning.*

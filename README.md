# FreelancerDotCom Assistant 🤖

Welcome to **FreelancerDotCom Assistant** – your automated, AI-powered solution for searching, evaluating, and bidding on freelance projects via Freelancer.com, with smart notification and proposal generation via Telegram.

## 🚀 Features

- **Automated Bidding:** Scans, filters, and bids on projects based on custom job types and budgets.
- **AI-Powered Proposals:** Generates friendly, tailored proposals in the project’s language using state-of-the-art AI models.
- **Semi-Automatic Mode:** Alerts for projects that need manual review or have missing information.
- **Telegram Integration:** Sends real-time notifications, proposals, and error alerts to your Telegram chat.
- **Web API:** Lightweight web server for status checks and to trigger proposal/bid generation.
- **Persistent Storage:** Tracks project IDs and details using SQLite and JSON for robust bid management.

## 🛠️ How It Works

1. **Project Search:** The bot regularly queries Freelancer.com’s API for new projects matching your criteria.
2. **Filtering:** Projects are filtered for relevance, currency, status, and budget.
3. **Language Detection:** The bot uses AI to detect the language of each project’s description.
4. **Proposal Generation:** Custom proposals are written using AI, adhering to professional, friendly guidelines.
5. **Bidding:** Automatically places bids with proposals; handles NDA, bid limits, and errors gracefully.
6. **Notifications:** All actions, including bids, errors, and manual alerts, are sent to your Telegram for review.
7. **Command Control:** Start, stop, and check status of auto/semi-auto modes via Telegram commands.

## 🤖 Bot Commands

Run these via Telegram (authorized users only):

- `/start` – Start all services
- `/start_auto` – Start auto-bidding
- `/start_semi` – Start semi-auto mode
- `/stop` – Pause all services
- `/stop_auto` – Pause auto-bidding
- `/stop_semi` – Pause semi-auto mode
- `/status` – Get current bot status

## 📦 Project Structure

- `main.py` — Entry point; wires up web server, Telegram, and main bot loop.
- `config.py` — Centralizes configuration, environment variables, job filters, and AI templates.
- `freelancer_service.py` — Handles project search, bid logic, and error management.
- `bot_commands.py` — Implements Telegram bot command handlers and user authorization.
- `database.py` — SQLite-based project tracking for persistent bid management.
- `utils.py` — Helper functions for project storage, sleep logic, and retrieval.
- `ai_service.py` — Integrates with multiple AI providers for proposals and language detection.
- `telegram_service.py` — Formats and sends all Telegram messages and alerts.

## ⚡️ Requirements

- Python 3.8+
- [Freelancer SDK](https://github.com/freelancer/freelancer-sdk)
- `python-telegram-bot`
- `quart`
- `g4f` (AI provider library)
- `sqlite3`, `dotenv`, `requests`, etc.

## 🔒 Security & Control

- Only authorized Telegram user IDs can control or receive notifications from the bot.
- Sensitive access credentials are stored in `.env` and loaded at runtime.

## 🌐 API Endpoints

- `/` — Health check
- `/gen_proposal?project_id=...` — Generate a proposal for a specified project
- `/place_bid?project_id=...` — Place a bid on a specified project

## 👤 Author

**Adegoke M.**  
Automating Freelancer success since 2025.

---

> *“Let the bot do the bidding, so you can focus on winning.”*

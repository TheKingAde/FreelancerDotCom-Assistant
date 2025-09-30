import requests
import urllib.parse
import html
import config

# Telegram POST url
url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"

async def send_auto_telegram_message(project_title, msg_type, proposal, seo_url):
    """Send telegram message based on message type."""

    # Escape user-generated text
    safe_proposal = html.escape(str(proposal))
    safe_seo_url = html.escape(str(seo_url))

    if isinstance(project_title, dict):
        safe_title = html.escape(str(project_title.get("title", "")))
        safe_amount = html.escape(str(project_title.get("amount", "")))
        safe_error_message = html.escape(str(project_title.get("error_message", "")))
    else:
        safe_title = html.escape(str(project_title))
        safe_amount = ""
        safe_error_message = ""

    if msg_type == "nda":
        msg_seo_url = f"https://www.freelancer.com/projects/{safe_seo_url}/details"
        message = (
            f"🚨 <b>Project Requires NDA</b>\n\n"
            f"Project: <b>{safe_title}</b>\n"
            f"<a href='{msg_seo_url}'>View Project on Freelancer</a>\n"
            f"An NDA must be signed to access this project.\n\n"
            f"Proposal: {safe_proposal}"
        )
    elif msg_type == "proposal":
        msg_seo_url = f"https://www.freelancer.com/projects/{safe_seo_url}/details"
        message = (
            f"✅ <b>Proposal sent</b>\n\n"
            f"Project: <b>{safe_title}</b>\n"
            f"<a href='{msg_seo_url}'>View Project on Freelancer</a>\n\n"
            f"Proposal: {safe_proposal}"
        )
    elif msg_type == "gen_proposal":
        place_bid_url = f"{config.host_url}/place_bid?project_id={urllib.parse.quote(str(proposal))}"
        message = (
            f"🚨 <b>Proposal generation Failed</b>\n\n"
            f"Action taken: <b> sleeping for {config.sleep_time}</b>\n"
            f"<a href='{place_bid_url}'>✅ Place bid</a>"
        )
    elif msg_type == "error":
        place_bid_url = f"{config.host_url}/place_bid?project_id={urllib.parse.quote(str(project_title.get('id') if isinstance(project_title, dict) else project_title))}"
        msg_seo_url = f"https://www.freelancer.com/projects/{safe_seo_url}/details" if seo_url else "https://www.freelancer.com"
        exch_rate = str(project_title.get('currency_exchange_rate', 1))

        error_message_title = "An error occurred" if seo_url == "" else f"Failed to send proposal: <b>{safe_error_message}</b>"
        error_message = "Error message" if seo_url == "" else "Proposal"

        if isinstance(project_title, dict):
            title_line = f"{error_message}: <b>{safe_title} ${float(exch_rate) * float(safe_amount)}</b>\n"
        else:
            title_line = f"{error_message}: <b>{safe_title}</b>\n"

        message = (
            f"🚨 <b>{error_message_title}</b>\n\n"
            f"{title_line}"
            f"<a href='{msg_seo_url}'>View Project on Freelancer</a>\n"
            f"Proposal: {safe_proposal}\n"
            f"<a href='{place_bid_url}'>✅ Place bid</a>"
        )
    else:
        message = f"⚠️ <b>Unknown message type</b>\n\n"

    payload = {
        "chat_id": config.telegram_chatid,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        print(f"❌ Failed to send message. Status: {response.status_code}, Error: {response.text}")


async def send_semi_auto_telegram_message(project, amount):
    """Send telegram message for semi-auto bidding."""
    project_seo_url = f"https://www.freelancer.com/projects/{html.escape(project['seo_url'])}/details"

    # Escape all dynamic text
    safe_title = html.escape(str(project['title']))
    safe_description = project['description']
    if len(safe_description) > 3500:
        safe_description = "[Description removed due to length]"
    else:
        safe_description = html.escape(safe_description)

    safe_amount = html.escape(str(amount))
    safe_submit_date = html.escape(str(project['submit_date']))
    safe_budget_min = html.escape(str(project['budget_min']))
    safe_budget_max = html.escape(str(project['budget_max']))
    safe_exchange_rate = html.escape(str(project['currency_exchange_rate']))
    safe_bid_avg = html.escape(str(project['bid_avg']))
    safe_bid_count = html.escape(str(project['bid_count']))
    type = html.escape(str(project['type']))

    place_bid_url = f"{config.host_url}/place_bid?project_id={urllib.parse.quote(str(project['id']))}"
    gen_bid_url = f"{config.host_url}/gen_proposal?project_id={urllib.parse.quote(str(project['id']))}"
    try:
        budget_min = float(safe_exchange_rate) * float(safe_budget_min)
        budget_max = float(safe_exchange_rate) * float(safe_budget_max)
        amount     = float(safe_exchange_rate) * float(safe_amount)
        bid_avg    = float(safe_exchange_rate) * float(safe_bid_avg)

        message = (
            f"🚨 <b>New Project Alert [CONVERTED]</b>\n\n"
            f"Project: <b>{safe_title}</b>\n"
            f"<a href='{project_seo_url}'>View Project on Freelancer</a>\n"
            f"Time posted: <b>{safe_submit_date}</b>\n"
            f"Budget min: ${budget_min}\n"
            f"Budget max: ${budget_max}\n"
            f"Proposed Amount: ${amount} {type}\n"
            f"Bid Average: {bid_avg}\n"
            f"Bid Count: {safe_bid_count}\n\n"
            f"Description: {safe_description}\n\n"
            f"<a href='{place_bid_url}'>✅ Place bid</a>\n\n"
            f"<a href='{gen_bid_url}'>✅ Generate Proposal</a>"
        )
    except Exception:
        message = (
            f"🚨 <b>New Project Alert [RAW]</b>\n\n"
            f"Project: <b>{safe_title}</b>\n"
            f"<a href='{project_seo_url}'>View Project on Freelancer</a>\n"
            f"Time posted: <b>{safe_submit_date}</b>\n"
            f"Budget min: {safe_budget_min}\n"
            f"Budget max: {safe_budget_max}\n"
            f"Proposed Amount: {safe_amount} {type}\n"
            f"Bid Average: {safe_bid_avg}\n"
            f"Bid Count: {safe_bid_count}\n\n"
            f"Description: {safe_description}\n\n"
            f"<a href='{gen_bid_url}'>✅ Generate Proposal</a>"
        )

    payload = {
        "chat_id": config.telegram_chatid,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        print(f"❌ Failed to send message. Status: {response.status_code}, Error: {response.text}")
        return False
    return True

async def send_project_followup_alert(data):
    project_seo_url = f"https://www.freelancer.com/projects/{html.escape(data['seo_url'])}/details"
    safe_title = html.escape(str(data['title']))
    message = (
        f"🚨 <b>Project Follow Up Alert</b>\n\n"
        f"Project <b>{safe_title}</b> has been awarded to a freelancer\n"
        f"Status: <b>{data["status"]}</b>\n\n"
        f"<a href='{project_seo_url}'>View Project on Freelancer</a>\n"
    )
    payload = {
        "chat_id": config.telegram_chatid,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        print(f"❌ Failed to send message. Status: {response.status_code}, Error: {response.text}")
        return False
    return True
    
async def send_generated_proposal_message(proposal):
    """Send telegram message for semi-auto bidding."""

    message = (
        f"✅ <b>Proposal Generated</b>\n\n"
        f"{proposal}\n"
    )
    
    payload = {
        "chat_id": config.telegram_chatid,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        print(f"❌ Failed to send message. Status: {response.status_code}, Error: {response.text}")
        return False
    return True

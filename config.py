"""Configuration module for freelancer bot."""

import os
from dotenv import load_dotenv
from freelancersdk.session import Session
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from telegram.ext import Application
from quart import Quart, request
from g4f.Provider import Yqcloud, Blackbox, PollinationsAI, OIVSCodeSer2, WeWordle, CohereForAI_C4AI_Command
import asyncio

# Load environment variables
load_dotenv()

# Environment configurations
token = os.getenv("PRODUCTION")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chatid = os.getenv("TELEGRAM_CHATID")
AUTHORIZED_USER_IDS = os.getenv("AUTHORIZED_USER_IDS", "")
host_url = os.getenv("HOST_URL")

# Global configuration
base_url = "https://www.freelancer.com"
project_number = 30
project_number_semi_auto = 70
look_back_hours = 24
exhaustion_sleep_time = 3
AUTHORIZED_USER_IDS = [int(x.strip()) for x in AUTHORIZED_USER_IDS.split(",") if x.strip()]
bid_avg_percent = 0.50
only_fixed = True
min_budget = 30
proposal_yrs_exp = 4
bid_period = 3

# Initialize external services
session = Session(oauth_token=token, url=base_url)
quart_app = Quart(__name__)
application = Application.builder().token(telegram_bot_token).build()

# Global flags and settings
id_flag = True
shutdown_flag = False
sleep_time = 0.0625
sleep_time_semi = 0.166
shutdown_event = asyncio.Event()

# Service control flags
auto_paused = False
semi_auto_paused = False

# Search filter configuration
auto_jobs = [3131,3033,3030] # eg. 3131,3033,3030,3931,333,3032
search_filter_auto = create_search_projects_filter(
    jobs=auto_jobs
)

# Project detail configuration
semi_auto_jobs = [3131,3033,3030] # eg. 3131,3033,3030,3931,333,3032
search_filter_semi_auto = create_search_projects_filter(
    jobs=semi_auto_jobs
)

project_detail = {
    "full_description": True,
    "job_details": True
}

# AI providers and models configuration
ai_chats = [
    {"provider": CohereForAI_C4AI_Command, "model": "command-a-03-2025", "label": "Cohere - Command A 03-2025"},
    {"provider": CohereForAI_C4AI_Command, "model": "command-r7b-12-2024", "label": "Cohere - Command R7B"},
    {"provider": Yqcloud, "model": "gpt-4", "label": "Yqcloud - GPT-4"},
    {"provider": Blackbox, "model": "gpt-4", "label": "Blackbox - GPT-4"},
    {"provider": PollinationsAI, "model": None, "label": "PollinationsAI - DEFAULT"},
    {"provider": OIVSCodeSer2, "model": "gpt-4o-mini", "label": "OIVSCodeSer2 - gpt-4o-mini"},
    {"provider": WeWordle, "model": "gpt-4", "label": "WeWordle - GPT-4"},
]

# AI service global variables
failed_ai_chats = set()
ai_chat_to_use = 0

# config.py

PROPOSAL_PROMPT_TEMPLATE = """
Write a freelance job proposal message for the project below:

project = [
    Title: {title}

    Description: {description}
]

RULES:
- first line should be or say "generated" and then a new line
- proposal language should be {language}
- Be between 100 and 1000 characters
- Sound friendly and human
- Begin proposal with "Hello," in {language} then a new line, Don't use Dear [Client] or Don't use Hello [Client]
- use the word "I" only when needed so it sound like it is typed by a human freelancer applying for a job
- Don't use words like believe, feel or related emotional words. Sound confident saying I have {proposal_yrs_exp}+ years experience in the field
- Don't list anything, write everything in paragraph form
- Include a very brief high-level summary of how I would approach the project
- Mention very briefly, possible solutions where relevant (but avoid technical detail)
- Towards the end of the proposal, ask the client to send a message for samples of similar project
- Don't use exclamation marks, emojis or Best regards [Your Name]
- use "Thanks, Adegoke. M" at the end
- The proposal language should be same language as the description (eg. english, polish, indian, russian etc...)
"""

description = """
You are a language detection system. 
Your task: Detect the language of the following text. 

Rules:  
- Respond with only the language name.  
- Respond with exactly one word (e.g., english).  
- Do not include punctuation, explanations, or extra words.  
- Do not return codes (e.g., "fr", "en"), only the full language name.  

Text: {text}
"""

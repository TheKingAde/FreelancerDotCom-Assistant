"""Main entry point for the freelancer bot."""

import asyncio
import signal
from telegram.ext import CommandHandler
import config
from freelancer_service import auto_function, semi_auto_function
from bot_commands import start, start_auto, start_semi, stop, stop_auto, stop_semi, status
from database import project_id_exists, store_project_keys
from utils import interruptible_sleep, load_projects, save_projects, add_project, delete_project, get_project
from ai_service import send_ai_request
from freelancersdk.resources.projects import place_project_bid
from freelancersdk.resources.projects.exceptions import ProjectsNotFoundException, BidNotPlacedException
from telegram_service import send_auto_telegram_message, send_semi_auto_telegram_message, send_generated_proposal_message

def handle_exit(signum, frame):
    """Handle exit signals."""
    config.shutdown_flag = True
    config.shutdown_event.set()

signal.signal(signal.SIGINT, handle_exit)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # kill command

@config.quart_app.route("/")
async def home():
    """Home route for the web server."""
    return "✅ Freelancer bot is running!"

@config.quart_app.route("/gen_proposal", methods=["GET"])
async def gen_proposal():
    """Generate Proposal"""
    from freelancer_service import user_id

    project_id = config.request.args.get("project_id")  
    if project_id:
        project = get_project(str(project_id))
        if project == None:
            return {"status": "null", "message": "project not found in storage"}

        project_title = project['data']['title']
        project_description = project['data']['description']
        lang_prompt = config.description.format(text=project_description)
        lang = await send_ai_request(lang_prompt, strict=False)
        if lang == False:
            return {"status": "error", "message": "Failed to detect language"}

        prompt = config.PROPOSAL_PROMPT_TEMPLATE.format(language=lang,title=project_title,description=project_description,proposal_yrs_exp=config.proposal_yrs_exp)
        proposal = await send_ai_request(prompt)
        if proposal != False:
            if await send_generated_proposal_message(proposal):
                store_project_keys(project_id)
                return {"status": "ok", "message": "proposal sent to telegram"}
            else:
                return {"status": "error", "message": "failed to send proposal to telegram"}
        else:
            return {"status": "error", "message": "Failed to generate proposal"}
    return {"status": "error", "message": "missing project_id"}
        

@config.quart_app.route("/place_bid", methods=["GET"])
async def place_bid():
    from freelancer_service import user_id

    project_id = config.request.args.get("project_id")  
    if project_id:
        project = get_project(str(project_id))
        if project == None:
            return {"status": "null", "message": "project not found in storage"}

        project_title = project['data']['title']
        project_description = project['data']['description']
        lang_prompt = config.description.format(text=project_description)
        lang = await send_ai_request(lang_prompt, strict=False)
        if lang == False:
            return {"status": "error", "message": "Failed to detect language"}

        prompt = config.PROPOSAL_PROMPT_TEMPLATE.format(language=lang,title=project_title,description=project_description,proposal_yrs_exp=config.proposal_yrs_exp)
        proposal = await send_ai_request(prompt)
        if proposal != False:
            bid_data = {
                'project_id': int(project_id),
                'bidder_id': user_id,
                'amount': project['amount'],
                'period': config.bid_period,
                'milestone_percentage': 100,
                'description': proposal,
            }
            
            try:
                response = place_project_bid(session=config.session, **bid_data)
                store_project_keys(project_id)
                await send_auto_telegram_message(str(project_title), "proposal", proposal, project['data']['seo_url'])
            except BidNotPlacedException as e:
                if str(e) == "You have already bid on that project.":
                    store_project_keys(str(project_id))

                if str(e) == "You must sign the NDA before you can bid on this project.":
                    proposal_data = {
                        'title': project_title,
                        'amount': project['amount'],
                    }
                    await send_auto_telegram_message(proposal_data, "nda", proposal, project['data']['seo_url'])
                    store_project_keys(str(project_id))
                else:
                    print('Server response: {}'.format(str(e)))
                    proposal_data = {
                        'title': project_title,
                        'amount': project['amount'],
                        'error_message': str(e)
                    }
                    await send_auto_telegram_message(proposal_data, "error", proposal, project['data']['seo_url'] or "")
                    store_project_keys(str(project_id))
        else:
            print(f"Failed to generate proposal for Project ID: {project_id}")
            proposal = "N/A"
            await send_auto_telegram_message(str(project_title), "gen_proposal", proposal, project['data']['seo_url'])
        return {"status": "ok", "project_id": project_id}
    return {"status": "error", "message": "missing project_id"}

async def run_bot():
    """Run the bot with all services."""
    # Add command handlers
    config.application.add_handler(CommandHandler("start", start))
    config.application.add_handler(CommandHandler("start_auto", start_auto))
    config.application.add_handler(CommandHandler("start_semi", start_semi))
    config.application.add_handler(CommandHandler("stop", stop))
    config.application.add_handler(CommandHandler("stop_auto", stop_auto))
    config.application.add_handler(CommandHandler("stop_semi", stop_semi))
    config.application.add_handler(CommandHandler("status", status))
    
    # Initialize and start telegram bot
    await config.application.initialize()
    await config.application.start()
    await config.application.updater.start_polling()

    # Start web server
    server = asyncio.create_task(
        config.quart_app.run_task(
            host="0.0.0.0",
            port=5000,
            debug=False,
            shutdown_trigger=config.shutdown_event.wait
        )
    )
    task_auto = asyncio.create_task(auto_function())
    task_semi_auto = asyncio.create_task(semi_auto_function())

    try:
        await config.shutdown_event.wait()
    finally:
        print("🛑 Shutting down freelancer bot...")
        task_auto.cancel()
        task_semi_auto.cancel()
        server.cancel()
        try:
            await task_auto
            await task_semi_auto
            await server
        except asyncio.CancelledError:
            pass
        print("✅ shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n")
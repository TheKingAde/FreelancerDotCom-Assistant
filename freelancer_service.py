"""Freelancer API operations."""

import asyncio
from datetime import datetime, timedelta, timezone
from freelancersdk.resources.projects.exceptions import ProjectsNotFoundException, BidNotPlacedException
from freelancersdk.resources.projects import search_projects, place_project_bid
from freelancersdk.resources.users.exceptions import SelfNotRetrievedException
from freelancersdk.resources.projects.projects import (
    get_projects, get_project_by_id
)
from freelancersdk.resources.projects.helpers import (
    create_get_projects_object, create_get_projects_project_details_object,
    create_get_projects_user_details_object
)
from freelancersdk.resources.users import get_self
import config
from database import project_id_exists, store_project_keys, get_all_project_ids, delete_project_by_id
from ai_service import send_ai_request
from telegram_service import send_auto_telegram_message, send_semi_auto_telegram_message, send_project_followup_alert
from utils import interruptible_sleep, load_projects, save_projects, add_project, delete_project, get_project
from lookup_utils import lookup_load_projects, lookup_save_projects, lookup_add_project, lookup_delete_project, lookup_get_project

async def auto_function():
    """Main auto bidding function."""
    global user_id
    try:
        while not config.shutdown_flag:
            try:
                if config.id_flag:
                    try:
                        response = get_self(session=config.session)
                        user_id = response.get("id")
                        username = response.get("username")
                        print("Starting FREELANCERDOTCOM Assistant...")
                        print(f"Username={username}")
                        print(f"UserID={user_id}")
                        print("running...")
                        config.id_flag = False
                    except SelfNotRetrievedException as e:
                        print('Server response: {}'.format(str(e)))
                        await asyncio.sleep(config.sleep_time)
                        continue
                if len(config.auto_jobs) < 1:
                    await asyncio.sleep(config.sleep_time)
                    continue
                if config.auto_paused:
                    await asyncio.sleep(config.sleep_time)
                    continue
                try:
                    try:
                        await interruptible_sleep(
                            hours=config.sleep_time,
                            check_interval=1,
                            shut_down_flag=lambda: config.shutdown_flag
                        )
                    except KeyboardInterrupt:
                        break
                    
                    response = search_projects(
                        session=config.session,
                        query=None,
                        search_filter=config.search_filter_auto,
                        project_details=config.project_detail,
                        limit=config.project_number,
                        offset=0,
                        active_only=True
                    )
                except ProjectsNotFoundException as e:
                    if str(e) == "You have made too many of these requests":
                        print("You have made too many of these requests")
                        try:
                            await interruptible_sleep(
                                hours=config.sleep_time,
                                check_interval=1,
                                shut_down_flag=lambda: config.shutdown_flag
                            )
                        except KeyboardInterrupt:
                            break
                    else:
                        print('Server response: {}'.format(str(e)))
                        await send_auto_telegram_message(str(e), "error", proposal="", seo_url="")
                    await asyncio.sleep(config.sleep_time)
                    continue

                for project in reversed(response.get("projects", [])):
                    data = {
                        "id": project.get("id"),
                        "title": project.get("title"),
                        "status": project.get("status"),
                        "type": project.get("type"),
						"owner_id": project.get("owner_id", 0),
                        "seo_url": project.get("seo_url"),
                        "currency_exchange_rate": project.get("currency", {}).get("exchange_rate"),
                        "description": project.get("description"),
                        "submit_date": datetime.fromtimestamp(project.get("submitdate", 0), tz=timezone.utc).isoformat(),
                        "nonpublic": project.get("nonpublic"),
                        "budget_min": project.get("budget", {}).get("minimum"),
                        "budget_max": project.get("budget", {}).get("maximum"),
                        "urgent": project.get("urgent"),
                        "bid_count": project.get("bid_stats", {}).get("bid_count"),
                        "bid_avg": project.get("bid_stats", {}).get("bid_avg"),
                        "time_submitted": datetime.fromtimestamp(project.get("time_submitted", 0), tz=timezone.utc).isoformat(),
                        "time_updated": datetime.fromtimestamp(project.get("time_updated", 0), tz=timezone.utc).isoformat()
                    }
                    
                    if project_id_exists(str(data["id"])) or get_project(str(data["id"])):
                        continue

                    time_submitted = data["time_submitted"]
                    budget_min = data["budget_min"]
                    budget_max = data["budget_max"]
                    bid_avg = data["bid_avg"]
                    bid_status = data["status"]
                    currency_exchange_rate = data["currency_exchange_rate"]
                    type = data["type"]
                    owner_id = data["owner_id"]

                    time_submitted_dt = datetime.fromisoformat(data["time_submitted"])
                    now = datetime.now(timezone.utc)
                    if now - time_submitted_dt >= timedelta(hours=config.look_back_hours):
                        print(f"Project {data['id']} is older than {config.look_back_hours} hours, skipping...")
                        add_project(str(data["id"]), data, 0)
                        await asyncio.sleep(config.sleep_time)
                        continue
                    
                    if bid_status != "active":
                        print(f"Project {data['id']} is not active, skipping...")
                        add_project(str(data["id"]), data, 0)
                        await asyncio.sleep(config.sleep_time)
                        continue
                    
                    if budget_max is None or budget_min is None:
                        print(f"⚠️ Project {data['id']} has missing budget info, skipping...")
                        response = await send_semi_auto_telegram_message(data, 0)
                        add_project(str(data["id"]), data, 0)
                        await asyncio.sleep(config.sleep_time)
                        continue
						
                    if str(type) == "fixed":
                        budget = float(budget_max) * float(currency_exchange_rate)
                        if budget < config.min_budget:
                            print("Project budget is lower than minimum budget, skipping...")
                            amount = round(float(budget_max) * float(config.bid_avg_percent))
                            if amount < (float(config.min_budget) / float(currency_exchange_rate)):
                                amount = (float(config.min_budget) / float(currency_exchange_rate))
                            response = await send_semi_auto_telegram_message(data, amount)
                            add_project(str(data["id"]), data, amount)
                            await asyncio.sleep(config.sleep_time)
                            continue
                    elif config.only_fixed:
                        amount = round(float(budget_max) * float(config.bid_avg_percent))
                        if amount < float(budget_min):
                            amount = max(round(float(budget_max) * (float(config.bid_avg_percent) / 2)), budget_min)
                        response = await send_semi_auto_telegram_message(data, amount)
                        add_project(str(data["id"]), data, amount)
                        await asyncio.sleep(config.sleep_time)
                        continue

                    lang_prompt = config.description.format(text=data["description"])
                    lang = await send_ai_request(lang_prompt, strict=False)
                    if lang == False:
                        print(f"Failed to detect language for Project ID: {data['id']}, sleeping for {config.exhaustion_sleep_time} hour(s)")
                        proposal = data['id']
                        await send_auto_telegram_message(str(data["title"]), "gen_proposal", proposal, data["seo_url"])
                        try:
                            await interruptible_sleep(
                                hours=config.sleep_time,
                                check_interval=5,
                                shut_down_flag=lambda: config.shutdown_flag
                            )
                        except KeyboardInterrupt:
                            break
                        continue

                    prompt = config.PROPOSAL_PROMPT_TEMPLATE.format(language=lang,title=data["title"],description=data["description"],proposal_yrs_exp=config.proposal_yrs_exp)
                    proposal = await send_ai_request(prompt)
                    if proposal != False:
                        amount = round(float(budget_max) * float(config.bid_avg_percent))
                        if str(type) == "fixed":
                            if amount < (float(config.min_budget) / float(currency_exchange_rate)):
                                amount = (float(config.min_budget) / float(currency_exchange_rate))
                        if amount < float(budget_min):
                            amount = max(round(float(budget_max) * (float(config.bid_avg_percent) / 2)), budget_min)
                        
                        bid_data = {
                            'project_id': int(data["id"]),
                            'bidder_id': user_id,
                            'amount': amount,
                            'period': config.bid_period,
                            'milestone_percentage': 100,
                            'description': proposal,
                        }
                        
                        try:
                            try:
                                await interruptible_sleep(
                                    hours=config.sleep_time,
                                    check_interval=1,
                                    shut_down_flag=lambda: config.shutdown_flag
                                )
                            except KeyboardInterrupt:
                                break
                            if project_id_exists(str(data["id"])):
                                continue
                            response = place_project_bid(session=config.session, **bid_data)
                            store_project_keys(str(data['id']))
                            await send_auto_telegram_message(str(data["title"]), "proposal", proposal, data["seo_url"])
                            
                        except BidNotPlacedException as e:
                            if str(e) == "You have used all of your bids.":
                                try:
                                    await interruptible_sleep(
                                        hours=config.exhaustion_sleep_time,
                                        check_interval=5,
                                        shut_down_flag=lambda: config.shutdown_flag
                                    )
                                except KeyboardInterrupt:
                                    break
                                continue
                            
                            if str(e) == "You have already bid on that project.":
                                store_project_keys(str(data['id']))
                                continue
                            
                            if str(e) == "You must sign the NDA before you can bid on this project.":
                                proposal_data = {
                                    'title': data["title"],
                                    'amount': amount,
									'currency_exchange_rate': data["currency_exchange_rate"]
                                }
                                await send_auto_telegram_message(proposal_data, "nda", proposal, data["seo_url"])
                                store_project_keys(str(data['id']))
                                continue
                            if str(e) == "You appear to be bidding too fast. Please take the time to write a quality bid. Improve your trust score by getting Verified by Freelancer.":
                                await send_auto_telegram_message(str(e), "error", proposal, data["seo_url"])
                                try:
                                    await interruptible_sleep(
                                        hours=config.sleep_time * 3,
                                        check_interval=1,
                                        shut_down_flag=lambda: config.shutdown_flag
                                    )
                                except KeyboardInterrupt:
                                    break
                                continue
                            else:
                                print('Server response: {}'.format(str(e)))
                                proposal_data = {
                                    'title': data["title"],
                                    'amount': amount,
									'currency_exchange_rate': data["currency_exchange_rate"],
                                    'error_message': str(e),
				                    'id': data['id']
                                }
                                await send_auto_telegram_message(proposal_data, "error", proposal, data["seo_url"] or "")
                                store_project_keys(str(data['id']))
                                continue
                    else:
                        print(f"Failed to generate proposal for Project ID: {data['id']}, sleeping for {config.exhaustion_sleep_time} hour(s)")
                        proposal = data['id']
                        await send_auto_telegram_message(str(data["title"]), "gen_proposal", proposal, data["seo_url"])
                        try:
                            await interruptible_sleep(
                                hours=config.sleep_time,
                                check_interval=5,
                                shut_down_flag=lambda: config.shutdown_flag
                            )
                        except KeyboardInterrupt:
                            break
                        continue
                
                await asyncio.sleep(config.sleep_time)
            except Exception as e:
                print(f"Error processing projects: {e}")
                await send_semi_auto_telegram_message(data, 0)
                continue
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
    finally:
        print("[🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨]")

async def semi_auto_function():
    """Semi-automatic function placeholder."""
    try:
        while not config.shutdown_flag:
            if len(config.semi_auto_jobs) < 1:
                await asyncio.sleep(config.sleep_time)
                continue
            if config.semi_auto_paused:
                await asyncio.sleep(config.sleep_time)
                continue

            bidden_projects = get_all_project_ids()
            q = create_get_projects_object(
                project_ids=[bidden_projects],
                project_details=create_get_projects_project_details_object(
                    selected_bids=True,
                ),
                limit=50
             )
            try:
                p = get_projects(config.session, q)
            except ProjectsNotFoundException as e:
                print('Error message: {}'.format(e.message))
                print('Server response: {}'.format(e.error_code))
            else:
                if p:
                    for project in reversed(p.get("projects", [])):
                        data = {
                            "id": project.get("id"),
                            "title": project.get("title"),
                            "status": project.get("status"),
                            "seo_url": project.get("seo_url")
                        }
                        if lookup_get_project(str(data["id"])):
                            continue
                        if await send_project_followup_alert(data):
                            lookup_add_project(str(data["id"]))
            try:
                try:
                    response = search_projects(
                        session=config.session,
                        query=None,
                        search_filter=config.search_filter_semi_auto,
                        project_details=config.project_detail,
                        limit=config.project_number_semi_auto,
                        offset=0,
                        active_only=True
                    )
                except ProjectsNotFoundException as e:
                    if str(e) == "You have made too many of these requests":
                        print("You have made too many of these requests")
                        try:
                            await interruptible_sleep(
                                hours=config.sleep_time_semi,
                                check_interval=1,
                                shut_down_flag=lambda: config.shutdown_flag
                            )
                        except KeyboardInterrupt:
                            break
                    else:
                        print('Server response: {}'.format(str(e)))
                        await send_auto_telegram_message(str(e), "error", proposal="", seo_url="")
                    await asyncio.sleep(config.sleep_time)
                    continue

                for project in reversed(response.get("projects", [])):
                    data = {
                        "id": project.get("id"),
                        "title": project.get("title"),
                        "status": project.get("status"),
                        "type": project.get("type"),
                        "owner_id": project.get("owner_id", 0),
                        "seo_url": project.get("seo_url"),
                        "currency_exchange_rate": project.get("currency", {}).get("exchange_rate"),
                        "description": project.get("description"),
                        "submit_date": datetime.fromtimestamp(project.get("submitdate", 0), tz=timezone.utc).isoformat(),
                        "nonpublic": project.get("nonpublic"),
                        "budget_min": project.get("budget", {}).get("minimum"),
                        "budget_max": project.get("budget", {}).get("maximum"),
                        "urgent": project.get("urgent"),
                        "bid_count": project.get("bid_stats", {}).get("bid_count"),
                        "bid_avg": project.get("bid_stats", {}).get("bid_avg"),
                        "time_submitted": datetime.fromtimestamp(project.get("time_submitted", 0), tz=timezone.utc).isoformat(),
                        "time_updated": datetime.fromtimestamp(project.get("time_updated", 0), tz=timezone.utc).isoformat()
                    }
                    
                    if project_id_exists(str(data["id"])) or get_project(str(data["id"])):
                        continue

                    time_submitted = data["time_submitted"]
                    budget_min = data["budget_min"]
                    budget_max = data["budget_max"]
                    bid_avg = data["bid_avg"]
                    bid_status = data["status"]
                    currency_exchange_rate = data["currency_exchange_rate"]
                    type = data["type"]

                    time_submitted_dt = datetime.fromisoformat(data["time_submitted"])
                    now = datetime.now(timezone.utc)
                    if now - time_submitted_dt >= timedelta(hours=config.look_back_hours):
                        print(f"Project {data['id']} is older than {config.look_back_hours} hours, skipping...")
                        store_project_keys(str(data['id']))
                        await asyncio.sleep(config.sleep_time)
                        continue
                    
                    if bid_status != "active":
                        print(f"Project {data['id']} is not active, skipping...")
                        store_project_keys(str(data['id']))
                        await asyncio.sleep(config.sleep_time)
                        continue
                    
                    if budget_max is None or budget_min is None:
                        print(f"⚠️ Project {data['id']} has missing budget info, skipping...")
                        await send_semi_auto_telegram_message(data, 0)
                        store_project_keys(str(data['id']))
                        await asyncio.sleep(config.sleep_time)
                        continue

                    amount = round(float(budget_max) * float(config.bid_avg_percent))
                    if str(type) == "fixed":
                        if amount < (float(config.min_budget) / float(currency_exchange_rate)):
                            amount = (float(config.min_budget) / float(currency_exchange_rate))
                    if amount < float(budget_min):
                        amount = max(round(float(budget_max) * (float(config.bid_avg_percent) / 2)), budget_min)
                    response = await send_semi_auto_telegram_message(data, amount)
                    if response:
                        add_project(str(data["id"]), data, amount)
                        continue
                try:
                    await interruptible_sleep(
                        hours=config.sleep_time_semi,
                        check_interval=1,
                        shut_down_flag=lambda: config.shutdown_flag
                    )
                except KeyboardInterrupt:
                    break
            except Exception as e:
                print(f"Error processing projects: {e}")
                await send_semi_auto_telegram_message(data, 0)
                continue
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
    finally:
        print("[🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨]")

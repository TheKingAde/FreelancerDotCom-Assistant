"""AI service for generating proposals."""

import asyncio
import re
import g4f
import config

async def send_ai_request(prompt: str, strict: bool = True):
    """Send AI request to generate proposal or detect language.
    
    Args:
        prompt (str): The user prompt to send.
        strict (bool): 
            - True → validate with 'hello' check (proposal mode).
            - False → validate that response is exactly one word (lang detect mode).
    """

    total_chats = len(config.ai_chats)
    attempts = 0

    while attempts < total_chats:
        current_chat = config.ai_chats[config.ai_chat_to_use]

        # Skip failed providers
        if config.ai_chat_to_use in config.failed_ai_chats:
            config.ai_chat_to_use = (config.ai_chat_to_use + 1) % total_chats
            attempts += 1
            continue

        await asyncio.sleep(config.sleep_time)

        try:
            kwargs = {
                "provider": current_chat["provider"],
                "messages": [{"role": "user", "content": prompt}],
            }
            if current_chat["model"]:
                kwargs["model"] = current_chat["model"]

            response = g4f.ChatCompletion.create(**kwargs)

            if response and isinstance(response, str):
                resp = response.strip()

                if strict:
                    # Proposal mode: must start with "hello"
                    lines = resp.splitlines()
                    if len(lines) >= 1 and "generated" in lines[0].lower():
                        # Remove the word "generated" from the proposal
                        lines[0] = lines[0].lower().replace("generated", "").strip()
                        return "\n".join(lines).strip()
                else:
                    # Lang detect mode: must be exactly one word
                    if len(resp.split()) == 1:
                        return resp

            # Mark provider as failed
            config.failed_ai_chats.add(config.ai_chat_to_use)

        except Exception:
            config.failed_ai_chats.add(config.ai_chat_to_use)

        # Move to next provider
        config.ai_chat_to_use = (config.ai_chat_to_use + 1) % total_chats
        attempts += 1

    # All failed → reset for next cycle
    config.failed_ai_chats.clear()
    return False

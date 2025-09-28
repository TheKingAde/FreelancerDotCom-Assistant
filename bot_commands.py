"""Bot commands and handlers."""

from telegram import Update
from telegram.ext import ContextTypes
import config

def is_authorized(update: Update) -> bool:
    """Check if the user is authorized."""
    return update.effective_user and update.effective_user.id in config.AUTHORIZED_USER_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command with optional service parameter."""

    if not is_authorized(update):
        await update.message.reply_text("❌ You are not an Authorized user")
        return

    # Get the command arguments
    args = context.args
    if not args:
        config.auto_paused = False
        config.semi_auto_paused = False
        await update.message.reply_text(
            "✅ All freelancing services started!\n"
            "🔄 Auto bidding: Running\n"
            "🔄 Semi-auto bidding: Running"
        )
    else:
        await update.message.reply_text(
            "❌ Too many parameters. Use:\n"
            "• /start - Start all services\n"
        )

async def start_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start_auto command."""
    
    if not is_authorized(update):
        await update.message.reply_text("❌ You are not an Authorized user")
        return

    args = context.args
    if not args:
        config.auto_paused = False
        await update.message.reply_text(
            "✅ Auto freelancing services started!\n"
            "🔄 Auto bidding: Running\n"
            "Use /stop_auto to stop/paused auto services\n"
            "Use /stop to stop/pause all services."
        )
    else:
        await update.message.reply_text(
            "❌ Too many parameters. Use:\n"
            "• /start_auto - Start auto services\n"
        )

async def start_semi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start_semi command."""

    if not is_authorized(update):
        await update.message.reply_text("❌ You are not an Authorized user")
        return

    args = context.args
    if not args:
        config.semi_auto_paused = False
        await update.message.reply_text(
            "✅ Semi auto freelancing services started!\n"
            "🔄 Auto bidding: Running\n"
            "Use /stop_semi to stop/pause semi services\n"
            "Use /stop to stop/pause all services."
        )
    else:
        await update.message.reply_text(
            "❌ Too many parameters. Use:\n"
            "• /start_semi - Start semi services\n"
        )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stop command"""

    if not is_authorized(update):
        await update.message.reply_text("❌ You are not an Authorized user")
        return

    args = context.args
    if not args:
        config.auto_paused = True
        config.semi_auto_paused = True
        await update.message.reply_text(
            "⏸️ All freelancing services paused!\n"
            "⏸️ Auto bidding: Paused\n"
            "⏸️ Semi-auto bidding: Paused\n\n"
            "Use /start to resume all services."
        )
    else:
        await update.message.reply_text(
            "❌ Invalid service parameter. Use:\n"
            "• /stop - Stop all services\n"
            "• /stop auto - Stop auto service\n"
            "• /stop semi - Stop semi-auto service"
        )

async def stop_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stop_auto command"""

    if not is_authorized(update):
        await update.message.reply_text("❌ You are not an Authorized user")
        return

    args = context.args
    if not args:
        config.auto_paused = True
        await update.message.reply_text(
            "⏸️ Auto freelancing services paused!\n"
            "⏸️ Auto bidding: Paused\n"
            "Use /start_auto to start/resume auto services\n"
            "Use /start to start/resume all services."
        )
    else:
        await update.message.reply_text(
            "❌ Invalid service parameter. Use:\n"
            "• /stop_auto - Stop/pause auto services\n"
        )

async def stop_semi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stop_semi command"""

    if not is_authorized(update):
        await update.message.reply_text("❌ You are not an Authorized user")
        return

    args = context.args  
    if not args:
        config.semi_auto_paused = True
        await update.message.reply_text(
            "⏸️ Semi freelancing services paused!\n"
            "⏸️ Semi-auto bidding: Paused\n\n"
            "Use /start_semi to start/resume semi auto services\n"
            "Use /start to start/resume all services."
        )
    else:
        await update.message.reply_text(
            "❌ Invalid service parameter. Use:\n"
            "• /stop_semi - Stop/pause semi services\n"
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /status command to show current service status."""

    if not is_authorized(update):
        await update.message.reply_text("❌ You are not an Authorized user")
        return

    auto_status = "⏸️ Paused" if config.auto_paused else "🔄 Running"
    semi_auto_status = "⏸️ Paused" if config.semi_auto_paused else "🔄 Running"
    
    await update.message.reply_text(
        f"📊 FREELANCERDOTCOM Assistant Status:\n\n"
        f"Auto bidding: {auto_status}\n"
        f"Semi-auto bidding: {semi_auto_status}\n\n"
    )

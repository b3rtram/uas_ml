"""Discord bot front-end for the income-prediction agent.

The bot connects OUT to Discord over the gateway (WebSocket), so it runs fine
locally behind a router — no public URL or open port needed. Every incoming
message is handed to the same ``run_agent`` used by the Streamlit chat page,
which lets the local LLM call the income model as a tool.

Setup:
  1. Create a bot at https://discord.com/developers/applications
     -> "Bot" -> enable the **MESSAGE CONTENT INTENT**.
  2. Put its token into ../.env as  DISCORD_BOT_TOKEN=...
  3. Invite the bot to your server (OAuth2 URL with the "bot" scope and the
     "Send Messages" / "Read Message History" permissions).
  4. Make sure `ollama serve` is running, then:  python discord_bot.py

Usage:
  - In a DM to the bot: just write your question.
  - In a server channel: @mention the bot in your message.
"""

import asyncio
import os
import re
from collections import defaultdict, deque
from pathlib import Path

import discord
from dotenv import load_dotenv

from agent import DEFAULT_MODEL, run_agent

# Load ../.env (repo root), regardless of where the bot is started from.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
MODEL = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
HISTORY_TURNS = 6  # remember the last 6 messages (≈3 exchanges) per channel
DISCORD_LIMIT = 2000  # max characters per Discord message

intents = discord.Intents.default()
intents.message_content = True  # requires the Message Content Intent in the portal
client = discord.Client(intents=intents)

# Per-channel short-term memory.
histories: dict[int, deque] = defaultdict(lambda: deque(maxlen=HISTORY_TURNS))


def _strip_mention(message: discord.Message) -> str:
    """Remove the bot mention from the message text."""
    text = message.content
    for uid in (client.user.id,):
        text = re.sub(rf"<@!?{uid}>", "", text)
    return text.strip()


def _chunk(text: str, size: int = DISCORD_LIMIT):
    """Split a long answer into Discord-sized pieces."""
    return [text[i : i + size] for i in range(0, len(text), size)] or ["…"]


@client.event
async def on_ready():
    print(f"Logged in as {client.user} — model: {MODEL}", flush=True)


@client.event
async def on_message(message: discord.Message):
    # Never react to our own (or other bots') messages.
    if message.author.bot:
        return

    is_dm = message.guild is None
    mentioned = client.user in message.mentions
    if not is_dm and not mentioned:
        return  # in servers, only respond when explicitly mentioned

    prompt = message.content if is_dm else _strip_mention(message)
    if not prompt:
        await message.channel.send("Ask me something about income 🙂 (e.g. \"45, manager, 60 hours/week\")")
        return

    history = histories[message.channel.id]
    history.append({"role": "user", "content": prompt})

    try:
        async with message.channel.typing():
            answer, _tool_steps = await asyncio.to_thread(
                run_agent, list(history), MODEL
            )
        if not answer.strip():
            answer = "(The model returned no text answer.)"
    except Exception as exc:
        answer = (
            f"⚠️ Error calling the agent: `{exc}`\n"
            "Is `ollama serve` running and the model available?"
        )
        history.pop()  # don't keep a failed turn in memory
        await message.channel.send(answer)
        return

    history.append({"role": "assistant", "content": answer})
    for piece in _chunk(answer):
        await message.channel.send(piece)


def main():
    if not TOKEN:
        raise SystemExit(
            "DISCORD_BOT_TOKEN is not set. Add it to ../.env."
        )
    client.run(TOKEN)


if __name__ == "__main__":
    main()

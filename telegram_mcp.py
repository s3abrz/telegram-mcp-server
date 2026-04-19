import asyncio
import json
import logging
import os
import sys
from typing import Any

import telegram
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, bot_token: str):
        self.bot = telegram.Bot(token=bot_token)

    async def send_message(self, chat_id: str, text: str, **kwargs) -> dict:
        try:
            message = await self.bot.send_message(chat_id=chat_id, text=text, **kwargs)
            return {"success": True, "message_id": message.message_id}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def get_chat(self, chat_id: str) -> dict:
        try:
            chat = await self.bot.get_chat(chat_id)
            return {"success": True, "chat": {"id": chat.id, "type": chat.type, "title": getattr(chat, 'title', None), "username": chat.username}}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def get_me(self) -> dict:
        try:
            me = await self.bot.get_me()
            return {"success": True, "bot": {"id": me.id, "username": me.username, "first_name": me.first_name}}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def get_chat_member_count(self, chat_id: str) -> dict:
        try:
            count = await self.bot.get_chat_member_count(chat_id)
            return {"success": True, "count": count}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def delete_message(self, chat_id: str, message_id: int) -> dict:
        try:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            return {"success": True}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def send_photo(self, chat_id: str, photo: str, caption: str = None) -> dict:
        try:
            kwargs = {"chat_id": chat_id, "photo": photo}
            if caption:
                kwargs["caption"] = caption
            message = await self.bot.send_photo(**kwargs)
            return {"success": True, "message_id": message.message_id}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def send_document(self, chat_id: str, document: str, caption: str = None) -> dict:
        try:
            kwargs = {"chat_id": chat_id, "document": document}
            if caption:
                kwargs["caption"] = caption
            message = await self.bot.send_document(**kwargs)
            return {"success": True, "message_id": message.message_id}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def send_location(self, chat_id: str, latitude: float, longitude: float) -> dict:
        try:
            message = await self.bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)
            return {"success": True, "message_id": message.message_id}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def kick_chat_member(self, chat_id: str, user_id: int) -> dict:
        try:
            await self.bot.kick_chat_member(chat_id=chat_id, user_id=user_id)
            return {"success": True}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def unban_chat_member(self, chat_id: str, user_id: int) -> dict:
        try:
            await self.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
            return {"success": True}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def pin_chat_message(self, chat_id: str, message_id: int) -> dict:
        try:
            await self.bot.pin_chat_message(chat_id=chat_id, message_id=message_id)
            return {"success": True}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def unpin_chat_message(self, chat_id: str) -> dict:
        try:
            await self.bot.unpin_chat_message(chat_id=chat_id)
            return {"success": True}
        except TelegramError as e:
            return {"success": False, "error": str(e)}

    async def export_chat_invite_link(self, chat_id: str) -> dict:
        try:
            link = await self.bot.export_chat_invite_link(chat_id=chat_id)
            return {"success": True, "link": link}
        except TelegramError as e:
            return {"success": False, "error": str(e)}


TOOLS = {


    "telegram_send_message": {
        "description": "Send a message to a Telegram chat",
        "params": {
            "chat_id": {"type": "string", "description": "Target chat ID or username"},
            "text": {"type": "string", "description": "Message text"},
            "parse_mode": {"type": "string", "description": "Parse mode (Markdown or HTML)"}
        },
        "required": ["chat_id", "text"]
    },
    "telegram_get_chat": {
        "description": "Get information about a Telegram chat",
        "params": {"chat_id": {"type": "string", "description": "Chat ID or username"}},
        "required": ["chat_id"]
    },
    "telegram_get_me": {
        "description": "Get bot information",
        "params": {},
        "required": []
    },
    "telegram_get_chat_member_count": {
        "description": "Get member count of a Telegram chat",
        "params": {"chat_id": {"type": "string"}},
        "required": ["chat_id"]
    },
    "telegram_delete_message": {
        "description": "Delete a message",
        "params": {
            "chat_id": {"type": "string"},
            "message_id": {"type": "integer"}
        },
        "required": ["chat_id", "message_id"]
    },
    "telegram_send_photo": {
        "description": "Send a photo to a Telegram chat",
        "params": {
            "chat_id": {"type": "string"},
            "photo": {"type": "string", "description": "Photo file ID or URL"},
            "caption": {"type": "string"}
        },
        "required": ["chat_id", "photo"]
    },
    "telegram_send_document": {
        "description": "Send a document to a Telegram chat",
        "params": {
            "chat_id": {"type": "string"},
            "document": {"type": "string"},
            "caption": {"type": "string"}
        },
        "required": ["chat_id", "document"]
    },
    "telegram_send_location": {
        "description": "Send a location to a Telegram chat",
        "params": {
            "chat_id": {"type": "string"},
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["chat_id", "latitude", "longitude"]
    },
    "telegram_kick_chat_member": {
        "description": "Kick a user from a chat",
        "params": {"chat_id": {"type": "string"}, "user_id": {"type": "integer"}},
        "required": ["chat_id", "user_id"]
    },
    "telegram_unban_chat_member": {
        "description": "Unban a user in a chat",
        "params": {"chat_id": {"type": "string"}, "user_id": {"type": "integer"}},
        "required": ["chat_id", "user_id"]
    },
    "telegram_pin_message": {
        "description": "Pin a message in a chat",
        "params": {"chat_id": {"type": "string"}, "message_id": {"type": "integer"}},
        "required": ["chat_id", "message_id"]
    },
    "telegram_unpin_message": {
        "description": "Unpin the latest message in a chat",
        "params": {"chat_id": {"type": "string"}},
        "required": ["chat_id"]
    },
    "telegram_export_invite_link": {
        "description": "Export an invite link for a chat",
        "params": {"chat_id": {"type": "string"}},
        "required": ["chat_id"]
    },
}


async def call_tool(bot: TelegramBot, name: str, arguments: dict) -> dict:
    if name == "telegram_send_message":
        kwargs = {"chat_id": arguments["chat_id"], "text": arguments["text"]}
        if "parse_mode" in arguments:
            kwargs["parse_mode"] = arguments["parse_mode"]
        return await bot.send_message(**kwargs)
    elif name == "telegram_get_chat":
        return await bot.get_chat(arguments["chat_id"])
    elif name == "telegram_get_me":
        return await bot.get_me()
    elif name == "telegram_get_chat_member_count":
        return await bot.get_chat_member_count(arguments["chat_id"])
    elif name == "telegram_delete_message":
        return await bot.delete_message(arguments["chat_id"], arguments["message_id"])
    elif name == "telegram_send_photo":
        return await bot.send_photo(arguments["chat_id"], arguments["photo"], arguments.get("caption"))
    elif name == "telegram_send_document":
        return await bot.send_document(arguments["chat_id"], arguments["document"], arguments.get("caption"))
    elif name == "telegram_send_location":
        return await bot.send_location(arguments["chat_id"], arguments["latitude"], arguments["longitude"])
    elif name == "telegram_kick_chat_member":
        return await bot.kick_chat_member(arguments["chat_id"], arguments["user_id"])
    elif name == "telegram_unban_chat_member":
        return await bot.unban_chat_member(arguments["chat_id"], arguments["user_id"])
    elif name == "telegram_pin_message":
        return await bot.pin_chat_message(arguments["chat_id"], arguments["message_id"])
    elif name == "telegram_unpin_message":
        return await bot.unpin_chat_message(arguments["chat_id"])
    elif name == "telegram_export_invite_link":
        return await bot.export_chat_invite_link(arguments["chat_id"])
    else:
        return {"success": False, "error": f"Unknown tool: {name}"}


async def handle_request(bot: TelegramBot, request: dict) -> dict | None:
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "telegram-mcp-server", "version": "1.0.0"},
            },
        }

    elif method == "tools/list":
        tools_list = []
        for name, info in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": info["description"],
                "inputSchema": {
                    "type": "object",
                    "properties": info["params"],
                    "required": info["required"]
                },
            })
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

    elif method == "tools/call":
        name = request.get("params", {}).get("name")
        arguments = request.get("params", {}).get("arguments", {})
        result = await call_tool(bot, name, arguments)
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    return None


async def main():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        print("Please set TELEGRAM_BOT_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)

    bot = TelegramBot(bot_token)
    logger.info("Telegram MCP Server started")

    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_readpipe(lambda: protocol, sys.stdin)

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            request = json.loads(line.decode())
            response = await handle_request(bot, request)
            if response:
                print(json.dumps(response), flush=True)
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
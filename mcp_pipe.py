import asyncio
import json
import logging
import os
import signal
import sys
import websockets
from subprocess import Popen, PIPE

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MCP Pipe:
    def __init__(self, mcp_endpoint: str, script_path: str):
        self.mcp_endpoint = mcp_endpoint
        self.script_path = script_path
        self.ws = None
        self.process = None
        self.running = True

    async def start(self):
        if not self.mcp_endpoint:
            logger.error("MCP_ENDPOINT not set")
            return False

        logger.info(f"Connecting to xiaozhi MCP: {self.mcp_endpoint}")
        try:
            self.ws = await websockets.connect(self.mcp_endpoint, ping_interval=30)
            logger.info("Connected to xiaozhi MCP")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

        logger.info(f"Starting MCP client: {self.script_path}")
        self.process = Popen(
            [sys.executable, self.script_path],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            env=os.environ.copy(),
        )
        logger.info("MCP client started")

        return True

    async def handle_messages(self):
        tasks = []
        if self.ws:
            tasks.append(self.handle_ws())
        if self.process:
            tasks.append(self.handle_process())
        await asyncio.gather(*tasks)

    async def handle_ws(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                method = data.get("method")
                msg_id = data.get("id")
                params = data.get("params", {})

                logger.info(f"Received: {method}")

                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "telegram-mcp-server", "version": "1.0.0"},
                        },
                    }
                    await self.ws.send(json.dumps(response))

                elif method in ("tools/list", "tools/call"):
                    self.process.stdin.write((message + "\n").encode())
                    self.process.stdin.flush()

        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.running = False

    async def handle_process(self):
        try:
            for line in iter(self.process.stdout.readline, b""):
                if not line:
                    break
                try:
                    msg = json.loads(line.decode())
                    if self.ws and self.running:
                        await self.ws.send(json.dumps(msg))
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.error(f"Process error: {e}")
        finally:
            self.running = False

    async def run(self):
        if not await self.start():
            return

        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
        signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

        try:
            await self.handle_messages()
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        if self.ws:
            await self.ws.close()
        if self.process:
            self.process.terminate()
            self.process.wait()
        logger.info("Disconnected")


async def main():
    mcp_endpoint = os.environ.get("MCP_ENDPOINT", "")
    script_path = os.environ.get("MCP_CLIENT_SCRIPT", "telegram_mcp.py")

    pipe = MCP Pipe(mcp_endpoint, script_path)
    await pipe.run()


if __name__ == "__main__":
    asyncio.run(main())
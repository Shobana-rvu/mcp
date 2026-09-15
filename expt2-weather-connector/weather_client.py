# expt2-weather-connector/client.py
import asyncio
import json
import os
from contextlib import AsyncExitStack

from groq import Groq
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "server.py")
MODEL = "openai/gpt-oss-20b"


async def main():
    groq = Groq()
    server_params = StdioServerParameters(command="python", args=[SERVER_SCRIPT])

    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(server_params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        tools_result = await session.list_tools()
        groq_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema,
                },
            }
            for t in tools_result.tools
        ]

        print("Weather Assistant ready. Type a query (or 'quit').")
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ("quit", "exit"):
                break

            messages = [{"role": "user", "content": user_input}]
            response = groq.chat.completions.create(
                model=MODEL, messages=messages, tools=groq_tools
            )
            msg = response.choices[0].message

            while msg.tool_calls:
                print("\n--- LLM's thought process ---")
                messages.append(msg)
                for call in msg.tool_calls:
                    args = json.loads(call.function.arguments)
                    print(f"Decision: call tool '{call.function.name}' with args {args}")
                    result = await session.call_tool(call.function.name, args)
                    result_text = "\n".join(
                        c.text for c in result.content if hasattr(c, "text")
                    )
                    print(f"Tool result (from MCP server): {result_text}")
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": result_text,
                        }
                    )
                print("--- end thought process ---\n")
                response = groq.chat.completions.create(
                    model=MODEL, messages=messages, tools=groq_tools
                )
                msg = response.choices[0].message

            print(f"Assistant: {msg.content}")


if __name__ == "__main__":
    asyncio.run(main())

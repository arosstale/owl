import asyncio
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from camel.models import ModelFactory
from camel.toolkits import FunctionTool
from camel.types import ModelPlatformType, ModelType
from camel.logger import set_log_level

from utils.async_role_playing import OwlRolePlaying, run_society

from utils.mcp.mcp_toolkit_manager import MCPToolkitManager


load_dotenv()
set_log_level(level="DEBUG")


async def construct_society(
    question: str,
    tools: List[FunctionTool],
) -> OwlRolePlaying:
    r"""build a multi-agent OwlRolePlaying instance.

    Args:
        question (str): The question to ask.
        tools (List[FunctionTool]): The MCP tools to use.
    """
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0},
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict={"temperature": 0},
        ),
    }

    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {
        "model": models["assistant"],
        "tools": tools,
    }

    task_kwargs = {
        "task_prompt": question,
        "with_task_specify": False,
    }

    society = OwlRolePlaying(
        **task_kwargs,
        user_role_name="user",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )
    return society


async def main():
    config_path = str(
        Path(__file__).parent / "utils/mcp/mcp_servers_config.json"
    )

    manager = MCPToolkitManager.from_config(config_path)

    question = (
        "I'd like a academic report about Guohao Li, including his research "
        "direction, published papers (up to 20), institutions, etc." 
        "Then organize the report in Markdown format and save it to my desktop"
    )

    # Connect to all MCP toolkits
    async with manager.connection():
        tools = manager.get_all_tools()

        society = await construct_society(question, tools)

        answer, chat_history, token_count = await run_society(society)

    print(f"\033[94mAnswer: {answer}\033[0m")


if __name__ == "__main__":
    asyncio.run(main())
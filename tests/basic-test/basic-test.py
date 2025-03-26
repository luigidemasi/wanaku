from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console

from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.tools.mcp import SseMcpToolAdapter, SseServerParams, mcp_server_tools

from pydantic import BaseModel

import asyncio

# Define output structure for the script
class ScriptOutput(BaseModel):
    topic: str
    takeaway: str
    captions: list[str]

async def main():

    # Initialize Ollama client (if needed)
    ollama_client = OllamaChatCompletionClient(
        # model="granite3.2:8b-instruct-q4_K_M",
        model="llama3.1:latest",
        api_key="placeholder",  # Placeholder API key for local model
        response_format=ScriptOutput,
        base_url="http://localhost:11434/v1",
        model_info={
            "function_calling": True,
            "json_output": True,
            "vision": False,
            "family": "unknown"
        }
    )

    # Create server params for the remote MCP service
    server_params = SseServerParams(
        url="http://localhost:8080/mcp/sse"
    )

    # Get all available tools
    adapter = await mcp_server_tools(server_params)

    tester_assistant = AssistantAgent(
        name="tester_assistant",
        model_client=ollama_client,  # Swap with ollama_client if needed
        tools=adapter,
        system_message='''
            You are an assistant tasked with helping me test Wanaku MCP router. Your job consists of calling tools according to the
            prompt I provide you.
            If you don't know which tool to call, then simply reply 'There is no tool available for this request'.
        ''',
        reflect_on_tool_use=True,
    )

    # Set up termination condition
    termination = TextMentionTermination("TERMINATE")

    inputs_map = {
        "dog-facts": "Please give me 3 dog facts",
        "meow-facts": "Please give me 2 cat facts",
        "camel-rider-quote-generator": "Please give me a random quote from the Camel rider. Extract whatever text you receive from it.",
#         "tavily-search": "Please search on the web, using Tavily, about Apache Spark",
        "laptop-order": "I need a new laptop. Please issue an order for a new one. If successful, provide me the order number",
    }

    participants = [tester_assistant]

    # Create sequential execution order
    # Use different agent groups with different max_rounds to ensure each agent completes its task
    agent_team = RoundRobinGroupChat(
        participants,
        termination_condition=termination,
        # Each agent gets one full turn
        max_turns=1
    )

    # for participant in participants:
    for tool in inputs_map.keys():
        prompt = inputs_map.get(tool, None)
        print("Using prompt: {}".format(prompt))
        stream = agent_team.run_stream(task=repr(prompt))
        await Console(stream)


# Run the main async function
if __name__ == "__main__":
    asyncio.run(main())

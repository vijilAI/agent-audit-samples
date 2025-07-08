import os

from pydantic import SecretStr
from setup import AgentSetup
from typing import Optional, List, Dict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    BaseMessage,
)


# Create the agent graph
def create_agent_graph(
    model_name: str = "phala/llama-3.3-70b-instruct",
    base_url: str = "https://api.redpill.ai/v1",
    model_api_key: Optional[str] = None,
    account_id: Optional[str] = None,
    private_key: Optional[str] = None,
    network: Optional[str] = None,
    kaito_api_key: Optional[str] = None,
    mock_balances: bool = True,
    mock_mindshare: bool = True,
    use_single_prompt: bool = True,
):
    """
    Create an agent with the given account ID, private key, network, and optional Kaito API key.
    """
    agent_setup = AgentSetup(account_id, private_key, network, kaito_api_key)

    system_prompt, mindshare_prompts = agent_setup.create_agent_prompts(
        mock_balances=mock_balances,
        mock_mindshare=mock_mindshare,
        use_single_prompt=use_single_prompt,
    )

    model_api_key = model_api_key or os.getenv("REDPILL_API_KEY")
    if not model_api_key:
        raise ValueError("REDPILL_API_KEY is not set. Please set the REDPILL_API_KEY environment variable.")
    model = ChatOpenAI(model=model_name, base_url=base_url, api_key=SecretStr(model_api_key))

    def agent_response(messages: Dict[str, List[BaseMessage]]):
        input_messages = messages.get("messages", [])
        chat_messages: List[BaseMessage] = [SystemMessage(content=system_prompt)]
        # If single prompt is used, the mindshare prompts are included in the system prompt, and the list is empty
        for balance_prompt in mindshare_prompts:
            chat_messages.append(AIMessage(content=balance_prompt))
        chat_messages.extend(input_messages)
        response = model.invoke(chat_messages).content
        return {"messages": [AIMessage(content=response)]}

    builder = StateGraph(MessagesState)

    # The mindshare agent is not designed to engage with multiple messages or conversations. To mimic that, we end the conversation after the agent responds.
    builder.add_node("mindshare-agent", agent_response)
    builder.add_edge(START, "mindshare-agent")
    builder.add_edge("mindshare-agent", END)
    return builder.compile(checkpointer=None)


if __name__ == "__main__":
    import logging
    import os
    from dotenv import load_dotenv

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # set env vars
    load_dotenv()

    # Swap out to redpill LLMs. The original agent uses Llama 3.1 70B on fireworks
    graph = create_agent_graph(
        model_name="phala/llama-3.3-70b-instruct",
        base_url="https://api.redpill.ai/v1",
        model_api_key=os.getenv("REDPILL_API_KEY"),
        account_id=os.getenv("NEAR_ACCOUNT_ID"),
        private_key=os.getenv("NEAR_PRIVATE_KEY"),
        network=os.getenv("NEAR_NETWORK", "mainnet"),
        kaito_api_key=os.getenv("KAITO_API_KEY", None),
        mock_balances=os.getenv("MOCK_BALANCES", "True").lower() == "true",
        mock_mindshare=os.getenv("MOCK_MINDSHARE", "True").lower() == "true",
        use_single_prompt=os.getenv("USE_SINGLE_PROMPT", "True").lower() == "true",
    )

    user_input = input("\nPrompt: ")

    for event in graph.stream({"messages": [HumanMessage(content=user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            print("-------------")

import random
import re
import os
import logging
from typing import List
import uuid

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from prompts import PROMPT_PM, PROMPT_SWE, PROMPT_TRAVEL, PROMPT_JOKER, PROMPT_ADHD, jokes
from constants import PM_FILENAME, PERSONALITIES, DEFAULT_PERSONALITY

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Create a logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize the LLM
model = ChatOpenAI(
    model="phala/llama-3.3-70b-instruct", 
    base_url="https://api.redpill.ai/v1", 
    api_key=os.getenv("REDPILL_API_KEY")
)

@tool
def get_joke(category: str = "") -> str:
    """
    Get a random joke. Optionally specify category: puns, dad_jokes, or knock_knock, or empty string for any category.
    
    Args:
        category (str): The category of joke to get (puns, dad_jokes, knock_knock) 
                       or empty string for any category
                       
    Returns:
        str: A random joke
    """
    if category and category in jokes:
        return random.choice(jokes[category])
    
    # If no category specified or invalid category, choose from all jokes
    all_jokes = []
    for joke_list in jokes.values():
        all_jokes.extend(joke_list)
    
    return random.choice(all_jokes) if all_jokes else "Why did the chicken cross the road? To get to the other side!"


def read_file(filename: str) -> str | None:
    """
    Read a file safely, handling errors and environment differences.

    Args:
        filename (str): The name of the file to read

    Returns:
        str: The content of the file or None if an error occurred
    """
    try:
        if not os.path.exists(filename):
            logger.warning(f"File {filename} does not exist.")
            return None
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        if content == "" or content == "N/A":
            return None
        return content
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return None


def write_file(filename: str, content: str) -> bool:
    """
    Write content to a file safely, handling errors and environment differences.

    Args:
        filename (str): The name of the file to write
        content (str): The content to write to the file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to file {filename}: {e}")
        return False


def determine_personality(user_query: str) -> str:
    """
    Determine personality to trigger based on user query.

    Args:
        user_query (str): The user's message

    Returns:
        str: The detected personality or default if detection fails
    """
    if not user_query:
        logger.warning("Empty user query, defaulting to ADHD personality")
        return DEFAULT_PERSONALITY

    try:
        prompt = f"""
        You are an agent that has multiple personalities: PM, travel agent, Joker, AI with ADHD, software developer
        Based on the following user query, which personality should handle it?
        Choose one of: {", ".join(PERSONALITIES)}
        
        User query: {user_query}
        
        Respond with just the personality name (lowercase).
        """

        # Get the model's response
        messages = [SystemMessage(content=prompt)]
        result = model.invoke(messages).content

        # Extract the personality from the response
        personality = result.strip().lower()

        # Validate the personality
        if personality in PERSONALITIES:
            logger.info(f"Detected personality: {personality}")
            return personality

        # Try to extract a valid personality from the response
        for choice in PERSONALITIES:
            if choice in result.lower():
                logger.info(f"Extracted personality from response: {choice}")
                return choice

        # Default if we can't determine
        logger.warning(f"Could not determine personality from: {result}, defaulting to {DEFAULT_PERSONALITY}")
        return DEFAULT_PERSONALITY

    except Exception as e:
        logger.error(f"Error determining personality: {e}")
        return DEFAULT_PERSONALITY


def multi_personality_agent(state: MessagesState, config: RunnableConfig) -> dict:
    """
    Main agent function that determines personality and generates responses.
    This follows the LangGraph StateGraph pattern.
    """
    messages = state["messages"]
    
    # Get the last user message
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    if not last_user_message:
        logger.warning("No user message found")
        return {"messages": [AIMessage(content="I didn't receive any message. Could you try again?")]}
    
    # Determine personality
    personality = determine_personality(last_user_message)
    logger.info(f"Using personality: {personality}")
    
    try:
        if personality == "pm":
            response = handle_pm_personality(messages)
        elif personality == "swe":
            response = handle_swe_personality(messages)
        elif personality == "travel":
            response = handle_travel_personality(messages)
        elif personality == "joker":
            response = handle_joker_personality(messages)
        elif personality == "adhd":
            response = handle_adhd_personality(messages)
        else:
            response = "I'm not sure how to respond to that. Could you try rephrasing your question?"
        
        return {"messages": [AIMessage(content=response)]}
        
    except Exception as e:
        logger.error(f"Error in personality handler: {e}")
        error_response = "I'm having trouble processing your request. Could you please try again?"
        return {"messages": [AIMessage(content=error_response)]}


def handle_pm_personality(messages):
    """Handle Product Manager personality logic."""
    # Read the current specification
    current_spec = read_file(PM_FILENAME)
    
    # Prepare the system message based on whether we have a spec or not
    if not current_spec:
        spec_or_instructions = """
        After each message from the user, you first respond, either confirming that you understood him and briefly explaining your next steps, or asking for clarifying questions. You have to obtain a full understanding about how to build the user's application.
        What message should we send to the user right now? Respond with the text that will be directly displayed to the user. If you have a full understanding about the user project, please reply with "I'm ready to write a specification".
        """
    else:
        spec_or_instructions = f"""
        The current version of the project specification is:
        
        {current_spec}
        === End of specification ===

        User may want to update this specification with additional features or fixes. After each message from the user, you first respond, either confirming that you understood him and briefly explaining your next steps, or asking for clarifying questions.
        What message should we send to the user right now? Respond with the text that will be directly displayed to the user. If you have a full understanding about specification updates, please reply with "I'm ready to update the specification".
        """
    
    # Generate response to user
    chat_messages = [
        SystemMessage(content=PROMPT_PM),
        SystemMessage(content=spec_or_instructions),
    ] + messages
    
    chat_response = model.invoke(chat_messages).content
    
    # Add the AI response to the conversation (like the original agent)
    updated_messages = messages + [AIMessage(content=chat_response)]
    
    # Check if we need to generate a specification (using AI's own response)
    if current_spec or "I'm ready to write a specification" in chat_response:
        if not current_spec:
            spec_or_instruction = f"""
            After each message from the user, you first respond, either confirming that you understood him and briefly explaining your next steps, or asking for clarifying questions. 
            Here is your last message: 
        
            {chat_response}
            === End of your last message ===
        
            I haven't asked you to write the updated markdown specification yet. If you have a full understanding about the user project, please write a project specification in a valid markdown format. 
            """
        else:
            spec_or_instruction = f"""
            The current version of the specification is:
        
            {current_spec}
            === End of specification ===
        
            User may want to update this specification with additional features or fixes. If you update this, try to preserve all parts of the specification that are not related to the current updates.
            Here is your last message:
        
            {chat_response}
            === End of your last message ===
        
            I haven't asked you to write the updated markdown specification yet. If you have a full understanding about the updates that user want to perform with this project, please write an updated project specification in a valid markdown format. 
            """

        # AI PM spec prompt
        AI_PM_SPEC_PROMPT = f"""
        You are an AI Product Manager assistant. You are in a dialog with a user, who wants you to write a specification for their application. User is not technical so you need to explain technical concepts in a simple way.
        The history of your conversation is provided below. The user provides details about the project they want to build, and the assistant asks clarifying questions and creates a product specification for building the project. Your ultimate goal is now is to create a valid markdown project specification that accurately describes the user's project which can be used by independent developer to build it.
        The final project will contain three parts: frontend, backend, and middleware. Your goal is to write the specifications as clearly as possible so that the team can understand the requirements and implement the three parts of the project. The specification should be as low as possible, commenting on possible code outlines, project architecture, how different components interact, function names and documentation, user stories, and multiple workflows. Don't add any description of the stack or projected timeline or milestones to the specification.
        
        {spec_or_instruction}
        
        Otherwise respond with N/A. Do not include plain text and any introduction like "Here is the specification:". Respond in valid markdown specifications only or N/A.
        """

        try:
            # Generate the specification using the updated conversation (including AI's response)
            spec_messages = [SystemMessage(content=AI_PM_SPEC_PROMPT)] + updated_messages
            spec_response = model.invoke(spec_messages).content

            # Extract markdown content if wrapped in code blocks
            pattern = r"```(.+?)```"
            result = re.search(pattern, spec_response, re.DOTALL)
            spec_content = result.group(1).strip() if result else spec_response

            # Write the specification to file
            if spec_content and spec_content != "N/A":
                success = write_file(PM_FILENAME, spec_content)
                if not success:
                    logger.error("Failed to write specification to file")
        except Exception as e:
            logger.error(f"Error generating or saving specification: {e}")
    
    return chat_response


def handle_swe_personality(messages: List[BaseMessage]):
    """Handle Software Engineer personality logic."""
    chat_messages = [SystemMessage(content=PROMPT_SWE)] + messages
    return model.invoke(chat_messages).content


def handle_travel_personality(messages: List[BaseMessage]):
    """Handle Travel Agent personality logic."""
    chat_messages = [SystemMessage(content=PROMPT_TRAVEL)] + messages
    return model.invoke(chat_messages).content


def handle_joker_personality(messages: List[BaseMessage]):
    """Handle Joker personality logic using LangGraph agent."""
    try:
        # Create a simple agent for joke telling
        joke_agent = create_react_agent(model, tools=[get_joke], prompt=PROMPT_JOKER)
        
        # Run the agent
        result = joke_agent.invoke({"messages": messages}, {"recursion_limit": 5})
        
        # Extract both tool messages (jokes) and AI messages
        if result.get("messages"):
            response_parts = []
            
            for msg in result["messages"]:
                # Check if it's a tool message (contains the actual joke)
                if isinstance(msg, ToolMessage):
                    response_parts.append(msg.content)
                # Check if it's an AI message (final response)
                elif isinstance(msg, AIMessage):
                    response_parts.append(msg.content)
            
            # Combine all response parts
            if response_parts:
                return "\n".join(response_parts)
            else:
                return result["messages"][-1].content
        else:
            return get_joke()  # Fallback to random joke
            
    except Exception as e:
        logger.warning(f"Error in joker agent: {e}")
        return "Hmm, my joke generator seems broken. Let me tell you a classic one instead: Why did the chicken cross the road? To get to the other side!"


def handle_adhd_personality(messages: List[BaseMessage]):
    """Handle ADHD personality logic."""
    chat_messages = [SystemMessage(content=PROMPT_ADHD)] + messages
    return model.invoke(chat_messages).content


def create_agent_graph():
    """Create the LangGraph StateGraph for the multi-personality agent."""
    builder = StateGraph(MessagesState)
    builder.add_node("agent", multi_personality_agent)
    builder.add_edge(START, "agent")
    
    # Use InMemorySaver for conversation persistence
    checkpointer = InMemorySaver()
    
    return builder.compile(checkpointer=checkpointer)


# Run the process
if __name__ == "__main__":
    try:
        graph = create_agent_graph()
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        user_input = input("\nPrompt: ")

        # Stream the conversation and let LangGraph handle state management
        for chunk in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config,
            stream_mode="values"
        ):
            # Print the final state messages
            if chunk.get("messages"):
                last_message = chunk["messages"][-1]
                if isinstance(last_message, AIMessage):
                    print(last_message.content)
                    print("-------------------")
            
    except Exception as e:
        logger.error(f"Unexpected error in main process: {e}")
        print(f"Error: {e}")
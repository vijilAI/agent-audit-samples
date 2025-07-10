# Mindshare Trade Recommendation Agent - LangGraph Edition

This is a refactored version of [Yonder Lab's Mindshare Agent](https://github.com/Yonder-Labs/mindshare_agent) that makes intelligent trade recommendations for a user given their Near Account details and the [Kaito Mindshare](https://www.kaito.ai/kaito-api) of their agent. 
This version extracts **only the underlying trade recommendation system**, and does not execute any trades. The agent has no Near AI Environment framework dependencies, and uses **LangGraph/LangChain** for agent execution.

This agent also includes Vijil Dome to guardrail the agent.

## Key Details

- **Phala Redpill LLMs**: Uses Phala's LLMs running in Trusted Execution Environments (TEEs) for enhanced security and privacy. The base agent used Llama 3.1 8B on Fireworks
- **Langchain/Langraph**: Uses Langgraph as the underlying framework
- **Easier testing**: Supports mocked near accounts and kaito mindshares. You can skip fetching near account balances and the mindshare if you just want to test the agent. 
- **Guardrails**: Includes Vijil Dome for guardrailing the agent

## Quick Start

### Prerequisites
- Python 3.11
- Poetry for dependency management
- RedPill API key for Phala LLM access
- (Optional) - A Near wallet with a private key
- (Optional) - A Kaito API key

### Installation

0. **Optional Accounts**
- Create a Near wallet and save your private key. This will allow you to connect your near account for live token balances. If you don't have a near account, or don't want to load any tokens, you can skip this step or use  `MOCK_BALANCES=True`
- Create a Kaito API key to get token mindshares. To skip this step or use  `MOCK_MINDHSARE=True`

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd mindshare-langgraph
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   create a `.env` file:
   ```
   REDPILL_API_KEY=your_api_key_here
   NEAR_ACCOUNT_ID=your_near_account # Optional
   NEAR_PRIVATE_KEY=your_near_private_key # Optional
   NEAR_NETWORK=mainnet # Use mainnet if you are using real account credentials
   MOCK_BALANCES=True # To mock near balances
   MOCK_MINDSHARE=True # To mock token mindshare
   USE_SINGLE_PROMPT=True # To consolidate balance prompts into the system prompt. If you wish to be true to the original agent, set this to False
   USE_DOME_GUARDRAILS=True # To enable/disable Vijil Dome guardrails for the agent
   WARMUP_DOME=True # To enable/disable guardrail warmup on agent initialization. This is useful for the first time Dome is setup, since it will need to download models. 
   DOME_CONFIG_PATH = path_to_optional_config_file # Optional. Path to a config file to use to initialize Dome. Feel free to ignore this to use Dome's default configuration.
   ```

4. **Run the agent:**

   ```bash
   poetry run python agent.py
   ```

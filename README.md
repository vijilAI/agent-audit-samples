# Auditable Agents

A curated collection of example agents—malicious, benign, and edge-case—designed for auditing and security evaluation.

Each agent is self-contained in its own folder with an independent Python environment defined via `pyproject.toml` (Poetry). This structure enables reproducible, isolated testing across a variety of agent behaviors and dependency sets.

## Repository Structure

```
agent-audit-samples/
├── agent-1/
│   ├── pyproject.toml
│   ├── agent.py
│   └── README.md (optional)
├── agent-2/
│   ├── pyproject.toml
│   ├── agent.py
│   └── tests/ (optional)
└── ...
```

Each agent directory contains:

- **`pyproject.toml`**: Poetry configuration with unique dependencies and metadata
- **`agent.py`**: Primary entry point for agent execution
- **Additional files**: Tests, documentation, or configuration as needed

## Agents

### Multi-Personality Agent (LangGraph Edition)
A conversational agent that can assume multiple distinct personalities including Project Manager, Travel Agent, Joker, AI with ADHD, and Software Developer. This is a refactored version of [@alomonos.near/multipersonality_agent_langchain](https://app.near.ai/agents/alomonos.near/multipersonality_agent_langchain/latest) that replaces the NEAR AI Environment framework with pure LangGraph/LangChain execution. Built using Phala Redpill LLMs running in Trusted Execution Environments (TEEs) for enhanced security and privacy. Features advanced state management and conversation memory persistence. This agent demonstrates personality switching capabilities and potential behavioral analysis scenarios for security evaluation.

### Mindshare LangGraph Agent
A blockchain-integrated agent that analyzes cryptocurrency mindshare data and NEAR protocol account balances. The agent connects to NEAR blockchain networks (mainnet/testnet) to retrieve multi-token balances from the intents.near contract and fetches real-time mindshare metrics via the Kaito API. Features include configurable mocking for testing environments, dynamic prompt generation based on portfolio composition, and integration with external market sentiment data. This agent is useful for testing financial data handling, API integration patterns, and blockchain interaction security in agent systems. This agent can also be protected using Vijil Dome guardrails.


## Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- Git for version control

## Quick Start

### Running a Single Agent

```bash
# Navigate to the agent directory
cd agent-1

# Install dependencies in isolated environment
poetry install

# Execute the agent
poetry run python agent.py
```

## Development Guidelines

### Adding New Agents

1. Create a new directory with a meaningful name for your agent
2. Initialize with Poetry: `poetry init`
3. Define dependencies in `pyproject.toml`
4. Implement the agent logic in `agent.py`
5. Add appropriate documentation and tests

### Best Practices

- Keep agents isolated with minimal cross-dependencies
- Document the expected behavior and security implications
- Include appropriate logging and error handling
- Follow consistent coding standards across agents

## Security Considerations

**Warning**: This repository contains agents with potentially harmful behaviors designed for testing purposes only.

- Run agents only in isolated, controlled environments
- Never execute unknown agents on production systems
- Review code thoroughly before execution
- Use appropriate sandboxing and monitoring tools
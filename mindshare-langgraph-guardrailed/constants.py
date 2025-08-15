# The assets the agent is allowed to use
ASSET_MAP = {
    "USDC": {
        "token_id": "nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near",
        "decimals": 6,
        "blockchain": "eth",
        "symbol": "USDC",
        "price": 0.999795,
        "price_updated_at": "2025-03-25T15:11:40.065Z",
        "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    },
    "NEAR": {
        "token_id": "wrap.near",
        "decimals": 24,
    },
    "WNEAR": {
        "token_id": "nep141:wrap.near",
        "decimals": 24,
        "blockchain": "near",
        "symbol": "wNEAR",
        "price": 3,
        "price_updated_at": "2025-03-25T15:11:40.065Z",
        "contract_address": "wrap.near",
    },
    "ETH": {
        "token_id": "nep141:eth.omft.near",
        "decimals": 18,
        "blockchain": "eth",
        "symbol": "ETH",
        "price": 2079.16,
        "price_updated_at": "2025-03-25T15:11:40.065Z",
    },
    "BTC": {
        "token_id": "nep141:btc.omft.near",
        "decimals": 8,
        "blockchain": "btc",
        "symbol": "BTC",
        "price": 88178,
        "price_updated_at": "2025-03-25T15:11:40.065Z",
    },
    "SOL": {
        "token_id": "nep141:sol.omft.near",
        "decimals": 9,
        "blockchain": "sol",
        "symbol": "SOL",
        "price": 146.28,
        "price_updated_at": "2025-03-25T15:11:40.065Z",
    },
    "TRUMP": {
        "token_id": "nep141:sol-c58e6539c2f2e097c251f8edf11f9c03e581f8d4.omft.near",
        "decimals": 6,
        "blockchain": "sol",
        "symbol": "TRUMP",
        "price": 11.65,
        "price_updated_at": "2025-03-25T15:11:40.065Z",
        "contract_address": "c58e6539c2f2e097c251f8edf11f9c03e581f8d4",
    },
    "XRP": {
        "token_id": "nep141:xrp.omft.near",
        "decimals": 6,
        "blockchain": "xrp",
        "symbol": "XRP",
        "price": 2.45,
        "price_updated_at": "2025-03-25T15:11:40.065Z",
    },
}

NEAR_TOKEN_NAME = "near"
TIMEOUT_LIMIT = 120

# Sample balances
MOCK_BALANCES = {
    "BTC": 0.0001,
    "NEAR": 10.0,
    "USDC": 100.0,
    "TRUMP": 50.0,
}

# Sample token mindshares
MOCK_MINDSHARES = {
    "BTC": {"mindshare": 0.75},
    "ETH": {"mindshare": 0.29},
    "SOL": {"mindshare": 0.85},
    "NEAR": {"mindshare": 0.80},
    "USDC": {"mindshare": 0.05},
    "TRUMP": {"mindshare": 0.05},
    "XRP": {"mindshare": 0.05},
}

GUARDRAILS_INPUT_BLOCKED_MESSAGE = "I'm sorry, but this request is in violation of my operating policies. I cannot answer it."
GUARDRAILS_OUTPUT_BLOCKED_MESSAGE = "I'm sorry, but the response to this request is in violation of my operating policies. I cannot respond to this request."

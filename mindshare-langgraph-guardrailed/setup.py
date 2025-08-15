import near_api
import requests
from pathlib import Path
from constants import (
    ASSET_MAP,
    MOCK_BALANCES,
    MOCK_MINDSHARES,
    NEAR_COIN_NAME,
    TIMEOUT_LIMIT,
)
from decimal import Decimal
from typing import Optional, Tuple, List
from datetime import datetime, timedelta


def get_asset_id(token_name: str):
    if token_name == NEAR_COIN_NAME:
        return "nep141:" + ASSET_MAP[token_name]["token_id"]
    else:
        return ASSET_MAP[token_name]["token_id"]


def get_provider(network):
    if network == "testnet":
        return "https://rpc.testnet.near.org"
    else:
        return "https://rpc.mainnet.near.org"


class AgentSetup:
    def __init__(
        self,
        account_id: Optional[str],
        private_key: Optional[str],
        network: Optional[str],
        kaito_api_key: Optional[str] = None,
    ):
        if any(var is None for var in (account_id, private_key, network)):
            print(
                "Account, Provider, or private key is None. Agent will not use a near account."
            )
            self.account = None
        else:
            provider = get_provider(network)
            near_provider = near_api.providers.JsonProvider(provider)
            key_pair = near_api.signer.KeyPair(private_key)
            signer = near_api.signer.Signer(account_id, key_pair)
            self.account = near_api.account.Account(near_provider, signer, account_id)

        self.kaito_api_key = kaito_api_key

    def _get_near_account_balances(self):
        """Get all assets for an account in intents.near contract"""
        balances = {}

        for token, info in ASSET_MAP.items():
            try:
                result = self.account.view_function(
                    "intents.near",
                    "mt_balance_of",
                    {
                        "account_id": self.account.account_id,
                        "token_id": get_asset_id(token),
                    },
                )

                if isinstance(result, dict) and "result" in result:
                    balance_str = result["result"]
                    if balance_str:
                        balance = Decimal(balance_str) / Decimal(
                            str(10 ** info["decimals"])
                        )
                        if balance > 0:
                            balances[token] = float(balance)
                        else:
                            balances[token] = 0

            except Exception as e:
                print(f"Error getting balance for {token}: {str(e)}")
                continue

        return balances

    def _mock_near_account_balances(self):
        "Mocked balances to test the agent without needing near balances"
        return MOCK_BALANCES

    def get_balances(self, mock=False):
        """Get balances for the account, either real or mocked"""
        if mock:
            return self._mock_near_account_balances()
        else:
            if self.account is None:
                raise ValueError("Account is not set up. Cannot get balances.")
            return self._get_near_account_balances()

    def _get_kaito_mindshare(self, token: str):
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        base_url = f"https://api.kaito.ai/api/v1/mindshare?token={token}&start_date={yesterday}&end_date={today}"
        headers = {"x-api-key": self.kaito_api_key}
        response = requests.get(base_url, headers=headers, timeout=TIMEOUT_LIMIT)
        print(f"Kaito API response for {token}: {response.text}")  # Debug log
        if response.status_code == 200:
            data = response.json()
            mindshare_value = list(data["mindshare"].values())[0]
            return {"mindshare": mindshare_value}
        else:
            return {"error": "Failed to get mindshare"}

    def _get_mock_mindshare(self, token: str):
        result = MOCK_MINDSHARES.get(token, {"error": "Token not found"})
        return result

    def get_mindshare(self, token, mock=False):
        if mock:
            return self._get_mock_mindshare(token)
        else:
            if self.kaito_api_key is None:
                raise ValueError(
                    "Kaito API key is required for unmocked mindshare queries"
                )
            return self._get_kaito_mindshare(token)

    # Helper function, just to keep things clean
    def get_allowed_assets(self):
        return list(ASSET_MAP.keys())

    def create_agent_prompts(
        self,
        mock_balances: bool = True,
        mock_mindshare: bool = True,
        use_single_prompt: bool = True,
    ) -> Tuple[str, List[str]]:
        # Get balances for the account
        balances = self.get_balances(mock=mock_balances)
        asset_keys = self.get_allowed_assets()

        # Load the template from file
        template_text = Path(__file__).parent / "system_prompt.txt"
        template_text = template_text.read_text()

        # Fill in the placeholders
        system_prompt = template_text.format(
            asset_keys=asset_keys, balance_keys=list(balances.keys())
        )

        # Get the mindshare balances and create the additional prompts
        # Note, in the original agent, the mindshare prompts are passed in as additional assistant prompts. If use_single_prompt is True, the mindshare prompts will be included in the main system prompt.
        mindshare_prompts = []
        for token, amount in balances.items():
            mindshare = self.get_mindshare(token, mock=mock_mindshare)
            if "error" not in mindshare:
                mindshare_value = mindshare["mindshare"]
                mindshare_prompts.append(
                    f"I have {amount} {token} and mindshare for this token is: {mindshare_value}"
                )
            else:
                mindshare_prompts.append(f"Error: No data available for {token}")

        if use_single_prompt:
            # Combine the system prompt with mindshare prompts
            system_prompt += "\n" + "\n".join(mindshare_prompts)
            mindshare_prompts = []

        return system_prompt, mindshare_prompts

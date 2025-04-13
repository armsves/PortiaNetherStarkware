"""Registry containing my custom tools."""

from portia import InMemoryToolRegistry
from my_web3_tools.fetch_wallet_balance_tool import CheckWalletBalanceTool

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        CheckWalletBalanceTool(),
    ],
)
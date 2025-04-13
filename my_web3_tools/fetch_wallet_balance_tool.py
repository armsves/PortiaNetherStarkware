from portia.tool import Tool, ToolRunContext
from pydantic import BaseModel, Field
import requests
from portia.clarification import ActionClarification
import json
import os

class CheckWalletBalanceToolSchema(BaseModel):
    """Schema defining the inputs for the CheckWalletBalanceTool."""
    test: str = Field(default="test", description="A test field for the tool.")


class CheckWalletBalanceTool(Tool[str]):
    id: str = "check_wallet_balance_tool"
    name: str = "Check Wallet Balance Tool"
    description: str = "Fetches the balance of a given wallet address."
    arg_schema: type[BaseModel] = CheckWalletBalanceToolSchema
    output_schema: tuple[str, str] = ("str", "The balance of the wallet address.")

    def run(self, ctx: ToolRunContext) -> str:
        """
        Run the CheckWalletBalanceTool to fetch the wallet balance.
        """
        try:
            # Construct the relative path to the balances directory
            balances_dir = os.path.join(os.path.dirname(__file__), "../balances")
            file_path = os.path.join(balances_dir, f"{ctx.plan_run_id}.json")

            with open(file_path, "r") as file:
                # Read the contents of the file
                content = file.read()

            data = json.loads(content)
            print(f"data: {data}")
        except (FileNotFoundError, ValueError):
            return ActionClarification(
                plan_run_id=ctx.plan_run_id,
                argument_name="filename",
                user_guidance=(
                    f"Please connect your wallet:"
                ),action_url="https://portianetherstarkware.onrender.com:5173/?id=" + str(ctx.plan_run_id),)

        return data  # Return the parsed JSON data

        #except requests.exceptions.RequestException as e:
            # Handle network-related errors
        #    return f"Error: Failed to fetch wallet balance. Details: {str(e)}"
        
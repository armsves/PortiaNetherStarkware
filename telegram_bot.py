import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
import webbrowser
from dotenv import load_dotenv
from portia import (
    Portia,
    example_tool_registry,
    ActionClarification,
    InputClarification,
    MultipleChoiceClarification,
    PlanRunState,
)
from portia.cli import (
    CLIExecutionHooks,
)
from my_web3_tools.registry import custom_tool_registry
from fastapi import FastAPI
import threading
from fastapi import Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, JSONResponse, HTMLResponse
from pydantic import BaseModel
import os
import json
from urllib.parse import urlparse, parse_qs

load_dotenv()

TOKEN = os.getenv("TOKEN")  # Get the TOKEN from the .env file

if not TOKEN:
    raise ValueError("TOKEN is not set in the .env file")

# Define states
MENU, OPTION1, OPTION2 = range(3)

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Directory to store balances
BALANCES_DIR = "balances"
os.makedirs(BALANCES_DIR, exist_ok=True)

class SaveBalanceRequest(BaseModel):
    id: str
    balance: str
##################################################

@app.post("/save-balance")
async def save_balance(request: SaveBalanceRequest):
    try:
        # Validate request body
        if not request.id and not request.balance:
            raise HTTPException(status_code=400, detail="Missing balance in the request body")

        # Save balance to a file
        file_path = os.path.join(BALANCES_DIR, f"{request.id}.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump({"balance": request.balance}, f, indent=2)

        return {"message": "Balance saved successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Endpoint 2: /balances
@app.api_route("/balances/{file_name}", methods=["GET", "HEAD"])
async def get_balance(file_name: str, request: Request):
    try:
        # Construct file path
        file_path = os.path.join(BALANCES_DIR, file_name)

        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Handle HEAD requests
        if request.method == "HEAD":
            return Response(status_code=200)

        # Handle GET requests
        with open(file_path, "r") as f:
            content = json.load(f)
        return content
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
# Endpoint 3: /api/approve-and-mint
@app.get("/api/approve-and-mint", response_class=HTMLResponse)
async def approve_and_mint(request: Request):
    # Parse the query parameters
    query_params = parse_qs(urlparse(str(request.url)).query)
    amount = query_params.get("amount", [None])[0]

    if not amount:
        raise HTTPException(status_code=400, detail="Missing amount in the query parameters")

    # Prepare the HTML response
    html_response = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Approve and Mint</title>
    </head>
    <body>
        <h1>Approve and Mint</h1>
        <p>Amount: {amount}</p>
        <button id="approveMintButton">Approve and Mint</button>
        <script src="https://cdn.jsdelivr.net/npm/starknet@5.14.1/dist/starknet.browser.min.js"></script>
        <script type="module">
            import {{ CallData, cairo }} from 'https://cdn.jsdelivr.net/npm/starknet@5.15.0/+esm';

            document.getElementById('approveMintButton').addEventListener('click', async () => {{
                try {{
                    let starknet;

                    // Function to connect to the wallet
                    async function connectWallet() {{
                        if (window.starknet) {{
                            await window.starknet.enable();
                            starknet = window.starknet;
                            return true;
                        }} else {{
                            alert("Please install the Argent X wallet!");
                            return false;
                        }}
                    }}

                    // Call the connectWallet function
                    const isConnected = await connectWallet();
                    if (!isConnected) {{
                        alert('Wallet connection failed');
                        return;
                    }}

                    // Define the contract details
                    const contractAddress_1 = '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d';
                    const contractAddress_2 = '0x07c2e1e733f28daa23e78be3a4f6c724c0ab06af65f6a95b5e0545215f1abc1b';

                    const callData1 = {{
                        contractAddress: contractAddress_1,
                        entrypoint: "approve",
                        calldata: CallData.compile({{
                            spender: contractAddress_2,
                            amount: cairo.uint256({amount}),
                        }}),
                    }};

                    const callData2 = {{
                        contractAddress: contractAddress_2,
                        entrypoint: "mint",
                        calldata: CallData.compile({{
                            to: contractAddress_1,
                            amount: cairo.uint256({amount}),
                        }}),
                    }};

                    const result = await starknet.account.execute([callData1, callData2]);
                    console.log("✅ Transaction hash:", result.transaction_hash);

                    alert('Transaction successful: ' + JSON.stringify(result));
                }} catch (error) {{
                    console.error('Error during approve and mint:', error);
                    alert('Error: ' + error.message);
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_response)

######################################

@app.get("/")
async def get_wallet_balance(request: Request):
    # Parse the query parameters
    query_params = parse_qs(urlparse(str(request.url)).query)
    id = query_params.get("id", [None])[0]

    if not id:
        raise HTTPException(status_code=400, detail="Missing id in the query parameters")
    # Prepare the HTML response
    
    html_response = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wallet Balance</title>
    </head>
    <body>
        <script src="https://cdn.jsdelivr.net/npm/starknet@5.14.1/dist/starknet.browser.min.js"></script>
        <script>
    const STRK_CONTRACT_ADDRESS = "0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d"; // Replace with real STRK address
    const DECIMALS = 18;

    let starknet;
    let userAddress;

    // Function to connect the wallet
    async function connectWallet() {
      if (window.starknet) {
        await window.starknet.enable();
        starknet = window.starknet;
        userAddress = starknet.selectedAddress;
        return true;
      } else {
        alert("Please install the Argent X wallet!");
        return false;
      }
    }

    // Function to fetch the balance
    async function getBalance() {
      if (!userAddress) return null;

      const balanceCall = {
        contractAddress: STRK_CONTRACT_ADDRESS,
        entrypoint: "balanceOf",
        calldata: [userAddress],
      };

      try {
        const result = await starknet.provider.callContract(balanceCall);

        // Convert from Uint256 (low + high)
        const low = BigInt(result.result[0]);
        const high = BigInt(result.result[1]);
        const rawBalance = high << 128n | low;
        const formattedBalance = Number(rawBalance) / 10 ** DECIMALS;

        return { balance: formattedBalance };
      } catch (error) {
        console.error("Error fetching balance:", error);
        return null;
      }
    }

    // Function to check if the file exists on the server
    async function checkFileExists(id) {
      try {
        const response = await fetch(`/balances/${id}.json`, { method: 'HEAD' });
        return response.ok; // Returns true if the file exists
      } catch (error) {
        console.error("Error checking file existence:", error);
        return false;
      }
    }

    // Function to save balance to the server
    async function saveBalanceToServer(id, balance) {
      try {
        const response = await fetch('/save-balance', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ id, balance }),
        });

        if (response.ok) {
          console.log(`Balance saved to server for ID ${id}`);
        } else {
          console.error('Failed to save balance to server:', await response.text());
        }
      } catch (error) {
        console.error('Error saving balance to server:', error);
      }
    }

    // Automatically connect wallet and fetch balance on page load
    window.onload = async () => {
      // Get the ID from the URL
      const urlParams = new URLSearchParams(window.location.search);
      const id = urlParams.get("id");

      if (!id) {
        console.error("No ID provided in the URL.");
        return;
      }

      // Check if the file exists on the server
      const fileExists = await checkFileExists(id);
      if (fileExists) {
        // If the file exists, fetch and display its content
        try {
          const response = await fetch(`/balances/${id}.json`);
          const balanceJson = await response.json();

            // Serve only the JSON data
            const jsonResponse = JSON.stringify(balanceJson);
            document.body.innerHTML = `<pre>${jsonResponse}</pre>`; // Display JSON directly

          console.log(`Balance for ID ${id} loaded from server:`, balanceJson);
        } catch (error) {
          console.error("Error fetching balance from server:", error);
        }
        return; // Exit early since the file exists
      }

      // If the file does not exist, prompt wallet connection
      const isConnected = await connectWallet();
      if (isConnected) {
        const balanceJson = await getBalance();
        if (balanceJson) {
          // Save the balance to the server
            await saveBalanceToServer(id, balanceJson.balance.toString());

            
          // Serve only the JSON data
          const jsonResponse = JSON.stringify(balanceJson);
          const blob = new Blob([jsonResponse], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          window.location.href = url;
        }
      }
    };
  </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_response)

@app.get("/status")
def get_status():
    return {"status": "Bot is running"}

@app.post("/custom-action")
def custom_action(data: dict):
    # Process the incoming data
    return {"received_data": data}

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data="option1")],
        [InlineKeyboardButton("Option 2", callback_data="option2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome! Please choose an option:", reply_markup=reply_markup
    )
    return MENU


async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "option1":
        await query.edit_message_text(text="You selected Option 1.")
        complete_tool_registry = example_tool_registry + custom_tool_registry
        portia = Portia(tools=complete_tool_registry)
        plan = portia.plan(
            'Get the balance for my wallet address 0x07B7B2EB67FEc2b054b5Da5c0e477Dd7CF97E7a9483C80e03bA4394699ED4154 and check the STRK token contract address 0x07b7b2eb67fec2b054b5da5c0e477dd7cf97e7a9483C80e03ba4394699ed4154 balance'
            )

        text = plan.pretty_print()
        await query.edit_message_text(text)
        #output = portia.run_plan(plan_plan)

        # Run the plan
        plan_run = portia.run_plan(plan)

        while plan_run.state == PlanRunState.NEED_CLARIFICATION:
        # If clarifications are needed, resolve them before resuming the plan run
            for clarification in plan_run.get_outstanding_clarifications():
                # Usual handling of Input and Multiple Choice clarifications
                if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
                    print(f"{clarification.user_guidance}")
                    user_input = input("Please enter a value:\n" 
                            + (("\n".join(clarification.options) + "\n") if "options" in clarification else ""))
                    plan_run = portia.resolve_clarification(clarification, user_input, plan_run)
                if isinstance(clarification, ActionClarification):
                    await query.edit_message_text(text=str(clarification.user_guidance+" -- Please click on the link below to proceed."))
                    webbrowser.open(str(clarification.action_url))
                    plan_run = portia.wait_for_ready(plan_run)
            plan_run = portia.resume(plan_run)
            await query.edit_message_text(plan_run.outputs.final_output.summary)
        return OPTION1
    elif query.data == "option2":
        await query.edit_message_text(text="You selected Option 2.")
        webbrowser.open("https://example.com/option2")
        return OPTION2
    else:
        await query.edit_message_text(text="Unknown option selected.")
        return MENU
    

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


def run_fastapi():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5173)

def main():
    # Start FastAPI in a separate thread
    threading.Thread(target=run_fastapi, daemon=True).start()

    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [CallbackQueryHandler(button)],
            OPTION1: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
            OPTION2: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()

I created a telegram bot defi asistant using Portia AI SDK Python that interacts with Starknet using starknetJs.
It's a compact project that uses portia sdk python, fast api to serve the endpoints to allow wallet connection in the frontend which removes the security issue of giving/hardcoding the private key to the agent.
It begins interacting with @PortiaNetherStarkbot in telegram and typing /start which will show the Menu, depending on the choice it will trigger the action that can be Get the wallets STRK balance, Deposit (approve/mint) NOSTR STRK Yield Bearing Token, Get NOSTR STRK Yield Bearing Token Balance and Withdraw NOSTR STRK Yield Bearing Token.
The workflow shows the steps that will be executed beforehand so the user can understand what is going on with the LLM call, after an action is selected it will trigger a clarification which is a way of portia to handle user inputs, that will trigger the wallet interaction in the browser.
This is a minimal implementation to showcase the uses of portia and interacting with the blockchain to work as a defi assistant in python and some parts in html+javascript,

How to use, clone the repo

Install the ArgentX wallet https://www.argent.xyz/argent-x

Set up your portia account https://app.portialabs.ai/

Create your telegram bot @BotFather then /newbot and follow instructions

copy .env.example and add your keys, token is the telegram bot token (must create first a bot with botfather in telegram)

pip install uv

uv venv myenv

source myenv/bin/activate

uv install -r requirements.txt

uv run telegram_bot.py

and it should work

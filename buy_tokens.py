import os
import logging
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
SOLANA_NETWORK_URL = os.getenv('SOLANA_NETWORK_URL')
GRAPHENE_TOKEN_ADDRESS = os.getenv('GRAPHENE_TOKEN_ADDRESS')

# Initialize Solana client
solana_client = Client(SOLANA_NETWORK_URL)

def buy_tokens(user_address: str, amount: int) -> bool:
    try:
        # Create a transaction to transfer tokens
        transaction = Transaction()
        transfer_params = TransferParams(
            from_pubkey=PublicKey(GRAPHENE_TOKEN_ADDRESS),
            to_pubkey=PublicKey(user_address),
            lamports=amount
        )
        transaction.add(transfer(transfer_params))

        # Send the transaction
        response = solana_client.send_transaction(transaction)
        logger.info(f"Tokens purchased by {user_address}: {response}")
        return True
    except Exception as e:
        logger.error(f"Failed to purchase tokens for {user_address}: {e}")
        return False

def update_user_balance(user_address: str, amount: int) -> str:
    # Implement logic to update user balance
    # For now, assume the balance is updated successfully
    if buy_tokens(user_address, amount):
        return f"Purchase of {amount} tokens successful!"
    else:
        return "Token purchase failed. Please try again later."

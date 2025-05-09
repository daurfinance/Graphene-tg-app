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

def distribute_airdrop(user_address: str, amount: int) -> bool:
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
        logger.info(f"Airdrop distributed to {user_address}: {response}")
        return True
    except Exception as e:
        logger.error(f"Failed to distribute airdrop to {user_address}: {e}")
        return False

def participate_in_airdrop(user_address: str) -> str:
    # Implement logic to check if the user is eligible for the airdrop
    # For now, assume all users are eligible
    amount = 1000  # Amount of tokens to airdrop
    if distribute_airdrop(user_address, amount):
        return f"Airdrop of {amount} tokens successful!"
    else:
        return "Airdrop failed. Please try again later."


import requests, json
from config import CLAIM_API_URL, BALANCE_API_URL

def load_wallets():
    try:
        with open("wallet_store.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_wallets(wallets):
    with open("wallet_store.json", "w") as f:
        json.dump(wallets, f, indent=2)

def add_wallet(address, api_token):
    wallets = load_wallets()
    if any(w['wallet_address'] == address for w in wallets):
        return False
    wallets.append({"wallet_address": address, "api_token": api_token})
    save_wallets(wallets)
    return True

def claim_all_wallets():
    wallets = load_wallets()
    results = []
    for wallet in wallets:
        headers = {
            "Authorization": f"Bearer {wallet['api_token']}",
            "Content-Type": "application/json"
        }
        try:
            r_claim = requests.post(CLAIM_API_URL, headers=headers, json={"address": wallet["wallet_address"]})
            claim_result = r_claim.json()
            r_balance = requests.get(f"{BALANCE_API_URL}?address={wallet['wallet_address']}", headers=headers)
            balance = r_balance.json().get("balance", "N/A")
            results.append(
                f"🧾 `{wallet['wallet_address'][:8]}...`\n📤 Claim : `{claim_result}`\n\n💰 Balance : `{balance}`\n\n"
            )
        except Exception as e:
            results.append(f"❌ `{wallet['wallet_address'][:8]}...`: ERROR {e}")
    return "\n".join(results)

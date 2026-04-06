import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import create_user, create_group, add_group_member, add_expense, get_group_balances
from services.graph_algo import simplify_debts

# ========================================================
# EDIT THE CODE BELOW TO ADD DATA DIRECTLY VIA PYTHON!
# ========================================================
print("[START] Running custom script...")

def run_custom_logic():
    # 1. OPTIONAL: Create users directly in code
    # alice_id = create_user("Alice Custom", "alice_custom@test.com")
    # bob_id = create_user("Bob Custom", "bob_custom@test.com")
    # charlie_id = create_user("Charlie Custom", "charlie_custom@test.com")
    # print(f"Created users: {alice_id}, {bob_id}, {charlie_id}")

    # 2. Assign your existing IDs from Supabase here
    USER_A = "5e485555-720d-4dc4-8603-a1439fe28b41"
    USER_B = "648adef4-eb29-4f3d-9f4c-9dd424fec433"
    GROUP_ID = "5b31d528-6d73-43fa-802a-60fa36b456d5"

    # NOTE: You MUST replace the placeholder UUID strings above with real IDs 
    # from your database before running this script, otherwise Supabase will reject it!

    if USER_A == "YOUR_FIRST_USER_UUID":
        print("[INFO] Please open custom_script.py and replace the 'YOUR_FIRST_USER_UUID' variables with real IDs from your Supabase Database!")
        return

    # 3. Inject an expense directly using code variables
    print("\nAdding custom hardcoded expense to DB...")
    
    expense_id = add_expense(
        group_id=GROUP_ID,
        description="Late Night Pizza via Python Code",
        category_id=None,
        total_amount=40.0,
        
        created_by=USER_A,
        
        # Dictionary of exactly who handed money to the merchant
        payers={
            USER_A: 40.0
        },
        
        # Dictionary of everyone's fair share of the bill
        splits={
            USER_A: 20.0,
            USER_B: 20.0
        }
    )
    
    print(f"[SUCCESS] Successfully inserted expense permanently into Supabase! Expense ID: {expense_id}")

    # 4. Immediately trigger the graph algorithm to see how debts shifted
    print("\n--- New Minimized Cash Flow ---")
    balances = get_group_balances(GROUP_ID)
    transactions = simplify_debts(balances)
    
    if not transactions:
        print("Everyone is perfectly settled up in this group!")
    for debtor, creditor, amount in transactions:
         print(f"-> {debtor} needs to pay {creditor} an amount of ${amount}")


if __name__ == "__main__":
    run_custom_logic()

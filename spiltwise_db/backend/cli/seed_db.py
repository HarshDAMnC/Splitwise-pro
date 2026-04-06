import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import create_user, create_group, add_group_member, add_expense, get_group_balances
from services.graph_algo import simplify_debts

def run():
    print("Starting Database Seed...")
    
    u1 = create_user("Alice", "alice@test.com")
    u2 = create_user("Bob", "bob@test.com")
    u3 = create_user("Charlie", "charlie@test.com")
    u4 = create_user("David", "david@test.com")
    users = [u1, u2, u3, u4]
    
    g1 = create_group("Goa Trip 2026", "A tech bro trip", u1)
    
    # Add everyone to group
    for u in users[1:]:
        add_group_member(g1, u)
        
    print(f"Group ID: {g1} created with {len(users)} users.")
    
    # Expense 1: Dinner total 100.
    # Alice pays 50, Bob pays 50.
    # Everyone splits equally (25 each).
    print("Adding expense 1: Dinner (100) - Alice(50), Bob(50)")
    add_expense(
        group_id=g1, description="Dinner", category_id=None,
        total_amount=100.0, created_by=u1,
        payers={u1: 50.0, u2: 50.0},
        splits={u1: 25.0, u2: 25.0, u3: 25.0, u4: 25.0}
    )
    
    # Expense 2: Hotel total 200.
    # Charlie pays 200.
    # Split: Bob (100), David(100). (Alice and Charlie didn't stay here, but Charlie booked it).
    print("Adding expense 2: Hotel (200) - Charlie(200)")
    add_expense(
        group_id=g1, description="Hotel", category_id=None,
        total_amount=200.0, created_by=u3,
        payers={u3: 200.0},
        splits={u2: 100.0, u4: 100.0}
    )
    
    # Expectation logic:
    # A pays 50. Spl: A(25). -> A(Net): +25
    # B pays 50. Spl: B(25, 100) -> 50 - 125 -> B(Net): -75
    # C pays 200. Spl: C(25) -> 200 - 25 -> C(Net): +175
    # D pays 0. Spl: D(25, 100) -> 0 - 125 -> D(Net): -125
    # Sum: 25 - 75 + 175 - 125 = 0.
    
    print("\nSeeding Complete!\n")
    
    print("--- Current Net Balances ---")
    bals = get_group_balances(g1)
    name_map = {u1: "Alice", u2: "Bob", u3: "Charlie", u4:"David"}
    
    for uid, amt in bals.items():
        print(f"  {name_map[uid]}: {amt}")
        
    print("\n--- Simplified Graph (Greedy Heap DSA) ---")
    transactions = simplify_debts(bals)
    for d, c, amt in transactions:
        print(f"  {name_map[d]} needs to pay {name_map[c]} an amount of ${amt}")
        
if __name__ == "__main__":
    run()

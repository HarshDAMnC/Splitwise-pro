import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import create_user, create_group, add_group_member, add_expense, add_settlement

def main():
    print("=== Database Manual Entry Tool ===")
    print("1. Add User")
    print("2. Add Group")
    print("3. Add Expense to Group")
    print("4. Settle Up (Pay Real Cash)")
    
    choice = input("Select an option (1-4): ")
    
    if choice == '1':
        name = input("Enter user name: ")
        email = input("Enter user email: ")
        uid = create_user(name, email)
        print(f"✅ User created successfully! ID: {uid}")
        
    elif choice == '2':
        name = input("Enter group name: ")
        desc = input("Enter group description: ")
        creator = input("Enter Creator's User ID: ")
        gid = create_group(name, desc, creator)
        print(f"✅ Group created successfully! ID: {gid}")
        
    elif choice == '3':
        gid = input("Enter Group ID: ")
        desc = input("Expense Description (e.g., Lunch): ")
        total = float(input("Total Amount: "))
        
        payer_id = input("Enter ID of the user who paid the bill: ")
        payers = {payer_id: total}
        
        print("\n--- Splitting the Bill ---")
        num_splits = int(input("How many people are splitting it? "))
        splits = {}
        for i in range(num_splits):
            u_id = input(f"Enter User ID #{i+1} splitting the bill: ")
            amt = float(input(f"Amount owed by User #{i+1}: "))
            splits[u_id] = amt
            
        print("Saving to database...")
        eid = add_expense(
            group_id=gid,
            description=desc,
            category_id=None,
            total_amount=total,
            created_by=payer_id,
            payers=payers,
            splits=splits
        )
        print(f"✅ Expense logged successfully in all normalized tables! Expense ID: {eid}")
        
    elif choice == '4':
        gid = input("Enter Group ID: ")
        payer = input("Enter ID of the user sending money: ")
        payee = input("Enter ID of the user receiving money: ")
        amt = float(input("Amount transferred: "))
        
        add_settlement(gid, payer, payee, amt)
        print(f"✅ Settlement of ${amt} successfully recorded from {payer[:6]}... to {payee[:6]}...")
        
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()

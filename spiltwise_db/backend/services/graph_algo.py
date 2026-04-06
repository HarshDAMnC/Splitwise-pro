import heapq
from collections import defaultdict

def simplify_debts(balances):
    """
    Simplifies debts using a Greedy Max-Heap approach.
    
    Time Complexity: O(V log V)
    Space Complexity: O(V)
    
    Args:
        balances (dict): A dictionary mapping user_id to their net balance.
                         Positive balance: User is a Creditor (is owed money)
                         Negative balance: User is a Debtor (owes money)
                         
    Returns:
        list of tuples (debtor_id, creditor_id, settle_amount)
    """
    creditors = [] # Max heap for creditors: (-balance, user_id)
    debtors = []   # Max heap for debtors: (-abs(balance), user_id)
    
    # Separate users into creditors and debtors
    for user_id, balance in balances.items():
        if balance > 0.001:  # Ignore floating point precision issues near zero
            heapq.heappush(creditors, (-balance, user_id))
        elif balance < -0.001:
            heapq.heappush(debtors, (balance, user_id)) 
            # Note: balance is negative, so placing it directly in heapq acts as a max heap 
            # based on its absolute value (since larger negative numbers are smaller, 
            # wait, Python's heapq is a MIN heap.
            # To get a MAX heap of positive balances, we store (-balance).
            # If balance is -50, and we want it to be popped first, we should store its absolute value 50 as -50.
            # E.g., balance = -50, we push -(-balance) = -50. Wait, no.
            # Python is min heap.
            # For creditors (+ve): To pop max first, store (-balance). So 50 -> -50, 20 -> -20. Min is -50 (Max creditor).
            # For debtors (-ve): To pop max absolute value first, store (balance). So -50 -> -50, -20 -> -20. Min is -50 (Max debtor).
            
    transactions = []
    
    # Process the heaps until everyone is settled
    while creditors and debtors:
        # Pop max creditor and max debtor
        c_neg_bal, c_id = heapq.heappop(creditors)
        d_val_bal, d_id = heapq.heappop(debtors)
        
        c_bal = -c_neg_bal  # Convert back to positive
        d_bal = -d_val_bal  # Convert back to positive magnitude
        
        # Settle the minimum of the two
        settle_amount = min(c_bal, d_bal)
        # Round up to 2 decimal places to avoid floating point sprawl
        settle_amount = round(settle_amount, 2)
        
        transactions.append((d_id, c_id, settle_amount))
        
        # Adjust remaining amounts and push back to heap if they still owe/are owed
        if c_bal > settle_amount + 0.001:
            heapq.heappush(creditors, (-(c_bal - settle_amount), c_id))
        if d_bal > settle_amount + 0.001:
            heapq.heappush(debtors, (-(d_bal - settle_amount), d_id))
            
    return transactions

if __name__ == "__main__":
    # Test cases to prove it works as an isolated script
    print("Testing Graph Algorithm...")
    # A owes B 10, B owes C 10 -> Net: A: -10, B: 0, C: +10
    test_balances_1 = {'A': -10, 'B': 0, 'C': 10}
    res_1 = simplify_debts(test_balances_1)
    print("Test 1 (A->C):", res_1) # Expect [('A', 'C', 10.0)]
    
    # Complex case
    # A: +50, B: +30, C: -40, D: -40
    test_balances_2 = {'A': 50, 'B': 30, 'C': -40, 'D': -40}
    res_2 = simplify_debts(test_balances_2)
    print("Test 2 Complex:", res_2) 
    # Mins picked:
    # 1. A(50), C/D(40) => D pays A 40
    # 2. A(10), C(40) => C pays A 10
    # 3. B(30), C(30) => C pays B 30

import uuid
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.supabase_client import get_db

class MockDB:
    """Fallback in-memory DB if Supabase is not configured."""
    def __init__(self):
        self.collections = {
            'users': {}, 'groups': {}, 'group_members': {},
            'categories': {}, 'expenses': {}, 'expense_payers': {},
            'expense_splits': {}, 'transactions': {}, 'settlements': {},
            'user_balances_cache': {}
        }

    def set(self, col, doc_id, data):
        self.collections[col][doc_id] = data

    def query(self, col, key, val):
        return [doc for doc in self.collections[col].values() if doc.get(key) == val]

    def get_all(self, col):
        return list(self.collections[col].values())

db_conn = get_db()
is_mock = (db_conn == "MOCK_DB_MISSING_KEY")
mock_db = MockDB() if is_mock else None

def generate_id():
    return str(uuid.uuid4())

def now():
    return datetime.utcnow().isoformat()

def insert_doc(table, data):
    if is_mock:
        doc_id = data.get('id')
        if not doc_id:
            doc_id = generate_id()
            data['id'] = doc_id
        mock_db.set(table, doc_id, data)
        return doc_id
    else:
        # Supabase API
        response = db_conn.table(table).insert(data).execute()
        return response.data[0]['id']

def create_user(name, email):
    # Depending on schema, id acts as uuid
    uid = generate_id()
    insert_doc('users', {
        'id': uid,
        'name': name,
        'email': email,
        'created_at': now()
    })
    return uid

def create_group(name, description, creator_id):
    gid = generate_id()
    insert_doc('groups', {
        'id': gid,
        'name': name,
        'description': description,
        'created_by': creator_id,
        'created_at': now()
    })
    add_group_member(gid, creator_id)
    return gid

def add_group_member(group_id, user_id):
    mid = generate_id()
    insert_doc('group_members', {
        'id': mid,
        'group_id': group_id,
        'user_id': user_id,
        'joined_at': now()
    })
    return mid

def update_balance_cache(group_id, user_id, amount_change):
    if is_mock:
        docs = mock_db.query('user_balances_cache', 'user_id', user_id)
        docs = [d for d in docs if d.get('group_id') == group_id]
        if docs:
            doc = docs[0]
            doc['net_balance'] += amount_change
        else:
            insert_doc('user_balances_cache', {
                'id': generate_id(),
                'group_id': group_id,
                'user_id': user_id,
                'net_balance': amount_change
            })
    else:
        # Supabase Logic
        response = db_conn.table('user_balances_cache').select('*').eq('group_id', group_id).eq('user_id', user_id).execute()
        if len(response.data) > 0:
            doc = response.data[0]
            new_bal = float(doc['net_balance']) + amount_change
            db_conn.table('user_balances_cache').update({'net_balance': new_bal}).eq('id', doc['id']).execute()
        else:
            insert_doc('user_balances_cache', {
                'id': generate_id(),
                'group_id': group_id,
                'user_id': user_id,
                'net_balance': amount_change
            })

def add_expense(group_id, description, category_id, total_amount, created_by, payers, splits):
    eid = generate_id()
    insert_doc('expenses', {
        'id': eid,
        'group_id': group_id,
        'category_id': category_id,
        'description': description,
        'total_amount': total_amount,
        'created_by': created_by,
        'created_at': now()
    })
    
    # 1. Who paid? Increase their balance
    for u_id, amt in payers.items():
        if amt > 0:
            insert_doc('expense_payers', {
                'id': generate_id(),
                'expense_id': eid,
                'user_id': u_id,
                'amount_paid': amt
            })
            update_balance_cache(group_id, u_id, amt)
            
    # 2. Who owes? Decrease their balance
    for u_id, amt in splits.items():
        if amt > 0:
            insert_doc('expense_splits', {
                'id': generate_id(),
                'expense_id': eid,
                'user_id': u_id,
                'amount_owed': amt
            })
            update_balance_cache(group_id, u_id, -amt)
            
    return eid

def get_group_balances(group_id):
    balances = {}
    if is_mock:
        docs = mock_db.query('user_balances_cache', 'group_id', group_id)
        for doc in docs:
            balances[doc['user_id']] = doc['net_balance']
    else:
        response = db_conn.table('user_balances_cache').select('user_id, net_balance').eq('group_id', group_id).execute()
        for doc in response.data:
            balances[doc['user_id']] = float(doc['net_balance'])
    return balances

def save_simplified_graph(group_id, transactions_list):
    """Caches the DSA algorithm output directly into the transactions table."""
    if is_mock: return
    
    # Clear old identical cached graph edges for this group to avoid duplication
    db_conn.table('transactions').delete().eq('group_id', group_id).eq('type', 'SYSTEM_GENERATED_DEBT').execute()
    
    # Store the highly minimized edges
    for debtor, creditor, amt in transactions_list:
        insert_doc('transactions', {
            'id': generate_id(),
            'group_id': group_id,
            'from_user_id': debtor,
            'to_user_id': creditor,
            'amount': amt,
            'type': 'SYSTEM_GENERATED_DEBT',
            'created_at': now()
        })

def add_settlement(group_id, from_user, to_user, amount):
    """Physically records a cash payment sent from a debtor to a creditor."""
    insert_doc('settlements', {
        'id': generate_id(),
        'from_user_id': from_user,
        'to_user_id': to_user,
        'amount': amount,
        'group_id': group_id,
        'status': 'COMPLETED',
        'settled_at': now()
    })
    
    # Crucially update the ongoing global tally:
    # If I owed you Money (my net balance is negative), and I pay you, my net balance increases
    # If You were owed Money (your net balance is positive), and I pay you, your net balance decreases
    update_balance_cache(group_id, from_user, amount)
    update_balance_cache(group_id, to_user, -amount)

def get_users():
    if is_mock:
        return mock_db.get_all('users')
    response = db_conn.table('users').select('*').execute()
    return response.data

def get_groups():
    if is_mock:
        return mock_db.get_all('groups')
    response = db_conn.table('groups').select('*').execute()
    return response.data

def get_expenses(group_id):
    if is_mock:
        return mock_db.query('expenses', 'group_id', group_id)
    response = db_conn.table('expenses').select('*').eq('group_id', group_id).execute()
    return sorted(response.data, key=lambda x: x.get('created_at', ''), reverse=True)


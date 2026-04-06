const API_BASE = 'http://localhost:5000/api';
let users = [];
let groups = [];
let activeGroup = null;

const usersList = document.getElementById('users-list');
const groupsList = document.getElementById('groups-list');
const expContainer = document.getElementById('expenses-container');
const balList = document.getElementById('balances-list');

async function init() {
    await fetchUsers();
    await fetchGroups();
    updateSidebar();
}

function setStatus(msg) {
    const t = document.getElementById('toast');
    t.innerText = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

async function fetchUsers() {
    const r = await fetch(`${API_BASE}/users`);
    users = await r.json();
}
async function fetchGroups() {
    const r = await fetch(`${API_BASE}/groups`);
    groups = await r.json();
}

function updateSidebar() {
    usersList.innerHTML = '';
    users.forEach(u => {
        let li = document.createElement('li');
        li.innerText = u.name;
        usersList.appendChild(li);
    });
    
    groupsList.innerHTML = '';
    groups.forEach(g => {
        let li = document.createElement('li');
        li.innerText = g.name;
        li.onclick = () => selectGroup(g.id, g.name, li);
        groupsList.appendChild(li);
    });
}

async function selectGroup(id, name, el) {
    activeGroup = id;
    document.getElementById('active-group-name').innerText = name;
    
    document.querySelectorAll('#groups-list li').forEach(l=>l.classList.remove('active'));
    if(el) el.classList.add('active');
    
    await refreshGroupView();
}

async function refreshGroupView() {
    if(!activeGroup) return;
    
    // 1. Fetch Expenses History
    const r1 = await fetch(`${API_BASE}/groups/${activeGroup}/expenses`);
    const expenses = await r1.json();
    expContainer.innerHTML = '';
    
    if(expenses.length === 0) {
        expContainer.innerHTML = '<div class="empty-state">No expenses found here yet.</div>';
    } else {
        expenses.forEach(e => {
            const payerName = users.find(u=>u.id === e.created_by)?.name || 'Someone';
            let div = document.createElement('div');
            div.className = 'expense-item';
            
            // Format nice date
            const dateStr = new Date(e.created_at).toLocaleDateString('en-US', {month:'short', day:'numeric'});
            
            div.innerHTML = `
                <div class="expense-date">${dateStr}</div>
                <div class="expense-desc">${e.description}</div>
                <div class="expense-info">${payerName} paid<br><span class="expense-amount">$${parseFloat(e.total_amount).toFixed(2)}</span></div>
            `;
            expContainer.appendChild(div);
        });
    }

    // 2. Fetch Minimized Graph and Cache
    const r2 = await fetch(`${API_BASE}/groups/${activeGroup}/settle`);
    const graph = await r2.json();
    balList.innerHTML = '';
    
    if(graph.minimized_transactions.length === 0) {
         balList.innerHTML = '<li class="empty-state">Everyone is fully settled up! 🎉</li>';
    } else {
         graph.minimized_transactions.forEach(t => {
             const fName = users.find(u=>u.id===t.from)?.name || t.from.substring(0,6);
             const tName = users.find(u=>u.id===t.to)?.name || t.to.substring(0,6);
             let li = document.createElement('li');
             li.innerHTML = `
                <div class="balance-row">
                    <span><span class="debtor">${fName}</span> <span class="owes-text">owes</span> <span class="creditor">${tName}</span></span>
                    <strong>$${t.amount.toFixed(2)}</strong>
                </div>
             `;
             balList.appendChild(li);
         });
    }
}

// ----------------------------
// MODAL & FORM LOGIC
// ----------------------------

document.getElementById('btn-refresh-balances').onclick = refreshGroupView;

document.getElementById('btn-new-group').onclick = async () => {
    let name = prompt("Group Name:");
    if(name) {
        await fetch(`${API_BASE}/groups`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: name, description: 'Created in UI'}) });
        setStatus('Group added!');
        init();
    }
};

document.getElementById('btn-new-user').onclick = async () => {
    let name = prompt("User Name:");
    if(name) {
        await fetch(`${API_BASE}/users`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name: name, email: name.toLowerCase()+'@test.com'}) });
        setStatus('User added!');
        init();
    }
};


document.getElementById('btn-add-expense').onclick = () => {
    if(!activeGroup) return setStatus("Select a group first!");
    const m = document.getElementById('modal-expense');
    
    const payerSelect = document.getElementById('exp-payer');
    payerSelect.innerHTML = users.map(u => `<option value="${u.id}">${u.name}</option>`).join('');
    
    const splitContainer = document.getElementById('split-users-container');
    splitContainer.innerHTML = users.map(u => `
        <div class="split-user-row">
            <span>${u.name}</span>
            <input type="number" data-uid="${u.id}" class="split-amt-input" value="0" step="0.01">
        </div>
    `).join('');
    
    m.classList.add('open');
};

document.getElementById('btn-settle-up').onclick = () => {
    if(!activeGroup) return setStatus("Select a group first!");
    const m = document.getElementById('modal-settle');
    
    document.getElementById('settle-payer').innerHTML = users.map(u => `<option value="${u.id}">${u.name}</option>`).join('');
    document.getElementById('settle-payee').innerHTML = users.map(u => `<option value="${u.id}">${u.name}</option>`).join('');
    
    m.classList.add('open');
};

window.closeModals = () => {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('open'));
};

document.getElementById('submit-expense').onclick = async () => {
    const desc = document.getElementById('exp-desc').value;
    const amt = parseFloat(document.getElementById('exp-amount').value);
    const payer = document.getElementById('exp-payer').value;
    
    if(!desc || !amt) return alert("Fill out description & amount!");

    let splitsDict = {};
    document.querySelectorAll('.split-amt-input').forEach(i => {
        let v = parseFloat(i.value);
        if(v > 0) splitsDict[i.dataset.uid] = v;
    });

    try {
        await fetch(`${API_BASE}/expenses`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                group_id: activeGroup,
                description: desc,
                total_amount: amt,
                created_by: payer,
                payers: { [payer]: amt },
                splits: splitsDict
            })
        });
        closeModals();
        setStatus("Expense Successfully Logged in Supabase!");
        document.getElementById('exp-desc').value = '';
        document.getElementById('exp-amount').value = '';
        refreshGroupView();
    } catch(e) { setStatus("Error logging expense"); }
};

document.getElementById('submit-settlement').onclick = async () => {
    const payer = document.getElementById('settle-payer').value;
    const payee = document.getElementById('settle-payee').value;
    const amt = parseFloat(document.getElementById('settle-amount').value);
    
    if(payer === payee) return alert("You can't pay yourself!");
    if(!amt || amt <= 0) return alert("Amount must be valid.");

    try {
        await fetch(`${API_BASE}/settlements`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ group_id: activeGroup, from_user: payer, to_user: payee, amount: amt })
        });
        closeModals();
        setStatus("Cash Payment Sent & Graph Updated!");
        document.getElementById('settle-amount').value = '';
        refreshGroupView();
    } catch(e) { setStatus("Error processing settlement"); }
};

// Start
init();

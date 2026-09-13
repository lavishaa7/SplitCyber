/**
 * SplitCyber - Cyber-Glass Single Page Web Application
 */

const API_BASE = '/api';

// Application State
const state = {
  users: [],
  groups: [],
  activeGroupId: null,
  activeGroupData: null,
  balanceSummary: null,
  expenses: [],
  settlements: [],
  activeSplitType: 'EQUAL',
};

// --- API Service Wrapper ---
const API = {
  async fetchJSON(url, options = {}) {
    try {
      const res = await fetch(`${API_BASE}${url}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'API Request failed' }));
        throw new Error(err.detail || `HTTP Error ${res.status}`);
      }
      return res.status === 204 ? null : await res.json();
    } catch (err) {
      showToast(err.message, 'error');
      throw err;
    }
  },

  getUsers: () => API.fetchJSON('/users'),
  createUser: (data) => API.fetchJSON('/users', { method: 'POST', body: JSON.stringify(data) }),
  
  getGroups: () => API.fetchJSON('/groups'),
  createGroup: (data) => API.fetchJSON('/groups', { method: 'POST', body: JSON.stringify(data) }),
  addMemberToGroup: (groupId, userId) => API.fetchJSON(`/groups/${groupId}/members`, { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
  
  getGroupBalances: (groupId) => API.fetchJSON(`/groups/${groupId}/balances`),
  getGroupExpenses: (groupId) => API.fetchJSON(`/groups/${groupId}/expenses`),
  createExpense: (groupId, data) => API.fetchJSON(`/groups/${groupId}/expenses`, { method: 'POST', body: JSON.stringify(data) }),
  deleteExpense: (expenseId) => API.fetchJSON(`/groups/0/expenses/expenses/${expenseId}`, { method: 'DELETE' }),

  getGroupSettlements: (groupId) => API.fetchJSON(`/groups/${groupId}/settlements`),
  createSettlement: (groupId, data) => API.fetchJSON(`/groups/${groupId}/settlements`, { method: 'POST', body: JSON.stringify(data) }),
};

// --- Toast Notifications ---
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// --- Initialize App ---
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await refreshUsersAndGroups();
  checkBackendHealth();
});

async function checkBackendHealth() {
  try {
    const res = await fetch('/api/health');
    if (res.ok) {
      document.getElementById('backend-status-text').innerText = 'Backend Connected (MySQL / SQLite)';
    }
  } catch (e) {
    document.getElementById('backend-status-text').innerText = 'Backend Disconnected';
  }
}

// --- Data Refresh Methods ---
async function refreshUsersAndGroups() {
  try {
    state.users = await API.getUsers();
    state.groups = await API.getGroups();
    renderSidebar();
    
    if (state.groups.length > 0 && !state.activeGroupId) {
      selectGroup(state.groups[0].id);
    }
  } catch (e) {
    console.error('Failed to load initial data', e);
  }
}

async function loadGroupDetails(groupId) {
  state.activeGroupId = groupId;
  try {
    const [balance, expenses, settlements] = await Promise.all([
      API.getGroupBalances(groupId),
      API.getGroupExpenses(groupId),
      API.getGroupSettlements(groupId)
    ]);
    
    state.balanceSummary = balance;
    state.expenses = expenses;
    state.settlements = settlements;

    const group = state.groups.find(g => g.id === groupId);
    state.activeGroupData = group;

    renderWorkspace();
  } catch (e) {
    console.error('Error loading group data', e);
  }
}

function selectGroup(groupId) {
  state.activeGroupId = groupId;
  renderSidebar();
  loadGroupDetails(groupId);
}

// --- Rendering Functions ---
function renderSidebar() {
  const groupsContainer = document.getElementById('groups-container');
  groupsContainer.innerHTML = '';

  if (state.groups.length === 0) {
    groupsContainer.innerHTML = '<div class="hint-text p-2">No groups created yet</div>';
  } else {
    state.groups.forEach(g => {
      const item = document.createElement('div');
      item.className = `group-item ${g.id === state.activeGroupId ? 'active' : ''}`;
      item.onclick = () => selectGroup(g.id);
      
      const memberCount = g.members ? g.members.length : 0;
      item.innerHTML = `
        <div class="group-icon"><i class="ri-folder-shared-line"></i></div>
        <div class="group-details">
          <span class="group-name">${escapeHTML(g.name)}</span>
          <span class="group-meta">${memberCount} members • ${g.category || 'General'}</span>
        </div>
      `;
      groupsContainer.appendChild(item);
    });
  }

  const usersContainer = document.getElementById('users-container');
  usersContainer.innerHTML = '';
  state.users.forEach(u => {
    const uItem = document.createElement('div');
    uItem.className = 'user-item';
    uItem.innerHTML = `
      <div class="user-avatar" style="background:${u.avatar_color || '#8B5CF6'}">${u.name.charAt(0).toUpperCase()}</div>
      <div class="group-details">
        <span class="group-name">${escapeHTML(u.name)}</span>
        <span class="group-meta">${escapeHTML(u.email)}</span>
      </div>
    `;
    usersContainer.appendChild(uItem);
  });
}

function renderWorkspace() {
  const emptyView = document.getElementById('empty-state-view');
  const dashboard = document.getElementById('main-dashboard');
  const group = state.activeGroupData;

  if (!group || !state.balanceSummary) {
    emptyView.style.display = 'flex';
    dashboard.style.display = 'none';
    return;
  }

  emptyView.style.display = 'none';
  dashboard.style.display = 'grid';

  // Update Header Info
  document.getElementById('current-group-name').innerText = group.name;
  document.getElementById('current-group-desc').innerText = group.description || `${group.category} Expense Group`;

  document.getElementById('btn-add-member').disabled = false;
  document.getElementById('btn-open-add-expense').disabled = false;

  // Metrics
  const summary = state.balanceSummary;
  document.getElementById('metric-total-spend').innerText = `$${summary.total_group_spending.toFixed(2)}`;
  document.getElementById('metric-members-count').innerText = `${summary.member_balances.length} Members`;
  document.getElementById('metric-transfers-count').innerText = `${summary.simplified_transactions.length} Transfers`;

  // Render Balances Tab
  renderBalancesList(summary.member_balances);
  renderDebtTransfers(summary.simplified_transactions);

  // Render Visual Graph Vector Map
  renderDebtVectorMap(summary);

  // Render Expenses Feed
  renderExpensesFeed();

  // Render Settlements Feed
  renderSettlementsFeed();
}

function renderBalancesList(balances) {
  const container = document.getElementById('balances-list-container');
  container.innerHTML = '';

  if (!balances || balances.length === 0) {
    container.innerHTML = '<div class="hint-text">No members in this group</div>';
    return;
  }

  balances.forEach(m => {
    const row = document.createElement('div');
    row.className = 'balance-row';
    
    let badgeClass = 'badge-settled';
    let statusText = 'Settled Up';
    let balanceDisplay = `$0.00`;

    if (m.net_balance > 0.01) {
      badgeClass = 'badge-creditor';
      statusText = 'Gets Back';
      balanceDisplay = `+$${m.net_balance.toFixed(2)}`;
    } else if (m.net_balance < -0.01) {
      badgeClass = 'badge-debtor';
      statusText = 'Owes';
      balanceDisplay = `-$${Math.abs(m.net_balance).toFixed(2)}`;
    }

    row.innerHTML = `
      <div class="user-info-chip">
        <div class="user-avatar" style="background:${m.avatar_color}">${m.name.charAt(0).toUpperCase()}</div>
        <div>
          <div style="font-weight:600">${escapeHTML(m.name)}</div>
          <div class="hint-text">Paid: $${m.total_paid.toFixed(2)} | Owed Share: $${m.total_share.toFixed(2)}</div>
        </div>
      </div>
      <div style="text-align:right">
        <span class="badge ${badgeClass}">${statusText}</span>
        <div style="font-family:var(--font-heading); font-weight:700; font-size:1.1rem; margin-top:0.2rem">${balanceDisplay}</div>
      </div>
    `;
    container.appendChild(row);
  });
}

function renderDebtTransfers(transfers) {
  const container = document.getElementById('debt-transfers-container');
  container.innerHTML = '';

  if (!transfers || transfers.length === 0) {
    container.innerHTML = `
      <div class="balance-row" style="justify-content:center; padding:1.5rem">
        <span class="badge badge-creditor"><i class="ri-checkbox-circle-fill"></i> All Group Debts are 100% Settled!</span>
      </div>
    `;
    return;
  }

  transfers.forEach(t => {
    const row = document.createElement('div');
    row.className = 'transfer-row';
    row.innerHTML = `
      <div class="transfer-flow">
        <span>${escapeHTML(t.payer_name)}</span>
        <span class="transfer-arrow"><i class="ri-arrow-right-line"></i> pays</span>
        <span>${escapeHTML(t.payee_name)}</span>
      </div>
      <div style="display:flex; align-items:center; gap:0.75rem">
        <span style="font-family:var(--font-heading); font-weight:700; color:var(--accent-purple); font-size:1.1rem">$${t.amount.toFixed(2)}</span>
        <button class="btn btn-sm btn-secondary" onclick="openSettleUpModal(${t.payer_id}, ${t.payee_id}, ${t.amount})">
          <i class="ri-exchange-dollar-line"></i> Settle
        </button>
      </div>
    `;
    container.appendChild(row);
  });
}

// --- SVG Debt Vector Map Visualizer ---
function renderDebtVectorMap(summary) {
  const svg = document.getElementById('debt-vector-svg');
  const connGroup = document.getElementById('svg-connections');
  const nodesGroup = document.getElementById('svg-nodes');

  connGroup.innerHTML = '';
  nodesGroup.innerHTML = '';

  const members = summary.member_balances;
  if (!members || members.length === 0) return;

  const width = 800;
  const height = 450;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(centerX, centerY) - 80;

  // Calculate circular layout coordinates for nodes
  const nodeCoords = {};
  const numNodes = members.length;

  members.forEach((m, idx) => {
    const angle = (idx / numNodes) * 2 * Math.PI - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    nodeCoords[m.user_id] = { x, y, member: m };
  });

  // Render Connection Curved Vector Arrows for simplified transactions
  summary.simplified_transactions.forEach(t => {
    const p1 = nodeCoords[t.payer_id];
    const p2 = nodeCoords[t.payee_id];
    if (!p1 || !p2) return;

    // Draw curved path
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const midX = (p1.x + p2.x) / 2 - dy * 0.2;
    const midY = (p1.y + p2.y) / 2 + dx * 0.2;

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M ${p1.x} ${p1.y} Q ${midX} ${midY} ${p2.x} ${p2.y}`);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#8B5CF6');
    path.setAttribute('stroke-width', '2.5');
    path.setAttribute('stroke-dasharray', '6 3');
    path.setAttribute('marker-end', 'url(#arrowhead)');
    path.setAttribute('filter', 'url(#neon-glow)');
    connGroup.appendChild(path);

    // Label for transaction amount
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', midX);
    text.setAttribute('y', midY - 6);
    text.setAttribute('fill', '#06B6D4');
    text.setAttribute('font-size', '12');
    text.setAttribute('font-weight', 'bold');
    text.setAttribute('text-anchor', 'middle');
    text.textContent = `$${t.amount.toFixed(2)}`;
    connGroup.appendChild(text);
  });

  // Render Nodes
  Object.values(nodeCoords).forEach(({ x, y, member }) => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', 'node-group');

    let strokeColor = '#06B6D4';
    if (member.net_balance > 0.01) strokeColor = '#10B981';
    if (member.net_balance < -0.01) strokeColor = '#F43F5E';

    // Outer Circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', x);
    circle.setAttribute('cy', y);
    circle.setAttribute('r', '26');
    circle.setAttribute('fill', '#0F172A');
    circle.setAttribute('stroke', strokeColor);
    circle.setAttribute('stroke-width', '3');
    circle.setAttribute('class', 'node-circle');
    circle.setAttribute('filter', 'url(#neon-glow)');
    g.appendChild(circle);

    // Text Name
    const textName = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    textName.setAttribute('x', x);
    textName.setAttribute('y', y + 4);
    textName.setAttribute('fill', '#FFFFFF');
    textName.setAttribute('font-size', '13');
    textName.setAttribute('font-weight', 'bold');
    textName.setAttribute('text-anchor', 'middle');
    textName.textContent = member.name.substring(0, 8);
    g.appendChild(textName);

    // Subtext Balance
    const textBal = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    textBal.setAttribute('x', x);
    textBal.setAttribute('y', y + 42);
    textBal.setAttribute('fill', strokeColor);
    textBal.setAttribute('font-size', '11');
    textBal.setAttribute('font-weight', '600');
    textBal.setAttribute('text-anchor', 'middle');
    textBal.textContent = member.net_balance >= 0 ? `+$${member.net_balance.toFixed(2)}` : `-$${Math.abs(member.net_balance).toFixed(2)}`;
    g.appendChild(textBal);

    nodesGroup.appendChild(g);
  });
}

function renderExpensesFeed() {
  const container = document.getElementById('expenses-feed-container');
  container.innerHTML = '';

  if (!state.expenses || state.expenses.length === 0) {
    container.innerHTML = '<div class="hint-text">No expenses recorded yet in this group</div>';
    return;
  }

  state.expenses.forEach(exp => {
    const item = document.createElement('div');
    item.className = 'expense-item';

    const categoryIcons = {
      Dining: 'ri-restaurant-line',
      Transport: 'ri-taxi-line',
      Housing: 'ri-hotel-line',
      Entertainment: 'ri-ticket-line',
      General: 'ri-shopping-bag-line',
    };

    const icon = categoryIcons[exp.category] || 'ri-bill-line';
    const splitCount = exp.splits ? exp.splits.length : 0;

    item.innerHTML = `
      <div class="expense-left">
        <div class="category-icon"><i class="${icon}"></i></div>
        <div class="expense-title-group">
          <h4>${escapeHTML(exp.title)}</h4>
          <span class="expense-sub">Paid by <strong>${escapeHTML(exp.paid_by ? exp.paid_by.name : 'Unknown')}</strong> • Split (${exp.split_type}) among ${splitCount} members</span>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:1rem">
        <span class="expense-amount-tag">$${exp.amount.toFixed(2)}</span>
        <button class="icon-btn" onclick="handleDeleteExpense(${exp.id})" title="Delete Expense"><i class="ri-delete-bin-line"></i></button>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderSettlementsFeed() {
  const container = document.getElementById('settlements-feed-container');
  container.innerHTML = '';

  if (!state.settlements || state.settlements.length === 0) {
    container.innerHTML = '<div class="hint-text">No settlement payments recorded yet</div>';
    return;
  }

  state.settlements.forEach(st => {
    const item = document.createElement('div');
    item.className = 'settlement-item';
    item.innerHTML = `
      <div class="expense-left">
        <div class="category-icon" style="background:rgba(16,185,129,0.15); color:var(--accent-emerald)">
          <i class="ri-checkbox-circle-line"></i>
        </div>
        <div class="expense-title-group">
          <h4>${escapeHTML(st.payer ? st.payer.name : 'Payer')} paid ${escapeHTML(st.payee ? st.payee.name : 'Payee')}</h4>
          <span class="expense-sub">${escapeHTML(st.notes || 'Settlement payment')} • ${new Date(st.created_at).toLocaleDateString()}</span>
        </div>
      </div>
      <span class="expense-amount-tag" style="color:var(--accent-emerald)">$${st.amount.toFixed(2)}</span>
    `;
    container.appendChild(item);
  });
}

// --- Event Listeners & Modals ---
function setupEventListeners() {
  // Modal Triggers
  document.getElementById('btn-open-create-group').onclick = () => openModal('modal-create-group');
  document.getElementById('btn-welcome-create-group').onclick = () => openModal('modal-create-group');
  document.getElementById('btn-open-create-user').onclick = () => openModal('modal-create-user');
  document.getElementById('btn-add-member').onclick = () => openAddMemberModal();
  document.getElementById('btn-open-add-expense').onclick = () => openAddExpenseModal();
  document.getElementById('btn-tab-add-expense').onclick = () => openAddExpenseModal();

  // Close buttons
  document.querySelectorAll('[data-close]').forEach(btn => {
    btn.onclick = () => closeModal(btn.getAttribute('data-close'));
  });

  // Tab Switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      document.getElementById(targetId).classList.add('active');
      if (targetId === 'tab-visual-graph' && state.balanceSummary) {
        renderDebtVectorMap(state.balanceSummary);
      }
    };
  });

  // Form Submissions
  document.getElementById('form-create-group').onsubmit = handleCreateGroup;
  document.getElementById('form-create-user').onsubmit = handleCreateUser;
  document.getElementById('form-add-member').onsubmit = handleAddMember;
  document.getElementById('form-quick-create-add-member').onsubmit = handleQuickCreateAndAddMember;
  document.getElementById('form-add-expense').onsubmit = handleCreateExpense;
  document.getElementById('form-settle-up').onsubmit = handleCreateSettlement;

  // Split Type Selector Buttons
  document.querySelectorAll('.split-toggle-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.split-toggle-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeSplitType = btn.getAttribute('data-split-type');
      renderSplitsMatrix();
    };
  });

  // Live validation on expense total input change
  document.getElementById('input-expense-amount').oninput = renderSplitsMatrix;
}

function openModal(id) {
  const modal = document.getElementById(id);
  modal.classList.add('active');
  if (id === 'modal-create-group') {
    populateCreateGroupUsers();
  }
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}

// --- Form Handlers ---
async function handleCreateUser(e) {
  e.preventDefault();
  const name = document.getElementById('input-user-name').value.trim();
  const email = document.getElementById('input-user-email').value.trim();
  const color = document.querySelector('input[name="user-color"]:checked')?.value || '#8B5CF6';

  try {
    await API.createUser({ name, email, avatar_color: color });
    showToast(`Registered user ${name}!`);
    closeModal('modal-create-user');
    document.getElementById('form-create-user').reset();
    await refreshUsersAndGroups();
  } catch (err) {}
}

function populateCreateGroupUsers() {
  const container = document.getElementById('create-group-user-checkboxes');
  container.innerHTML = '';
  state.users.forEach(u => {
    const label = document.createElement('label');
    label.className = 'checkbox-item';
    label.innerHTML = `
      <input type="checkbox" value="${u.id}" checked>
      <span>${escapeHTML(u.name)} (${escapeHTML(u.email)})</span>
    `;
    container.appendChild(label);
  });
}

async function handleCreateGroup(e) {
  e.preventDefault();
  const name = document.getElementById('input-group-name').value.trim();
  const category = document.getElementById('input-group-category').value;
  const description = document.getElementById('input-group-desc').value.trim();
  
  const selectedUserIds = Array.from(
    document.querySelectorAll('#create-group-user-checkboxes input:checked')
  ).map(cb => parseInt(cb.value));

  try {
    const group = await API.createGroup({
      name,
      category,
      description,
      initial_member_ids: selectedUserIds,
    });
    showToast(`Created group "${name}"!`);
    closeModal('modal-create-group');
    document.getElementById('form-create-group').reset();
    await refreshUsersAndGroups();
    selectGroup(group.id);
  } catch (err) {}
}

function openAddMemberModal() {
  if (!state.activeGroupData) return;
  const select = document.getElementById('select-add-member-user');
  const submitBtn = document.getElementById('btn-submit-add-existing');
  select.innerHTML = '';

  const existingMemberIds = (state.activeGroupData.members || []).map(m => m.user_id);
  const availableUsers = state.users.filter(u => !existingMemberIds.includes(u.id));

  if (availableUsers.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.innerText = 'No unassigned users available';
    select.appendChild(opt);
    select.disabled = true;
    submitBtn.disabled = true;
  } else {
    select.disabled = false;
    submitBtn.disabled = false;
    availableUsers.forEach(u => {
      const opt = document.createElement('option');
      opt.value = u.id;
      opt.innerText = `${u.name} (${u.email})`;
      select.appendChild(opt);
    });
  }

  openModal('modal-add-member');
}

async function handleAddMember(e) {
  e.preventDefault();
  const userIdStr = document.getElementById('select-add-member-user').value;
  if (!userIdStr) return;
  const userId = parseInt(userIdStr);

  try {
    await API.addMemberToGroup(state.activeGroupId, userId);
    showToast('Member added to group!');
    closeModal('modal-add-member');
    await refreshUsersAndGroups();
    await loadGroupDetails(state.activeGroupId);
  } catch (err) {}
}

async function handleQuickCreateAndAddMember(e) {
  e.preventDefault();
  const name = document.getElementById('input-quick-user-name').value.trim();
  const email = document.getElementById('input-quick-user-email').value.trim();
  
  const colors = ['#8B5CF6', '#06B6D4', '#10B981', '#F43F5E', '#F59E0B', '#EC4899'];
  const randomColor = colors[Math.floor(Math.random() * colors.length)];

  try {
    const newUser = await API.createUser({ name, email, avatar_color: randomColor });
    await API.addMemberToGroup(state.activeGroupId, newUser.id);
    showToast(`Created & added member ${name}!`);
    closeModal('modal-add-member');
    document.getElementById('form-quick-create-add-member').reset();
    await refreshUsersAndGroups();
    await loadGroupDetails(state.activeGroupId);
  } catch (err) {}
}

function openAddExpenseModal() {
  if (!state.activeGroupData) return;
  
  const payerSelect = document.getElementById('select-expense-payer');
  payerSelect.innerHTML = '';
  
  const members = state.balanceSummary ? state.balanceSummary.member_balances : [];
  members.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m.user_id;
    opt.innerText = m.name;
    payerSelect.appendChild(opt);
  });

  renderSplitsMatrix();
  openModal('modal-add-expense');
}

function renderSplitsMatrix() {
  const container = document.getElementById('splits-matrix-container');
  container.innerHTML = '';

  const totalAmount = parseFloat(document.getElementById('input-expense-amount').value) || 0;
  const members = state.balanceSummary ? state.balanceSummary.member_balances : [];

  members.forEach(m => {
    const row = document.createElement('div');
    row.className = 'split-member-row';

    let splitInputHTML = '';
    if (state.activeSplitType === 'EQUAL') {
      const equalShare = members.length > 0 ? (totalAmount / members.length).toFixed(2) : '0.00';
      splitInputHTML = `<span class="hint-text">$${equalShare} per person</span>`;
    } else if (state.activeSplitType === 'EXACT') {
      splitInputHTML = `<input type="number" step="0.01" class="split-amount-input" data-user-id="${m.user_id}" placeholder="0.00" style="width:110px" oninput="validateSplitMatrix()">`;
    } else if (state.activeSplitType === 'PERCENTAGE') {
      splitInputHTML = `<input type="number" step="0.1" class="split-pct-input" data-user-id="${m.user_id}" placeholder="0%" style="width:90px" oninput="validateSplitMatrix()"> %`;
    }

    row.innerHTML = `
      <span style="font-weight:600">${escapeHTML(m.name)}</span>
      <div>${splitInputHTML}</div>
    `;
    container.appendChild(row);
  });

  validateSplitMatrix();
}

function validateSplitMatrix() {
  const badge = document.getElementById('split-validation-badge');
  const totalAmount = parseFloat(document.getElementById('input-expense-amount').value) || 0;

  if (state.activeSplitType === 'EQUAL') {
    badge.className = 'badge badge-success';
    badge.innerText = 'Split 100% Equal';
    return true;
  }

  if (state.activeSplitType === 'EXACT') {
    const exactInputs = document.querySelectorAll('.split-amount-input');
    let sum = 0;
    exactInputs.forEach(i => sum += parseFloat(i.value) || 0);

    const diff = Math.abs(sum - totalAmount);
    if (totalAmount > 0 && diff <= 0.05) {
      badge.className = 'badge badge-success';
      badge.innerText = `Exact Sum: $${sum.toFixed(2)} (Valid)`;
      return true;
    } else {
      badge.className = 'badge badge-debtor';
      badge.innerText = `Sum: $${sum.toFixed(2)} / Total: $${totalAmount.toFixed(2)}`;
      return false;
    }
  }

  if (state.activeSplitType === 'PERCENTAGE') {
    const pctInputs = document.querySelectorAll('.split-pct-input');
    let sumPct = 0;
    pctInputs.forEach(i => sumPct += parseFloat(i.value) || 0);

    if (Math.abs(sumPct - 100.0) <= 0.1) {
      badge.className = 'badge badge-success';
      badge.innerText = `Percentage: 100% (Valid)`;
      return true;
    } else {
      badge.className = 'badge badge-debtor';
      badge.innerText = `Percentage: ${sumPct.toFixed(1)}% / 100%`;
      return false;
    }
  }
}

async function handleCreateExpense(e) {
  e.preventDefault();
  const title = document.getElementById('input-expense-title').value.trim();
  const amount = parseFloat(document.getElementById('input-expense-amount').value);
  const paidById = parseInt(document.getElementById('select-expense-payer').value);
  const category = document.getElementById('select-expense-category').value;
  const splitType = state.activeSplitType;

  if (!validateSplitMatrix()) {
    showToast('Please fix split values before submitting', 'error');
    return;
  }

  const splitsPayload = [];
  if (splitType === 'EXACT') {
    document.querySelectorAll('.split-amount-input').forEach(input => {
      splitsPayload.push({
        user_id: parseInt(input.getAttribute('data-user-id')),
        amount: parseFloat(input.value) || 0,
      });
    });
  } else if (splitType === 'PERCENTAGE') {
    document.querySelectorAll('.split-pct-input').forEach(input => {
      splitsPayload.push({
        user_id: parseInt(input.getAttribute('data-user-id')),
        percentage: parseFloat(input.value) || 0,
      });
    });
  }

  try {
    await API.createExpense(state.activeGroupId, {
      title,
      amount,
      paid_by_id: paidById,
      category,
      split_type: splitType,
      splits: splitsPayload,
    });

    showToast(`Recorded expense "${title}"!`);
    closeModal('modal-add-expense');
    document.getElementById('form-add-expense').reset();
    await loadGroupDetails(state.activeGroupId);
  } catch (err) {}
}

async function handleDeleteExpense(expenseId) {
  if (!confirm('Are you sure you want to delete this expense?')) return;
  try {
    await API.deleteExpense(expenseId);
    showToast('Expense deleted');
    await loadGroupDetails(state.activeGroupId);
  } catch (err) {}
}

function openSettleUpModal(payerId, payeeId, amount) {
  const payerSelect = document.getElementById('select-settle-payer');
  const payeeSelect = document.getElementById('select-settle-payee');
  payerSelect.innerHTML = '';
  payeeSelect.innerHTML = '';

  const members = state.balanceSummary ? state.balanceSummary.member_balances : [];
  members.forEach(m => {
    const optPayer = document.createElement('option');
    optPayer.value = m.user_id;
    optPayer.innerText = m.name;
    if (m.user_id === payerId) optPayer.selected = true;
    payerSelect.appendChild(optPayer);

    const optPayee = document.createElement('option');
    optPayee.value = m.user_id;
    optPayee.innerText = m.name;
    if (m.user_id === payeeId) optPayee.selected = true;
    payeeSelect.appendChild(optPayee);
  });

  document.getElementById('input-settle-amount').value = amount.toFixed(2);
  openModal('modal-settle-up');
}

async function handleCreateSettlement(e) {
  e.preventDefault();
  const payerId = parseInt(document.getElementById('select-settle-payer').value);
  const payeeId = parseInt(document.getElementById('select-settle-payee').value);
  const amount = parseFloat(document.getElementById('input-settle-amount').value);
  const notes = document.getElementById('input-settle-notes').value.trim();

  try {
    await API.createSettlement(state.activeGroupId, {
      payer_id: payerId,
      payee_id: payeeId,
      amount,
      notes,
    });
    showToast('Settlement recorded successfully! 🎉');
    closeModal('modal-settle-up');
    document.getElementById('form-settle-up').reset();
    await loadGroupDetails(state.activeGroupId);
  } catch (err) {}
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

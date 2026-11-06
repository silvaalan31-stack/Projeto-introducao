(() => {
  'use strict';
  const STORE_KEY = 'espaco-santa-maria-demo-v1';
  const LANES = [
    { id: 'backlog', title: 'Backlog', cls: 'backlog' },
    { id: 'current', title: 'Sprint Atual', cls: 'current' },
    { id: 'progress', title: 'Em Progresso', cls: 'progress' },
    { id: 'done', title: 'Concluído', cls: 'done' }
  ];
  const defaultData = {
    activeSprint: 's1',
    sprints: [
      { id: 's1', name: 'Sprint 01 — Organização', goal: 'Mapear o fluxo inicial de atendimento e definir os requisitos demonstrativos do projeto.', start: '2026-11-02', end: '2026-11-13' },
      { id: 's2', name: 'Sprint 02 — Protótipo', goal: 'Concluir o protótipo acadêmico e revisar a documentação e os exemplos.', start: '2026-11-16', end: '2026-11-27' }
    ],
    tasks: [
      { id: 't1', sprint: 's1', title: 'Mapear etapas do atendimento', description: 'Descrever o percurso do cadastro até o atendimento.', lane: 'done', due: '2026-11-04', checklist: [{ text: 'Listar etapas', done: true }, { text: 'Conferir ordem do fluxo', done: true }], comments: 'Fluxo inicial revisado para a demonstração.' },
      { id: 't2', sprint: 's1', title: 'Definir quadro da sprint', description: 'Organizar as listas e os cartões iniciais.', lane: 'progress', due: '2026-11-10', checklist: [{ text: 'Criar listas', done: true }, { text: 'Adicionar tarefas', done: false }, { text: 'Revisar status', done: false }], comments: 'Acompanhar os itens pendentes na revisão.' },
      { id: 't3', sprint: 's1', title: 'Esboçar tabela-verdade', description: 'Validar as expressões de consulta normal e emergência.', lane: 'current', due: '2026-11-12', checklist: [{ text: 'Registrar variáveis', done: true }, { text: 'Conferir 16 combinações', done: false }], comments: '' },
      { id: 't4', sprint: 's1', title: 'Revisar requisitos do projeto', description: 'Separar as cinco entregas acadêmicas.', lane: 'backlog', due: '2026-11-13', checklist: [{ text: 'Ler o enunciado', done: false }, { text: 'Confirmar entregáveis', done: false }], comments: '' },
      { id: 't5', sprint: 's2', title: 'Implementar cadastro Python', description: 'Preparar o menu, o cadastro e as estatísticas em Python.', lane: 'current', due: '2026-11-18', checklist: [{ text: 'Criar menu em loop', done: true }, { text: 'Validar idade e telefone', done: false }], comments: 'Dados fictícios para demonstração.' },
      { id: 't6', sprint: 's2', title: 'Modelar casos de uso', description: 'Desenhar atores, casos de uso e relações include.', lane: 'backlog', due: '2026-11-24', checklist: [{ text: 'Inserir atores', done: false }, { text: 'Conferir relações include', done: false }], comments: '' }
    ],
    reports: {
      s1: { results: 'Duas tarefas demonstrativas concluídas; o quadro e o fluxo inicial foram estruturados.', challenges: 'A tabela-verdade ainda requer conferência completa das 16 combinações.', positives: 'As atividades foram divididas em itens menores, facilitando o acompanhamento.', improvements: 'Reservar uma revisão dedicada à validação da lógica antes do próximo fechamento.' },
      s2: { results: 'Sprint demonstrativa planejada; entregas ainda em andamento.', challenges: 'O exemplo depende de revisão das validações e da documentação.', positives: 'A organização por checklist torna os próximos passos visíveis.', improvements: 'Atualizar o status dos cartões ao concluir cada item.' }
    }
  };
  let data = loadData();
  let toastTimer;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const esc = (value = '') => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
  function clone(value) { return JSON.parse(JSON.stringify(value)); }
  function loadData() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORE_KEY) || 'null');
      if (saved && Array.isArray(saved.sprints) && Array.isArray(saved.tasks)) return { ...clone(defaultData), ...saved };
    } catch (error) { console.warn('Os dados locais anteriores não puderam ser carregados.', error); }
    return clone(defaultData);
  }
  function saveData() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(data)); $('#reportSaved').textContent = 'Salvo neste navegador'; }
    catch (error) { $('#reportSaved').textContent = 'Não foi possível salvar localmente'; }
  }
  function showToast(message) {
    const node = $('#toast'); node.textContent = message; node.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove('show'), 2400);
  }
  function dateLabel(value) {
    if (!value) return 'Sem data';
    const date = new Date(`${value}T12:00:00`);
    return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short' }).format(date).replace('.', '');
  }
  function sprintById(id) { return data.sprints.find(sprint => sprint.id === id); }
  function activeSprint() { return sprintById(data.activeSprint) || data.sprints[0]; }
  function activeTasks() { const sprint = activeSprint(); return data.tasks.filter(task => sprint && task.sprint === sprint.id); }
  function renderSprintOptions() {
    const select = $('#sprintSelect');
    select.innerHTML = data.sprints.map(sprint => `<option value="${esc(sprint.id)}">${esc(sprint.name)}</option>`).join('');
    if (!sprintById(data.activeSprint)) data.activeSprint = data.sprints[0]?.id || '';
    select.value = data.activeSprint;
    const taskSelect = $('#taskSprint');
    taskSelect.innerHTML = data.sprints.map(sprint => `<option value="${esc(sprint.id)}">${esc(sprint.name)}</option>`).join('');
  }
  function renderBoard() {
    renderSprintOptions();
    const sprint = activeSprint();
    const board = $('#board');
    if (!sprint) { board.innerHTML = '<p class="board-empty">Crie uma sprint para organizar tarefas.</p>'; $('#sprintSummary').textContent = 'Nenhuma sprint cadastrada.'; return; }
    const tasks = activeTasks();
    $('#sprintSummary').textContent = `${dateLabel(sprint.start)} – ${dateLabel(sprint.end)} · Objetivo: ${sprint.goal}`;
    board.innerHTML = LANES.map(lane => {
      const items = tasks.filter(task => task.lane === lane.id);
      return `<section class="board-lane lane-${lane.cls}" data-lane="${lane.id}" aria-label="Lista ${lane.title}"><div class="lane-head"><span class="lane-title"><i class="lane-dot"></i>${lane.title}</span><span class="lane-count">${items.length}</span></div><div class="lane-drop" data-drop="${lane.id}">${items.length ? items.map(renderTask).join('') : '<div class="board-empty">Solte uma tarefa aqui</div>'}</div></section>`;
    }).join('');
    renderReportMetrics(); loadReportFields();
  }
  function renderTask(task) {
    const checks = task.checklist || [];
    const finished = checks.filter(check => check.done).length;
    const checklistHtml = checks.length ? `<div class="mini-checks">${checks.map((check, index) => `<label class="mini-check"><input type="checkbox" data-check-task="${esc(task.id)}" data-check-index="${index}" ${check.done ? 'checked' : ''} aria-label="${check.done ? 'Concluído' : 'Marcar'}: ${esc(check.text)}"><span>${esc(check.text)}</span></label>`).join('')}</div>` : '';
    const comments = (task.comments || '').trim();
    return `<article class="task-card" draggable="true" data-task="${esc(task.id)}"><button class="task-edit" type="button" data-edit-task="${esc(task.id)}" aria-label="Editar ${esc(task.title)}">···</button><h4>${esc(task.title)}</h4><p>${esc(task.description || 'Sem descrição.')}</p><div class="task-meta"><span title="Data prevista">◷ ${dateLabel(task.due)}</span>${checks.length ? `<span title="Itens concluídos">☑ ${finished}/${checks.length}</span>` : ''}${comments ? '<span title="Tem comentários">▤ comentário</span>' : ''}</div>${checklistHtml}</article>`;
  }
  function reportForCurrent() { const report = data.reports[activeSprint()?.id]; return report || { results: '', challenges: '', positives: '', improvements: '' }; }
  function loadReportFields() {
    const report = reportForCurrent();
    $('#reportResults').value = report.results || ''; $('#reportChallenges').value = report.challenges || '';
    $('#reportPositives').value = report.positives || ''; $('#reportImprovements').value = report.improvements || '';
    $('#reportSaved').textContent = 'Relatório demonstrativo';
  }
  function renderReportMetrics() {
    const tasks = activeTasks();
    const done = tasks.filter(task => task.lane === 'done').length;
    const totalChecks = tasks.reduce((sum, task) => sum + (task.checklist || []).length, 0);
    const completedChecks = tasks.reduce((sum, task) => sum + (task.checklist || []).filter(check => check.done).length, 0);
    const sprint = activeSprint();
    const days = sprint?.start && sprint?.end ? Math.max(1, Math.round((new Date(`${sprint.end}T12:00:00`) - new Date(`${sprint.start}T12:00:00`)) / 86400000) + 1) : 0;
    const completion = tasks.length ? Math.round(done / tasks.length * 100) : 0;
    const metrics = [['Tarefas concluídas', `${done}/${tasks.length}`], ['Progresso da sprint', `${completion}%`], ['Checklist', `${completedChecks}/${totalChecks}`], ['Duração planejada', `${days} dias`]];
    $('#reportMetrics').innerHTML = metrics.map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`).join('');
  }
  function saveCurrentReport() {
    if (!activeSprint()) return;
    data.reports[activeSprint().id] = { results: $('#reportResults').value.trim(), challenges: $('#reportChallenges').value.trim(), positives: $('#reportPositives').value.trim(), improvements: $('#reportImprovements').value.trim() };
    saveData();
  }
  function renderTruthTables() {
    const normalRows = [], emergencyRows = [];
    for (let bits = 0; bits < 16; bits++) {
      const vals = [Boolean(bits & 8), Boolean(bits & 4), Boolean(bits & 2), Boolean(bits & 1)];
      const [A, B, C, D] = vals;
      const normal = (A && B && C) || (B && C && D);
      const emergency = C && (B || D);
      normalRows.push({ vals, result: normal }); emergencyRows.push({ vals, result: emergency });
    }
    const fill = (tableId, rows) => {
      $(`#${tableId} tbody`).innerHTML = rows.map(({ vals, result }) => `<tr class="${result ? 'truth-yes' : 'truth-no'}">${vals.map(value => `<td>${value ? 'V' : 'F'}</td>`).join('')}<td>${result ? 'V · Liberado' : 'F · Não liberado'}</td></tr>`).join('');
    };
    fill('normalTable', normalRows); fill('emergencyTable', emergencyRows);
    $('#normalCount').textContent = `Liberado em ${normalRows.filter(row => row.result).length} de 16 situações`;
    $('#emergencyCount').textContent = `Liberado em ${emergencyRows.filter(row => row.result).length} de 16 situações`;
    window.truthRows = { normal: normalRows, emergency: emergencyRows };
  }
  function downloadFile(filename, contents, type = 'text/plain;charset=utf-8') {
    const blob = new Blob([contents], { type }); const url = URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = filename; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function reportMarkdown() {
    saveCurrentReport(); const sprint = activeSprint(); const tasks = activeTasks();
    const done = tasks.filter(task => task.lane === 'done').length; const percent = tasks.length ? Math.round(done / tasks.length * 100) : 0;
    const fields = [['Resultados', $('#reportResults').value], ['Desafios', $('#reportChallenges').value], ['Pontos positivos', $('#reportPositives').value], ['Melhorias', $('#reportImprovements').value]];
    return `# Relatório de sprint — ${sprint.name}\n\n**Espaço Santa Maria · Projeto acadêmico demonstrativo**\n\n- **Objetivo:** ${sprint.goal}\n- **Período:** ${dateLabel(sprint.start)} a ${dateLabel(sprint.end)}\n- **Tarefas concluídas:** ${done}/${tasks.length} (${percent}%)\n\n${fields.map(([title, text]) => `## ${title}\n${text || '_A preencher pela equipe._'}\n`).join('\n')}\n---\nRelatório gerado localmente pelo quadro demonstrativo.\n`;
  }
  function openTaskDialog(task = null) {
    const form = $('#taskForm'); form.reset(); $('#taskId').value = task?.id || ''; $('#taskDialogTitle').textContent = task ? 'Editar tarefa' : 'Nova tarefa';
    renderSprintOptions(); $('#taskSprint').value = task?.sprint || data.activeSprint;
    $('#taskTitle').value = task?.title || ''; $('#taskDescription').value = task?.description || ''; $('#taskLane').value = task?.lane || 'backlog'; $('#taskDue').value = task?.due || '';
    $('#taskChecklist').value = (task?.checklist || []).map(check => check.text).join('\n'); $('#taskComments').value = task?.comments || '';
    $('#deleteTask').style.visibility = task ? 'visible' : 'hidden'; $('#taskDialog').showModal();
  }
  function openSprintDialog() {
    const sprint = activeSprint(); if (!sprint) { showToast('Crie uma sprint primeiro.'); return; }
    $('#sprintForm').reset(); $('#sprintDialogTitle').textContent = 'Editar sprint'; $('#sprintId').value = sprint.id;
    $('#sprintName').value = sprint.name; $('#sprintGoal').value = sprint.goal; $('#sprintStart').value = sprint.start; $('#sprintEnd').value = sprint.end;
    $('#sprintDialog').showModal();
  }
  function exportTable(kind) {
    const rows = window.truthRows?.[kind]; if (!rows) return;
    const headers = ['A', 'B', 'C', 'D', 'Resultado']; const csv = [headers.join(';'), ...rows.map(row => [...row.vals.map(v => v ? 'V' : 'F'), row.result ? 'V - Liberado' : 'F - Não liberado'].join(';'))].join('\n');
    downloadFile(`tabela-verdade-${kind}.csv`, '\ufeff' + csv, 'text/csv;charset=utf-8'); showToast('Tabela exportada em CSV.');
  }
  function bindEvents() {
    $('#sprintSelect').addEventListener('change', event => { data.activeSprint = event.target.value; saveData(); renderBoard(); });
    $('#newTask').addEventListener('click', () => openTaskDialog()); $('#editSprint').addEventListener('click', openSprintDialog);
    $('#taskForm').addEventListener('submit', event => {
      event.preventDefault(); const id = $('#taskId').value || `t${Date.now()}`;
      const old = data.tasks.find(task => task.id === id);
      const checklist = $('#taskChecklist').value.split('\n').map(text => text.trim()).filter(Boolean).map((text, index) => ({ text, done: old?.checklist?.find(check => check.text === text)?.done || false }));
      const task = { id, sprint: $('#taskSprint').value, title: $('#taskTitle').value.trim(), description: $('#taskDescription').value.trim(), lane: $('#taskLane').value, due: $('#taskDue').value, checklist, comments: $('#taskComments').value.trim() };
      if (!task.title) return;
      if (old) data.tasks[data.tasks.indexOf(old)] = task; else data.tasks.push(task);
      saveData(); $('#taskDialog').close(); renderBoard(); showToast(old ? 'Tarefa atualizada.' : 'Tarefa adicionada.');
    });
    $('#deleteTask').addEventListener('click', () => {
      const id = $('#taskId').value; if (!id || !confirm('Excluir esta tarefa?')) return;
      data.tasks = data.tasks.filter(task => task.id !== id); saveData(); $('#taskDialog').close(); renderBoard(); showToast('Tarefa excluída.');
    });
    $('#sprintForm').addEventListener('submit', event => {
      event.preventDefault(); const sprint = sprintById($('#sprintId').value); if (!sprint) return;
      const start = $('#sprintStart').value, end = $('#sprintEnd').value;
      if (end < start) { showToast('A data final deve ser igual ou posterior à data inicial.'); return; }
      Object.assign(sprint, { name: $('#sprintName').value.trim(), goal: $('#sprintGoal').value.trim(), start, end });
      saveData(); $('#sprintDialog').close(); renderBoard(); showToast('Sprint atualizada.');
    });
    $('#board').addEventListener('click', event => {
      const button = event.target.closest('[data-edit-task]'); if (!button) return;
      const task = data.tasks.find(item => item.id === button.dataset.editTask); if (task) openTaskDialog(task);
    });
    $('#board').addEventListener('change', event => {
      const checkbox = event.target.closest('[data-check-task]'); if (!checkbox) return;
      const task = data.tasks.find(item => item.id === checkbox.dataset.checkTask); const check = task?.checklist?.[Number(checkbox.dataset.checkIndex)];
      if (check) { check.done = checkbox.checked; saveData(); renderBoard(); }
    });
    $('#board').addEventListener('dragstart', event => { const card = event.target.closest('[data-task]'); if (!card) return; event.dataTransfer.setData('text/plain', card.dataset.task); event.dataTransfer.effectAllowed = 'move'; card.classList.add('dragging'); });
    $('#board').addEventListener('dragend', event => event.target.closest('[data-task]')?.classList.remove('dragging'));
    $('#board').addEventListener('dragover', event => { const drop = event.target.closest('[data-drop]'); if (drop) { event.preventDefault(); drop.classList.add('drag-over'); } });
    $('#board').addEventListener('dragleave', event => { const drop = event.target.closest('[data-drop]'); if (drop && !drop.contains(event.relatedTarget)) drop.classList.remove('drag-over'); });
    $('#board').addEventListener('drop', event => { const drop = event.target.closest('[data-drop]'); if (!drop) return; event.preventDefault(); drop.classList.remove('drag-over'); const task = data.tasks.find(item => item.id === event.dataTransfer.getData('text/plain')); if (task) { task.lane = drop.dataset.drop; saveData(); renderBoard(); } });
    ['reportResults', 'reportChallenges', 'reportPositives', 'reportImprovements'].forEach(id => $(`#${id}`).addEventListener('input', () => { saveCurrentReport(); $('#reportSaved').textContent = 'Alterações salvas'; }));
    $('#generateReport').addEventListener('click', () => { saveCurrentReport(); renderReportMetrics(); showToast('Relatório atualizado com os dados desta sprint.'); });
    $('#exportReport').addEventListener('click', () => { downloadFile(`relatorio-${activeSprint()?.id || 'sprint'}.md`, reportMarkdown(), 'text/markdown;charset=utf-8'); showToast('Relatório exportado em Markdown.'); });
    $$('[data-export-table]').forEach(button => button.addEventListener('click', () => exportTable(button.dataset.exportTable)));
    $$('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
    $$('[data-close-dialog]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
    $('#copyQueue').addEventListener('click', async () => {
      const text = $('#passo4 pre').innerText;
      try { await navigator.clipboard.writeText(text); showToast('Pseudocódigo copiado.'); }
      catch (_) { const area = document.createElement('textarea'); area.value = text; document.body.append(area); area.select(); document.execCommand('copy'); area.remove(); showToast('Pseudocódigo copiado.'); }
    });
    $('#menuToggle').addEventListener('click', () => { const nav = $('#mainNav'); const open = nav.classList.toggle('open'); $('#menuToggle').setAttribute('aria-expanded', String(open)); });
    $$('#mainNav a').forEach(link => link.addEventListener('click', () => { $('#mainNav').classList.remove('open'); $('#menuToggle').setAttribute('aria-expanded', 'false'); }));
  }
  renderTruthTables(); renderBoard(); bindEvents();
})();

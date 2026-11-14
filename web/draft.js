let current;
const notice = document.querySelector('#notice');
async function loadDraft() {
  const response = await fetch('/state');
  if (!response.ok) return;
  current = await response.json();
  document.querySelector('#login').hidden = true;
  document.querySelector('#editor').hidden = false;
  render();
}
function render() {
  const revision = document.querySelector('#revision');
  revision.textContent = current.revision;
  revision.dataset.revision = current.revision;
  const table = document.querySelector('tbody');
  table.replaceChildren();
  for (const line of current.lines) {
    const row = document.createElement('tr');
    row.dataset.lineId = line.line_id;
    const label = document.createElement('td');
    label.textContent = line.description;
    row.append(label);
    for (const field of ['quantity', 'price', 'tax', 'note']) {
      const cell = document.createElement('td');
      const input = field === 'tax' ? document.createElement('select') : document.createElement('input');
      input.name = field;
      input.setAttribute('aria-label', field);
      if (field === 'tax') {
        for (const value of ['normal', 'exempt']) {
          const option = document.createElement('option');
          option.value = value;
          option.textContent = value;
          input.append(option);
        }
        input.addEventListener('change', () => branch(row, input.value, line.exemption));
      }
      input.value = line[field] || '';
      cell.append(input);
      row.append(cell);
    }
    const action = document.createElement('td');
    const button = document.createElement('button');
    button.textContent = '保存此行';
    button.addEventListener('click', async () => {
      const values = Object.fromEntries([...row.querySelectorAll('input, select')].map(input => [input.name, input.value]));
      const response = await fetch('/save', {method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({revision: current.revision, line_id: line.line_id, values})});
      const result = await response.json();
      if (!response.ok) {notice.textContent = result.error; notice.dataset.saved = 'false'; return;}
      current = result;
      render();
      notice.textContent = '已保存 ' + line.line_id + ' 修订 ' + current.revision;
      notice.dataset.saved = 'true';
    });
    action.append(button);
    row.append(action);
    table.append(row);
    branch(row, line.tax, line.exemption);
  }
}
function branch(row, tax, original) {
  row.querySelector('[data-branch]')?.remove();
  if (tax !== 'exempt') return;
  const cell = document.createElement('td');
  cell.dataset.branch = 'exempt';
  const input = document.createElement('input');
  input.name = 'exemption';
  input.setAttribute('aria-label', '免税用途');
  input.value = original || '';
  cell.append(input);
  row.append(cell);
}
document.querySelector('#login').addEventListener('submit', async event => {
  event.preventDefault();
  await fetch('/login', {method: 'POST'});
  await loadDraft();
});
document.querySelector('#reverse').addEventListener('click', () => {current.lines.reverse(); render();});
document.querySelector('#refresh').addEventListener('click', loadDraft);
document.querySelector('#submit').addEventListener('click', async () => {await fetch('/submit', {method: 'POST'}); notice.textContent = '已提交';});
fetch('/session').then(response => response.json()).then(session => {
  if (session.authenticated) return loadDraft();
});

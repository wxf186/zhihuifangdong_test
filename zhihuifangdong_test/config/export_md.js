function exportMd(seq) {
  const modal = document.getElementById('detail-' + seq);
  if (!modal) return;
  const header = modal.querySelector('.modal-header h3');
  const tags = modal.querySelector('.detail-tags');
  const body = modal.querySelector('.modal-body');
  if (!body) return;

  let name = header ? header.textContent.replace(/^[✅❌]\s*/, '').trim() : '';
  let grp = tags ? (tags.querySelector('.grp-tag') || {}).textContent || '' : '';
  let status = tags ? (tags.querySelector('.status-tag') || {}).textContent || '' : '';

  const rows = body.querySelectorAll('.detail-row');
  let api = '', httpStatus = '', duration = '';
  rows.forEach(row => {
    const strong = row.querySelector('strong');
    if (!strong) return;
    const label = strong.textContent.replace(/[：:]/g, '').trim();
    const val = row.querySelector('span') ? row.querySelector('span').textContent.trim() : '';
    if (label === '接口') api = val;
    if (label === '状态码') httpStatus = val;
    if (label === '耗时') duration = val;
  });

  const sections = body.querySelectorAll('.detail-section');
  let reqBlock = '', respInfo = '', resultInfo = '';
  sections.forEach(sec => {
    const lbl = sec.querySelector('.detail-label');
    if (!lbl) return;
    const label = lbl.textContent.trim();
    const pre = sec.querySelector('pre');
    let txt = pre ? pre.textContent.trim() : '';
    if (label.includes('公共参数')) reqBlock = txt;
    if (label.includes('响应信息')) respInfo = txt;
    if (label.includes('结果信息')) resultInfo = txt;
  });

  let reqHeaders = reqBlock, reqParams = reqBlock;
  try {
    const reqObj = JSON.parse(reqBlock);
    const { headers, url, method, params, json_data, data } = reqObj;
    reqHeaders = JSON.stringify({ headers, url, method }, null, 2);
    const combined = {};
    if (params) combined.params = params;
    if (json_data) combined.json_data = json_data;
    if (data) combined.data = data;
    reqParams = JSON.stringify(Object.keys(combined).length ? combined : reqObj, null, 2);
  } catch (e) {}

  const md = [
    '# ' + name,
    '',
    '| 字段 | 值 |',
    '|------|----|',
    '| 用例名称 | ' + name + ' |',
    '| 来源 | ' + grp + ' |',
    '| 接口 | ' + api + ' |',
    '| 状态码 | ' + httpStatus + ' |',
    '| 耗时 | ' + duration + ' |',
    '',
    '## 公共参数（请求头）',
    '',
    '```json',
    reqHeaders || '-',
    '```',
    '',
    '## 请求参数',
    '',
    '```json',
    reqParams || '-',
    '```',
    '',
    '## 响应信息',
    '',
    '```json',
    respInfo || '-',
    '```',
    '',
    '## 结果信息',
    '',
    '```',
    resultInfo || '-',
    '```',
  ].join('\n');

  const blob = new Blob([md], {type: 'text/markdown;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_') + '.md';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

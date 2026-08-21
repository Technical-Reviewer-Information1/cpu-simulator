(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const NADDR = 12;

  /* 命令の種類 */
  const OPS = [
    { id: 'NONE', label: '（なし）', arg: false, text: () => '' },
    { id: 'READA', label: 'READ A, (X)', arg: true, text: x => 'READ A, (' + x + ')' },
    { id: 'READB', label: 'READ B, (X)', arg: true, text: x => 'READ B, (' + x + ')' },
    { id: 'WRITEA', label: 'WRITE (X), A', arg: true, text: x => 'WRITE (' + x + '), A' },
    { id: 'ADD', label: 'ADD A, B', arg: false, text: () => 'ADD A, B' },
    { id: 'SUB', label: 'SUB A, B（発展）', arg: false, text: () => 'SUB A, B' },
    { id: 'STOP', label: 'STOP', arg: false, text: () => 'STOP' }
  ];
  const opOf = id => OPS.find(o => o.id === id) || OPS[0];
  const DESC = {
    READA: x => '主記憶装置の ' + x + '番地のデータをレジスタAに読み出す',
    READB: x => '主記憶装置の ' + x + '番地のデータをレジスタBに読み出す',
    WRITEA: x => 'レジスタAの値を主記憶装置の ' + x + '番地に書き込む',
    ADD: () => 'レジスタAとレジスタBの和を求め、結果をレジスタAに保存する',
    SUB: () => 'レジスタAからレジスタBを引き、結果をレジスタAに保存する',
    STOP: () => 'プログラムを停止する',
    NONE: () => '命令がありません'
  };

  /* プログラム（本文の表2） */
  const BOOK = {
    prog: { 1: ['READA', 10], 2: ['READB', 11], 3: ['ADD', null], 4: ['WRITEA', 12], 5: ['STOP', null] },
    data: { 10: 4, 11: 5, 12: null }
  };
  const SWAP = {
    prog: { 1: ['READA', 11], 2: ['READB', 10], 3: ['ADD', null], 4: ['WRITEA', 12], 5: ['STOP', null] },
    data: { 10: 4, 11: 5, 12: null }
  };
  const SUM3 = {
    prog: { 1: ['READA', 10], 2: ['READB', 11], 3: ['ADD', null], 4: ['READB', 12], 5: ['ADD', null], 6: ['WRITEA', 9], 7: ['STOP', null] },
    data: { 9: null, 10: 4, 11: 5, 12: 6 }
  };
  let prog = {}, mem = {}, PC = 1, A = 0, B = 0, phase = -1, trace = [], wrote = null, halted = false;

  function load(src) {
    prog = {}; mem = {};
    for (let i = 1; i <= NADDR; i++) { prog[i] = null; mem[i] = null; }
    Object.keys(src.prog).forEach(k => { prog[+k] = src.prog[k].slice(); });
    Object.keys(src.data).forEach(k => { mem[+k] = src.data[k]; });
    reset();
  }
  function reset() { PC = 1; A = 0; B = 0; phase = -1; trace = []; wrote = null; halted = false; draw(); }

  /* ---- 表示 ---- */
  function memRows() {
    let h = '<thead><tr><th class="ad">番地</th><th>命令またはデータ</th></tr></thead><tbody>';
    for (let i = 1; i <= NADDR; i++) {
      const isCur = i === PC && !halted;
      const p = prog[i];
      const content = p ? opOf(p[0]).text(p[1]) : (mem[i] === null || mem[i] === undefined ? '' : mem[i]);
      h += '<tr class="' + (isCur ? 'cur' : '') + (wrote === i ? ' wrote' : '') + '"><td class="ad">' + i + '</td>' +
        '<td class="mono">' + (content === '' ? '<span style="color:var(--ink-3)">—</span>' : content) + '</td></tr>';
    }
    return h + '</tbody>';
  }
  function draw() {
    $('memTable').innerHTML = memRows();
    $('regPC').querySelector('.v').textContent = halted ? '停止' : PC;
    $('regA').querySelector('.v').textContent = A;
    $('regB').querySelector('.v').textContent = B;
    ['regPC', 'regA', 'regB'].forEach(id => $(id).classList.remove('hit'));
    [...$('phaseBox').children].forEach(p => p.classList.toggle('on', +p.dataset.p === phase));
    $('traceTable').innerHTML = '<thead><tr><th>プログラム<br>カウンタ</th><th>実行した命令</th><th>レジスタA</th><th>レジスタB</th></tr></thead><tbody>' +
      (trace.length ? trace.map(t => '<tr><td class="mono">' + t.pc + '</td><td class="mono">' + t.inst + '</td>' +
        '<td class="mono"><strong>' + t.a + '</strong></td><td class="mono">' + t.b + '</td></tr>').join('')
        : '<tr><td colspan="4" style="color:var(--ink-3)">まだ実行していません</td></tr>') + '</tbody>';
    $('runStep').disabled = halted;
  }

  /* ---- 実行 ---- */
  function stepOnce() {
    if (halted) return;
    const p = prog[PC];
    wrote = null;
    if (!p || p[0] === 'NONE') { halted = true; $('curInst').className = 'note ng'; $('curInst').textContent = PC + '番地に命令がありません。停止します。'; draw(); return; }
    const op = opOf(p[0]), x = p[1];
    phase = 2;
    let msg = '';
    if (op.id === 'READA') { A = mem[x] === null ? 0 : mem[x]; msg = x + '番地の ' + A + ' をレジスタAへ読み出しました。'; }
    else if (op.id === 'READB') { B = mem[x] === null ? 0 : mem[x]; msg = x + '番地の ' + B + ' をレジスタBへ読み出しました。<strong>レジスタAは変わりません。</strong>'; }
    else if (op.id === 'WRITEA') { mem[x] = A; wrote = x; msg = 'レジスタAの ' + A + ' を ' + x + '番地に書き込みました。'; }
    else if (op.id === 'ADD') { A = A + B; msg = 'A ＋ B ＝ ' + A + ' を計算し、レジスタAに保存しました。'; }
    else if (op.id === 'SUB') { A = A - B; msg = 'A − B ＝ ' + A + ' を計算し、レジスタAに保存しました。'; }
    else if (op.id === 'STOP') { halted = true; msg = 'プログラムを停止しました。'; }
    trace.push({ pc: PC, inst: op.text(x), a: A, b: B });
    const shown = PC;
    if (!halted) PC = PC + 1;
    draw();
    $('curInst').className = 'note ok';
    $('curInst').innerHTML = '<strong>' + shown + '番地：' + op.text(x) + '</strong><br>' +
      '<span class="small">' + DESC[op.id](x) + '</span><br>' + msg +
      (halted ? '' : '<br>プログラムカウンタは <strong>' + PC + '</strong> になりました。');
    ['READA', 'ADD', 'SUB'].indexOf(op.id) >= 0 && $('regA').classList.add('hit');
    if (op.id === 'READB') $('regB').classList.add('hit');
    checkDone();
  }
  function checkDone() {
    const n = $('runNote');
    if (!halted) { n.className = 'note info'; n.innerHTML = '実行した命令の分だけ表が伸びていきます。'; return; }
    n.className = 'note ok';
    const isBook = JSON.stringify(trace.map(t => t.inst)) === JSON.stringify(['READ A, (10)', 'READ B, (11)', 'ADD A, B', 'WRITE (12), A', 'STOP']);
    n.innerHTML = '実行が終わりました。' +
      (isBook
        ? '本文の表3と同じ値になっています。<br>プログラムカウンタ1のとき <strong>4</strong>（【イ】＝②）、2のとき <strong>4</strong>（【ウ】＝②）、3のとき <strong>9</strong>（【エ】＝④）。' +
          '<br><strong>2番地は READ B なのでレジスタAは変わらない</strong>のがポイントです。'
        : '10番地以降のデータや命令を変えて、結果がどう変わるか試してみましょう。');
  }

  /* ---- STEP 1 の表 ---- */
  function drawTables() {
    $('partsTable').innerHTML = '<thead><tr><th>名前</th><th>はたらき</th></tr></thead><tbody>' +
      '<tr><td>レジスタ</td><td>CPUの内部にある、データを一時的に記憶する領域。</td></tr>' +
      '<tr><td>プログラムカウンタ</td><td>次に実行する命令が入っている主記憶装置の<strong>番地</strong>を保存するレジスタ。1命令終わるごとに更新される。</td></tr>' +
      '<tr><td>データレジスタA・B</td><td>主記憶装置から読み出したデータを一時的に保存する。</td></tr>' +
      '<tr><td>主記憶装置</td><td>1番地から順に番号がついている。1〜9番地に命令、10番地以降にデータが入っている。</td></tr></tbody>';
    $('isaTable').innerHTML = '<thead><tr><th>命令</th><th>内容</th></tr></thead><tbody>' +
      '<tr><td class="mono">READ A, (X)</td><td>主記憶装置の番地Xに保存されているデータをレジスタAに読み出す。</td></tr>' +
      '<tr><td class="mono">READ B, (X)</td><td>主記憶装置の番地Xに保存されているデータをレジスタBに読み出す。</td></tr>' +
      '<tr><td class="mono">WRITE (X), A</td><td>レジスタAに保存されているデータを主記憶装置の番地Xに書き込む。</td></tr>' +
      '<tr><td class="mono">ADD A, B</td><td>レジスタAとレジスタBの和（A＋B）を求め、計算結果をレジスタAに保存する。</td></tr>' +
      '<tr><td class="mono">STOP</td><td>プログラムを停止する。</td></tr></tbody>';
  }

  /* ---- STEP 3 エディタ ---- */
  function drawEdit() {
    let h = '<thead><tr><th class="ad">番地</th><th>命令</th><th>番地X</th><th>データ</th></tr></thead><tbody>';
    for (let i = 1; i <= NADDR; i++) {
      const p = prog[i];
      const sel = '<select data-i="' + i + '" class="op">' + OPS.map(o =>
        '<option value="' + o.id + '"' + (p && p[0] === o.id ? ' selected' : (!p && o.id === 'NONE' ? ' selected' : '')) + '>' + o.label + '</option>').join('') + '</select>';
      const arg = '<input type="number" min="1" max="' + NADDR + '" data-i="' + i + '" class="arg" value="' + (p && p[1] != null ? p[1] : '') + '"' +
        (p && opOf(p[0]).arg ? '' : ' disabled') + '>';
      const dat = '<input type="number" data-i="' + i + '" class="dat" value="' + (mem[i] == null ? '' : mem[i]) + '"' + (p ? ' disabled' : '') + '>';
      h += '<tr><td class="ad">' + i + '</td><td>' + sel + '</td><td>' + arg + '</td><td>' + dat + '</td></tr>';
    }
    $('editTable').innerHTML = h + '</tbody>';
    $('editTable').querySelectorAll('select.op').forEach(s => s.addEventListener('change', () => {
      const i = +s.dataset.i;
      if (s.value === 'NONE') prog[i] = null;
      else prog[i] = [s.value, opOf(s.value).arg ? (prog[i] && prog[i][1] ? prog[i][1] : 10) : null];
      if (prog[i]) mem[i] = null;
      drawEdit();
    }));
    $('editTable').querySelectorAll('input.arg').forEach(x => x.addEventListener('input', () => {
      const i = +x.dataset.i; if (prog[i]) prog[i][1] = +x.value || 1;
    }));
    $('editTable').querySelectorAll('input.dat').forEach(x => x.addEventListener('input', () => {
      const i = +x.dataset.i; mem[i] = x.value === '' ? null : +x.value;
    }));
  }

  /* ---- STEP 4 ---- */
  const BLANKS = [
    { k: 'ア', q: 'コンピュータの【　】機能と制御機能はCPUが担っている。', ch: ['入力', '出力', '演算', '記憶', '処理'], a: '演算',
      why: 'CPUは制御装置と演算装置からできています。だから「演算機能と制御機能」を担当します。' },
    { k: 'イ', q: 'プログラムカウンタが1のときのレジスタAの値は', ch: ['0', '1', '4', '5', '9', '10', 'A', 'B'], a: '4',
      why: '1番地の READ A, (10) で10番地の 4 を読み出すので、レジスタAは 4 になります。' },
    { k: 'ウ', q: 'プログラムカウンタが2のときのレジスタAの値は', ch: ['0', '1', '4', '5', '9', '10', 'A', 'B'], a: '4',
      why: '2番地は READ <strong>B</strong>, (11)。レジスタBに5が入るだけで、<strong>レジスタAは4のまま</strong>です。ここが最大の注意点。' },
    { k: 'エ', q: 'プログラムカウンタが3のときのレジスタAの値は', ch: ['0', '1', '4', '5', '9', '10', 'A', 'B'], a: '9',
      why: '3番地の ADD A, B で 4＋5＝9 が計算され、レジスタAに保存されます。' }
  ];
  let bAns = {};
  function drawBlanks() {
    $('blankBox').innerHTML = BLANKS.map((b, i) =>
      '<div' + (i ? ' style="margin-top:18px;padding-top:16px;border-top:1px solid var(--line)"' : '') + '>' +
      '<p class="pq">【' + b.k + '】　' + b.q + '</p>' +
      '<div class="choice4" data-i="' + i + '">' + b.ch.map((c, j) =>
        '<button class="btn" data-i="' + i + '" data-c="' + c + '" style="text-align:center">' + '⓪①②③④⑤⑥⑦'[j] + '　' + c + '</button>').join('') +
      '</div><div class="note" id="bfb' + i + '" hidden></div></div>').join('');
    $('blankBox').querySelectorAll('button[data-c]').forEach(btn => btn.addEventListener('click', () => {
      const i = +btn.dataset.i, b = BLANKS[i], ok = btn.dataset.c === b.a;
      const row = $('blankBox').querySelector('.choice4[data-i="' + i + '"]');
      row.classList.add('locked');
      [...row.children].forEach(x => { if (x.dataset.c === b.a) x.classList.add('correct'); else if (x === btn) x.classList.add('wrong'); });
      const fb = $('bfb' + i);
      fb.hidden = false; fb.className = 'note ' + (ok ? 'ok' : 'ng');
      fb.innerHTML = (ok ? '正解。' : '正解は <strong>' + b.a + '</strong>。') + b.why;
      bAns[i] = ok;
      const done = Object.keys(bAns).length, right = Object.values(bAns).filter(Boolean).length;
      const n = $('blankNote');
      n.className = 'note ' + (done === BLANKS.length ? (right === done ? 'ok' : 'warn') : 'info');
      n.innerHTML = done + ' / ' + BLANKS.length + ' 問解答（正解 ' + right + ' 問）' +
        (done === BLANKS.length ? '<br>本文の答えは【ア】②　【イ】②　【ウ】②　【エ】④ です。' : '');
    }));
    $('blankNote').className = 'note info';
    $('blankNote').textContent = '0 / ' + BLANKS.length + ' 問解答';
  }

  function init() {
    load(BOOK);
    drawTables(); drawEdit(); drawBlanks();
    $('runStep').addEventListener('click', stepOnce);
    $('runAll').addEventListener('click', () => { let g = 0; while (!halted && g++ < 50) stepOnce(); });
    $('runReset').addEventListener('click', () => { reset(); $('curInst').className = 'note info'; $('curInst').textContent = '「1命令すすめる」を押してください。'; $('runNote').className = 'note info'; $('runNote').textContent = ''; });
    $('preBook').addEventListener('click', () => { load(BOOK); drawEdit(); $('editNote').className = 'note info'; $('editNote').textContent = '本文の表2と同じプログラムです。'; });
    $('preSwap').addEventListener('click', () => { load(SWAP); drawEdit(); $('editNote').className = 'note info'; $('editNote').innerHTML = '読み出す番地を入れかえました。和は同じですが、レジスタAとBに入る値が逆になります。'; });
    $('preSum3').addEventListener('click', () => { load(SUM3); drawEdit(); $('editNote').className = 'note info'; $('editNote').innerHTML = '10・11・12番地の3つの和を9番地に書き込みます。ADD を2回使うのがポイントです。'; });
    $('applyProg').addEventListener('click', () => {
      reset(); drawEdit();
      $('editNote').className = 'note ok';
      $('editNote').textContent = 'プログラムを入れました。STEP 2 で実行してください。';
      $('step2').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    window.Terms.glossary($('glossBox'), ['CPU', 'レジスタ', 'プログラムカウンタ', '主記憶装置', '制御装置', '演算装置', '五大装置']);
    window.Terms.attach();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

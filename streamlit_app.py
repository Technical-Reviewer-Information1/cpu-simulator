import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time

st.set_page_config(
    page_title="CPUにおける計算の仕組み",
    page_icon="💻",
    layout="wide"
)

st.title("CPUにおける計算の仕組み（pp.178-180）")
st.caption("Created by Dit-Lab.(Daiki ITO)")
st.caption("Supported by Tomoaki ATSUMI")

# 初期化
if 'cpu_state' not in st.session_state:
    st.session_state.cpu_state = {
        'memory': {
            0: 'READ A, (10)',
            1: 'READ B, (11)', 
            2: 'ADD A, B',
            3: 'WRITE (12), A',
            4: 'STOP',
            10: 5,  # データ
            11: 8,  # データ
            12: 0   # 結果格納用
        },
        'pc': 0,  # プログラムカウンタ
        'ir': '',  # 命令レジスタ
        'registers': {'A': 0, 'B': 0},  # データレジスタ
        'current_step': 0,
        'execution_log': [],
        'is_running': False,
        'is_finished': False
    }

def reset_cpu():
    st.session_state.cpu_state = {
        'memory': {
            0: 'READ A, (10)',
            1: 'READ B, (11)', 
            2: 'ADD A, B',
            3: 'WRITE (12), A',
            4: 'STOP',
            10: 5,
            11: 8,
            12: 0
        },
        'pc': 0,
        'ir': '',
        'registers': {'A': 0, 'B': 0},
        'current_step': 0,
        'execution_log': [],
        'is_running': False,
        'is_finished': False
    }

def create_memory_visualization():
    memory_data = []
    for addr, content in st.session_state.cpu_state['memory'].items():
        if addr <= 4:
            memory_data.append({'番地': addr, '内容': content, 'タイプ': '命令'})
        else:
            memory_data.append({'番地': addr, '内容': content, 'タイプ': 'データ'})
    
    df = pd.DataFrame(memory_data)
    
    fig = go.Figure(data=[go.Table(
        header=dict(values=['番地', '内容', 'タイプ'],
                   fill_color='lightblue',
                   align='center',
                   font=dict(size=14, color='black')),
        cells=dict(values=[df['番地'], df['内容'], df['タイプ']],
                  fill_color=[['lightgray' if addr == st.session_state.cpu_state['pc'] and addr <= 4 else 'white' 
                              for addr in df['番地']]],
                  align='center',
                  font=dict(size=12, color='black'))
    )])
    
    fig.update_layout(
        title="🧠 主記憶装置",
        title_x=0.5,
        height=300,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

def create_cpu_visualization():
    fig = go.Figure()
    
    # CPU内部のレジスタを可視化
    registers_text = f"""
    <b>🔢 プログラムカウンタ (PC)</b><br>
    現在の値: {st.session_state.cpu_state['pc']}<br><br>
    
    <b>📋 命令レジスタ (IR)</b><br>
    現在の命令: {st.session_state.cpu_state['ir']}<br><br>
    
    <b>💾 データレジスタ</b><br>
    レジスタA: {st.session_state.cpu_state['registers']['A']}<br>
    レジスタB: {st.session_state.cpu_state['registers']['B']}
    """
    
    fig.add_annotation(
        x=0.5, y=0.5,
        text=registers_text,
        showarrow=False,
        font=dict(size=16, color='black'),
        bgcolor="lightcyan",
        bordercolor="blue",
        borderwidth=2,
        xref="paper", yref="paper"
    )
    
    fig.update_layout(
        title="🖥️ CPU内部状態",
        title_x=0.5,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=300,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig

def execute_instruction():
    cpu = st.session_state.cpu_state
    
    if cpu['pc'] >= 5 or cpu['is_finished']:
        return
    
    # 命令フェッチ
    instruction = cpu['memory'][cpu['pc']]
    cpu['ir'] = instruction
    
    # 命令実行
    if instruction.startswith('READ'):
        parts = instruction.split()
        reg = parts[1].rstrip(',')
        addr = int(parts[2].strip('()'))
        cpu['registers'][reg] = cpu['memory'][addr]
        log_msg = f"READ命令: 番地{addr}からデータ{cpu['memory'][addr]}を読み出し、レジスタ{reg}に格納"
        
    elif instruction.startswith('ADD'):
        result = cpu['registers']['A'] + cpu['registers']['B']
        cpu['registers']['A'] = result
        log_msg = f"ADD命令: レジスタA({cpu['registers']['A']-cpu['registers']['B']}) + レジスタB({cpu['registers']['B']}) = {result}"
        
    elif instruction.startswith('WRITE'):
        parts = instruction.split()
        addr = int(parts[1].strip('(),'))
        reg = parts[2]
        cpu['memory'][addr] = cpu['registers'][reg]
        log_msg = f"WRITE命令: レジスタ{reg}の値{cpu['registers'][reg]}を番地{addr}に書き込み"
        
    elif instruction == 'STOP':
        cpu['is_finished'] = True
        log_msg = "STOP命令: プログラム終了"
    
    cpu['execution_log'].append(log_msg)
    
    if not cpu['is_finished']:
        cpu['pc'] += 1
    
    cpu['current_step'] += 1

# メイン画面レイアウト
st.markdown("---")

# プログラム表示
st.subheader("📝 実行プログラム")
program_code = """
READ A, (10)  # 主記憶装置の番地10からデータを読み出し、レジスタAに格納
READ B, (11)  # 主記憶装置の番地11からデータを読み出し、レジスタBに格納  
ADD A, B      # レジスタAとレジスタBのデータを加算し、結果をレジスタAに格納
WRITE (12), A # レジスタAのデータを主記憶装置の番地12に書き込み
STOP          # プログラムの終了
"""
st.code(program_code, language='text')

st.markdown("---")

# CPUの状態可視化
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(create_memory_visualization(), use_container_width=True)

with col2:
    st.plotly_chart(create_cpu_visualization(), use_container_width=True)

# 実行制御ボタン
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("▶️ 1ステップ実行", disabled=st.session_state.cpu_state['is_finished']):
        execute_instruction()

with col2:
    if st.button("🔄 リセット"):
        reset_cpu()

with col3:
    auto_run = st.button("⚡ 自動実行", disabled=st.session_state.cpu_state['is_finished'])

# 自動実行処理
if auto_run:
    placeholder = st.empty()
    while not st.session_state.cpu_state['is_finished']:
        execute_instruction()
        with placeholder.container():
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_memory_visualization(), use_container_width=True)
            with col2:
                st.plotly_chart(create_cpu_visualization(), use_container_width=True)
        time.sleep(1)

# 実行ログ表示
if st.session_state.cpu_state['execution_log']:
    st.markdown("---")
    st.subheader("📊 実行ログ")
    for i, log in enumerate(st.session_state.cpu_state['execution_log'], 1):
        st.write(f"**ステップ {i}:** {log}")

# 完了時のまとめ
if st.session_state.cpu_state['is_finished']:
    st.markdown("---")
    st.success("✅ プログラム実行完了!")
    
    st.subheader("🎯 学習のまとめ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🧠 CPUの役割
        - コンピュータの「頭脳」として機能
        - プログラムを一つずつ順番に読み込み
        - 指示に従ってデータ処理を実行
        - プログラムカウンタで次の命令を管理
        """)
    
    with col2:
        st.markdown("""
        ### 📋 命令とデータの流れ
        - **命令**：CPUに何をするかを指示
        - **データ**：実際に処理される値
        - 主記憶装置から区別して読み込み
        - レジスタで一時的に保持して処理
        """)
    
    # 処理結果の確認
    result_data = {
        '項目': ['初期値A', '初期値B', '計算結果', '最終格納先'],
        '値': [5, 8, st.session_state.cpu_state['memory'][12], '番地12']
    }
    
    result_df = pd.DataFrame(result_data)
    
    fig_result = go.Figure(data=[go.Table(
        header=dict(values=['項目', '値'],
                   fill_color='lightgreen',
                   align='center',
                   font=dict(size=14, color='black')),
        cells=dict(values=[result_df['項目'], result_df['値']],
                  fill_color='lightcyan',
                  align='center',
                  font=dict(size=12, color='black'))
    )])
    
    fig_result.update_layout(
        title="🎯 処理結果",
        title_x=0.5,
        height=200,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig_result, use_container_width=True)

# 追加の学習コンテンツ
st.markdown("---")
st.subheader("🚀 発展学習")

with st.expander("💡 CPUの基本動作サイクル"):
    st.markdown("""
    CPUは以下の基本サイクルを繰り返して動作します：
    
    1. **フェッチ（Fetch）**
       - プログラムカウンタが指す番地から命令を読み出し
       - 命令レジスタに格納
    
    2. **デコード（Decode）**
       - 命令を解読し、必要な制御信号を生成
       - どのような操作を行うかを決定
    
    3. **実行（Execute）**
       - 実際にデータ処理や演算を実行
       - 結果をレジスタや主記憶装置に保存
    
    4. **次の命令へ**
       - プログラムカウンタを更新
       - 次の命令サイクルへ
    """)

with st.expander("🔍 レジスタの役割"):
    st.markdown("""
    **レジスタ**はCPU内部の高速な記憶領域です：
    
    - **プログラムカウンタ（PC）**: 次に実行する命令の番地を保持
    - **命令レジスタ（IR）**: 現在実行中の命令を保持  
    - **データレジスタ**: 演算に使用するデータを一時的に保持
    - **演算結果**: 計算結果を一時的に保存
    
    レジスタは主記憶装置よりもはるかに高速で、CPUが効率的に動作するために不可欠です。
    """)

st.markdown("---")
st.markdown("### 👨‍🎓 このシミュレーションで学べること")
st.markdown("""
- CPUは非常にシンプルな命令の繰り返しで複雑な処理を実現
- プログラムとデータが主記憶装置に格納され、CPUが順次処理
- レジスタによる高速な一時記憶がCPU性能の鍵
- コンピュータの「計算」の本質的な仕組み
""")

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
        'state_history': [],  # 状態履歴を保存
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
        'state_history': [],
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

def create_unified_cpu_visualization():
    fig = go.Figure()

    # メモリテーブルの描画（左側）
    memory_y_positions = [0.85, 0.75, 0.65, 0.55, 0.45, 0.25, 0.15, 0.05]

    for i, (addr, content) in enumerate(sorted(st.session_state.cpu_state['memory'].items())):
        y_pos = memory_y_positions[i] if i < len(memory_y_positions) else 0.05

        # 現在のPC位置をハイライト
        bg_color = "yellow" if addr == st.session_state.cpu_state['pc'] and addr <= 4 else "lightgray"

        # メモリセルの描画
        fig.add_shape(
            type="rect",
            x0=0.05, y0=y_pos-0.03, x1=0.35, y1=y_pos+0.03,
            fillcolor=bg_color,
            line=dict(color="black", width=1)
        )

        # アドレスと内容の表示
        content_type = "命令" if addr <= 4 else "データ"
        fig.add_annotation(
            x=0.2, y=y_pos,
            text=f"<b>{addr}</b>: {content} ({content_type})",
            showarrow=False,
            font=dict(size=12, color='black'),
            xref="paper", yref="paper"
        )

    # CPUレジスタの描画（右側）
    # プログラムカウンタ
    fig.add_shape(
        type="rect",
        x0=0.65, y0=0.8, x1=0.95, y1=0.9,
        fillcolor="lightblue",
        line=dict(color="blue", width=2)
    )
    fig.add_annotation(
        x=0.8, y=0.85,
        text=f"<b>PC: {st.session_state.cpu_state['pc']}</b>",
        showarrow=False,
        font=dict(size=14, color='black'),
        xref="paper", yref="paper"
    )

    # 命令レジスタ
    fig.add_shape(
        type="rect",
        x0=0.65, y0=0.65, x1=0.95, y1=0.75,
        fillcolor="lightgreen",
        line=dict(color="green", width=2)
    )
    fig.add_annotation(
        x=0.8, y=0.7,
        text=f"<b>IR:</b> {st.session_state.cpu_state['ir']}",
        showarrow=False,
        font=dict(size=12, color='black'),
        xref="paper", yref="paper"
    )

    # データレジスタA
    fig.add_shape(
        type="rect",
        x0=0.65, y0=0.45, x1=0.8, y1=0.55,
        fillcolor="lightyellow",
        line=dict(color="orange", width=2)
    )
    fig.add_annotation(
        x=0.725, y=0.5,
        text=f"<b>A: {st.session_state.cpu_state['registers']['A']}</b>",
        showarrow=False,
        font=dict(size=13, color='black'),
        xref="paper", yref="paper"
    )

    # データレジスタB
    fig.add_shape(
        type="rect",
        x0=0.8, y0=0.45, x1=0.95, y1=0.55,
        fillcolor="lightcoral",
        line=dict(color="red", width=2)
    )
    fig.add_annotation(
        x=0.875, y=0.5,
        text=f"<b>B: {st.session_state.cpu_state['registers']['B']}</b>",
        showarrow=False,
        font=dict(size=13, color='black'),
        xref="paper", yref="paper"
    )

    # データフローの矢印を追加
    # メモリからCPUへの命令フェッチ矢印
    if st.session_state.cpu_state['pc'] <= 4:
        pc_y = memory_y_positions[st.session_state.cpu_state['pc']]
        fig.add_annotation(
            x=0.35, y=pc_y,
            ax=0.65, ay=0.7,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=3,
            arrowcolor="blue",
            text="命令フェッチ",
            font=dict(size=11, color='blue', family='Arial Black'),
            textangle=0,
            bgcolor="white",
            bordercolor="blue",
            borderwidth=1
        )

    # データ読み込み矢印（READ命令時）
    if st.session_state.cpu_state['ir'].startswith('READ'):
        # 番地10または11からレジスタへの矢印
        if 'A' in st.session_state.cpu_state['ir']:
            fig.add_annotation(
                x=0.35, y=0.25,  # 番地10
                ax=0.65, ay=0.5,  # レジスタA
                arrowhead=3,
                arrowsize=1.5,
                arrowwidth=3,
                arrowcolor="orange",
                text="データ読み込み",
                font=dict(size=10, color='orange', family='Arial Black'),
                bgcolor="white",
                bordercolor="orange",
                borderwidth=1
            )
        elif 'B' in st.session_state.cpu_state['ir']:
            fig.add_annotation(
                x=0.35, y=0.15,  # 番地11
                ax=0.8, ay=0.5,   # レジスタB
                arrowhead=3,
                arrowsize=1.5,
                arrowwidth=3,
                arrowcolor="red",
                text="データ読み込み",
                font=dict(size=10, color='red', family='Arial Black'),
                bgcolor="white",
                bordercolor="red",
                borderwidth=1
            )

    # ADD命令時のレジスタ間8の矢印
    if st.session_state.cpu_state['ir'].startswith('ADD'):
        # レジスタAとBからの加算矢印
        fig.add_annotation(
            x=0.8, y=0.45,  # レジスタBの下
            ax=0.725, ay=0.45,  # レジスタAへ
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=3,
            arrowcolor="green",
            text="加算",
            font=dict(size=10, color='green', family='Arial Black'),
            bgcolor="white",
            bordercolor="green",
            borderwidth=1
        )

    # 書き込み矢印（WRITE命令時）
    if st.session_state.cpu_state['ir'].startswith('WRITE'):
        fig.add_annotation(
            x=0.725, y=0.45,  # レジスタA
            ax=0.35, ay=0.05,  # 番地12
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=3,
            arrowcolor="purple",
            text="結果書き込み",
            font=dict(size=10, color='purple', family='Arial Black'),
            bgcolor="white",
            bordercolor="purple",
            borderwidth=1
        )

    # プログラムカウンタの更新矢印（次の命令へ）
    if st.session_state.cpu_state['current_step'] > 0 and not st.session_state.cpu_state['is_finished']:
        next_pc = st.session_state.cpu_state['pc']
        if next_pc < 5:
            # PCから次の命令への点線矢印
            next_y = memory_y_positions[next_pc] if next_pc < len(memory_y_positions) else 0.05
            fig.add_annotation(
                x=0.8, y=0.8,  # PCから
                ax=0.35, ay=next_y,  # 次の命令へ
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="gray",
                opacity=0.7,
                text="次の命令",
                font=dict(size=9, color='gray'),
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1
            )

    # タイトルとラベル
    fig.add_annotation(
        x=0.2, y=0.98,
        text="<b>🧠 主記憶装置</b>",
        showarrow=False,
        font=dict(size=16, color='black'),
        xref="paper", yref="paper"
    )

    fig.add_annotation(
        x=0.8, y=0.98,
        text="<b>🖥️ CPU</b>",
        showarrow=False,
        font=dict(size=16, color='black'),
        xref="paper", yref="paper"
    )

    # 実行中の命令の説明
    if st.session_state.cpu_state['ir']:
        instruction_desc = ""
        if st.session_state.cpu_state['ir'].startswith('READ'):
            instruction_desc = "📀 メモリからデータ読み込み"
        elif st.session_state.cpu_state['ir'].startswith('ADD'):
            instruction_desc = "➕ レジスタの値を加算"
        elif st.session_state.cpu_state['ir'].startswith('WRITE'):
            instruction_desc = "💾 結果をメモリに書き込み"
        elif st.session_state.cpu_state['ir'] == 'STOP':
            instruction_desc = "⏹️ プログラム終了"

        if instruction_desc:
            fig.add_annotation(
                x=0.5, y=0.35,
                text=f"<b>{instruction_desc}</b>",
                showarrow=False,
                font=dict(size=13, color='darkblue'),
                bgcolor="lightyellow",
                bordercolor="darkblue",
                borderwidth=2,
                xref="paper", yref="paper"
            )

    # 実行ステップ表示
    if st.session_state.cpu_state['current_step'] > 0:
        fig.add_annotation(
            x=0.5, y=0.02,
            text=f"<b>実行ステップ: {st.session_state.cpu_state['current_step']}</b>",
            showarrow=False,
            font=dict(size=14, color='darkblue'),
            xref="paper", yref="paper"
        )

    fig.update_layout(
        title="💻 CPUと主記憶装置の動作シミュレーション",
        title_x=0.5,
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        height=600,
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig

def save_state():
    """현재 상태를 이력에 저장"""
    cpu = st.session_state.cpu_state
    state_snapshot = {
        'memory': cpu['memory'].copy(),
        'pc': cpu['pc'],
        'ir': cpu['ir'],
        'registers': cpu['registers'].copy(),
        'current_step': cpu['current_step'],
        'execution_log': cpu['execution_log'].copy(),
        'is_finished': cpu['is_finished']
    }
    cpu['state_history'].append(state_snapshot)

def execute_instruction():
    cpu = st.session_state.cpu_state

    if cpu['pc'] >= 5 or cpu['is_finished']:
        return

    # 現在 状態を 履歴に 保存
    save_state()

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

def step_backward():
    """一ステップ 戻る"""
    cpu = st.session_state.cpu_state

    if len(cpu['state_history']) > 0:
        # 最後 状態を 復元
        previous_state = cpu['state_history'].pop()
        cpu['memory'] = previous_state['memory']
        cpu['pc'] = previous_state['pc']
        cpu['ir'] = previous_state['ir']
        cpu['registers'] = previous_state['registers']
        cpu['current_step'] = previous_state['current_step']
        cpu['execution_log'] = previous_state['execution_log']
        cpu['is_finished'] = previous_state['is_finished']

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

# CPUと主記憶装置の統合可視化
st.plotly_chart(create_unified_cpu_visualization(), use_container_width=True)

# 実行制御ボタン
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("◀️ 1ステップ戻る", disabled=len(st.session_state.cpu_state['state_history']) == 0):
        step_backward()

with col2:
    if st.button("▶️ 1ステップ進む", disabled=st.session_state.cpu_state['is_finished']):
        execute_instruction()

with col3:
    if st.button("🔄 リセット"):
        reset_cpu()

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

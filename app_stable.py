import streamlit as st
import pandas as pd

# ================================
# ページ設定
# ================================
st.set_page_config(page_title="KEIBA APP（安定版）", layout="wide")

st.title("🏇 KEIBA APP（安定版）")
st.write("出馬表・印・スコアが安定動作するバージョン")


# ================================
# デモ用 出馬表データ
# ================================
base_horses = [
    {"枠": 1, "馬番": 1, "馬名": "サンプルホースA", "性齢": "牡4", "斤量": 55.0, "騎手": "川田"},
    {"枠": 2, "馬番": 2, "馬名": "サンプルホースB", "性齢": "牝3", "斤量": 53.0, "騎手": "ルメール"},
    {"枠": 3, "馬番": 3, "馬名": "サンプルホースC", "性齢": "牡5", "斤量": 57.0, "騎手": "武豊"},
]

# ※ df は「元データ」。ここには印を持たせない前提。
df = pd.DataFrame(base_horses)

# ================================
# セッション初期化
# ================================
if "marks" not in st.session_state:
    st.session_state.marks = [""] * len(df)

if "manual_scores" not in st.session_state:
    st.session_state.manual_scores = [50] * len(df)


# ================================
# タブ構成（5つ）
# ================================
tab_shutuba, tab_score, tab_ai, tab_baken, tab_info = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)

# ================================
# 出馬表タブ
# ================================
with tab_shutuba:
    st.subheader("📋 出馬表（印つき）")

    marks = ["", "◎", "○", "▲", "△", "⭐︎", "×"]
    new_marks = []

    st.write("※ 印を選択すると下の出馬表にも反映されます")

    # 印セレクトボックス
    for i, row in df.iterrows():
        val = st.selectbox(
            f"{row['馬番']} {row['馬名']} の印",
            marks,
            index=marks.index(st.session_state.marks[i]),
            key=f"mark_{i}",
        )
        new_marks.append(val)

    st.session_state.marks = new_marks

    # 表示用に「印」カラムを追加した DataFrame
    df_out = df.copy()
    df_out["印"] = st.session_state.marks

    st.dataframe(df_out, use_container_width=True, hide_index=True)


# ================================
# スコアタブ（印は一切表示しない）
# ================================
with tab_score:
    st.subheader("🔢 手動スコア入力（印なし）")
    st.write("※ このタブには印カラムを表示しません")

    # 万が一 df に「印」が付いていても、ここでは必ず除外する
    base_cols = [c for c in df.columns if c != "印"]
    df_for_score = df[base_cols].copy()

    new_scores = []
    for i, row in df_for_score.iterrows():
        val = st.number_input(
            f"{row['馬名']} のスコア",
            min_value=0,
            max_value=100,
            value=int(st.session_state.manual_scores[i]),
            key=f"score_{i}",
        )
        new_scores.append(val)

    st.session_state.manual_scores = new_scores

    df_score = df_for_score.copy()
    df_score["手動スコア"] = st.session_state.manual_scores

    st.dataframe(df_score, use_container_width=True, hide_index=True)


# ================================
# AIスコアタブ（仮）
# ================================
with tab_ai:
    st.subheader("🤖 AIスコア（デモ）")
    st.info("ここに AI スコアを実装します（現在はダミー）")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ================================
# 馬券タブ（仮）
# ================================
with tab_baken:
    st.subheader("🎫 馬券シミュレーション（デモ）")
    st.write("ここに馬券計算機能を入れます（現在はダミー）")


# ================================
# 基本情報タブ（仮）
# ================================
with tab_info:
    st.subheader("📘 レース基本情報（デモ）")
    st.write("ここにレース詳細を表示します（現在はダミー）")

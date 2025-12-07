import streamlit as st
import pandas as pd

# ---------------------------------------------------
# ページ設定
# ---------------------------------------------------
st.set_page_config(page_title="競馬アプリ（安定版）", layout="wide")

# ---------------------------------------------------
# デモ用の簡易データ
# ---------------------------------------------------
demo_horses = [
    {"枠": 1, "馬番": 1, "馬名": "サンプルホースA", "性齢": "牡4", "騎手": "川田"},
    {"枠": 2, "馬番": 2, "馬名": "サンプルホースB", "性齢": "牝3", "騎手": "ルメール"},
    {"枠": 3, "馬番": 3, "馬名": "サンプルホースC", "性齢": "牡5", "騎手": "武豊"},
]
df = pd.DataFrame(demo_horses)

# セッションに印とスコアを保持
if "marks" not in st.session_state:
    st.session_state.marks = [""] * len(df)

if "manual_scores" not in st.session_state:
    st.session_state.manual_scores = [50] * len(df)

# ---------------------------------------------------
# タブ構成
# ---------------------------------------------------
tab_shutuba, tab_score, tab_ai, tab_baken, tab_info = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)

# ---------------------------------------------------
# 出馬表タブ
# ---------------------------------------------------
with tab_shutuba:
    st.subheader("🐴 出馬表（印つき）")

    marks = ["", "◎", "○", "▲", "△", "⭐︎", "×"]

    # 印セレクトボックス（各馬ごと）
    new_marks = []
    for i, row in df.iterrows():
        sel = st.selectbox(
            f"{row['馬番']} {row['馬名']} の印",
            marks,
            index=marks.index(st.session_state.marks[i]),
            key=f"mark_{i}"
        )
        new_marks.append(sel)

    st.session_state.marks = new_marks

    # 出馬表に印を追加
    df_shutuba = df.copy()
    df_shutuba["印"] = st.session_state.marks

    st.write("### 出馬表（印反映済み）")
    st.dataframe(df_shutuba, width="stretch", hide_index=True)

# ---------------------------------------------------
# スコアタブ（印なし）
# ---------------------------------------------------
with tab_score:
    st.subheader("🔢 手動スコア入力")

    new_scores = []
    for i, row in df.iterrows():
        val = st.number_input(
            f"{row['馬名']} のスコア",
            min_value=0,
            max_value=100,
            value=int(st.session_state.manual_scores[i]),
            key=f"manual_score_{i}"
        )
        new_scores.append(val)

    st.session_state.manual_scores = new_scores

    df_score = df.copy()
    df_score["手動スコア"] = st.session_state.manual_scores

    st.write("### スコア付き出馬表示（確認用）")
    st.dataframe(df_score, width="stretch", hide_index=True)

# ---------------------------------------------------
# AIスコアタブ（仮）
# ---------------------------------------------------
with tab_ai:
    st.subheader("🤖 AIスコア（デモ）")
    st.write("AIロジックは後で搭載します。")
    st.dataframe(df, width="stretch", hide_index=True)

# ---------------------------------------------------
# 馬券タブ（仮）
# ---------------------------------------------------
with tab_baken:
    st.subheader("🎫 馬券計算（デモ）")
    st.write("ここに馬券計算が入ります。")

# ---------------------------------------------------
# 基本情報タブ
# ---------------------------------------------------
with tab_info:
    st.subheader("📘 基本情報（デモ）")
    st.write("ここにレース情報を表示します。")

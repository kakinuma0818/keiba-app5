import streamlit as st
import pandas as pd

# ================================
# ページ設定
# ================================
st.set_page_config(page_title="KEIBA APP（安定版）", layout="wide")

st.title("🏇 KEIBA APP（安定版）")
st.write("出馬表・印・スコアが安定動作するバージョン")


# ================================
# 🔰 出馬表の“原本データ”
# ================================
base_horses = [
    {"枠": 1, "馬番": 1, "馬名": "サンプルホースA", "性齢": "牡4", "斤量": 55.0, "騎手": "川田"},
    {"枠": 2, "馬番": 2, "馬名": "サンプルホースB", "性齢": "牝3", "斤量": 53.0, "騎手": "ルメール"},
    {"枠": 3, "馬番": 3, "馬名": "サンプルホースC", "性齢": "牡5", "斤量": 57.0, "騎手": "武豊"},
]

# DataFrame 原本
df_original = pd.DataFrame(base_horses)


# ================================
# セッション初期化
# ================================
if "marks" not in st.session_state:
    st.session_state.marks = [""] * len(df_original)

if "manual_scores" not in st.session_state:
    st.session_state.manual_scores = [50] * len(df_original)


# ================================
# タブ構成
# ================================
tab_shutuba, tab_score, tab_ai, tab_baken, tab_info = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)


# ================================
# 📋 出馬表タブ
# ================================
with tab_shutuba:
    st.subheader("📋 出馬表（印つき）")

    df = df_original.copy()

    marks = ["", "◎", "○", "▲", "△", "⭐︎", "×"]
    new_marks = []

    for i, row in df.iterrows():
        val = st.selectbox(
            f"{row['馬番']} {row['馬名']} の印",
            marks,
            index=marks.index(st.session_state.marks[i]),
            key=f"mark_{i}",
        )
        new_marks.append(val)

    st.session_state.marks = new_marks

    df["印"] = st.session_state.marks
    st.dataframe(df, use_container_width=True, hide_index=True)


# ================================
# 🔢 スコアタブ（印を完全排除）
# ================================
with tab_score:
    st.subheader("🔢 手動スコア入力（印なし）")
    st.write("※ スコアタブでは印は絶対に表示されません")

    # ⛔ 出馬表タブで追加された「印」は絶対に引き継がないため
    #    “原本から再生成”
    df_score = pd.DataFrame(base_horses).copy()

    new_scores = []
    for i, row in df_score.iterrows():
        val = st.number_input(
            f"{row['馬名']} のスコア",
            min_value=0,
            max_value=100,
            value=int(st.session_state.manual_scores[i]),
            key=f"score_{i}",
        )
        new_scores.append(val)

    st.session_state.manual_scores = new_scores

    df_score["手動スコア"] = st.session_state.manual_scores

    st.dataframe(df_score, use_container_width=True, hide_index=True)


# ================================
# AIスコアタブ（デモ）
# ================================
with tab_ai:
    st.subheader("🤖 AIスコア（デモ）")
    st.dataframe(df_original, use_container_width=True, hide_index=True)


# ================================
# 馬券タブ
# ================================
with tab_baken:
    st.subheader("🎫 馬券（デモ）")
    st.write("馬券ロジックを後で実装します。")


# ================================
# 基本情報タブ
# ================================
with tab_info:
    st.subheader("📘 基本情報（デモ）")
    st.write("レース詳細をここに表示します。")

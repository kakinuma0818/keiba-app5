import streamlit as st
import pandas as pd

# =========================================
# ページ設定
# =========================================
st.set_page_config(page_title="競馬アプリ（安定版）", layout="wide")

# =========================================
# デモ用データ
# =========================================
demo_horses = [
    {"枠": 1, "馬番": 1, "馬名": "サンプルA", "性齢": "牡4", "斤量": 55},
    {"枠": 2, "馬番": 2, "馬名": "サンプルB", "性齢": "牝3", "斤量": 53},
    {"枠": 3, "馬番": 3, "馬名": "サンプルC", "性齢": "牡5", "斤量": 57},
]
df_demo = pd.DataFrame(demo_horses)

# =========================================
# 擬似タブ（Segmented Control）
# =========================================
menu = st.segmented_control(
    "メニュー選択",
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"],
)

# =========================================
# 出馬表
# =========================================
def show_shutuba():
    st.subheader("出馬表（デモ）")

    marks = ["", "◎", "○", "▲", "△", "⭐︎", "×"]

    # 印の session_state 初期化
    for i in range(len(df_demo)):
        key = f"mark_{i}"
        if key not in st.session_state:
            st.session_state[key] = ""

    updated_marks = []
    for i, row in df_demo.iterrows():
        key = f"mark_{i}"
        val = st.selectbox(
            f"{row['馬番']} {row['馬名']} 印",
            marks,
            index=marks.index(st.session_state[key]),
            key=key,
        )
        updated_marks.append(val)

    df_out = df_demo.copy()
    df_out["印"] = updated_marks

    st.dataframe(df_out, width="stretch")


# =========================================
# スコア
# =========================================
def show_score():
    st.subheader("スコア（デモ）")

    for i in range(len(df_demo)):
        key = f"score_{i}"
        if key not in st.session_state:
            st.session_state[key] = 0

    scores = []
    for i, row in df_demo.iterrows():
        key = f"score_{i}"
        val = st.number_input(
            f"{row['馬名']} 手動スコア",
            min_value=-10,
            max_value=10,
            value=st.session_state[key],
            key=key,
        )
        scores.append(val)

    df_out = df_demo.copy()
    df_out["手動スコア"] = scores
    df_out["合計"] = df_out["手動スコア"]

    st.dataframe(df_out, width="stretch")


# =========================================
# AIスコア
# =========================================
def show_ai():
    st.subheader("AIスコア（仮）")
    df_ai = df_demo.copy()
    df_ai["AIスコア"] = [68, 72, 65]
    st.dataframe(df_ai, width="stretch")


# =========================================
# 馬券
# =========================================
def show_baken():
    st.subheader("馬券（デモ）")
    st.info("ここに馬券シミュレーションを追加予定。")


# =========================================
# 基本情報
# =========================================
def show_info():
    st.subheader("基本情報（デモ）")
    st.write("ここにレース情報を追加予定。")


# =========================================
# タブ描画
# =========================================
if menu == "出馬表":
    show_shutuba()
elif menu == "スコア":
    show_score()
elif menu == "AIスコア":
    show_ai()
elif menu == "馬券":
    show_baken()
elif menu == "基本情報":
    show_info()

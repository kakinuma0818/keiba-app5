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
# → Streamlit tabs() のバグを完全回避
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

    # 印入力
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

    # 手動スコア初期値
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
    df_out["合計"] = df_out["手動スコア"]  # 今は簡易版

    st.dataframe(df_out, width="stretch")


# =========================================
# AIスコア
# =========================================
def show_ai():
    st.subheader("AIスコア（まだ仮）")
    df_ai = df_demo.copy()
    df_ai["AIスコア"] = [65, 70, 60]
    st.dataframe(df_ai, width="stretch")


# =========================================
# 馬券
# =========================================
def show_baken():
    st.subheader("馬券（デモ）")
    st.info("後で自動配分ロジックを組み込みます。")


# =========================================
# 基本情報
# =========================================
def show_info():
    st.subheader("基本情報（デモ）")
    st.write("ここにレース情報が入ります。")


# =========================================
# 表示切り替え
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

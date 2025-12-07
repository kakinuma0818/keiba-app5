import streamlit as st
import pandas as pd

st.set_page_config(page_title="競馬アプリ（復旧版）", layout="wide")

# ---------------------------------------------------
# デモ用データ（安定稼働のため最小構成）
# ---------------------------------------------------

demo_horses = [
    {"枠": 1, "馬番": 1, "馬名": "サンプルホースA", "性齢": "牡4", "斤量": 55.0, "騎手": "川田"},
    {"枠": 2, "馬番": 2, "馬名": "サンプルホースB", "性齢": "牝3", "斤量": 53.0, "騎手": "ルメール"},
    {"枠": 3, "馬番": 3, "馬名": "サンプルホースC", "性齢": "牡5", "斤量": 57.0, "騎手": "武豊"},
]
df_demo = pd.DataFrame(demo_horses)

# ---------------------------------------------------
# ★ タブ構成（ここが最重要）
# ---------------------------------------------------
tab_shutuba, tab_score, tab_ai, tab_baken, tab_info = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)

# ---------------------------------------------------
# 出馬表タブ
# ---------------------------------------------------
with tab_shutuba:
    st.subheader("出馬表（デモ）")
    st.dataframe(df_demo, width="stretch")


# ---------------------------------------------------
# スコアタブ
# ---------------------------------------------------
with tab_score:
    st.subheader("スコア入力（デモ）")

    # セッションステート（壊れない最小構成）
    if "manual_scores" not in st.session_state:
        st.session_state.manual_scores = [50, 50, 50]

    new_scores = []
    for idx, row in df_demo.iterrows():
        score = st.number_input(
            f"{row['馬名']} のスコア",
            min_value=0,
            max_value=100,
            value=st.session_state.manual_scores[idx],
            key=f"manual_score_{idx}"
        )
        new_scores.append(score)

    st.session_state.manual_scores = new_scores

    df_out = df_demo.copy()
    df_out["手動スコア"] = st.session_state.manual_scores

    st.write("手動スコア確認：")
    st.dataframe(df_out, width="stretch")


# ---------------------------------------------------
# AIスコアタブ
# ---------------------------------------------------
with tab_ai:
    st.subheader("AIスコア（デモ）")
    st.info("ここにAIスコアが表示されます。（今はデモ）")
    st.dataframe(df_demo, width="stretch")


# ---------------------------------------------------
# 馬券タブ
# ---------------------------------------------------
with tab_baken:
    st.subheader("馬券計算（デモ）")
    st.write("ここに馬券シミュレーションを実装できます。")


# ---------------------------------------------------
# 基本情報タブ
# ---------------------------------------------------
with tab_info:
    st.subheader("レース基本情報（デモ）")
    st.write("ここにレースの詳細情報が入ります。")

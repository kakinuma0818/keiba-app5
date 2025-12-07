import streamlit as st
import pandas as pd

st.set_page_config(page_title="競馬アプリ（復旧版）", layout="wide")

# ---------------------------------------------------
# 🐎 デモ用のベースデータ
# ---------------------------------------------------
BASE_HORSES = [
    {"枠": 1, "馬番": 1, "馬名": "サンプルホースA", "性齢": "牡4", "斤量": 55.0, "騎手": "川田"},
    {"枠": 2, "馬番": 2, "馬名": "サンプルホースB", "性齢": "牝3", "斤量": 53.0, "騎手": "ルメール"},
    {"枠": 3, "馬番": 3, "馬名": "サンプルホースC", "性齢": "牡5", "斤量": 57.0, "騎手": "武豊"},
]

def get_base_df() -> pd.DataFrame:
    """常にクリーンな出馬表データを返す（印など一切なし）"""
    return pd.DataFrame(BASE_HORSES)

# ---------------------------------------------------
# 🔖 セッションステート初期化
# ---------------------------------------------------
MARK_CHOICES = ["", "◎", "◯", "▲", "△", "×", "⭐︎"]

if "marks" not in st.session_state:
    st.session_state.marks = [""] * len(BASE_HORSES)

if "manual_scores" not in st.session_state:
    st.session_state.manual_scores = [50] * len(BASE_HORSES)

# ---------------------------------------------------
# 📌 タブ
# ---------------------------------------------------
tab_shutuba, tab_score, tab_ai, tab_baken, tab_info = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)

# ---------------------------------------------------
# 🐴 出馬表タブ（ここにだけ印が存在）
# ---------------------------------------------------
with tab_shutuba:
    st.subheader("🐴 出馬表（印つき）")

    df_shutuba = get_base_df()
    df_shutuba["印"] = ""  # 空の印列

    updated_marks = []
    for i, row in df_shutuba.iterrows():
        col1, col2 = st.columns([4, 2])
        with col1:
            st.write(f"{row['馬名']}（{row['枠']}枠{row['馬番']}番）")
        with col2:
            val = st.selectbox(
                "印",
                MARK_CHOICES,
                key=f"mark_{i}",
                index=MARK_CHOICES.index(st.session_state.marks[i]),
            )
        updated_marks.append(val)

    st.session_state.marks = updated_marks
    df_shutuba["印"] = st.session_state.marks

    st.dataframe(df_shutuba, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# 🔢 スコアタブ（印を強制排除）
# ---------------------------------------------------
with tab_score:
    st.subheader("🔢 手動スコア入力（印なし）")
    st.write("※ このタブでは印は一切表示されません。")

    df_score = get_base_df()

    # 万が一「印」列が混入しても絶対に消す
    if "印" in df_score.columns:
        df_score = df_score.drop(columns=["印"])

    # 表示したい列だけに絞る（念のため）
    columns_allowed = ["枠", "馬番", "馬名", "性齢", "斤量", "騎手"]
    df_score = df_score[columns_allowed]

    new_scores = []
    for idx, row in df_score.iterrows():
        val = st.number_input(
            f"{row['馬名']} のスコア",
            min_value=0,
            max_value=100,
            value=int(st.session_state.manual_scores[idx]),
            key=f"score_{idx}",
        )
        new_scores.append(val)

    st.session_state.manual_scores = new_scores
    df_score["手動スコア"] = st.session_state.manual_scores

    st.dataframe(df_score, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# 🤖 AIスコアタブ
# ---------------------------------------------------
with tab_ai:
    st.subheader("🤖 AIスコア（デモ）")
    st.info("AIスコアはここに表示されます。（仮データ）")
    df_ai = get_base_df()
    st.dataframe(df_ai, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# 🎫 馬券タブ
# ---------------------------------------------------
with tab_baken:
    st.subheader("🎫 馬券シミュレーション（デモ）")
    st.write("ここに馬券機能が入ります。")

# ---------------------------------------------------
# 📘 基本情報タブ
# ---------------------------------------------------
with tab_info:
    st.subheader("📘 レース基本情報（デモ）")
    st.write("ここにレース情報を表示します。")

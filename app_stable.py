import streamlit as st
import pandas as pd

st.set_page_config(page_title="競馬アプリ（復旧版）", layout="wide")

# ---------------------------------------------------
# 🐎 デモ用のベースデータ（本番では scrape で置換）
# ---------------------------------------------------
base_horses = [
    {"枠": 1, "馬番": 1, "馬名": "サンプルホースA", "性齢": "牡4", "斤量": 55.0, "騎手": "川田"},
    {"枠": 2, "馬番": 2, "馬名": "サンプルホースB", "性齢": "牝3", "斤量": 53.0, "騎手": "ルメール"},
    {"枠": 3, "馬番": 3, "馬名": "サンプルホースC", "性齢": "牡5", "斤量": 57.0, "騎手": "武豊"},
]

df_base = pd.DataFrame(base_horses)

# ---------------------------------------------------
# 🔖 セッションステート初期化
# ---------------------------------------------------
marks = ["", "◎", "◯", "▲", "△", "×", "⭐︎"]

if "marks" not in st.session_state:
    st.session_state.marks = [""] * len(df_base)

if "manual_scores" not in st.session_state:
    st.session_state.manual_scores = [50] * len(df_base)

# ---------------------------------------------------
# 📌 タブセット
# ---------------------------------------------------
tab_shutuba, tab_score, tab_ai, tab_baken, tab_info = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)

# ---------------------------------------------------
# 🐴 出馬表タブ（印選択がここにのみ存在）
# ---------------------------------------------------
with tab_shutuba:
    st.subheader("🐴 出馬表（印つき）")

    df_shutuba = df_base.copy()
    df_shutuba["印"] = ""  # 空の列を初期化

    # 印入力 UI
    updated_marks = []
    for i, row in df_shutuba.iterrows():
        col1, col2 = st.columns([4, 2])
        with col1:
            st.write(f"{row['馬名']}（{row['枠']}枠{row['馬番']}番）")
        with col2:
            val = st.selectbox(
                "印",
                marks,
                key=f"mark_{i}",
                index=marks.index(st.session_state.marks[i])
            )
        updated_marks.append(val)

    st.session_state.marks = updated_marks

    # 印を反映した出馬表
    df_shutuba["印"] = st.session_state.marks
    st.dataframe(df_shutuba, use_container_width=True, hide_index=True)

# ---------------------------------------------------
# 🔢 スコアタブ（印を完全排除）
# ---------------------------------------------------
with tab_score:
    st.subheader("🔢 手動スコア入力（印なし）")
    st.write("※ スコアタブでは印は一切表示されません")

    # Streamlit が持つ内部キャッシュで "印" が混入するのを強制排除
    columns_allowed = ["枠", "馬番", "馬名", "性齢", "斤量", "騎手"]

    df_score = pd.DataFrame(base_horses).copy()
    df_score = df_score.reindex(columns=columns_allowed)

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
    st.dataframe(df_base, use_container_width=True, hide_index=True)

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

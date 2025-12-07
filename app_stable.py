import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# =========================================================
# 基本設定（タブ構成は絶対に崩さない）
# =========================================================
st.set_page_config(page_title="競馬アプリ（安定版）", layout="wide")

# ---------------------------------------------------------
# スタイル
# ---------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #ffffff;
    color: #000000;
}
.header-box {
    font-size: 1.3rem;
    font-weight: bold;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-box">🏇 KEIBA APP（安定版）</div>', unsafe_allow_html=True)


# =========================================================
# レースIDパース
# =========================================================
def parse_race_id(text):
    """URL or 12桁 race_id を認識して race_id を返す"""
    text = text.strip()

    # race_id=xxxx 形式
    m = re.search(r"race_id=(\d{12})", text)
    if m:
        return m.group(1)

    # 単なる12桁
    if re.fullmatch(r"\d{12}", text):
        return text

    # URL中の12桁
    m2 = re.search(r"(\d{12})", text)
    if m2:
        return m2.group(1)

    return None


# =========================================================
# 出馬表スクレイピング（安定版）
# =========================================================
def fetch_shutuba(race_id: str):
    url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code != 200:
        return None, None

    # 文字化け回避
    r.encoding = r.apparent_encoding

    soup = BeautifulSoup(r.text, "html.parser")

    # ------------------------------
    # レース名・情報
    ------------------------------
    race_name = soup.select_one(".RaceName")
    race_name = race_name.get_text(strip=True) if race_name else "レース名取得不可"

    race_info = soup.select_one(".RaceData01")
    race_info = race_info.get_text(" ", strip=True) if race_info else ""

    # 頭数抽出
    n = None
    m_n = re.search(r"(\d+)頭", r.text)
    if m_n:
        n = int(m_n.group(1))

    # ------------------------------
    # 出馬表テーブル
    # ------------------------------
    table = soup.select_one("table.RaceTable01")
    if table is None:
        return None, {
            "race_name": race_name,
            "race_info": race_info,
            "num": n
        }

    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue

        def tx(i):
            return tds[i].get_text(strip=True) if i < len(tds) else ""

        # 列構造は netkeiba 固定なので位置で取る
        row = {
            "枠": tx(0),
            "馬番": tx(1),
            "馬名": tx(3),
            "性齢": tx(4),
            "斤量": tx(5),
            "騎手": tx(6),
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    meta = {
        "race_name": race_name,
        "race_info": race_info,
        "num": n,
        "url": url
    }
    return df, meta


# =========================================================
# UI：レースID入力 → 出馬表読み込み
# =========================================================
st.markdown("### 1. レースIDを入力（URL でも可）")

id_in = st.text_input("レースID または URL")

df_loaded = None
meta_loaded = None

if st.button("出馬表を取得"):
    rid = parse_race_id(id_in)
    if rid is None:
        st.error("❌ race_id を認識できません。")
    else:
        with st.spinner("出馬表を取得中…"):
            df_loaded, meta_loaded = fetch_shutuba(rid)

        if df_loaded is None:
            st.error("❌ 出馬表データが取得できませんでした。")
        else:
            st.success("✅ 出馬表取得OK！")
            st.write(f"**レース名**：{meta_loaded['race_name']}")
            st.write(f"**情報**：{meta_loaded['race_info']}")
            st.write(f"**頭数**：{meta_loaded['num']} 頭")
            st.write(f"[netkeibaページへ]({meta_loaded['url']})")


# =========================================================
# タブ構造（絶対に崩さない）
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)

# =========================================================
# 出馬表タブ
# =========================================================
with tab1:
    st.markdown("### 📌 出馬表")

    if df_loaded is None:
        st.info("まだ出馬表が読み込まれていません。")
    else:
        # 印セレクト（表示されるのはここだけ）
        marks = ["", "◎", "○", "▲", "△", "⭐︎", "×"]

        if "marks" not in st.session_state:
            st.session_state.marks = [""] * len(df_loaded)

        new_marks = []
        for i, row in df_loaded.iterrows():
            m = st.selectbox(
                f"{row['馬番']}：{row['馬名']} の印",
                marks,
                index=marks.index(st.session_state.marks[i]),
                key=f"mk_{i}"
            )
            new_marks.append(m)

        st.session_state.marks = new_marks

        out_df = df_loaded.copy()
        out_df["印"] = st.session_state.marks

        st.dataframe(out_df, use_container_width=True)


# =========================================================
# スコアタブ（印は絶対に表示しない）
# =========================================================
with tab2:
    st.markdown("### 📌 スコア")

    if df_loaded is None:
        st.info("まだ出馬表が読み込まれていません。")
    else:
        # 手動スコアのみ
        if "manual_scores" not in st.session_state:
            st.session_state.manual_scores = [50] * len(df_loaded)

        new_scores = []
        for i, row in df_loaded.iterrows():
            sc = st.number_input(
                f"{row['馬名']} の手動スコア",
                min_value=0,
                max_value=100,
                value=st.session_state.manual_scores[i],
                key=f"sc_{i}"
            )
            new_scores.append(sc)

        st.session_state.manual_scores = new_scores

        df_sc = df_loaded.copy()
        df_sc["手動スコア"] = new_scores

        st.dataframe(df_sc, use_container_width=True)


# =========================================================
# AIスコアタブ（仮）
# =========================================================
with tab3:
    st.markdown("### 📌 AIスコア（仮）")
    if df_loaded is None:
        st.info("まだ出馬表が読み込まれていません。")
    else:
        st.info("ここにAIスコアが入ります（仮）")
        st.dataframe(df_loaded, use_container_width=True)


# =========================================================
# 馬券タブ（仮）
# =========================================================
with tab4:
    st.markdown("### 📌 馬券（仮）")
    st.info("馬券計算は後で実装します。")


# =========================================================
# 基本情報タブ
# =========================================================
with tab5:
    st.markdown("### 📌 基本情報")
    if meta_loaded is None:
        st.info("まだレース情報がありません。")
    else:
        st.write(f"**レース名**：{meta_loaded['race_name']}")
        st.write(f"**概要**：{meta_loaded['race_info']}")
        st.write(f"**頭数**：{meta_loaded['num']} 頭")
        st.write(f"[netkeibaページへ]({meta_loaded['url']})")

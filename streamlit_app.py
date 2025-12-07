import re
import math
import requests
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

# ======================
# ページ設定 & テーマ
# ======================
st.set_page_config(page_title="KEIBA APP", layout="wide")

PRIMARY = "#ff7f00"  # エルメスオレンジ

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #ffffff;
        color: #111111;
        font-family: "Helvetica", sans-serif;
    }}
    .keiba-title {{
        font-size: 1.4rem;
        font-weight: 700;
        color: {PRIMARY};
    }}
    .keiba-subtitle {{
        font-size: 0.9rem;
        color: #555555;
    }}
    .accent {{
        color: {PRIMARY};
    }}
    .small-label {{
        font-size: 0.8rem;
        color: #666666;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="keiba-title">KEIBA APP</div>', unsafe_allow_html=True)
st.markdown('<div class="keiba-subtitle">出馬表 → スコア → 馬券配分まで一括サポート</div>', unsafe_allow_html=True)
st.markdown("---")


# ======================
# race_id 抽出
# ======================
def parse_race_id(text: str):
    text = text.strip()
    if re.fullmatch(r"\d{12}", text):
        return text
    m = re.search(r"race_id=(\d{12})", text)
    if m:
        return m.group(1)
    m2 = re.search(r"(\d{12})", text)
    if m2:
        return m2.group(1)
    return None


# ======================
# 出馬表スクレイピング（文字化け対応）
# ======================
def fetch_shutuba(race_id: str):
    url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None, None

    # 文字化け対策
    r.encoding = r.apparent_encoding

    soup = BeautifulSoup(r.text, "html.parser")

    race_name_el = soup.select_one(".RaceName")
    race_name = race_name_el.get_text(strip=True) if race_name_el else ""

    race_info_el = soup.select_one(".RaceData01")
    race_info_raw = race_info_el.get_text(" ", strip=True) if race_info_el else ""

    # 馬場・距離など簡易抽出
    surface = "不明"
    distance = None
    if "芝" in race_info_raw:
        surface = "芝"
    elif "ダ" in race_info_raw:
        surface = "ダート"
    m_dist = re.search(r"(\d+)m", race_info_raw)
    if m_dist:
        distance = int(m_dist.group(1))

    # 出馬表テーブル
    table = soup.select_one("table.RaceTable01")
    if table is None:
        meta = {
            "race_name": race_name,
            "race_info": race_info_raw,
            "surface": surface,
            "distance": distance,
            "head_count": 0,
            "url": url,
        }
        return None, meta

    header_row = table.find("tr")
    headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

    def idx(contain_str):
        for i, h in enumerate(headers):
            if contain_str in h:
                return i
        return None

    idx_waku = idx("枠")
    idx_umaban = idx("馬番")
    idx_name = idx("馬名")
    idx_sexage = idx("性齢")
    idx_weight = idx("斤量")
    idx_jockey = idx("騎手")
    idx_body = idx("馬体重")
    idx_odds = idx("オッズ")
    idx_pop = idx("人気")

    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue

        def safe(i):
            return tds[i].get_text(strip=True) if i is not None and i < len(tds) else ""

        rows.append(
            {
                "枠": safe(idx_waku),
                "馬番": safe(idx_umaban),
                "馬名": safe(idx_name),
                "性齢": safe(idx_sexage),
                "斤量": safe(idx_weight),
                "前走体重": safe(idx_body),
                "騎手": safe(idx_jockey),
                "オッズ": safe(idx_odds),
                "人気": safe(idx_pop),
            }
        )

    df = pd.DataFrame(rows)
    # 数値変換
    df["オッズ"] = pd.to_numeric(df["オッズ"], errors="coerce")
    df["人気"] = pd.to_numeric(df["人気"], errors="coerce")

    head_count = len(df)
    # レース情報に頭数を統合
    if race_info_raw:
        race_info = f"{race_info_raw} / 頭数: {head_count}頭"
    else:
        race_info = f"頭数: {head_count}頭"

    meta = {
        "race_name": race_name,
        "race_info": race_info,
        "surface": surface,
        "distance": distance,
        "head_count": head_count,
        "url": url,
    }
    return df, meta


# ======================
# 年齢スコア
# ======================
def score_age(sexage: str, surface: str) -> float:
    m = re.search(r"(\d+)", sexage)
    if not m:
        return 2.0
    age = int(m.group(1))

    if surface == "ダート":
        if 3 <= age <= 4:
            return 3.0
        elif age == 5:
            return 2.0
        elif age == 6:
            return 1.5
        else:
            return 1.0
    else:
        if 3 <= age <= 5:
            return 3.0
        elif age == 6:
            return 2.0
        else:
            return 1.0


# ======================
# スコアのベース部分（手動を除く）
# ======================
def build_base_score_df(df: pd.DataFrame, meta: dict) -> pd.DataFrame:
    surface = meta.get("surface", "不明")

    sc = df.copy().reset_index(drop=True)
    sc["年齢"] = sc["性齢"].fillna("").apply(lambda x: score_age(x, surface))

    # 今後拡張予定のカラムは 0 で初期化
    for col in [
        "血統",
        "騎手スコア",
        "馬主",
        "生産者",
        "調教師",
        "成績",
        "競馬場",
        "距離",
        "脚質",
        "枠スコア",
        "馬場",
    ]:
        sc[col] = 0.0

    return sc


# ======================
# 馬券 自動配分（単勝想定）
# ======================
def allocate_bets(bets_df, total_budget, target_multiplier, loss_tolerance=0.1):
    # 目標払い戻し P
    P = total_budget * target_multiplier
    threshold = P * (1 - loss_tolerance)

    results = []
    needed = 0

    selected = bets_df[bets_df["購入"] & bets_df["オッズ"].notna()]
    for _, row in selected.iterrows():
        odds = float(row["オッズ"])
        raw = threshold / odds
        stake = int(math.ceil(raw / 100) * 100)

        payout = stake * odds
        needed += stake

        results.append(
            {
                "馬名": row["馬名"],
                "オッズ": odds,
                "推奨金額": stake,
                "想定払い戻し": payout,
            }
        )

    df = pd.DataFrame(results)
    info = {
        "目標払い戻し額": P,
        "許容下限": threshold,
        "必要合計金額": needed,
        "残り予算": total_budget - needed,
    }
    return df, info


# ======================
# セッションにレースデータを保持
# ======================
if "race_df" not in st.session_state:
    st.session_state.race_df = None
if "race_meta" not in st.session_state:
    st.session_state.race_meta = None

# ======================
# 1. レース指定（入力エリア）
# ======================
st.markdown("### 1. レース指定")

race_input = st.text_input(
    "netkeiba レースURL または race_id（12桁）",
    placeholder="例）https://race.netkeiba.com/race/shutuba.html?race_id=202507050211",
)
go = st.button("このレースを読み込む")

if go and race_input:
    race_id = parse_race_id(race_input)
    if not race_id:
        st.error("race_id を認識できませんでした。")
    else:
        with st.spinner("出馬表を取得中..."):
            df, meta = fetch_shutuba(race_id)
        if df is None:
            st.error("出馬表の取得に失敗しました。")
        else:
            st.session_state.race_df = df
            st.session_state.race_meta = meta
            st.success("出馬表取得OK！")
            st.write(f"**レース名**: {meta['race_name']}")
            st.write(f"**概要**: {meta['race_info']}")
            st.write(f"[netkeibaページへ]({meta['url']})")

# ======================
# レース情報表示（最新のセッション状態から）
# ======================
race_df = st.session_state.race_df
race_meta = st.session_state.race_meta

if race_df is not None and race_meta is not None and not go:
    # 直前にロードしたわけではないが、再描画時にも表示
    st.markdown("### 現在のレース情報")
    st.write(f"**レース名**: {race_meta.get('race_name', '')}")
    st.write(f"**概要**: {race_meta.get('race_info', '')}")
    st.write(f"[netkeibaページへ]({race_meta.get('url', '')})")

st.markdown("---")
st.markdown("### 2. 解析タブ")


# ======================
# タブ定義（常に 5 個表示）
# ======================
tab_ma, tab_sc, tab_ai, tab_be, tab_pr = st.tabs(
    ["出馬表", "スコア", "AIスコア", "馬券", "基本情報"]
)

# ----------------------
# 出馬表タブ
# ----------------------
with tab_ma:
    st.markdown("#### 出馬表＋印")

    if race_df is None or race_meta is None:
        st.info("レースを読み込むと出馬表が表示されます。")
    else:
        # ベーススコアと手動スコア（スコアタブと共通のロジック）
        base_sc = build_base_score_df(race_df, race_meta)

        # 手動スコアは session_state から読む（スコアタブで編集）
        manual_scores = []
        for i in range(len(base_sc)):
            manual_scores.append(st.session_state.get(f"manual_{i}", 0))

        base_cols = [
            "年齢",
            "血統",
            "騎手スコア",
            "馬主",
            "生産者",
            "調教師",
            "成績",
            "競馬場",
            "距離",
            "脚質",
            "枠スコア",
            "馬場",
        ]

        score_df = base_sc.copy()
        score_df["手動"] = manual_scores
        score_df["合計"] = score_df[base_cols].sum(axis=1) + score_df["手動"]

        # 合計スコア順
        score_df = score_df.sort_values("合計", ascending=False).reset_index(drop=True)
        score_df["スコア順"] = score_df.index + 1

        # 出馬表と結合して、スコア順で並べ替えた出馬表を作成
        ma_df = race_df.merge(
            score_df[["馬名", "合計", "スコア順"]],
            on="馬名",
            how="left",
        )
        ma_df = ma_df.sort_values("スコア順").reset_index(drop=True)

        marks = ["", "◎", "○", "▲", "△", "⭐︎", "×"]

        st.markdown("印の入力：")

        # 印の入力UI（選択は上部に縦並び）
        for i, row in ma_df.iterrows():
            key = f"mark_{i}"
            current = st.session_state.get(key, "")
            try:
                default_index = marks.index(current)
            except ValueError:
                default_index = 0

            st.selectbox(
                f"{row['馬番']} {row['馬名']} の印",
                marks,
                index=default_index,
                key=key,
            )

        # テーブルに印を反映
        mark_values = [st.session_state.get(f"mark_{i}", "") for i in range(len(ma_df))]
        ma_df["印"] = mark_values

        st.markdown("##### 印付き出馬表（確認用）")
        st.dataframe(
            ma_df[
                [
                    "枠",
                    "馬番",
                    "馬名",
                    "性齢",
                    "斤量",
                    "前走体重",
                    "騎手",
                    "オッズ",
                    "人気",
                    "合計",
                    "スコア順",
                    "印",
                ]
            ],
            width="stretch",
        )


# ----------------------
# スコアタブ
# ----------------------
with tab_sc:
    st.markdown("#### スコア（手動補正つき）")

    if race_df is None or race_meta is None:
        st.info("レースを読み込むとスコア入力ができます。")
    else:
        base_sc = build_base_score_df(race_df, race_meta)

        st.markdown("手動スコア（-3〜+3）を入力してください。")

        choices = [-3, -2, -1, 0, 1, 2, 3]

        # 手動入力UI
        for i, row in base_sc.iterrows():
            key = f"manual_{i}"
            current = st.session_state.get(key, 0)
            if current not in choices:
                current = 0
            default_index = choices.index(current)

            st.selectbox(
                f"{row['馬番']} {row['馬名']} 手動スコア",
                choices,
                index=default_index,
                key=key,
            )

        # 入力結果を DataFrame に反映
        manual_scores = [st.session_state.get(f"manual_{i}", 0) for i in range(len(base_sc))]

        base_cols = [
            "年齢",
            "血統",
            "騎手スコア",
            "馬主",
            "生産者",
            "調教師",
            "成績",
            "競馬場",
            "距離",
            "脚質",
            "枠スコア",
            "馬場",
        ]

        score_df = base_sc.copy()
        score_df["手動"] = manual_scores
        score_df["合計"] = score_df[base_cols].sum(axis=1) + score_df["手動"]

        score_df = score_df.sort_values("合計", ascending=False).reset_index(drop=True)

        st.markdown("##### スコア一覧")
        st.dataframe(
            score_df[
                [
                    "馬名",
                    "合計",
                    "年齢",
                    "血統",
                    "騎手スコア",
                    "馬主",
                    "生産者",
                    "調教師",
                    "成績",
                    "競馬場",
                    "距離",
                    "脚質",
                    "枠スコア",
                    "馬場",
                    "手動",
                ]
            ],
            width="stretch",
        )


# ----------------------
# AIスコアタブ（仮）
# ----------------------
with tab_ai:
    st.markdown("#### AIスコア（仮）")
    if race_df is None or race_meta is None:
        st.info("レースを読み込むと AI スコア（仮）が表示されます。")
    else:
        base_sc = build_base_score_df(race_df, race_meta)
        manual_scores = [st.session_state.get(f"manual_{i}", 0) for i in range(len(base_sc))]

        base_cols = [
            "年齢",
            "血統",
            "騎手スコア",
            "馬主",
            "生産者",
            "調教師",
            "成績",
            "競馬場",
            "距離",
            "脚質",
            "枠スコア",
            "馬場",
        ]

        score_df = base_sc.copy()
        score_df["手動"] = manual_scores
        score_df["AIスコア"] = score_df[base_cols].sum(axis=1) + score_df["手動"]

        out = score_df[["馬名", "AIスコア"]].sort_values(
            "AIスコア", ascending=False
        ).reset_index(drop=True)

        st.dataframe(out, width="stretch")


# ----------------------
# 馬券タブ
# ----------------------
with tab_be:
    st.markdown("#### 馬券配分（単勝想定）")

    if race_df is None or race_meta is None:
        st.info("レースを読み込むと馬券配分シミュレーションができます。")
    else:
        col1, col2 = st.columns(2)
        with col1:
            total_budget = st.number_input("総投資額（円）", 100, 1000000, 1000, 100)
        with col2:
            target_mult = st.slider("希望払い戻し倍率", 1.0, 10.0, 1.5, 0.5)

        st.write("→ チェックした馬すべてで、ほぼ同じ払い戻しを狙う自動配分")

        bet_df = race_df[["馬名", "オッズ"]].copy()
        bet_df["購入"] = False

        edited = st.data_editor(
            bet_df,
            num_rows="fixed",
            width="stretch",
        )

        if st.button("自動配分計算"):
            if edited["購入"].sum() == 0:
                st.warning("1つ以上チェックしてください。")
            else:
                alloc, info = allocate_bets(edited, total_budget, target_mult)

                st.markdown("##### 推奨配分")
                st.dataframe(alloc, width="stretch")

                st.write(f"- 目標払い戻し額: {info['目標払い戻し額']:.0f} 円")
                st.write(f"- 下限（許容）: {info['許容下限']:.0f} 円")
                st.write(f"- 必要合計: {info['必要合計金額']} 円")
                st.write(f"- 残り: {info['残り予算']} 円")

                if info["必要合計金額"] > total_budget:
                    st.error("💡 この設定では目標払い戻しを満たせません。")


# ----------------------
# 基本情報タブ
# ----------------------
with tab_pr:
    st.markdown("#### 基本情報")
    if race_df is None or race_meta is None:
        st.info("レースを読み込むと基本情報が表示されます。")
    else:
        st.markdown("##### レース情報")
        st.write(f"**レース名**: {race_meta.get('race_name', '')}")
        st.write(f"**概要**: {race_meta.get('race_info', '')}")
        st.write(f"[netkeibaページへ]({race_meta.get('url', '')})")

        st.markdown("##### 出馬表（素データ）")
        st.dataframe(
            race_df[
                [
                    "枠",
                    "馬番",
                    "馬名",
                    "性齢",
                    "斤量",
                    "前走体重",
                    "騎手",
                    "オッズ",
                    "人気",
                ]
            ],
            width="stretch",
        )

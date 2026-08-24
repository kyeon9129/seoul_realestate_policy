# ============================================================
# 서울·경기 10·15 부동산 정책 거래량 변화 Dashboard
# Streamlit 전용 app.py
# ============================================================

from pathlib import Path
import json

import numpy as np
import pandas as pd

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# 1. Streamlit 기본 설정
# ============================================================

st.set_page_config(
    page_title="10·15 부동산 정책 거래시장 변화",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. 분석 기준
# ============================================================

POLICY_DATE = pd.Timestamp("2025-10-15")

BEFORE_START = pd.Timestamp("2025-04-15")
BEFORE_END = pd.Timestamp("2025-10-14")

AFTER_START = pd.Timestamp("2025-10-15")
AFTER_END = pd.Timestamp("2026-04-14")

BEFORE_DAYS = (
    BEFORE_END - BEFORE_START
).days + 1

AFTER_DAYS = (
    AFTER_END - AFTER_START
).days + 1


# 서울 기존 규제지역
SEOUL_EXISTING_REGULATED = [
    "강남구",
    "서초구",
    "송파구",
    "용산구"
]


# 지도 색상
# 음수(거래 감소) = 빨강
# 0 = 흰색
# 양수(거래 증가) = 파랑

CHANGE_COLORSCALE = [
    [0.00, "#9c0000"],
    [0.25, "#d6604d"],
    [0.50, "#f7f7f7"],
    [0.75, "#4393c3"],
    [1.00, "#2166ac"]
]


# ============================================================
# 3. CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1550px;
    }

    h1 {
        font-weight: 750;
        letter-spacing: -1.5px;
    }

    h2, h3 {
        letter-spacing: -0.7px;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e9e9e9;
        border-radius: 12px;
        padding: 18px;
        min-height: 125px;
    }

    [data-testid="stSidebar"] {
        background-color: #fafafa;
    }

    .small-note {
        font-size: 0.86rem;
        color: #777777;
        line-height: 1.5;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. 파일 경로
#
# GitHub 구조
#
# repository/
# ├── app.py
# ├── requirements.txt
# └── data/
#     ├── seoul_policy_summary.csv
#     ├── ...
#     └── gyeonggi_policy_map.geojson
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# 5. 필요한 파일 목록
# ============================================================

FILES = {

    "seoul_summary":
        DATA_DIR / "seoul_policy_summary.csv",

    "seoul_daily":
        DATA_DIR / "seoul_daily_transactions.csv",

    "seoul_district_daily":
        DATA_DIR / "seoul_district_daily.csv",

    "seoul_monthly":
        DATA_DIR / "seoul_monthly_transactions.csv",

    "seoul_geojson":
        DATA_DIR / "seoul_policy_map.geojson",


    "gyeonggi_summary":
        DATA_DIR / "gyeonggi_policy_summary.csv",

    "gyeonggi_daily":
        DATA_DIR / "gyeonggi_daily_transactions.csv",

    "gyeonggi_district_daily":
        DATA_DIR / "gyeonggi_district_daily.csv",

    "gyeonggi_monthly":
        DATA_DIR / "gyeonggi_monthly_transactions.csv",

    "gyeonggi_geojson":
        DATA_DIR / "gyeonggi_policy_map.geojson"
}


# ============================================================
# 6. 파일 존재 확인
# ============================================================

missing_files = [

    path.name

    for path in FILES.values()

    if not path.exists()
]


if missing_files:

    st.error(
        "다음 데이터 파일을 찾을 수 없습니다."
    )

    st.code(
        "\n".join(missing_files)
    )

    st.info(
        "GitHub 저장소의 data 폴더에 "
        "위 파일이 있는지 확인해주세요."
    )

    st.stop()


# ============================================================
# 7. 데이터 로딩
# ============================================================

@st.cache_data
def load_data():

    # --------------------------------------------------------
    # 서울
    # --------------------------------------------------------

    seoul_summary = pd.read_csv(
        FILES["seoul_summary"]
    )

    seoul_daily = pd.read_csv(
        FILES["seoul_daily"]
    )

    seoul_district_daily = pd.read_csv(
        FILES["seoul_district_daily"]
    )

    seoul_monthly = pd.read_csv(
        FILES["seoul_monthly"]
    )


    with open(
        FILES["seoul_geojson"],
        "r",
        encoding="utf-8"
    ) as f:

        seoul_geojson = json.load(f)


    # --------------------------------------------------------
    # 경기도
    # --------------------------------------------------------

    gyeonggi_summary = pd.read_csv(
        FILES["gyeonggi_summary"]
    )

    gyeonggi_daily = pd.read_csv(
        FILES["gyeonggi_daily"]
    )

    gyeonggi_district_daily = pd.read_csv(
        FILES["gyeonggi_district_daily"]
    )

    gyeonggi_monthly = pd.read_csv(
        FILES["gyeonggi_monthly"]
    )


    with open(
        FILES["gyeonggi_geojson"],
        "r",
        encoding="utf-8"
    ) as f:

        gyeonggi_geojson = json.load(f)


    # --------------------------------------------------------
    # 날짜형 변환
    # --------------------------------------------------------

    seoul_daily["deal_date"] = pd.to_datetime(
        seoul_daily["deal_date"]
    )

    seoul_district_daily["deal_date"] = pd.to_datetime(
        seoul_district_daily["deal_date"]
    )

    seoul_monthly["year_month"] = pd.to_datetime(
        seoul_monthly["year_month"]
    )


    gyeonggi_daily["deal_date"] = pd.to_datetime(
        gyeonggi_daily["deal_date"]
    )

    gyeonggi_district_daily["deal_date"] = pd.to_datetime(
        gyeonggi_district_daily["deal_date"]
    )

    gyeonggi_monthly["year_month"] = pd.to_datetime(
        gyeonggi_monthly["year_month"]
    )


    return (
        seoul_summary,
        seoul_daily,
        seoul_district_daily,
        seoul_monthly,
        seoul_geojson,

        gyeonggi_summary,
        gyeonggi_daily,
        gyeonggi_district_daily,
        gyeonggi_monthly,
        gyeonggi_geojson
    )


(
    seoul_summary,
    seoul_daily,
    seoul_district_daily,
    seoul_monthly,
    seoul_geojson,

    gyeonggi_summary,
    gyeonggi_daily,
    gyeonggi_district_daily,
    gyeonggi_monthly,
    gyeonggi_geojson

) = load_data()


# ============================================================
# 8. Summary 데이터 공통 전처리
# ============================================================

def prepare_summary(df):

    df = df.copy()


    numeric_columns = [

        "before_count",
        "after_count",

        "before_daily_avg",
        "after_daily_avg",

        "count_change_pct",
        "daily_avg_change_pct"
    ]


    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )


    # --------------------------------------------------------
    # 점유율 정보가 없는 경우 자동 계산
    #
    # 경기도 데이터에는 원래 없으므로 여기에서 계산
    # --------------------------------------------------------

    total_before = (
        df["before_count"].sum()
    )

    total_after = (
        df["after_count"].sum()
    )


    df["before_share_pct"] = (

        df["before_count"]

        / total_before

        * 100
    )


    df["after_share_pct"] = (

        df["after_count"]

        / total_after

        * 100
    )


    df["share_change_pp"] = (

        df["after_share_pct"]

        - df["before_share_pct"]
    )


    if "lawd_cd" in df.columns:

        df["lawd_cd"] = (

            df["lawd_cd"]

            .astype(str)

            .str.replace(
                ".0",
                "",
                regex=False
            )

            .str.zfill(5)
        )


    return df


seoul_summary = prepare_summary(
    seoul_summary
)

gyeonggi_summary = prepare_summary(
    gyeonggi_summary
)


# ============================================================
# 9. GeoJSON 라벨 위치 추출
# ============================================================

def get_geo_label_data(geojson):

    rows = []


    for feature in geojson.get(
        "features",
        []
    ):

        properties = feature.get(
            "properties",
            {}
        )


        feature_id = str(
            feature.get(
                "id",
                ""
            )
        )


        lon = properties.get(
            "label_lon"
        )

        lat = properties.get(
            "label_lat"
        )


        if (
            lon is None
            or lat is None
        ):

            continue


        try:

            lon = float(lon)
            lat = float(lat)

        except (
            TypeError,
            ValueError
        ):

            continue


        rows.append({

            "feature_id":
                feature_id,

            "label_lon":
                lon,

            "label_lat":
                lat,

            "district":
                properties.get(
                    "district"
                ),

            "name":
                properties.get(
                    "name"
                ),

            "lawd_cd":
                str(
                    properties.get(
                        "lawd_cd",
                        feature_id
                    )
                )
        })


    return pd.DataFrame(
        rows
    )


# ============================================================
# 10. 서울 지도
# ============================================================

def make_seoul_map(
    summary,
    geojson,
    metric_col,
    metric_name
):

    map_df = summary.copy()


    map_df[metric_col] = (
        pd.to_numeric(
            map_df[metric_col],
            errors="coerce"
        )
    )


    valid_values = (

        map_df[
            metric_col
        ]

        .dropna()

        .abs()
    )


    if len(valid_values) > 0:

        max_abs = max(
            valid_values.max(),
            1
        )

    else:

        max_abs = 1


    fig = go.Figure()


    # --------------------------------------------------------
    # 신규 규제지역 21개
    # --------------------------------------------------------

    custom_data = np.column_stack(
        [

            map_df[
                "before_count"
            ],

            map_df[
                "after_count"
            ],

            map_df[
                "before_daily_avg"
            ],

            map_df[
                "after_daily_avg"
            ],

            map_df[
                metric_col
            ]
        ]
    )


    fig.add_trace(

        go.Choropleth(

            geojson=geojson,

            locations=map_df[
                "region"
            ],

            z=map_df[
                metric_col
            ],

            featureidkey="id",

            zmin=-max_abs,

            zmax=max_abs,

            zmid=0,

            colorscale=(
                CHANGE_COLORSCALE
            ),

            marker_line_color=(
                "white"
            ),

            marker_line_width=1.2,

            colorbar=dict(

                title=metric_name,

                thickness=13,

                len=0.55
            ),

            customdata=custom_data,

            hovertemplate=(

                "<b>%{location}</b>"
                "<br><br>"

                "정책 이전 거래량: "
                "%{customdata[0]:,.0f}건"
                "<br>"

                "정책 이후 거래량: "
                "%{customdata[1]:,.0f}건"
                "<br>"

                "정책 이전 일평균: "
                "%{customdata[2]:.2f}건"
                "<br>"

                "정책 이후 일평균: "
                "%{customdata[3]:.2f}건"
                "<br>"

                f"{metric_name}: "
                "%{customdata[4]:.2f}"

                "<extra></extra>"
            )
        )
    )


    # --------------------------------------------------------
    # 기존 규제지역
    # --------------------------------------------------------

    fig.add_trace(

        go.Choropleth(

            geojson=geojson,

            locations=(
                SEOUL_EXISTING_REGULATED
            ),

            z=[1, 1, 1, 1],

            featureidkey="id",

            colorscale=[

                [0, "#7f0000"],
                [1, "#7f0000"]
            ],

            showscale=False,

            marker_line_color="white",

            marker_line_width=1.8,

            hovertemplate=(

                "<b>%{location}</b>"
                "<br>기존 규제지역"
                "<br>이번 변화량 분석 제외"

                "<extra></extra>"
            )
        )
    )


    # --------------------------------------------------------
    # 지도 라벨
    # --------------------------------------------------------

    label_df = get_geo_label_data(
        geojson
    )


    if not label_df.empty:

        label_df[
            "label_name"
        ] = label_df[
            "feature_id"
        ]


        analysis_labels = label_df[
            ~label_df[
                "feature_id"
            ].isin(
                SEOUL_EXISTING_REGULATED
            )
        ]


        existing_labels = label_df[
            label_df[
                "feature_id"
            ].isin(
                SEOUL_EXISTING_REGULATED
            )
        ]


        fig.add_trace(

            go.Scattergeo(

                lon=analysis_labels[
                    "label_lon"
                ],

                lat=analysis_labels[
                    "label_lat"
                ],

                text=analysis_labels[
                    "label_name"
                ],

                mode="text",

                textfont=dict(
                    size=10,
                    color="#222222"
                ),

                hoverinfo="skip",

                showlegend=False
            )
        )


        fig.add_trace(

            go.Scattergeo(

                lon=existing_labels[
                    "label_lon"
                ],

                lat=existing_labels[
                    "label_lat"
                ],

                text=existing_labels[
                    "label_name"
                ],

                mode="text",

                textfont=dict(
                    size=11,
                    color="white"
                ),

                hoverinfo="skip",

                showlegend=False
            )
        )


    # --------------------------------------------------------
    # 지도 스타일
    # --------------------------------------------------------

    fig.update_geos(

        fitbounds="locations",

        visible=False,

        projection_type="mercator"
    )


    fig.update_layout(

        height=650,

        paper_bgcolor="white",

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        )
    )


    return fig


# ============================================================
# 11. 경기도 지도
# ============================================================

def make_gyeonggi_map(
    summary,
    geojson,
    metric_col,
    metric_name
):

    map_df = summary.copy()


    map_df["lawd_cd"] = (

        map_df["lawd_cd"]

        .astype(str)

        .str.zfill(5)
    )


    map_df[metric_col] = (
        pd.to_numeric(
            map_df[metric_col],
            errors="coerce"
        )
    )


    valid_values = (

        map_df[
            metric_col
        ]

        .dropna()

        .abs()
    )


    if len(valid_values) > 0:

        max_abs = max(
            valid_values.max(),
            1
        )

    else:

        max_abs = 1


    # --------------------------------------------------------
    # GeoJSON 전체 feature ID
    # --------------------------------------------------------

    all_ids = [

        str(
            feature.get(
                "id",
                ""
            )
        )

        for feature
        in geojson.get(
            "features",
            []
        )
    ]


    regulated_ids = set(

        map_df[
            "lawd_cd"
        ].tolist()
    )


    unregulated_ids = [

        code

        for code in all_ids

        if code not in regulated_ids
    ]


    fig = go.Figure()


    # --------------------------------------------------------
    # 비규제 지역
    # --------------------------------------------------------

    if len(
        unregulated_ids
    ) > 0:

        fig.add_trace(

            go.Choropleth(

                geojson=geojson,

                locations=(
                    unregulated_ids
                ),

                z=[
                    1
                ] * len(
                    unregulated_ids
                ),

                featureidkey="id",

                colorscale=[

                    [0, "#e5e5e5"],
                    [1, "#e5e5e5"]
                ],

                showscale=False,

                marker_line_color=(
                    "white"
                ),

                marker_line_width=0.7,

                hoverinfo="skip"
            )
        )


    # --------------------------------------------------------
    # 12개 신규 규제지역
    # --------------------------------------------------------

    custom_data = np.column_stack(
        [

            map_df[
                "before_count"
            ],

            map_df[
                "after_count"
            ],

            map_df[
                "before_daily_avg"
            ],

            map_df[
                "after_daily_avg"
            ],

            map_df[
                metric_col
            ]
        ]
    )


    fig.add_trace(

        go.Choropleth(

            geojson=geojson,

            locations=map_df[
                "lawd_cd"
            ],

            z=map_df[
                metric_col
            ],

            text=map_df[
                "region"
            ],

            featureidkey="id",

            zmin=-max_abs,

            zmax=max_abs,

            zmid=0,

            colorscale=(
                CHANGE_COLORSCALE
            ),

            marker_line_color=(
                "white"
            ),

            marker_line_width=1.4,

            colorbar=dict(

                title=metric_name,

                thickness=13,

                len=0.55
            ),

            customdata=custom_data,

            hovertemplate=(

                "<b>%{text}</b>"
                "<br><br>"

                "정책 이전 거래량: "
                "%{customdata[0]:,.0f}건"
                "<br>"

                "정책 이후 거래량: "
                "%{customdata[1]:,.0f}건"
                "<br>"

                "정책 이전 일평균: "
                "%{customdata[2]:.2f}건"
                "<br>"

                "정책 이후 일평균: "
                "%{customdata[3]:.2f}건"
                "<br>"

                f"{metric_name}: "
                "%{customdata[4]:.2f}"

                "<extra></extra>"
            )
        )
    )


    # --------------------------------------------------------
    # 규제지역 라벨
    # --------------------------------------------------------

    label_df = get_geo_label_data(
        geojson
    )


    if not label_df.empty:

        label_df[
            "feature_id"
        ] = (

            label_df[
                "feature_id"
            ]

            .astype(str)

            .str.zfill(5)
        )


        region_lookup = dict(

            zip(

                map_df[
                    "lawd_cd"
                ],

                map_df[
                    "region"
                ]
            )
        )


        label_df = label_df[

            label_df[
                "feature_id"
            ].isin(
                regulated_ids
            )

        ].copy()


        label_df[
            "label_name"
        ] = (

            label_df[
                "feature_id"
            ]

            .map(
                region_lookup
            )
        )


        if len(label_df) > 0:

            fig.add_trace(

                go.Scattergeo(

                    lon=label_df[
                        "label_lon"
                    ],

                    lat=label_df[
                        "label_lat"
                    ],

                    text=label_df[
                        "label_name"
                    ],

                    mode="text",

                    textfont=dict(
                        size=9,
                        color="#222222"
                    ),

                    hoverinfo="skip",

                    showlegend=False
                )
            )


    fig.update_geos(

        fitbounds="locations",

        visible=False,

        projection_type="mercator"
    )


    fig.update_layout(

        height=650,

        paper_bgcolor="white",

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        )
    )


    return fig


# ============================================================
# 12. 정책 기준선 추가 함수
#
# add_vline 날짜 오류를 피하기 위해
# add_shape + add_annotation 사용
# ============================================================

def add_policy_line(
    fig,
    text="2025.10.15 정책 발표"
):

    fig.add_shape(

        type="line",

        x0=POLICY_DATE,
        x1=POLICY_DATE,

        y0=0,
        y1=1,

        xref="x",
        yref="paper",

        line=dict(
            dash="dash",
            width=2,
            color="#333333"
        )
    )


    fig.add_annotation(

        x=POLICY_DATE,

        y=1,

        xref="x",
        yref="paper",

        text=text,

        showarrow=False,

        xanchor="left",
        yanchor="bottom",

        font=dict(
            size=11
        )
    )


    return fig


# ============================================================
# 13. 전체 일별 거래량 그래프
# ============================================================

def make_daily_chart(
    daily,
    title
):

    fig = go.Figure()


    fig.add_trace(

        go.Scatter(

            x=daily[
                "deal_date"
            ],

            y=daily[
                "transaction_count"
            ],

            mode="lines",

            name="일별 거래량",

            line=dict(
                width=1
            ),

            opacity=0.25
        )
    )


    fig.add_trace(

        go.Scatter(

            x=daily[
                "deal_date"
            ],

            y=daily[
                "rolling_14d"
            ],

            mode="lines",

            name="14일 이동평균",

            line=dict(
                width=3
            )
        )
    )


    fig = add_policy_line(
        fig,
        "10·15 대책"
    )


    fig.update_layout(

        title=title,

        template="simple_white",

        xaxis_title="계약일",

        yaxis_title="거래건수",

        hovermode="x unified",

        height=440,

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )


    return fig


# ============================================================
# 14. 지역 상세 일별 데이터
#
# 거래 없는 날짜도 0건으로 채운 후
# 14일 이동평균을 다시 계산
# ============================================================

def prepare_region_daily(
    district_daily,
    selected_region
):

    temp = district_daily[

        district_daily[
            "region"
        ] == selected_region

    ][
        [
            "deal_date",
            "transaction_count"
        ]
    ].copy()


    full_dates = pd.DataFrame({

        "deal_date":
            pd.date_range(
                BEFORE_START,
                AFTER_END,
                freq="D"
            )
    })


    temp = full_dates.merge(

        temp,

        on="deal_date",

        how="left"
    )


    temp[
        "transaction_count"
    ] = (

        temp[
            "transaction_count"
        ]

        .fillna(0)
    )


    temp[
        "rolling_14d"
    ] = (

        temp[
            "transaction_count"
        ]

        .rolling(
            window=14,
            center=True,
            min_periods=1
        )

        .mean()
    )


    return temp


# ============================================================
# 15. 변화량 순위 그래프
# ============================================================

def make_ranking_chart(
    summary,
    metric_col,
    metric_name
):

    ranking = (

        summary

        .sort_values(
            metric_col,
            ascending=True
        )
    )


    fig = px.bar(

        ranking,

        x=metric_col,

        y="region",

        orientation="h",

        color=metric_col,

        color_continuous_scale=(
            CHANGE_COLORSCALE
        ),

        color_continuous_midpoint=0,

        text_auto=".1f",

        labels={

            metric_col:
                metric_name,

            "region":
                ""
        }
    )


    fig.add_vline(

        x=0,

        line_dash="dash",

        line_width=1
    )


    fig.update_layout(

        template="simple_white",

        height=650,

        coloraxis_showscale=False,

        margin=dict(
            l=0,
            r=10,
            t=10,
            b=10
        )
    )


    return fig


# ============================================================
# 16. 권역 선택
# ============================================================

with st.sidebar:

    st.title(
        "Dashboard"
    )


    scope = st.radio(

        "분석 권역",

        options=[
            "서울",
            "경기"
        ],

        horizontal=True
    )


    st.divider()


# ============================================================
# 17. 권역별 데이터 연결
# ============================================================

if scope == "서울":

    summary = (
        seoul_summary.copy()
    )

    daily = (
        seoul_daily.copy()
    )

    district_daily = (
        seoul_district_daily.copy()
    )

    monthly = (
        seoul_monthly.copy()
    )

    geojson = (
        seoul_geojson
    )

    scope_title = (
        "서울 신규 규제대상 21개 자치구"
    )

    map_note = (
        "강남·서초·송파·용산은 "
        "기존 규제지역으로 별도 표시"
    )


else:

    summary = (
        gyeonggi_summary.copy()
    )

    daily = (
        gyeonggi_daily.copy()
    )

    district_daily = (
        gyeonggi_district_daily.copy()
    )

    monthly = (
        gyeonggi_monthly.copy()
    )

    geojson = (
        gyeonggi_geojson
    )

    scope_title = (
        "경기도 신규 규제지역 12개"
    )

    map_note = (
        "회색은 비규제·비분석지역"
    )


# ============================================================
# 18. Sidebar 지역 선택
# ============================================================

with st.sidebar:

    selected_region = st.selectbox(

        "지역 상세보기",

        options=sorted(
            summary[
                "region"
            ].dropna().tolist()
        )
    )


    # 경기도인 경우 도시정보도 표시
    if (
        scope == "경기"
        and
        "parent_city"
        in summary.columns
    ):

        selected_city = (

            summary.loc[
                summary[
                    "region"
                ]
                ==
                selected_region,
                "parent_city"
            ]

            .iloc[0]
        )


        st.caption(
            f"상위 도시 : {selected_city}"
        )


    st.divider()


    st.caption(
        "분석기간"
    )

    st.write(
        "**정책 이전**"
    )

    st.write(
        "2025.04.15 ~ 2025.10.14"
    )

    st.write(
        "**정책 이후**"
    )

    st.write(
        "2025.10.15 ~ 2026.04.14"
    )


# ============================================================
# 19. Header
# ============================================================

st.title(
    "10·15 부동산 규제정책 이후 거래시장 변화"
)

st.caption(
    "2025년 10월 15일 정책 발표 전후 "
    "6개월간 아파트 매매 실거래량 비교"
)


st.markdown(
    f"### {scope_title}"
)


# ============================================================
# 20. 전체 KPI 계산
# ============================================================

total_before = (
    summary[
        "before_count"
    ].sum()
)

total_after = (
    summary[
        "after_count"
    ].sum()
)


before_daily = (
    total_before
    / BEFORE_DAYS
)

after_daily = (
    total_after
    / AFTER_DAYS
)


overall_change_pct = (

    (
        after_daily
        -
        before_daily
    )

    /
    before_daily

    * 100
)


largest_drop = (

    summary

    .sort_values(
        "daily_avg_change_pct"
    )

    .iloc[0]
)


largest_increase = (

    summary

    .sort_values(
        "daily_avg_change_pct",
        ascending=False
    )

    .iloc[0]
)


# ============================================================
# 21. KPI 카드
# ============================================================

kpi1, kpi2, kpi3, kpi4 = (
    st.columns(4)
)


with kpi1:

    st.metric(

        "정책 이전 거래량",

        f"{total_before:,.0f}건",

        help=(
            "2025.04.15~2025.10.14 "
            "전체 거래건수"
        )
    )


with kpi2:

    st.metric(

        "정책 이후 거래량",

        f"{total_after:,.0f}건",

        delta=(
            f"{overall_change_pct:.1f}% "
            "일평균"
        ),

        help=(
            "2025.10.15~2026.04.14 "
            "전체 거래건수"
        )
    )


with kpi3:

    st.metric(

        "거래량 최대 감소",

        largest_drop[
            "region"
        ],

        delta=(
            f"{largest_drop['daily_avg_change_pct']:.1f}%"
        )
    )


with kpi4:

    st.metric(

        "상대적 최대 증가",

        largest_increase[
            "region"
        ],

        delta=(
            f"{largest_increase['daily_avg_change_pct']:.1f}%"
        )
    )


st.divider()


# ============================================================
# 22. Tab 구성
# ============================================================

overview_tab, detail_tab, data_tab = st.tabs(

    [
        "Overview",
        "지역 상세",
        "Data"
    ]
)


# ============================================================
# 23. OVERVIEW
# ============================================================

with overview_tab:


    # --------------------------------------------------------
    # 지도 지표 선택
    # --------------------------------------------------------

    metric_choice = st.radio(

        "지도·순위 지표",

        options=[

            "일평균 거래량 증감률",

            "분석대상 내 거래점유율 변화"
        ],

        horizontal=True
    )


    if metric_choice == (
        "일평균 거래량 증감률"
    ):

        metric_col = (
            "daily_avg_change_pct"
        )

        metric_name = (
            "증감률(%)"
        )


    else:

        metric_col = (
            "share_change_pp"
        )

        metric_name = (
            "점유율 변화(%p)"
        )


    # --------------------------------------------------------
    # 지도 + 순위
    # --------------------------------------------------------

    map_col, rank_col = st.columns(
        [1.45, 1]
    )


    with map_col:

        st.subheader(
            "공간별 거래시장 변화"
        )


        st.caption(
            map_note
        )


        if scope == "서울":

            map_fig = make_seoul_map(

                summary,

                geojson,

                metric_col,

                metric_name
            )


        else:

            map_fig = make_gyeonggi_map(

                summary,

                geojson,

                metric_col,

                metric_name
            )


        st.plotly_chart(

            map_fig,

            use_container_width=True,

            config={
                "displayModeBar": False
            }
        )


    with rank_col:

        st.subheader(
            "지역별 변화 순위"
        )


        rank_fig = make_ranking_chart(

            summary,

            metric_col,

            metric_name
        )


        st.plotly_chart(

            rank_fig,

            use_container_width=True,

            config={
                "displayModeBar": False
            }
        )


    st.divider()


    # --------------------------------------------------------
    # 전체 일별 시계열
    # --------------------------------------------------------

    st.subheader(
        "전체 아파트 매매 거래량 추이"
    )


    daily_fig = make_daily_chart(

        daily,

        (
            f"{scope_title} "
            "일별 거래량 변화"
        )
    )


    st.plotly_chart(

        daily_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


    st.caption(
        "얇은 선은 일별 거래량, "
        "굵은 선은 14일 이동평균입니다."
    )


# ============================================================
# 24. 지역 상세
# ============================================================

with detail_tab:


    st.subheader(
        selected_region
    )


    selected_summary = (

        summary[

            summary[
                "region"
            ]
            ==
            selected_region

        ]

        .iloc[0]
    )


    d1, d2, d3, d4 = (
        st.columns(4)
    )


    with d1:

        st.metric(

            "정책 이전 거래량",

            (
                f"{selected_summary['before_count']:,.0f}건"
            )
        )


    with d2:

        st.metric(

            "정책 이후 거래량",

            (
                f"{selected_summary['after_count']:,.0f}건"
            )
        )


    with d3:

        st.metric(

            "일평균 거래량 변화",

            (
                f"{selected_summary['daily_avg_change_pct']:.1f}%"
            )
        )


    with d4:

        st.metric(

            "거래 점유율 변화",

            (
                f"{selected_summary['share_change_pp']:.2f}%p"
            )
        )


    st.divider()


    # --------------------------------------------------------
    # 지역별 일별 시계열
    # --------------------------------------------------------

    selected_daily = (
        prepare_region_daily(

            district_daily,

            selected_region
        )
    )


    detail_fig = make_daily_chart(

        selected_daily,

        (
            f"{selected_region} "
            "일별 아파트 거래량 변화"
        )
    )


    st.plotly_chart(

        detail_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


    # --------------------------------------------------------
    # 월별 추이 + Before/After
    # --------------------------------------------------------

    left_chart, right_chart = (
        st.columns(
            [1.5, 1]
        )
    )


    with left_chart:

        st.subheader(
            "월별 거래량"
        )


        selected_monthly = (

            monthly[

                monthly[
                    "region"
                ]
                ==
                selected_region

            ]

            .copy()
        )


        monthly_fig = px.line(

            selected_monthly,

            x="year_month",

            y="transaction_count",

            markers=True,

            labels={

                "year_month":
                    "계약연월",

                "transaction_count":
                    "거래건수"
            }
        )


        monthly_fig = add_policy_line(

            monthly_fig,

            "10·15 대책"
        )


        monthly_fig.update_layout(

            template="simple_white",

            height=420,

            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10
            )
        )


        st.plotly_chart(

            monthly_fig,

            use_container_width=True,

            config={
                "displayModeBar": False
            }
        )


        st.caption(
            "2025년 4월과 2026년 4월은 "
            "분석기간 경계 때문에 부분월입니다."
        )


    with right_chart:

        st.subheader(
            "정책 전후 6개월 비교"
        )


        compare_df = pd.DataFrame({

            "기간": [
                "정책 이전",
                "정책 이후"
            ],

            "거래건수": [

                selected_summary[
                    "before_count"
                ],

                selected_summary[
                    "after_count"
                ]
            ]
        })


        compare_fig = px.bar(

            compare_df,

            x="기간",

            y="거래건수",

            text_auto=",",

            labels={
                "거래건수":
                    "거래건수"
            }
        )


        compare_fig.update_layout(

            template="simple_white",

            showlegend=False,

            height=420,

            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10
            )
        )


        st.plotly_chart(

            compare_fig,

            use_container_width=True,

            config={
                "displayModeBar": False
            }
        )


# ============================================================
# 25. DATA
# ============================================================

with data_tab:


    st.subheader(
        f"{scope_title} 분석 데이터"
    )


    show_columns = [

        "region",
        "before_count",
        "after_count",
        "before_daily_avg",
        "after_daily_avg",
        "daily_avg_change_pct",
        "before_share_pct",
        "after_share_pct",
        "share_change_pp"
    ]


    if (
        scope == "경기"
        and
        "parent_city"
        in summary.columns
    ):

        show_columns.insert(
            1,
            "parent_city"
        )


    data_view = (

        summary[
            show_columns
        ]

        .sort_values(
            "daily_avg_change_pct"
        )

        .reset_index(
            drop=True
        )
    )


    st.dataframe(

        data_view,

        use_container_width=True,

        hide_index=True,

        column_config={

            "region":
                "지역",

            "parent_city":
                "상위 도시",

            "before_count":
                st.column_config.NumberColumn(
                    "정책 이전 거래량",
                    format="%d건"
                ),

            "after_count":
                st.column_config.NumberColumn(
                    "정책 이후 거래량",
                    format="%d건"
                ),

            "before_daily_avg":
                st.column_config.NumberColumn(
                    "정책 이전 일평균",
                    format="%.2f"
                ),

            "after_daily_avg":
                st.column_config.NumberColumn(
                    "정책 이후 일평균",
                    format="%.2f"
                ),

            "daily_avg_change_pct":
                st.column_config.NumberColumn(
                    "일평균 증감률",
                    format="%.1f%%"
                ),

            "before_share_pct":
                st.column_config.NumberColumn(
                    "정책 이전 점유율",
                    format="%.2f%%"
                ),

            "after_share_pct":
                st.column_config.NumberColumn(
                    "정책 이후 점유율",
                    format="%.2f%%"
                ),

            "share_change_pp":
                st.column_config.NumberColumn(
                    "점유율 변화",
                    format="%.2f%%p"
                )
        }
    )


    # --------------------------------------------------------
    # CSV 다운로드
    # --------------------------------------------------------

    csv_data = (

        data_view

        .to_csv(
            index=False
        )

        .encode(
            "utf-8-sig"
        )
    )


    st.download_button(

        label="분석 결과 CSV 다운로드",

        data=csv_data,

        file_name=(

            "seoul_policy_summary.csv"

            if scope == "서울"

            else
            "gyeonggi_policy_summary.csv"
        ),

        mime="text/csv"
    )


# ============================================================
# 26. 분석 설명
# ============================================================

st.divider()


with st.expander(
    "분석 기준 및 해석 시 유의사항"
):

    st.markdown(
        """
        **분석 기준**

        - 정책 기준일: 2025년 10월 15일
        - 정책 이전: 2025년 4월 15일 ~ 2025년 10월 14일
        - 정책 이후: 2025년 10월 15일 ~ 2026년 4월 14일
        - 분석 대상: 아파트 매매 실거래
        - 거래량 증감률은 두 기간의 일수 차이를 보정하기 위해
          일평균 거래건수를 기준으로 계산했습니다.

        **서울**

        강남구·서초구·송파구·용산구는 기존 규제지역으로
        이번 신규 규제지역 거래량 변화 분석에서 제외했습니다.

        **경기**

        2025년 10월 15일 신규 규제지역으로 지정된
        12개 시·구를 분석했습니다.

        **주의**

        본 대시보드는 정책 발표 전후 거래량의 변화 패턴을
        시각화한 기술적 분석입니다.
        거래량 변화 전체를 정책의 인과효과로 해석해서는 안 됩니다.
        """
    )


st.caption(
    "Data: 국토교통부 아파트 매매 실거래가 자료 · "
    "분석기간 2025.04.15–2026.04.14"
)

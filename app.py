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

    # ========================================================
    # 1. 지도에 사용할 데이터 준비
    # ========================================================

    map_df = summary.copy()


    # 시각화할 지표를 숫자형으로 변환
    map_df[metric_col] = pd.to_numeric(
        map_df[metric_col],
        errors="coerce"
    )


    # ========================================================
    # 2. 색상 범위 설정
    #
    # 감소(-)와 증가(+)를 0 기준으로 대칭 표현
    # ========================================================

    valid_values = (
        map_df[metric_col]
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


    # ========================================================
    # 3. Figure 생성
    # ========================================================

    fig = go.Figure()


    # ========================================================
    # 4. 2025.10.15 신규 규제지역 21개
    # ========================================================

    custom_data = np.column_stack(
        [
            map_df["before_count"],
            map_df["after_count"],
            map_df["before_daily_avg"],
            map_df["after_daily_avg"],
            map_df[metric_col]
        ]
    )


    fig.add_trace(

        go.Choropleth(

            geojson=geojson,

            # 서울 GeoJSON의 feature id가
            # 자치구명으로 저장되어 있으므로 region 사용
            locations=map_df["region"],

            z=map_df[metric_col],

            featureidkey="id",

            # ------------------------------------------------
            # 0을 중심으로 색상 범위 대칭 설정
            # ------------------------------------------------

            zmin=-max_abs,

            zmax=max_abs,

            zmid=0,

            colorscale=CHANGE_COLORSCALE,

            # 자치구 일반 경계
            marker_line_color="white",

            marker_line_width=1.2,

            # 범례
            colorbar=dict(

                title=metric_name,

                thickness=13,

                len=0.55
            ),

            customdata=custom_data,

            # ------------------------------------------------
            # Hover 정보
            # ------------------------------------------------

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


    # ========================================================
    # 5. 기존 규제지역 4개
    #
    # 강남구
    # 서초구
    # 송파구
    # 용산구
    #
    # 데이터 색상과 혼동하지 않도록
    # 회색 면 + 노란색 굵은 경계선으로 표시
    # ========================================================

    fig.add_trace(

        go.Choropleth(

            geojson=geojson,

            locations=SEOUL_EXISTING_REGULATED,

            z=[
                1,
                1,
                1,
                1
            ],

            featureidkey="id",

            # ------------------------------------------------
            # 내부 색상은 회색
            #
            # 빨강을 사용하면
            # "거래량 감소지역"과 혼동될 수 있으므로
            # 회색으로 구분
            # ------------------------------------------------

            colorscale=[
                [0, "#D9D9D9"],
                [1, "#D9D9D9"]
            ],

            showscale=False,

            # ------------------------------------------------
            # 핵심 수정
            # 기존 규제지역 = 노란색 경계선
            # ------------------------------------------------

            marker_line_color="#FFD400",

            marker_line_width=4,

            name="기존 규제지역",

            hovertemplate=(

                "<b>%{location}</b>"
                "<br><br>"

                "10·15 대책 이전 기존 규제지역"
                "<br>"

                "이번 거래량 변화 분석에서는 제외"

                "<extra></extra>"
            )
        )
    )


    # ========================================================
    # 6. 지도 라벨 데이터 가져오기
    # ========================================================

    label_df = get_geo_label_data(
        geojson
    )


    if not label_df.empty:


        # GeoJSON의 feature id가 자치구명
        label_df["label_name"] = (
            label_df["feature_id"]
        )


        # ----------------------------------------------------
        # 신규 규제지역 21개
        # ----------------------------------------------------

        analysis_labels = label_df[

            ~label_df[
                "feature_id"
            ].isin(
                SEOUL_EXISTING_REGULATED
            )

        ].copy()


        # ----------------------------------------------------
        # 기존 규제지역 4개
        # ----------------------------------------------------

        existing_labels = label_df[

            label_df[
                "feature_id"
            ].isin(
                SEOUL_EXISTING_REGULATED
            )

        ].copy()


        # ====================================================
        # 7. 신규 규제지역 자치구 이름 표시
        # ====================================================

        if not analysis_labels.empty:

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


        # ====================================================
        # 8. 기존 규제지역 이름 표시
        # ====================================================

        if not existing_labels.empty:

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

                        # 회색 내부이므로
                        # 검정 계열 글씨 사용
                        color="#333333",

                        family="Arial Black"
                    ),

                    hoverinfo="skip",

                    showlegend=False
                )
            )


    # ========================================================
    # 9. 지도 범위 설정
    # ========================================================

    fig.update_geos(

        fitbounds="locations",

        visible=False,

        projection_type="mercator"
    )


    # ========================================================
    # 10. 지도 Layout
    # ========================================================

    fig.update_layout(

        height=650,

        paper_bgcolor="white",

        margin=dict(
            l=0,
            r=0,
            t=10,
            b=0
        ),

        showlegend=False
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
# 16. 통합 Dashboard
# 서울 + 경기를 한 페이지에서 동시에 표시
# ============================================================


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "10·15 Policy Dashboard"
    )

    st.caption(
        "서울·경기 아파트 거래시장 변화"
    )

    st.divider()


    # --------------------------------------------------------
    # 서울 상세지역 선택
    # --------------------------------------------------------

    st.subheader(
        "서울 상세지역"
    )

    selected_seoul = st.selectbox(

        "서울 자치구",

        options=sorted(

            seoul_summary[
                "region"
            ]

            .dropna()

            .tolist()
        ),

        key="selected_seoul"
    )


    st.divider()


    # --------------------------------------------------------
    # 경기 상세지역 선택
    # --------------------------------------------------------

    st.subheader(
        "경기 상세지역"
    )

    selected_gyeonggi = st.selectbox(

        "경기 시·구",

        options=sorted(

            gyeonggi_summary[
                "region"
            ]

            .dropna()

            .tolist()
        ),

        key="selected_gyeonggi"
    )


    st.divider()


    # --------------------------------------------------------
    # 분석기간
    # --------------------------------------------------------

    st.caption(
        "분석기간"
    )

    st.markdown(
        """
        **정책 이전**  
        2025.04.15 ~ 2025.10.14

        **정책 발표일**  
        2025.10.15

        **정책 이후**  
        2025.10.15 ~ 2026.04.14
        """
    )


# ============================================================
# HEADER
# ============================================================

st.title(
    "10·15 부동산 규제정책 이후 거래시장 변화"
)

st.caption(
    "2025년 10월 15일 정책 발표 전후 "
    "6개월간 서울 및 경기 신규 규제지역 "
    "아파트 매매 실거래량 비교"
)


# ============================================================
# 지도 분석지표 선택
# ============================================================

metric_choice = st.radio(

    "지도 및 지역 순위 지표",

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


st.divider()


# ============================================================
# 17. 서울 KPI 계산
# ============================================================

seoul_total_before = (

    seoul_summary[
        "before_count"
    ].sum()
)


seoul_total_after = (

    seoul_summary[
        "after_count"
    ].sum()
)


seoul_before_daily = (

    seoul_total_before

    / BEFORE_DAYS
)


seoul_after_daily = (

    seoul_total_after

    / AFTER_DAYS
)


seoul_change_pct = (

    (
        seoul_after_daily
        -
        seoul_before_daily
    )

    /
    seoul_before_daily

    * 100
)


seoul_largest_drop = (

    seoul_summary

    .sort_values(
        "daily_avg_change_pct"
    )

    .iloc[0]
)


# ============================================================
# 18. 경기 KPI 계산
# ============================================================

gg_total_before = (

    gyeonggi_summary[
        "before_count"
    ].sum()
)


gg_total_after = (

    gyeonggi_summary[
        "after_count"
    ].sum()
)


gg_before_daily = (

    gg_total_before

    / BEFORE_DAYS
)


gg_after_daily = (

    gg_total_after

    / AFTER_DAYS
)


gg_change_pct = (

    (
        gg_after_daily
        -
        gg_before_daily
    )

    /
    gg_before_daily

    * 100
)


gg_largest_drop = (

    gyeonggi_summary

    .sort_values(
        "daily_avg_change_pct"
    )

    .iloc[0]
)


# ============================================================
# 19. 서울 KPI
# ============================================================

st.subheader(
    "서울 신규 규제지역"
)


s1, s2, s3, s4 = st.columns(
    4
)


with s1:

    st.metric(

        "정책 이전 거래량",

        f"{seoul_total_before:,.0f}건"
    )


with s2:

    st.metric(

        "정책 이후 거래량",

        f"{seoul_total_after:,.0f}건"
    )


with s3:

    st.metric(

        "일평균 거래량 변화",

        f"{seoul_change_pct:.1f}%",

        delta=f"{seoul_change_pct:.1f}%"
    )


with s4:

    st.metric(

        "거래량 최대 감소",

        seoul_largest_drop[
            "region"
        ],

        delta=(

            f"{seoul_largest_drop['daily_avg_change_pct']:.1f}%"
        )
    )


# ============================================================
# 20. 경기 KPI
# ============================================================

st.subheader(
    "경기도 신규 규제지역"
)


g1, g2, g3, g4 = st.columns(
    4
)


with g1:

    st.metric(

        "정책 이전 거래량",

        f"{gg_total_before:,.0f}건"
    )


with g2:

    st.metric(

        "정책 이후 거래량",

        f"{gg_total_after:,.0f}건"
    )


with g3:

    st.metric(

        "일평균 거래량 변화",

        f"{gg_change_pct:.1f}%",

        delta=f"{gg_change_pct:.1f}%"
    )


with g4:

    st.metric(

        "거래량 최대 감소",

        gg_largest_drop[
            "region"
        ],

        delta=(

            f"{gg_largest_drop['daily_avg_change_pct']:.1f}%"
        )
    )


st.divider()


# ============================================================
# 21. 서울 + 경기 지도 동시 표시
# ============================================================

st.header(
    "공간별 거래시장 변화"
)


st.caption(
    "붉은색은 거래량 감소, "
    "파란색은 거래량 증가를 의미합니다. "
    "서울의 노란색 테두리는 10·15 대책 이전부터 "
    "규제지역이었던 강남·서초·송파·용산입니다."
)


map_left, map_right = st.columns(
    [1, 1]
)


# ------------------------------------------------------------
# 서울 지도
# ------------------------------------------------------------

with map_left:

    st.subheader(
        "서울"
    )

    st.caption(
        "21개 신규 규제지역 / "
        "노란 테두리 = 기존 규제지역"
    )


    seoul_map_fig = make_seoul_map(

        seoul_summary,

        seoul_geojson,

        metric_col,

        metric_name
    )


    st.plotly_chart(

        seoul_map_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


# ------------------------------------------------------------
# 경기 지도
# ------------------------------------------------------------

with map_right:

    st.subheader(
        "경기도"
    )

    st.caption(
        "색상지역 = 10·15 신규 규제지역 / "
        "회색 = 비규제·비분석지역"
    )


    gyeonggi_map_fig = (
        make_gyeonggi_map(

            gyeonggi_summary,

            gyeonggi_geojson,

            metric_col,

            metric_name
        )
    )


    st.plotly_chart(

        gyeonggi_map_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


st.divider()


# ============================================================
# 22. 지역별 변화 순위
# ============================================================

st.header(
    "지역별 거래시장 변화 순위"
)


rank_left, rank_right = st.columns(
    [1, 1]
)


# ------------------------------------------------------------
# 서울 순위
# ------------------------------------------------------------

with rank_left:

    st.subheader(
        "서울"
    )


    seoul_rank_fig = (

        make_ranking_chart(

            seoul_summary,

            metric_col,

            metric_name
        )
    )


    seoul_rank_fig.update_layout(
        height=650
    )


    st.plotly_chart(

        seoul_rank_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


# ------------------------------------------------------------
# 경기 순위
# ------------------------------------------------------------

with rank_right:

    st.subheader(
        "경기도"
    )


    gg_rank_fig = (

        make_ranking_chart(

            gyeonggi_summary,

            metric_col,

            metric_name
        )
    )


    gg_rank_fig.update_layout(
        height=650
    )


    st.plotly_chart(

        gg_rank_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


st.divider()


# ============================================================
# 23. 서울 + 경기 전체 일별 거래량
# ============================================================

st.header(
    "정책 발표 전후 거래량 추이"
)


trend_left, trend_right = st.columns(
    [1, 1]
)


# ------------------------------------------------------------
# 서울 전체
# ------------------------------------------------------------

with trend_left:

    seoul_daily_fig = (

        make_daily_chart(

            seoul_daily,

            "서울 신규 규제지역 일별 거래량"
        )
    )


    st.plotly_chart(

        seoul_daily_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


# ------------------------------------------------------------
# 경기 전체
# ------------------------------------------------------------

with trend_right:

    gg_daily_fig = (

        make_daily_chart(

            gyeonggi_daily,

            "경기 신규 규제지역 일별 거래량"
        )
    )


    st.plotly_chart(

        gg_daily_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


st.caption(
    "얇은 선 = 일별 거래량 / "
    "굵은 선 = 14일 이동평균"
)


st.divider()


# ============================================================
# 24. 지역 상세 분석
# ============================================================

st.header(
    "지역 상세 비교"
)


detail_left, detail_right = st.columns(
    [1, 1]
)


# ============================================================
# 서울 상세
# ============================================================

with detail_left:

    st.subheader(
        f"서울 · {selected_seoul}"
    )


    selected_seoul_summary = (

        seoul_summary[

            seoul_summary[
                "region"
            ]
            ==
            selected_seoul

        ]

        .iloc[0]
    )


    ss1, ss2, ss3 = st.columns(
        3
    )


    with ss1:

        st.metric(

            "정책 이전",

            (
                f"{selected_seoul_summary['before_count']:,.0f}건"
            )
        )


    with ss2:

        st.metric(

            "정책 이후",

            (
                f"{selected_seoul_summary['after_count']:,.0f}건"
            )
        )


    with ss3:

        st.metric(

            "일평균 증감률",

            (
                f"{selected_seoul_summary['daily_avg_change_pct']:.1f}%"
            )
        )


    selected_seoul_daily = (

        prepare_region_daily(

            seoul_district_daily,

            selected_seoul
        )
    )


    selected_seoul_fig = (

        make_daily_chart(

            selected_seoul_daily,

            f"{selected_seoul} 거래량"
        )
    )


    st.plotly_chart(

        selected_seoul_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


# ============================================================
# 경기 상세
# ============================================================

with detail_right:

    st.subheader(
        f"경기 · {selected_gyeonggi}"
    )


    selected_gg_summary = (

        gyeonggi_summary[

            gyeonggi_summary[
                "region"
            ]
            ==
            selected_gyeonggi

        ]

        .iloc[0]
    )


    gs1, gs2, gs3 = st.columns(
        3
    )


    with gs1:

        st.metric(

            "정책 이전",

            (
                f"{selected_gg_summary['before_count']:,.0f}건"
            )
        )


    with gs2:

        st.metric(

            "정책 이후",

            (
                f"{selected_gg_summary['after_count']:,.0f}건"
            )
        )


    with gs3:

        st.metric(

            "일평균 증감률",

            (
                f"{selected_gg_summary['daily_avg_change_pct']:.1f}%"
            )
        )


    selected_gg_daily = (

        prepare_region_daily(

            gyeonggi_district_daily,

            selected_gyeonggi
        )
    )


    selected_gg_fig = (

        make_daily_chart(

            selected_gg_daily,

            f"{selected_gyeonggi} 거래량"
        )
    )


    st.plotly_chart(

        selected_gg_fig,

        use_container_width=True,

        config={
            "displayModeBar": False
        }
    )


st.divider()


# ============================================================
# 25. 정책 전후 지역별 거래량 비교
# ============================================================

st.header(
    "정책 전후 거래량 직접 비교"
)


compare_left, compare_right = st.columns(
    [1, 1]
)


# ------------------------------------------------------------
# 서울
# ------------------------------------------------------------

with compare_left:

    seoul_compare = (

        seoul_summary[
            [
                "region",
                "before_count",
                "after_count"
            ]
        ]

        .melt(

            id_vars="region",

            value_vars=[
                "before_count",
                "after_count"
            ],

            var_name="period",

            value_name="transaction_count"
        )
    )


    seoul_compare[
        "period"
    ] = (

        seoul_compare[
            "period"
        ]

        .replace({

            "before_count":
                "정책 이전",

            "after_count":
                "정책 이후"
        })
    )


    fig_seoul_compare = px.bar(

        seoul_compare,

        y="region",

        x="transaction_count",

        color="period",

        orientation="h",

        barmode="group",

        title="서울",

        labels={

            "region":
                "",

            "transaction_count":
                "거래건수",

            "period":
                "기간"
        }
    )


    fig_seoul_compare.update_layout(

        template="simple_white",

        height=750
    )


    st.plotly_chart(

        fig_seoul_compare,

        use_container_width=True
    )


# ------------------------------------------------------------
# 경기
# ------------------------------------------------------------

with compare_right:

    gg_compare = (

        gyeonggi_summary[
            [
                "region",
                "before_count",
                "after_count"
            ]
        ]

        .melt(

            id_vars="region",

            value_vars=[
                "before_count",
                "after_count"
            ],

            var_name="period",

            value_name="transaction_count"
        )
    )


    gg_compare[
        "period"
    ] = (

        gg_compare[
            "period"
        ]

        .replace({

            "before_count":
                "정책 이전",

            "after_count":
                "정책 이후"
        })
    )


    fig_gg_compare = px.bar(

        gg_compare,

        y="region",

        x="transaction_count",

        color="period",

        orientation="h",

        barmode="group",

        title="경기도",

        labels={

            "region":
                "",

            "transaction_count":
                "거래건수",

            "period":
                "기간"
        }
    )


    fig_gg_compare.update_layout(

        template="simple_white",

        height=750
    )


    st.plotly_chart(

        fig_gg_compare,

        use_container_width=True
    )


st.divider()


# ============================================================
# 26. 데이터 테이블
# ============================================================

with st.expander(
    "분석 데이터 확인"
):

    data_left, data_right = (
        st.columns(2)
    )


    with data_left:

        st.subheader(
            "서울"
        )


        st.dataframe(

            seoul_summary[
                [
                    "region",
                    "before_count",
                    "after_count",
                    "before_daily_avg",
                    "after_daily_avg",
                    "daily_avg_change_pct",
                    "share_change_pp"
                ]
            ]

            .sort_values(
                "daily_avg_change_pct"
            ),

            use_container_width=True,

            hide_index=True
        )


    with data_right:

        st.subheader(
            "경기도"
        )


        gg_columns = [

            "region",
            "before_count",
            "after_count",
            "before_daily_avg",
            "after_daily_avg",
            "daily_avg_change_pct",
            "share_change_pp"
        ]


        if (
            "parent_city"
            in
            gyeonggi_summary.columns
        ):

            gg_columns.insert(
                1,
                "parent_city"
            )


        st.dataframe(

            gyeonggi_summary[
                gg_columns
            ]

            .sort_values(
                "daily_avg_change_pct"
            ),

            use_container_width=True,

            hide_index=True
        )


# ============================================================
# 27. 분석 설명
# ============================================================

st.divider()


with st.expander(
    "분석 기준 및 해석 시 유의사항"
):

    st.markdown(
        """
        ### 분석기간

        - **정책 이전**  
          2025.04.15 ~ 2025.10.14

        - **정책 기준일**  
          2025.10.15

        - **정책 이후**  
          2025.10.15 ~ 2026.04.14


        ### 서울

        강남구·서초구·송파구·용산구는
        10·15 대책 이전의 기존 규제지역이므로
        신규 규제지역 거래량 변화 분석에서는 제외했습니다.

        지도에서는 해당 4개 자치구를
        **노란색 경계선**으로 표시했습니다.


        ### 경기도

        2025년 10월 15일 신규 규제지역으로 지정된
        12개 시·구의 거래량 변화를 분석합니다.


        ### 해석 주의

        본 분석은 정책 발표 전후의 거래량 변화를
        비교한 기술적 분석입니다.

        거래량 변화 전체를 정책의 인과효과로
        해석해서는 안 됩니다.
        """
    )


st.caption(
    "Data: 국토교통부 아파트 매매 실거래가 자료"
)

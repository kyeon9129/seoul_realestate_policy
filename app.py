# ============================================================
# app.py
# ============================================================

import json

import numpy as np
import pandas as pd

import streamlit as st

import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(

    page_title=(
        "서울 부동산 정책 대시보드"
    ),

    page_icon="🏙️",

    layout="wide",

    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1 {
        font-weight: 750;
        letter-spacing: -1.5px;
    }

    h2, h3 {
        letter-spacing: -0.6px;
    }

    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        padding: 18px;
    }

    [data-testid="stSidebar"] {
        background-color: #fafafa;
    }

    </style>
    """,

    unsafe_allow_html=True
)


# ============================================================
# 데이터 로딩
# ============================================================

@st.cache_data
def load_data():

    summary = pd.read_csv(
        "data/seoul_policy_summary.csv"
    )

    daily = pd.read_csv(
        "data/seoul_daily_transactions.csv"
    )

    district_daily = pd.read_csv(
        "data/seoul_district_daily.csv"
    )

    monthly = pd.read_csv(
        "data/seoul_monthly_transactions.csv"
    )


    daily["deal_date"] = pd.to_datetime(
        daily["deal_date"]
    )

    district_daily["deal_date"] = pd.to_datetime(
        district_daily["deal_date"]
    )

    monthly["year_month"] = pd.to_datetime(
        monthly["year_month"]
    )


    with open(

        "data/seoul_policy_map.geojson",

        "r",

        encoding="utf-8"

    ) as f:

        geojson = json.load(f)


    return (
        summary,
        daily,
        district_daily,
        monthly,
        geojson
    )


(
    summary,
    daily,
    district_daily,
    monthly,
    geojson
) = load_data()

# ============================================================
# GeoJSON 속성 → DataFrame
# ============================================================

map_rows = []


for feature in geojson["features"]:

    prop = feature[
        "properties"
    ].copy()

    prop["district"] = (
        feature["id"]
    )

    map_rows.append(
        prop
    )


map_df = pd.DataFrame(
    map_rows
)


EXISTING_REGULATED = [

    "강남구",
    "서초구",
    "송파구",
    "용산구"
]

# ============================================================
# 서울 지도 함수
# ============================================================

def make_seoul_map(
    metric_col,
    metric_name
):

    analysis_map = map_df[

        ~map_df[
            "district"
        ].isin(
            EXISTING_REGULATED
        )

    ].copy()


    existing_map = map_df[

        map_df[
            "district"
        ].isin(
            EXISTING_REGULATED
        )

    ].copy()


    analysis_map[
        metric_col
    ] = pd.to_numeric(

        analysis_map[
            metric_col
        ],

        errors="coerce"
    )


    max_abs = np.nanmax(

        np.abs(
            analysis_map[
                metric_col
            ]
        )
    )


    max_abs = max(
        max_abs,
        1
    )


    fig = go.Figure()


    # --------------------------------------------------------
    # 신규 규제지역
    # --------------------------------------------------------

    fig.add_trace(

        go.Choropleth(

            geojson=geojson,

            locations=analysis_map[
                "district"
            ],

            z=analysis_map[
                metric_col
            ],

            featureidkey="id",

            zmin=-max_abs,

            zmax=max_abs,

            zmid=0,

            colorscale=[

                [0, "#9c0000"],

                [0.25, "#d6604d"],

                [0.5, "#f7f7f7"],

                [0.75, "#4393c3"],

                [1, "#2166ac"]
            ],

            marker_line_color="white",

            marker_line_width=1,

            colorbar=dict(

                title=metric_name,

                thickness=12
            ),

            hovertemplate=(

                "<b>%{location}</b><br>"

                f"{metric_name}: "

                "%{z:.1f}"

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

            locations=existing_map[
                "district"
            ],

            z=[
                1
            ] * len(
                existing_map
            ),

            featureidkey="id",

            colorscale=[

                [0, "#aa0000"],
                [1, "#aa0000"]
            ],

            showscale=False,

            marker_line_color="white",

            marker_line_width=1.8,

            hovertemplate=(

                "<b>%{location}</b><br>"

                "기존 규제지역"

                "<extra></extra>"
            )
        )
    )


    # --------------------------------------------------------
    # 신규지역 이름
    # --------------------------------------------------------

    fig.add_trace(

        go.Scattergeo(

            lon=analysis_map[
                "label_lon"
            ],

            lat=analysis_map[
                "label_lat"
            ],

            text=analysis_map[
                "district"
            ],

            mode="text",

            textfont=dict(

                size=10,

                color="#222"
            ),

            hoverinfo="skip",

            showlegend=False
        )
    )


    # --------------------------------------------------------
    # 기존지역 이름
    # --------------------------------------------------------

    fig.add_trace(

        go.Scattergeo(

            lon=existing_map[
                "label_lon"
            ],

            lat=existing_map[
                "label_lat"
            ],

            text=existing_map[
                "district"
            ],

            mode="text",

            textfont=dict(

                size=12,

                color="white"
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

        margin=dict(
            l=0,
            r=0,
            t=20,
            b=0
        ),

        height=630,

        paper_bgcolor="white"
    )


    return fig

# ============================================================
# HEADER
# ============================================================

st.title(
    "서울 부동산 규제정책 거래시장 변화"
)

st.caption(
    "2025.10.15 주택시장 안정화 대책 전후 "
    "서울 아파트 거래량 분석"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "Dashboard Controls"
    )


    selected_district = st.selectbox(

        "자치구 선택",

        options=sorted(
            summary["region"].tolist()
        ),

        index=0
    )


    st.divider()


    st.caption(
        "분석기간"
    )

    st.write(
        "정책 이전"
    )

    st.write(
        "2025.04.15 ~ 2025.10.14"
    )


    st.write(
        "정책 이후"
    )

    st.write(
        "2025.10.15 ~ 2026.04.14"
    )

# ============================================================
# 지도 지표 선택
# ============================================================

metric_choice = st.segmented_control(

    "지도 지표",

    options=[

        "일평균 거래량 증감률",

        "거래 점유율 변화"
    ],

    default=(
        "일평균 거래량 증감률"
    )
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

# ============================================================
# 전체 KPI
# ============================================================

total_before = (
    summary["before_count"].sum()
)

total_after = (
    summary["after_count"].sum()
)


before_daily = (
    summary["before_daily_avg"].sum()
)

after_daily = (
    summary["after_daily_avg"].sum()
)


overall_change = (

    (
        after_daily
        - before_daily
    )

    / before_daily

    * 100
)


largest_drop = (

    summary

    .sort_values(
        "daily_avg_change_pct"
    )

    .iloc[0]
)


c1, c2, c3, c4 = st.columns(
    4
)


c1.metric(

    "정책 이전 거래량",

    f"{total_before:,.0f}건"
)


c2.metric(

    "정책 이후 거래량",

    f"{total_after:,.0f}건"
)


c3.metric(

    "일평균 거래량 변화",

    f"{overall_change:.1f}%",

    delta=f"{overall_change:.1f}%"
)


c4.metric(

    "거래량 최대 감소",

    largest_drop["region"],

    (
        f"{largest_drop['daily_avg_change_pct']:.1f}%"
    )
)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(

    [

        "Overview",

        "자치구 상세",

        "Data"
    ]
)


# ============================================================
# OVERVIEW
# ============================================================

with tab1:


    left, right = st.columns(
        [1.45, 1]
    )


    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    with left:

        st.subheader(
            "자치구별 거래시장 변화"
        )


        map_fig = make_seoul_map(

            metric_col,

            metric_name
        )


        st.plotly_chart(

            map_fig,

            width="stretch",

            config={
                "displayModeBar": False
            }
        )


    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    with right:

        st.subheader(
            "자치구 변화 순위"
        )


        ranking = (

            summary

            .sort_values(
                metric_col
            )
        )


        rank_fig = px.bar(

            ranking,

            x=metric_col,

            y="region",

            orientation="h",

            color=metric_col,

            color_continuous_scale="RdBu",

            color_continuous_midpoint=0,

            labels={

                metric_col:
                metric_name,

                "region":
                ""
            }
        )


        rank_fig.update_layout(

            height=630,

            coloraxis_showscale=False,

            margin=dict(

                l=0,
                r=0,
                t=10,
                b=0
            ),

            template="simple_white"
        )


        st.plotly_chart(

            rank_fig,

            width="stretch"
        )

# ============================================================
# DISTRICT DETAIL
# ============================================================

with tab2:


    selected_summary = (

        summary[

            summary["region"]
            == selected_district

        ]

        .iloc[0]
    )


    st.subheader(
        selected_district
    )


    a, b, c, d = st.columns(
        4
    )


    a.metric(

        "정책 이전",

        (
            f"{selected_summary['before_count']:,.0f}건"
        )
    )


    b.metric(

        "정책 이후",

        (
            f"{selected_summary['after_count']:,.0f}건"
        )
    )


    c.metric(

        "일평균 증감률",

        (
            f"{selected_summary['daily_avg_change_pct']:.1f}%"
        )
    )


    d.metric(

        "거래점유율 변화",

        (
            f"{selected_summary['share_change_pp']:.2f}%p"
        )
    )


    # --------------------------------------------------------
    # 일별 추이
    # --------------------------------------------------------

    temp_daily = (

        district_daily[

            district_daily["region"]
            == selected_district

        ]

        .copy()
    )


    fig_detail = go.Figure()


    fig_detail.add_trace(

        go.Scatter(

            x=temp_daily[
                "deal_date"
            ],

            y=temp_daily[
                "transaction_count"
            ],

            name="일별 거래량",

            opacity=0.25
        )
    )


    fig_detail.add_trace(

        go.Scatter(

            x=temp_daily[
                "deal_date"
            ],

            y=temp_daily[
                "rolling_14d"
            ],

            name="14일 이동평균",

            line=dict(
                width=3
            )
        )
    )


    # 정책 기준선
    policy_date = pd.Timestamp(
        "2025-10-15"
    )


    fig_detail.add_shape(

        type="line",

        x0=policy_date,

        x1=policy_date,

        y0=0,

        y1=1,

        xref="x",

        yref="paper",

        line=dict(

            dash="dash",

            width=2
        )
    )


    fig_detail.add_annotation(

        x=policy_date,

        y=1,

        xref="x",

        yref="paper",

        text="10·15 대책",

        showarrow=False,

        xanchor="left"
    )


    fig_detail.update_layout(

        template="simple_white",

        height=480,

        hovermode="x unified",

        xaxis_title="계약일",

        yaxis_title="거래건수",

        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10
        )
    )


    st.plotly_chart(

        fig_detail,

        width="stretch"
    )

# ============================================================
# DATA
# ============================================================

with tab3:

    st.subheader(
        "자치구별 분석 데이터"
    )


    show_df = (

        summary

        .sort_values(
            "daily_avg_change_pct"
        )

        .copy()
    )


    st.dataframe(

        show_df,

        width="stretch",

        hide_index=True,

        column_config={

            "region":
            "자치구",

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

            "daily_avg_change_pct":
            st.column_config.NumberColumn(
                "일평균 증감률",
                format="%.1f%%"
            ),

            "share_change_pp":
            st.column_config.NumberColumn(
                "점유율 변화",
                format="%.2f%%p"
            )
        }
    )


from pathlib import Path
import json
import hashlib

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
    initial_sidebar_state="expanded",
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


SEOUL_EXISTING_REGULATED = [
    "강남구",
    "서초구",
    "송파구",
    "용산구",
]


CHANGE_COLORSCALE = [
    [0.00, "#9c0000"],
    [0.25, "#d6604d"],
    [0.50, "#f7f7f7"],
    [0.75, "#4393c3"],
    [1.00, "#2166ac"],
]


# ============================================================
# 3. CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1800px;
    }

    h1 {
        font-weight: 760;
        letter-spacing: -1.5px;
    }

    h2,
    h3 {
        letter-spacing: -0.6px;
    }

    [data-testid="stSidebar"] {
        background-color: #fafafa;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 10px;
        padding: 12px;
    }

    button[data-baseweb="tab"] {
        font-size: 0.90rem;
        font-weight: 650;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }

    div[data-baseweb="tab-list"] {
        gap: 0.2rem;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.75rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4. 파일 경로
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

DATA_DIR = (
    BASE_DIR
    / "data"
)


FILES = {

    # 서울
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


    # 경기
    "gyeonggi_summary":
        DATA_DIR / "gyeonggi_policy_summary.csv",

    "gyeonggi_daily":
        DATA_DIR / "gyeonggi_daily_transactions.csv",

    "gyeonggi_district_daily":
        DATA_DIR / "gyeonggi_district_daily.csv",

    "gyeonggi_monthly":
        DATA_DIR / "gyeonggi_monthly_transactions.csv",

    "gyeonggi_geojson":
        DATA_DIR / "gyeonggi_policy_map.geojson",
}


# ============================================================
# 5. 파일 존재 확인
# ============================================================

missing_files = [

    str(
        path.relative_to(
            BASE_DIR
        )
    )

    for path
    in FILES.values()

    if not path.exists()
]


if missing_files:

    st.error(
        "다음 데이터 파일을 찾을 수 없습니다."
    )

    st.code(
        "\n".join(
            missing_files
        )
    )

    st.stop()


# ============================================================
# 6. 파일 변경 감지
# ============================================================

def get_file_signature(
    path
):

    sha = hashlib.md5()

    with open(
        path,
        "rb"
    ) as f:

        while True:

            chunk = f.read(
                1024 * 1024
            )

            if not chunk:

                break

            sha.update(
                chunk
            )

    return sha.hexdigest()


DATA_SIGNATURE = "|".join(

    get_file_signature(
        path
    )

    for path
    in FILES.values()
)


# ============================================================
# 7. 데이터 로딩
# ============================================================

@st.cache_data(
    show_spinner=False
)
def load_data(
    data_signature
):

    # 서울
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

        seoul_geojson = json.load(
            f
        )


    # 경기
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

        gyeonggi_geojson = json.load(
            f
        )


    # 날짜형
    seoul_daily[
        "deal_date"
    ] = pd.to_datetime(
        seoul_daily[
            "deal_date"
        ]
    )

    seoul_district_daily[
        "deal_date"
    ] = pd.to_datetime(
        seoul_district_daily[
            "deal_date"
        ]
    )

    seoul_monthly[
        "year_month"
    ] = pd.to_datetime(
        seoul_monthly[
            "year_month"
        ]
    )


    gyeonggi_daily[
        "deal_date"
    ] = pd.to_datetime(
        gyeonggi_daily[
            "deal_date"
        ]
    )

    gyeonggi_district_daily[
        "deal_date"
    ] = pd.to_datetime(
        gyeonggi_district_daily[
            "deal_date"
        ]
    )

    gyeonggi_monthly[
        "year_month"
    ] = pd.to_datetime(
        gyeonggi_monthly[
            "year_month"
        ]
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

) = load_data(
    DATA_SIGNATURE
)


# ============================================================
# 8. Summary 전처리
# ============================================================

def prepare_summary(
    df
):

    df = df.copy()


    numeric_columns = [

        "before_count",
        "after_count",

        "before_daily_avg",
        "after_daily_avg",

        "count_change_pct",
        "daily_avg_change_pct",
    ]


    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(

                df[col],

                errors="coerce"
            )


    total_before = (
        df["before_count"]
        .sum()
    )

    total_after = (
        df["after_count"]
        .sum()
    )


    df[
        "before_share_pct"
    ] = (

        df["before_count"]

        / total_before

        * 100
    )


    df[
        "after_share_pct"
    ] = (

        df["after_count"]

        / total_after

        * 100
    )


    df[
        "share_change_pp"
    ] = (

        df["after_share_pct"]

        - df["before_share_pct"]
    )


    if "lawd_cd" in df.columns:

        df[
            "lawd_cd"
        ] = (

            df[
                "lawd_cd"
            ]

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

def get_geo_label_data(
    geojson
):

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

            lon = float(
                lon
            )

            lat = float(
                lat
            )

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
                ),
        })


    return pd.DataFrame(
        rows
    )


# ============================================================
# 10. GeoJSON 좌표 범위 확인
# ============================================================

def get_geojson_bounds(
    geojson
):

    xs = []
    ys = []


    def collect_coordinates(
        coords
    ):

        if not isinstance(
            coords,
            list
        ):

            return


        if (
            len(coords) >= 2
            and isinstance(
                coords[0],
                (int, float)
            )
            and isinstance(
                coords[1],
                (int, float)
            )
        ):

            xs.append(
                float(
                    coords[0]
                )
            )

            ys.append(
                float(
                    coords[1]
                )
            )

            return


        for item in coords:

            collect_coordinates(
                item
            )


    for feature in geojson.get(
        "features",
        []
    ):

        geometry = feature.get(
            "geometry",
            {}
        )


        collect_coordinates(

            geometry.get(
                "coordinates",
                []
            )
        )


    if not xs:

        return None


    return {

        "min_lon":
            min(xs),

        "min_lat":
            min(ys),

        "max_lon":
            max(xs),

        "max_lat":
            max(ys),
    }


def is_korea_bounds(
    bounds
):

    if bounds is None:

        return False


    return (

        124
        <= bounds["min_lon"]
        <= 132

        and

        124
        <= bounds["max_lon"]
        <= 132

        and

        33
        <= bounds["min_lat"]
        <= 39.5

        and

        33
        <= bounds["max_lat"]
        <= 39.5
    )


# ============================================================
# 11. 정책 기준선
# ============================================================

def add_policy_line(
    fig,
    text="10·15 대책",
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
        ),
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
            size=10
        ),
    )


    return fig


# ============================================================
# 12. 일별 거래량 그래프
# ============================================================

def make_daily_chart(
    daily,
    title,
    height=310,
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

            opacity=0.25,
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
            ),
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

        height=height,

        margin=dict(

            l=10,

            r=10,

            t=45,

            b=10
        ),

        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="right",

            x=1
        ),
    )


    return fig


# ============================================================
# 13. 지역 상세 데이터
# ============================================================

def prepare_region_daily(
    district_daily,
    selected_region,
):


    temp = (

        district_daily[

            district_daily[
                "region"
            ]
            ==
            selected_region

        ][

            [
                "deal_date",
                "transaction_count"
            ]

        ].copy()
    )


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
# 14. 지역별 순위 그래프
# ============================================================

def make_ranking_chart(

    summary,

    metric_col,

    metric_name,

    title,

    height=360,
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

        title=title,

        labels={

            metric_col:
                metric_name,

            "region":
                "",
        },
    )


    fig.add_vline(

        x=0,

        line_dash="dash",

        line_width=1
    )


    fig.update_layout(

        template="simple_white",

        height=height,

        coloraxis_showscale=False,

        margin=dict(

            l=0,

            r=10,

            t=45,

            b=10
        ),
    )


    return fig


# ============================================================
# 15. 정책 전후 직접 비교 그래프
# ============================================================

def make_before_after_chart(

    summary,

    title,

    height=360,
):


    compare_df = (

        summary[

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


    compare_df[
        "period"
    ] = (

        compare_df[
            "period"
        ]

        .replace({

            "before_count":
                "정책 이전",

            "after_count":
                "정책 이후",
        })
    )


    fig = px.bar(

        compare_df,

        y="region",

        x="transaction_count",

        color="period",

        orientation="h",

        barmode="group",

        title=title,

        labels={

            "region":
                "",

            "transaction_count":
                "거래건수",

            "period":
                "기간",
        },
    )


    fig.update_layout(

        template="simple_white",

        height=height,

        margin=dict(

            l=0,

            r=10,

            t=45,

            b=10
        ),

        legend=dict(

            orientation="h",

            yanchor="bottom",

            y=1.02,

            xanchor="right",

            x=1
        ),
    )


    return fig


# ============================================================
# 16. 공통 데이터 표
# ============================================================

def show_chart_data(

    df,

    title="활용 데이터 보기",

    columns=None,

    sort_by=None,
):


    show_df = df.copy()


    if columns is not None:

        existing_columns = [

            col

            for col
            in columns

            if col
            in show_df.columns
        ]


        show_df = show_df[
            existing_columns
        ]


    if (
        sort_by is not None
        and sort_by
        in show_df.columns
    ):

        show_df = (

            show_df

            .sort_values(
                sort_by
            )

            .reset_index(
                drop=True
            )
        )


    with st.expander(

        f"📊 {title}",

        expanded=False
    ):


        st.dataframe(

            show_df,

            use_container_width=True,

            hide_index=True
        )


# ============================================================
# 17. 수도권 통합 지도
# ============================================================

def make_capital_map(

    seoul_summary,

    gyeonggi_summary,

    seoul_geojson,

    gyeonggi_geojson,

    metric_col,

    metric_name,
):


    seoul_df = (
        seoul_summary.copy()
    )


    gyeonggi_df = (
        gyeonggi_summary.copy()
    )


    seoul_df[
        metric_col
    ] = pd.to_numeric(

        seoul_df[
            metric_col
        ],

        errors="coerce"
    )


    gyeonggi_df[
        metric_col
    ] = pd.to_numeric(

        gyeonggi_df[
            metric_col
        ],

        errors="coerce"
    )


    gyeonggi_df[
        "lawd_cd"
    ] = (

        gyeonggi_df[
            "lawd_cd"
        ]

        .astype(str)

        .str.replace(
            ".0",
            "",
            regex=False
        )

        .str.zfill(5)
    )


    # --------------------------------------------------------
    # 서울 + 경기 동일 색상 범위
    # --------------------------------------------------------

    combined_values = pd.concat(

        [

            seoul_df[
                metric_col
            ],

            gyeonggi_df[
                metric_col
            ],
        ],

        ignore_index=True
    )


    valid_values = (

        combined_values

        .dropna()

        .abs()
    )


    if len(
        valid_values
    ) > 0:

        max_abs = max(

            valid_values.max(),

            1
        )

    else:

        max_abs = 1


    fig = go.Figure()


    # ========================================================
    # 경기도 비규제 지역
    # ========================================================

    gyeonggi_all_ids = [

        str(

            feature.get(
                "id",
                ""
            )
        )

        for feature
        in gyeonggi_geojson.get(
            "features",
            []
        )
    ]


    gyeonggi_regulated_ids = set(

        gyeonggi_df[
            "lawd_cd"
        ].tolist()
    )


    gyeonggi_unregulated_ids = [

        code

        for code
        in gyeonggi_all_ids

        if code
        not in gyeonggi_regulated_ids
    ]


    if gyeonggi_unregulated_ids:

        fig.add_trace(

            go.Choropleth(

                geojson=(
                    gyeonggi_geojson
                ),

                locations=(
                    gyeonggi_unregulated_ids
                ),

                z=[

                    1

                ] * len(
                    gyeonggi_unregulated_ids
                ),

                featureidkey="id",

                colorscale=[

                    [0, "#ECECEC"],

                    [1, "#ECECEC"],
                ],

                showscale=False,

                marker_line_color=(
                    "white"
                ),

                marker_line_width=0.7,

                hovertemplate=(

                    "경기도 비규제·비분석지역"

                    "<extra></extra>"
                ),
            )
        )


    # ========================================================
    # 경기 신규 규제지역
    # ========================================================

    gyeonggi_custom_data = (

        np.column_stack(

            [

                gyeonggi_df[
                    "before_count"
                ],

                gyeonggi_df[
                    "after_count"
                ],

                gyeonggi_df[
                    "before_daily_avg"
                ],

                gyeonggi_df[
                    "after_daily_avg"
                ],

                gyeonggi_df[
                    metric_col
                ],
            ]
        )
    )


    fig.add_trace(

        go.Choropleth(

            geojson=(
                gyeonggi_geojson
            ),

            locations=(

                gyeonggi_df[
                    "lawd_cd"
                ]
            ),

            z=(

                gyeonggi_df[
                    metric_col
                ]
            ),

            text=(

                gyeonggi_df[
                    "region"
                ]
            ),

            featureidkey="id",

            zmin=-max_abs,

            zmax=max_abs,

            zmid=0,

            colorscale=(
                CHANGE_COLORSCALE
            ),

            colorbar=dict(

                title=metric_name,

                thickness=13,

                len=0.45,

                x=1.02
            ),

            marker_line_color=(
                "white"
            ),

            marker_line_width=1.2,

            customdata=(
                gyeonggi_custom_data
            ),

            hovertemplate=(

                "<b>%{text}</b>"

                "<br>"
                "경기도 신규 규제지역"

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
            ),
        )
    )


    # ========================================================
    # 서울 신규 규제지역
    # ========================================================

    seoul_custom_data = (

        np.column_stack(

            [

                seoul_df[
                    "before_count"
                ],

                seoul_df[
                    "after_count"
                ],

                seoul_df[
                    "before_daily_avg"
                ],

                seoul_df[
                    "after_daily_avg"
                ],

                seoul_df[
                    metric_col
                ],
            ]
        )
    )


    fig.add_trace(

        go.Choropleth(

            geojson=(
                seoul_geojson
            ),

            locations=(

                seoul_df[
                    "region"
                ]
            ),

            z=(

                seoul_df[
                    metric_col
                ]
            ),

            featureidkey="id",

            zmin=-max_abs,

            zmax=max_abs,

            zmid=0,

            colorscale=(
                CHANGE_COLORSCALE
            ),

            showscale=False,

            marker_line_color=(
                "white"
            ),

            marker_line_width=1.3,

            customdata=(
                seoul_custom_data
            ),

            hovertemplate=(

                "<b>%{location}</b>"

                "<br>"
                "서울 신규 규제지역"

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
            ),
        )
    )


    # ========================================================
    # 서울 기존 규제지역
    # ========================================================

    fig.add_trace(

        go.Choropleth(

            geojson=(
                seoul_geojson
            ),

            locations=(
                SEOUL_EXISTING_REGULATED
            ),

            z=[
                1,
                1,
                1,
                1
            ],

            featureidkey="id",

            colorscale=[

                [0, "#D9D9D9"],

                [1, "#D9D9D9"],
            ],

            showscale=False,

            marker_line_color=(
                "#FFD400"
            ),

            marker_line_width=4,

            hovertemplate=(

                "<b>%{location}</b>"

                "<br><br>"

                "10·15 대책 이전 기존 규제지역"

                "<br>"

                "이번 신규 규제지역 분석 제외"

                "<extra></extra>"
            ),
        )
    )


    # ========================================================
    # 서울 라벨
    # ========================================================

    seoul_labels = (
        get_geo_label_data(
            seoul_geojson
        )
    )


    if not seoul_labels.empty:

        seoul_labels[
            "label_name"
        ] = (

            seoul_labels[
                "feature_id"
            ]
        )


        normal_labels = (

            seoul_labels[

                ~seoul_labels[
                    "feature_id"
                ].isin(
                    SEOUL_EXISTING_REGULATED
                )

            ].copy()
        )


        existing_labels = (

            seoul_labels[

                seoul_labels[
                    "feature_id"
                ].isin(
                    SEOUL_EXISTING_REGULATED
                )

            ].copy()
        )


        if not normal_labels.empty:

            fig.add_trace(

                go.Scattergeo(

                    lon=(

                        normal_labels[
                            "label_lon"
                        ]
                    ),

                    lat=(

                        normal_labels[
                            "label_lat"
                        ]
                    ),

                    text=(

                        normal_labels[
                            "label_name"
                        ]
                    ),

                    mode="text",

                    textfont=dict(

                        size=8,

                        color="#222222"
                    ),

                    hoverinfo="skip",

                    showlegend=False,
                )
            )


        if not existing_labels.empty:

            fig.add_trace(

                go.Scattergeo(

                    lon=(

                        existing_labels[
                            "label_lon"
                        ]
                    ),

                    lat=(

                        existing_labels[
                            "label_lat"
                        ]
                    ),

                    text=(

                        existing_labels[
                            "label_name"
                        ]
                    ),

                    mode="text",

                    textfont=dict(

                        size=8,

                        color="#333333",

                        family="Arial Black"
                    ),

                    hoverinfo="skip",

                    showlegend=False,
                )
            )


    # ========================================================
    # 경기 규제지역 라벨
    # ========================================================

    gyeonggi_labels = (
        get_geo_label_data(
            gyeonggi_geojson
        )
    )


    if not gyeonggi_labels.empty:

        gyeonggi_labels[
            "feature_id"
        ] = (

            gyeonggi_labels[
                "feature_id"
            ]

            .astype(str)

            .str.zfill(5)
        )


        region_lookup = dict(

            zip(

                gyeonggi_df[
                    "lawd_cd"
                ],

                gyeonggi_df[
                    "region"
                ],
            )
        )


        gyeonggi_labels = (

            gyeonggi_labels[

                gyeonggi_labels[
                    "feature_id"
                ].isin(
                    gyeonggi_regulated_ids
                )

            ].copy()
        )


        gyeonggi_labels[
            "label_name"
        ] = (

            gyeonggi_labels[
                "feature_id"
            ]

            .map(
                region_lookup
            )
        )


        if not gyeonggi_labels.empty:

            fig.add_trace(

                go.Scattergeo(

                    lon=(

                        gyeonggi_labels[
                            "label_lon"
                        ]
                    ),

                    lat=(

                        gyeonggi_labels[
                            "label_lat"
                        ]
                    ),

                    text=(

                        gyeonggi_labels[
                            "label_name"
                        ]
                    ),

                    mode="text",

                    textfont=dict(

                        size=8,

                        color="#222222"
                    ),

                    hoverinfo="skip",

                    showlegend=False,
                )
            )


    # ========================================================
    # 수도권 지도 범위 고정
    # ========================================================

    fig.update_geos(

        visible=False,

        projection_type="mercator",

        lonaxis_range=[
            126.0,
            128.2
        ],

        lataxis_range=[
            36.5,
            38.4
        ],

        showcountries=False,

        showcoastlines=False,

        showland=False,

        showlakes=False,

        bgcolor="white"
    )


    fig.update_layout(

        height=1080,

        paper_bgcolor="white",

        margin=dict(

            l=0,

            r=50,

            t=10,

            b=0
        ),

        showlegend=False
    )


    return fig


# ============================================================
# 18. Header
# ============================================================

st.title(
    "10·15 부동산 규제정책 이후 거래시장 변화"
)


st.caption(
    "서울·경기 신규 규제지역의 "
    "정책 발표 전후 아파트 매매 실거래량 변화"
)


# ============================================================
# GeoJSON 좌표 확인
# ============================================================

seoul_bounds = (
    get_geojson_bounds(
        seoul_geojson
    )
)

gyeonggi_bounds = (
    get_geojson_bounds(
        gyeonggi_geojson
    )
)


# ============================================================
# 19. Sidebar
# ============================================================

with st.sidebar:


    st.header(
        "Dashboard Settings"
    )


    metric_choice = st.radio(

        "지도·순위 지표",

        [

            "일평균 거래량 증감률",

            "분석대상 내 거래점유율 변화",
        ],
    )


    if (
        metric_choice
        ==
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


    st.caption(
        "분석기간"
    )


    st.write(
        "정책 이전: "
        "2025.04.15 ~ 2025.10.14"
    )


    st.write(
        "정책 이후: "
        "2025.10.15 ~ 2026.04.14"
    )


    st.caption(
        "※ 거래점유율 변화는 "
        "서울과 경기도 각각의 분석대상 "
        "내부 점유율입니다."
    )


    # --------------------------------------------------------
    # 좌표 진단
    # --------------------------------------------------------

    with st.expander(
        "지도 좌표 진단",
        expanded=False
    ):


        st.write(
            "서울 GeoJSON"
        )

        st.json(
            seoul_bounds
        )


        st.write(
            "경기 GeoJSON"
        )

        st.json(
            gyeonggi_bounds
        )


# ============================================================
# 좌표 오류 경고
# ============================================================

if not is_korea_bounds(
    seoul_bounds
):

    st.error(
        "서울 GeoJSON 좌표 범위가 "
        "한국 좌표 범위를 벗어났습니다."
    )


if not is_korea_bounds(
    gyeonggi_bounds
):

    st.error(

        "경기도 GeoJSON 좌표 범위가 "
        "한국 좌표 범위를 벗어났습니다. "
        "data/gyeonggi_policy_map.geojson을 "
        "다시 확인해주세요."
    )


# ============================================================
# 20. 메인 레이아웃
# ============================================================

map_col, data_col = st.columns(

    [
        1.0,
        1.0
    ],

    gap="large"
)


# ============================================================
# 왼쪽 - 수도권 통합 지도
# ============================================================

with map_col:


    with st.container(
        border=True
    ):


        st.subheader(
            "수도권 공간별 거래시장 변화"
        )


        st.caption(

            "빨강 = 거래량 감소 · "
            "파랑 = 거래량 증가 · "
            "회색 = 경기 비규제·비분석지역 · "
            "노란 경계 = 서울 기존 규제지역"
        )


        capital_map_fig = (
            make_capital_map(

                seoul_summary,

                gyeonggi_summary,

                seoul_geojson,

                gyeonggi_geojson,

                metric_col,

                metric_name
            )
        )


        st.plotly_chart(

            capital_map_fig,

            use_container_width=True,

            config={

                "displayModeBar": True,
                "scrollZoom": True,
                "displaylogo": False,
            },
        )


        # ----------------------------------------------------
        # 통합지도 활용 데이터
        # ----------------------------------------------------

        with st.expander(

            "🗺️ 수도권 지도 활용 데이터 보기",

            expanded=False
        ):


            st.markdown(
                "**서울 신규 규제지역**"
            )


            st.dataframe(

                seoul_summary[

                    [
                        "region",
                        "before_count",
                        "after_count",
                        "daily_avg_change_pct",
                        "share_change_pp",
                    ]
                ],

                use_container_width=True,

                hide_index=True
            )


            st.markdown(
                "**경기도 신규 규제지역**"
            )


            gg_map_cols = [

                "region",

                "parent_city",

                "before_count",

                "after_count",

                "daily_avg_change_pct",

                "share_change_pp",
            ]


            gg_map_cols = [

                col

                for col
                in gg_map_cols

                if col
                in gyeonggi_summary.columns
            ]


            st.dataframe(

                gyeonggi_summary[
                    gg_map_cols
                ],

                use_container_width=True,

                hide_index=True
            )


# ============================================================
# 오른쪽 - Tabs
# ============================================================

with data_col:


    (
        ranking_tab,
        trend_tab,
        detail_tab,
        compare_tab,

    ) = st.tabs(

        [

            "지역별 거래시장 변화 순위",

            "정책 발표 전후 거래량 추이",

            "지역 상세 비교",

            "정책 전후 거래량 직접 비교",
        ]
    )


    # ========================================================
    # TAB 1. 지역별 거래시장 변화 순위
    # ========================================================

    with ranking_tab:


        with st.container(
            border=True
        ):


            st.subheader(
                "서울시 데이터"
            )


            seoul_rank_fig = (
                make_ranking_chart(

                    seoul_summary,

                    metric_col,

                    metric_name,

                    "서울 지역별 거래시장 변화 순위",

                    height=420
                )
            )


            st.plotly_chart(

                seoul_rank_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                seoul_summary,

                title=(
                    "서울 지역별 거래시장 변화 "
                    "활용 데이터"
                ),

                columns=[

                    "region",

                    "before_count",

                    "after_count",

                    "before_daily_avg",

                    "after_daily_avg",

                    "daily_avg_change_pct",

                    "before_share_pct",

                    "after_share_pct",

                    "share_change_pp",
                ],

                sort_by=metric_col
            )


        with st.container(
            border=True
        ):


            st.subheader(
                "경기도 데이터"
            )


            gyeonggi_rank_fig = (
                make_ranking_chart(

                    gyeonggi_summary,

                    metric_col,

                    metric_name,

                    "경기 지역별 거래시장 변화 순위",

                    height=390
                )
            )


            st.plotly_chart(

                gyeonggi_rank_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                gyeonggi_summary,

                title=(
                    "경기도 지역별 거래시장 변화 "
                    "활용 데이터"
                ),

                columns=[

                    "region",

                    "parent_city",

                    "before_count",

                    "after_count",

                    "before_daily_avg",

                    "after_daily_avg",

                    "daily_avg_change_pct",

                    "before_share_pct",

                    "after_share_pct",

                    "share_change_pp",
                ],

                sort_by=metric_col
            )


    # ========================================================
    # TAB 2. 정책 발표 전후 거래량 추이
    # ========================================================

    with trend_tab:


        with st.container(
            border=True
        ):


            st.subheader(
                "서울시 데이터"
            )


            seoul_daily_fig = (
                make_daily_chart(

                    seoul_daily,

                    "서울 신규 규제지역 일별 거래량",

                    height=360
                )
            )


            st.plotly_chart(

                seoul_daily_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                seoul_daily,

                title=(
                    "서울 일별 거래량 "
                    "활용 데이터"
                ),

                columns=[

                    "deal_date",

                    "transaction_count",

                    "rolling_14d",
                ]
            )


        with st.container(
            border=True
        ):


            st.subheader(
                "경기도 데이터"
            )


            gyeonggi_daily_fig = (
                make_daily_chart(

                    gyeonggi_daily,

                    "경기 신규 규제지역 일별 거래량",

                    height=360
                )
            )


            st.plotly_chart(

                gyeonggi_daily_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                gyeonggi_daily,

                title=(
                    "경기도 일별 거래량 "
                    "활용 데이터"
                ),

                columns=[

                    "deal_date",

                    "transaction_count",

                    "rolling_14d",
                ]
            )


    # ========================================================
    # TAB 3. 지역 상세 비교
    # ========================================================

    with detail_tab:


        # ----------------------------------------------------
        # 서울
        # ----------------------------------------------------

        with st.container(
            border=True
        ):


            st.subheader(
                "서울시 데이터"
            )


            selected_seoul = (
                st.selectbox(

                    "서울 자치구 선택",

                    options=sorted(

                        seoul_summary[
                            "region"
                        ]

                        .dropna()

                        .tolist()
                    ),

                    key="detail_seoul"
                )
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


            c1, c2, c3 = (
                st.columns(3)
            )


            c1.metric(

                "정책 이전",

                (
                    f"{selected_seoul_summary['before_count']:,.0f}건"
                )
            )


            c2.metric(

                "정책 이후",

                (
                    f"{selected_seoul_summary['after_count']:,.0f}건"
                )
            )


            c3.metric(

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

                    (
                        f"{selected_seoul} 거래량"
                    ),

                    height=310
                )
            )


            st.plotly_chart(

                selected_seoul_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                selected_seoul_daily,

                title=(

                    f"{selected_seoul} "
                    "일별 거래량 활용 데이터"
                ),

                columns=[

                    "deal_date",

                    "transaction_count",

                    "rolling_14d",
                ]
            )


        # ----------------------------------------------------
        # 경기
        # ----------------------------------------------------

        with st.container(
            border=True
        ):


            st.subheader(
                "경기도 데이터"
            )


            selected_gyeonggi = (
                st.selectbox(

                    "경기 시·구 선택",

                    options=sorted(

                        gyeonggi_summary[
                            "region"
                        ]

                        .dropna()

                        .tolist()
                    ),

                    key="detail_gyeonggi"
                )
            )


            selected_gyeonggi_summary = (

                gyeonggi_summary[

                    gyeonggi_summary[
                        "region"
                    ]
                    ==
                    selected_gyeonggi

                ]

                .iloc[0]
            )


            c1, c2, c3 = (
                st.columns(3)
            )


            c1.metric(

                "정책 이전",

                (
                    f"{selected_gyeonggi_summary['before_count']:,.0f}건"
                )
            )


            c2.metric(

                "정책 이후",

                (
                    f"{selected_gyeonggi_summary['after_count']:,.0f}건"
                )
            )


            c3.metric(

                "일평균 증감률",

                (
                    f"{selected_gyeonggi_summary['daily_avg_change_pct']:.1f}%"
                )
            )


            selected_gyeonggi_daily = (

                prepare_region_daily(

                    gyeonggi_district_daily,

                    selected_gyeonggi
                )
            )


            selected_gyeonggi_fig = (

                make_daily_chart(

                    selected_gyeonggi_daily,

                    (
                        f"{selected_gyeonggi} 거래량"
                    ),

                    height=310
                )
            )


            st.plotly_chart(

                selected_gyeonggi_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                selected_gyeonggi_daily,

                title=(

                    f"{selected_gyeonggi} "
                    "일별 거래량 활용 데이터"
                ),

                columns=[

                    "deal_date",

                    "transaction_count",

                    "rolling_14d",
                ]
            )


    # ========================================================
    # TAB 4. 정책 전후 거래량 직접 비교
    # ========================================================

    with compare_tab:


        with st.container(
            border=True
        ):


            st.subheader(
                "서울시 데이터"
            )


            seoul_compare_fig = (
                make_before_after_chart(

                    seoul_summary,

                    "서울 정책 전후 거래량 직접 비교",

                    height=430
                )
            )


            st.plotly_chart(

                seoul_compare_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                seoul_summary,

                title=(
                    "서울 정책 전후 거래량 "
                    "활용 데이터"
                ),

                columns=[

                    "region",

                    "before_count",

                    "after_count",

                    "daily_avg_change_pct",
                ],

                sort_by=(
                    "daily_avg_change_pct"
                )
            )


        with st.container(
            border=True
        ):


            st.subheader(
                "경기도 데이터"
            )


            gyeonggi_compare_fig = (
                make_before_after_chart(

                    gyeonggi_summary,

                    "경기 정책 전후 거래량 직접 비교",

                    height=390
                )
            )


            st.plotly_chart(

                gyeonggi_compare_fig,

                use_container_width=True,

                config={
                    "displayModeBar":
                        False
                },
            )


            show_chart_data(

                gyeonggi_summary,

                title=(
                    "경기도 정책 전후 거래량 "
                    "활용 데이터"
                ),

                columns=[

                    "region",

                    "parent_city",

                    "before_count",

                    "after_count",

                    "daily_avg_change_pct",
                ],

                sort_by=(
                    "daily_avg_change_pct"
                )
            )


# ============================================================
# 21. 분석 기준
# ============================================================

st.divider()


with st.expander(
    "분석 기준 및 해석 시 유의사항"
):


    st.markdown(
        """
        ### 분석기간

        - **정책 이전**: 2025.04.15 ~ 2025.10.14
        - **정책 기준일**: 2025.10.15
        - **정책 이후**: 2025.10.15 ~ 2026.04.14


        ### 서울

        강남·서초·송파·용산은
        10·15 대책 이전부터 규제지역이었던 곳으로,
        신규 규제지역 변화량 분석에서 제외했습니다.

        통합 지도에서는 해당 4개 자치구를
        **회색 면 + 노란색 경계선**으로 표시합니다.


        ### 경기도

        2025년 10월 15일 신규 규제지역으로 지정된
        12개 시·구를 분석합니다.


        ### 해석 시 유의사항

        본 대시보드는 정책 발표 전후 거래량 변화 패턴을
        비교하는 기술적 분석입니다.

        거래량 변화 전체를 정책의 인과효과로
        해석해서는 안 됩니다.
        """
    )


st.caption(
    "Data: 국토교통부 아파트 매매 실거래가 자료"
)

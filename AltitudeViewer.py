
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from math import radians, sin, cos, sqrt, atan2
import numpy as np

st.title("Altitude Viewer")

# --------------------------------------------------
# Haversine Distance Function
# --------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius (meters)

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# --------------------------------------------------
# File Upload
# --------------------------------------------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
st.write("Column 1: Timestamp")
st.write("Column 2: Longitude")
st.write("Column 3: Latitude")
st.write("Column 4: Elevation (meters)")
if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    # --------------------------------------------------
    # Column Assumptions
    # --------------------------------------------------
    # Column 1 = Timestamp
    # Column 2 = Longitude
    # Column 3 = Latitude
    # Column 4 = Elevation (meters)
    timestamp_col = df.columns[0]
    longitude_col = df.columns[1]
    latitude_col = df.columns[2]
    elevation_col = df.columns[3]

    total_length = len(df)

    # --------------------------------------------------
    # Parse Timestamps
    # --------------------------------------------------
    df["timestamp"] = pd.to_datetime(df[timestamp_col])

    # Convert UTC -> Pacific Time
    df["timestamp_pacific"] = (
        df["timestamp"]
        .dt.tz_localize("UTC")
        .dt.tz_convert("US/Pacific")
    )

    df["pacific_date"] = df["timestamp_pacific"].dt.date

    # --------------------------------------------------
    # Date Boundaries
    # --------------------------------------------------
    date_change_indices = df.index[
        df["pacific_date"] != df["pacific_date"].shift()
    ].tolist()

    if len(date_change_indices) > 0:
        date_change_indices = date_change_indices[1:]

    st.write(f"Total rows: {total_length:,}")

    # --------------------------------------------------
    # Row Scrubber
    # --------------------------------------------------
   # Initialize
    if "current_row" not in st.session_state:
        st.session_state.current_row = 0

    col1, col2 = st.columns([4, 1])

    with col1:
        st.session_state.current_row = st.slider(
            "Row Scrubber",
            min_value=0,
            max_value=total_length - 1,
            value=st.session_state.current_row
        )

    with col2:
        jump_row = st.number_input(
            "Jump To",
            min_value=0,
            max_value=total_length - 1,
            value=st.session_state.current_row,
            step=1
        )

    # If user changed the Jump To box, update scrubber
    if jump_row != st.session_state.current_row:
        st.session_state.current_row = int(jump_row)
        st.rerun()

    current_row = st.session_state.current_row

    # --------------------------------------------------
    # Use Row-2 and Row+2
    # --------------------------------------------------
    row_before = max(0, current_row - 5)
    row_after = min(total_length - 1, current_row + 5)

    lat1 = df.loc[row_before, latitude_col]
    lon1 = df.loc[row_before, longitude_col]
    elev1 = df.loc[row_before, elevation_col]

    lat2 = df.loc[row_after, latitude_col]
    lon2 = df.loc[row_after, longitude_col]
    elev2 = df.loc[row_after, elevation_col]

    # Horizontal distance
    distance_m = haversine(
        lat1,
        lon1,
        lat2,
        lon2
    )

    # Elevation difference
    elevation_change_m = elev2 - elev1

    # Grade (%)
    if distance_m > 0:
        grade_percent = (
            elevation_change_m / distance_m
        ) * 100

        slope_deg = np.degrees(
            np.arctan(
                elevation_change_m / distance_m
            )
        )
    else:
        grade_percent = 0
        slope_deg = 0

    # --------------------------------------------------
    # Metrics
    # --------------------------------------------------
    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            "Distance (Row -2 → Row +2)",
            f"{distance_m:.2f} m"
        )

    with m2:
        st.metric(
            "Elevation Change",
            f"{elevation_change_m:.2f} m"
        )

    with m3:
        st.metric(
            "Grade",
            f"{grade_percent:.2f}%"
        )

    st.write(
        f"Slope Angle: **{slope_deg:.2f}°**"
    )

    # --------------------------------------------------
    # Zoom Controls
    # --------------------------------------------------
    zoom_percent = st.slider(
        "Zoom (% of data shown, max 99)",
        min_value=1,
        max_value=100,
        value=99
    )

    points_displayed = st.slider(
        "Downsampling max points",
        min_value = 100,
        max_value = 500000,
        value = 50000
    )

    window_size = max(
        1,
        int(total_length * zoom_percent / 100)
    )

    max_start_index = max(
        0,
        total_length - window_size
    )

    start_index = st.slider(
        "Time (data position)",
        min_value=0,
        max_value=max_start_index,
        value=0
    )

    end_index = start_index + window_size

    # --------------------------------------------------
    # Slice Data
    # --------------------------------------------------
    display_data = df[elevation_col].iloc[
        start_index:end_index
    ]

    # --------------------------------------------------
    # Downsampling
    # --------------------------------------------------
    max_points = points_displayed

    step = max(
        1,
        len(display_data) // max_points
    )

    display_ds = display_data.iloc[::step]

    # --------------------------------------------------
    # Plot
    # --------------------------------------------------
    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            x=display_ds.index,
            y=display_ds.values,
            mode="lines",
            line=dict(width=1),
            name="Elevation"
        )
    )

    # --------------------------------------------------
    # Current Row Marker
    # --------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=[current_row],
            y=[df.loc[current_row, elevation_col]],
            mode="markers",
            marker=dict(
                color="lime",
                size=12
            ),
            name="Current Position"
        )
    )

    # # --------------------------------------------------
    # # Pacific Day Boundaries
    # # --------------------------------------------------
    # y_top = display_ds.max()

    # for idx in date_change_indices:

    #     if start_index <= idx < end_index:

    #         date_label = str(
    #             df.loc[idx, "pacific_date"]
    #         )

    #         fig.add_vline(
    #             x=idx,
    #             line_color="red",
    #             line_width=2
    #         )

    #         fig.add_annotation(
    #             x=idx,
    #             y=y_top,
    #             text=date_label,
    #             showarrow=False,
    #             textangle=90,
    #             font=dict(
    #                 color="red",
    #                 size=10
    #             )
    #         )

    fig.update_layout(
        title="Elevation vs Row Index",
        xaxis_title="Row Index",
        yaxis_title="Elevation (m)",
        height=550,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.write(
        f"Showing rows {start_index:,} to {end_index - 1:,}"
    )

    st.write(
        f"Rendered {len(display_ds):,} points "
        f"(downsampled from {len(display_data):,})"
    )
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Altitude Viewer")

# File upload
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Normalize column name just in case (Altitude vs altitude)
    columns_lower = {col.lower(): col for col in df.columns}
    
    if "elevation" not in columns_lower:
        st.error("CSV must contain an 'elevation' column.")
    else:
        altitude_col = columns_lower["elevation"]
        
        altitude_data = df[altitude_col]

        total_length = len(altitude_data)

        st.write(f"Total rows: {total_length}")

        # Zoom slider (percentage of dataset to show)
        zoom_percent = st.slider(
            "Zoom (% of data shown)",
            min_value=1,
            max_value=100,
            value=100
        )

        # Compute window size
        window_size = max(1, int(total_length * (zoom_percent / 100)))

        # Time slider (position of window)
        max_start_index = max(0, total_length - window_size)

        start_index = st.slider(
            "Time (data position)",
            min_value=0,
            max_value=max_start_index,
            value=0
        )

        end_index = start_index + window_size

        # Slice data
        display_data = altitude_data.iloc[start_index:end_index]

        # Plot
        fig, ax = plt.subplots()
        ax.plot(display_data.values)
        ax.set_title("Altitude")
        ax.set_xlabel("Index")
        ax.set_ylabel("Altitude")

        st.pyplot(fig)

        st.write(f"Showing rows {start_index} to {end_index - 1}")
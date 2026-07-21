import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Titanic Operations & Port Weather Dashboard",
    page_icon="🚢",
    layout="wide",
)

st.title("🚢 Titanic Passenger Analytics & Departure Port Weather")
st.markdown(
    "Explore passenger demography and real-time current weather conditions at historical departure ports."
)



# DATA LOADING & PREPARATION (Self-Contained)

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    df = pd.read_csv(url)

    # Clean missing Embarked ports
    df["Embarked"] = df["Embarked"].fillna("S")

    # Map Port abbreviations to full names
    port_names = {
        "S": "Southampton (UK)",
        "C": "Cherbourg (France)",
        "Q": "Queenstown (Ireland)",
    }
    df["Port_Name"] = df["Embarked"].map(port_names)

    # Class labels
    df["Pclass_Label"] = df["Pclass"].map(
        {1: "1st Class", 2: "2nd Class", 3: "3rd Class"}
    )
    df["Survival_Label"] = df["Survived"].map({0: "Perished", 1: "Survived"})

    return df


df = load_data()


# EXTERNAL API INTEGRATION (Open-Meteo REST API)

# Coordinates for historical ports
PORT_COORDINATES = {
    "Southampton (UK)": {"lat": 50.9097, "lon": -1.4044},
    "Cherbourg (France)": {"lat": 49.6337, "lon": -1.6221},
    "Queenstown (Ireland)": {"lat": 51.8503, "lon": -8.2943},
}


def fetch_port_weather(lat, lon):
    """Fetches real-time weather metrics using HTTP GET from Open-Meteo public REST API."""
    endpoint = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    }
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch live weather data: {e}")
        return None



# SIDEBAR CONTROLS & WIDGETS

st.sidebar.header("🔍 Filter Passenger Data")

# Widget 1: Port Selection
selected_ports = st.sidebar.multiselect(
    "Select Departure Port(s):",
    options=list(PORT_COORDINATES.keys()),
    default=list(PORT_COORDINATES.keys()),
)

# Widget 2: Passenger Class Selection
selected_classes = st.sidebar.multiselect(
    "Select Ticket Class:",
    options=["1st Class", "2nd Class", "3rd Class"],
    default=["1st Class", "2nd Class", "3rd Class"],
)

# Widget 3: Fare Slider
max_fare_val = float(df["Fare"].max())
fare_range = st.sidebar.slider(
    "Filter Ticket Fare ($):",
    min_value=0.0,
    max_value=max_fare_val,
    value=(0.0, max_fare_val),
)

# Filter Dataset based on widgets
filtered_df = df[
    (df["Port_Name"].isin(selected_ports))
    & (df["Pclass_Label"].isin(selected_classes))
    & (df["Fare"] >= fare_range[0])
    & (df["Fare"] <= fare_range[1])
]


# LIVE EXTERNAL API DISPLAY

st.subheader("🌐 Live Port Weather Conditions (External API Integration)")

if selected_ports:
    # Pick the first selected port to display weather metrics
    primary_port = selected_ports[0]
    coords = PORT_COORDINATES[primary_port]
    weather_data = fetch_port_weather(coords["lat"], coords["lon"])

    if weather_data and "current" in weather_data:
        current_data = weather_data["current"]
        temp = current_data.get("temperature_2m", "N/A")
        humidity = current_data.get("relative_humidity_2m", "N/A")
        wind_speed = current_data.get("wind_speed_10m", "N/A")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Selected Port", primary_port)
        col2.metric("Current Temperature", f"{temp} °C")
        col3.metric("Relative Humidity", f"{humidity} %")
        col4.metric("Wind Speed (10m)", f"{wind_speed} km/h")
        st.caption(
            "Weather data provided by Open-Meteo.com (CC BY 4.0 Attribution)"
        )
else:
    st.info("Select at least one port in the sidebar to view weather metrics.")

st.markdown("---")


# VISUALIZATIONS (3 Plots)

st.subheader("📊 Filtered Passenger Visualizations")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Chart 1: Survival Rate by Passenger Class (Bar Chart)
    st.markdown("##### 1. Survival Rate by Passenger Class")
    if not filtered_df.empty:
        survival_summary = (
            filtered_df.groupby("Pclass_Label")["Survived"]
            .mean()
            .reset_index()
        )
        fig_bar = px.bar(
            survival_summary,
            x="Pclass_Label",
            y="Survived",
            labels={"Pclass_Label": "Ticket Class", "Survived": "Survival Rate"},
            color="Pclass_Label",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_bar.update_layout(yaxis_range=[0, 1])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No data available for selected filters.")

with chart_col2:
    # Chart 2: Fare Distribution across Classes (Box Plot)
    st.markdown("##### 2. Fare Distribution by Passenger Class")
    if not filtered_df.empty:
        fig_box = px.box(
            filtered_df,
            x="Pclass_Label",
            y="Fare",
            color="Pclass_Label",
            labels={"Pclass_Label": "Ticket Class", "Fare": "Fare ($)"},
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No data available for selected filters.")

# Chart 3: Age vs Fare Scatter Plot
st.markdown("##### 3. Ticket Fare vs. Passenger Age (by Survival)")
if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df,
        x="Age",
        y="Fare",
        color="Survival_Label",
        hover_data=["Name", "Port_Name"],
        labels={"Age": "Age (Years)", "Fare": "Ticket Fare ($)"},
        color_discrete_map={"Perished": "#EF553B", "Survived": "#00CC96"},
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")


# DATA TABLE

st.subheader("📋 Interactive Data Table")
st.markdown(f"Displaying **{len(filtered_df)}** matching passenger records:")

st.dataframe(
    filtered_df[
        [
            "PassengerId",
            "Name",
            "Sex",
            "Age",
            "Pclass_Label",
            "Fare",
            "Port_Name",
            "Survival_Label",
        ]
    ],
    use_container_width=True,
)
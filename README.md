# API-Integrated Interactive Titanic & Port Weather Dashboard

## 1. Live Public Dashboard URL
* Deployed Dashboard URL:`titanic-analytics-part3-dashboardgit-kcczsy4bsdqf9dgg9jkcha.streamlit.app` 

---

## 2. Integrated REST API Explanation

### External API Details
* Service:Open-Meteo Weather Forecast API
* Endpoint URL:`https://api.open-meteo.com/v1/forecast`
* HTTP Method Used:`GET`

### Explanation of HTTP Method & Payload
* Why `GET` is used:A `GET` request is used because the client is requesting data from an external server without modifying state, creating new records, or passing sensitive form bodies. Parameters (`latitude`, `longitude`, `current`) are passed directly via URL query parameters.
* API Response Payload:The API returns a structured JSON payload containing real-time meteorology metrics for the specified geographic coordinates.
* Fields Extracted & Displayed:
  * `temperature_2m`: Current air temperature measured 2 meters above ground (displayed in °C).
  * `relative_humidity_2m`: Current relative humidity percentage (displayed in %).
  * `wind_speed_10m`: Current wind speed at 10 meters height (displayed in km/h).

---

## 3. Interactive Dashboard Components

1. Input Widgets (`st.multiselect`, `st.slider`):
   * Multi-select dropdown for departure ports (`Port_Name`).
   * Multi-select dropdown for ticket class (`1st`, `2nd`, `3rd Class`).
   * Range slider for filtering passenger ticket fares (`Fare`).

2. Visualizations (Plotly / Streamlit):
   * Chart 1 (Bar):Average survival rate grouped by passenger ticket class.
   * Chart 2 (Box):Distribution of ticket fares across different class tiers.
   * Chart 3 (Scatter):Relationship between passenger age and ticket fare colored by survival outcome.

3. Live Data Table (`st.dataframe`):
   * Reactively updates to display all individual passenger records matching the widget filters.

---

## 4. Attribution
Weather data provided by [Open-Meteo.com](https://open-meteo.com/) under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(
    page_title="S&P 500",
    page_icon="📊",
    layout="wide"
)

st.markdown("<h1 style='text-align: center;'>📊 S&P 500 Company Financials</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Explore sectors, EPS, and P/E ratios!</h4>", unsafe_allow_html=True)
st.markdown('**Data source:** [S&P 500 Companies – Constituents Financials (Kaggle)](https://www.kaggle.com/datasets/priteshraj10/sp-500-companies)')


df = pd.read_csv("sp500_clean.csv")
st.write("")

st.markdown("### Raw data")
st.dataframe(df)  

st.write("")
st.divider()
st.write("")

st.markdown("### Filter by Sector and P/E Ratio")
st.write("Filter from the sidebar to see companies in a specific sector:")
st.sidebar.header("Filter by Sector")

sector = st.sidebar.selectbox("Select a sector:", sorted(df["Sector"].unique()))

pe_max = st.sidebar.slider("Max P/E", 
                           float(df["Price/Earnings"].min()), 
                           float(df["Price/Earnings"].max()), 
                           float(df["Price/Earnings"].quantile(0.75)))


filtered = df[(df["Sector"]==sector) & (df["Price/Earnings"] <= pe_max)]
st.dataframe(filtered)

sectors = st.sidebar.multiselect("Select multiple sectors:", sorted(df["Sector"].unique()))
if st.sidebar.button("Show"):
    filtered = df[df["Sector"].isin(sectors)] if sectors else df
    st.dataframe(filtered)


st.write("")
st.divider()
st.write("")

st.markdown("### Strong Stocks: High EPS & Low P/E Ratio")

def get_strong_stocks(df):
    eps_median = df["Earnings/Share"].median()
    pe_median = df["Price/Earnings"].median()
    return df[(df["Earnings/Share"] > eps_median) & (df["Price/Earnings"] < pe_median)]

sc = alt.Chart(filtered).mark_circle().encode(
    x="Price/Earnings:Q",
    y="Earnings/Share:Q",
    color="Sector:N",
    tooltip=["Name","Sector","Earnings/Share","Price/Earnings"]
).interactive()
st.altair_chart(sc, use_container_width=True)


strong_stocks = get_strong_stocks(df)

st.sidebar.divider()


st.sidebar.markdown("### Strong Stocks Filter")
strong_sector = st.sidebar.selectbox(
    "Select Sector for Strong Stocks:",
    ["All"] + sorted(strong_stocks["Sector"].unique())
)

if strong_sector == "All":
    filtered_strong = strong_stocks
else:
    filtered_strong = strong_stocks[strong_stocks["Sector"] == strong_sector]


st.write(f"Showing **{len(filtered_strong)}** strong companies in sector: **{strong_sector}**")
st.dataframe(filtered_strong[["Name", "Sector", "Earnings/Share", "Price/Earnings"]])


st.write("")
st.divider()
st.write("")

st.markdown("### Number of Companies per Sector")
sector_counts = df["Sector"].value_counts().reset_index()
sector_counts.columns = ["Sector", "Count"]

base = alt.Chart(sector_counts).encode(
    y=alt.Y("Sector:N", sort='-x'),
    x=alt.X("Count:Q")
)

bars = base.mark_bar().encode(
    color=alt.Color("Sector:N", scale=alt.Scale(scheme="set2"), legend=None)
)
labels = base.mark_text(align="left", dx=3).encode(text="Count:Q")

st.altair_chart(bars + labels, use_container_width=True)

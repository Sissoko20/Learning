# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Analyse automatique de vos données")

uploaded_file = st.file_uploader("Chargez un fichier CSV ou Excel", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Aperçu des données :", df.head())

    col1 = st.selectbox("Colonne pour l'axe X", df.columns)
    col2 = st.selectbox("Colonne pour l'axe Y", df.columns)

    fig = px.bar(df, x=col1, y=col2, title=f"{col2} par {col1}")
    st.plotly_chart(fig)

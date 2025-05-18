import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analyse de ventes", layout="wide")
st.title("📊 Analyse automatique de vos données de vente")

uploaded_file = st.file_uploader("📁 Chargez un fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du fichier : {e}")
        st.stop()

    st.success("✅ Fichier chargé avec succès")
    st.write("🧾 Aperçu des données :", df.head())

    # ---- SIDEBAR : FILTRES ----
    st.sidebar.header("🎛️ Filtres dynamiques")

    # Filtre par date si colonne existe
    if 'Date' in df.columns:
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
            min_date, max_date = df['Date'].min(), df['Date'].max()
            date_range = st.sidebar.date_input("📅 Filtrer par date", [min_date, max_date])
            if len(date_range) == 2:
                df = df[(df['Date'] >= pd.to_datetime(date_range[0])) & (df['Date'] <= pd.to_datetime(date_range[1]))]
        except Exception:
            st.sidebar.warning("⚠️ Problème avec la colonne 'Date'")

    # Filtre par produit si colonne existe
    if 'Produit' in df.columns:
        produits = df['Produit'].dropna().unique().tolist()
        selected_produits = st.sidebar.multiselect("🛍️ Filtrer par produit", produits, default=produits)
        df = df[df['Produit'].isin(selected_produits)]

    # ---- SELECTION COLONNES POUR GRAPHIQUES ----
    if len(df.columns) >= 2:
        # Choix de la colonne numérique pour les valeurs Y
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if not numeric_cols:
            st.warning("⚠️ Aucune colonne numérique disponible pour l'axe Y.")
        else:
            y_col = st.selectbox("📐 Colonne pour valeurs numériques (axe Y)", numeric_cols)

            # Colonnes pour regrouper (X, couleur, ...)
            group_cols = st.multiselect("🧩 Colonnes de regroupement (axe X, couleur, etc.)", df.columns.tolist())

            chart_type = st.selectbox("📊 Type de graphique", ["Barres", "Lignes", "Camembert"])

            if group_cols:
                grouped_df = df.groupby(group_cols)[y_col].sum().reset_index()

                fig = None
                if chart_type == "Barres":
                    fig = px.bar(
                        grouped_df, 
                        x=group_cols[0], 
                        y=y_col, 
                        color=group_cols[1] if len(group_cols) > 1 else None
                    )
                elif chart_type == "Lignes":
                    fig = px.line(
                        grouped_df, 
                        x=group_cols[0], 
                        y=y_col, 
                        color=group_cols[1] if len(group_cols) > 1 else None,
                        markers=True
                    )
                elif chart_type == "Camembert":
                    if len(group_cols) == 1:
                        fig = px.pie(
                            grouped_df,
                            names=group_cols[0],
                            values=y_col
                        )
                    else:
                        st.warning("📛 Le camembert ne supporte qu’un seul regroupement.")

                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Sélectionnez au moins une colonne de regroupement pour générer un graphique.")

    else:
        st.info("📌 Pas assez de colonnes pour générer un graphique.")

    # ---- EXPORT ----
    st.subheader("💾 Exporter les données filtrées")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger le CSV filtré", data=csv, file_name="donnees_filtrees.csv", mime='text/csv')

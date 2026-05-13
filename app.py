import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Dashboard Yassir - Business Intelligence", layout="wide")
st.title("📊 Dashboard Stratégique & Opérationnel")

# --- Zone d'upload ---
uploaded_file = st.file_uploader("Uploadez votre fichier CSV (Export Admin)", type=['csv'])

if uploaded_file is not None:
    # 1. Lecture et Nettoyage des données
    df = pd.read_csv(uploaded_file, low_memory=False)
    
    # Nettoyage de base pour s'assurer que les valeurs financières sont des nombres
    df['item total'] = pd.to_numeric(df['item total'], errors='coerce').fillna(0)
    df['delivery time(M)'] = pd.to_numeric(df['delivery time(M)'], errors='coerce')
    
    # Création des 3 onglets
    tab_sales, tab_marketing, tab_ops = st.tabs(["💰 Sales (Ventes)", "🎯 Marketing", "⚙️ Opérations (Logistique)"])

    # ==========================================
    # ONGLET 1 : SALES (VENTES & PERFORMANCES)
    # ==========================================
    with tab_sales:
        st.header("Analyse des Ventes (GMV, AOV, Volume)")
        
        # --- KPIs SALES ---
        requests = len(df)
        delivered = len(df[df['status'] == 'Delivered'])
        gmv = df['item total'].sum()
        aov = gmv / requests if requests > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Requests (Total Commandes)", f"{requests:,}")
        col2.metric("Delivered (Livrées)", f"{delivered:,}")
        col3.metric("GMV (Chiffre d'Affaires)", f"{gmv:,.2f} MAD")
        col4.metric("AOV (Panier Moyen)", f"{aov:,.2f} MAD")
        st.divider()

        # --- CHARTS : TOP 10 RESTAURANTS ---
        st.subheader("🏆 Top 10 Restaurants")
        # Agrégation par restaurant
        rest_stats = df.groupby('restaurant name').agg(
            Requests=('order id', 'count'),
            GMV=('item total', 'sum')
        ).reset_index()
        rest_stats['AOV'] = rest_stats['GMV'] / rest_stats['Requests']

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            top_gmv = rest_stats.nlargest(10, 'GMV')
            fig_r1 = px.bar(top_gmv, x='GMV', y='restaurant name', orientation='h', title="Par GMV", color='GMV', color_continuous_scale='Blues')
            fig_r1.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r1, use_container_width=True)
            
        with col_r2:
            top_aov = rest_stats.nlargest(10, 'AOV')
            fig_r2 = px.bar(top_aov, x='AOV', y='restaurant name', orientation='h', title="Par AOV (Panier Moyen)", color='AOV', color_continuous_scale='Greens')
            fig_r2.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r2, use_container_width=True)

        with col_r3:
            top_req = rest_stats.nlargest(10, 'Requests')
            fig_r3 = px.bar(top_req, x='Requests', y='restaurant name', orientation='h', title="Par Requests (Volume)", color='Requests', color_continuous_scale='Oranges')
            fig_r3.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r3, use_container_width=True)

        st.divider()

        # --- CHARTS : CITY & AREA ---
        st.subheader("📍 Performance par Ville et Quartier (City & Area)")
        
        # Agrégation par Ville
        city_stats = df.groupby('city').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
        city_stats['AOV'] = city_stats['GMV'] / city_stats['Requests']
        
        # Agrégation par Area
        area_stats = df.groupby('Area').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
        area_stats['AOV'] = area_stats['GMV'] / area_stats['Requests']

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_city = px.bar(city_stats, x='city', y=['GMV', 'Requests', 'AOV'], barmode='group', title="Métriques par Ville (City)")
            st.plotly_chart(fig_city, use_container_width=True)
        with col_c2:
            fig_area = px.scatter(area_stats, x='Requests', y='GMV', size='AOV', color='Area', title="Quartiers (Area) : GMV vs Requests (Taille = AOV)")
            st.plotly_chart(fig_area, use_container_width=True)

        st.divider()

        # --- TABLEAU DE BORD RESTAURANTS (AVEC FILTRES) ---
        st.subheader("📋 Listing Détaillé des Restaurants")
        
        # Filtres UI
        col_f1, col_f2 = st.columns(2)
        ville_filter = col_f1.multiselect("Filtrer par Ville", options=df['city'].dropna().unique())
        area_filter = col_f2.multiselect("Filtrer par Quartier", options=df['Area'].dropna().unique())
        
        # Application des filtres sur la donnée brute
        df_filtered = df.copy()
        if ville_filter:
            df_filtered = df_filtered[df_filtered['city'].isin(ville_filter)]
        if area_filter:
            df_filtered = df_filtered[df_filtered['Area'].isin(area_filter)]

        # Création du tableau final
        table_rest = df_filtered.groupby(['restaurant name', 'city', 'Area']).agg(
            Requests=('order id', 'count'),
            Delivered=('status', lambda x: (x == 'Delivered').sum()),
            GMV=('item total', 'sum')
        ).reset_index()
        table_rest['AOV'] = (table_rest['GMV'] / table_rest['Requests']).round(2)
        table_rest['Taux de Livraison (%)'] = ((table_rest['Delivered'] / table_rest['Requests']) * 100).round(1)
        
        # Affichage du tableau interactif (Streamlit permet de trier en cliquant sur les colonnes)
        st.dataframe(table_rest.sort_values(by='GMV', ascending=False), use_container_width=True)


    # ==========================================
    # ONGLET 2 : MARKETING (ACQUISITION & PROMOS)
    # ==========================================
    with tab_marketing:
        st.header("Marketing : Utilisateurs & Promotions")
        
        # KPIs Marketing
        unique_users = df['customer Phone'].nunique() # Proxy pour les utilisateurs uniques
        total_coupons_used = len(df[df['coupon'].notna() & (df['coupon'] != ' ')])
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Utilisateurs Uniques (Reach)", f"{unique_users:,}")
        col_m2.metric("Commandes avec Code Promo", f"{total_coupons_used:,}")
        col_m3.metric("Ratio d'utilisation Promo", f"{(total_coupons_used / requests * 100):.1f} %")
        st.divider()

        # Analyse des Coupons
        st.subheader("🎟️ Performance des Codes Promo (Coupons)")
        df_coupons = df[df['coupon'].notna() & (df['coupon'] != ' ')]
        
        if not df_coupons.empty:
            coupon_stats = df_coupons.groupby('coupon').agg(
                Utilisations=('order id', 'count'),
                Total_Discount=('Discount Amount', 'sum')
            ).reset_index()
            
            col_m4, col_m5 = st.columns(2)
            with col_m4:
                fig_coup1 = px.bar(coupon_stats.nlargest(10, 'Utilisations'), x='Utilisations', y='coupon', orientation='h', title="Top 10 Coupons (par Utilisation)", color='Utilisations', color_continuous_scale='Purples')
                fig_coup1.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_coup1, use_container_width=True)
            with col_m5:
                fig_coup2 = px.bar(coupon_stats.nlargest(10, 'Total_Discount'), x='Total_Discount', y='coupon', orientation='h', title="Coût par Coupon (Total Discount)", color='Total_Discount', color_continuous_scale='Reds')
                fig_coup2.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_coup2, use_container_width=True)
        else:
            st.info("Aucune donnée de coupon (Code Promo) trouvée dans cet export.")


    # ==========================================
    # ONGLET 3 : OPÉRATIONS (LOGISTIQUE & LIVRAISONS)
    # ==========================================
    with tab_ops:
        st.header("Opérations : Logistique, Flotte & Annulations")
        
        # KPIs Ops
        avg_delivery_time = df['delivery time(M)'].mean()
        cancellations = len(df[df['status'] == 'Cancelled'])
        cancel_rate = (cancellations / requests * 100) if requests > 0 else 0
        
        col_o1, col_o2, col_o3, col_o4 = st.columns(4)
        col_o1.metric("Temps de Livraison Moyen", f"{avg_delivery_time:.1f} min")
        col_o2.metric("Distance Moyenne", f"{df['Distance travel'].mean():.2f} km")
        col_o3.metric("Commandes Annulées", f"{cancellations:,}")
        col_o4.metric("Taux d'Annulation", f"{cancel_rate:.2f} %")
        st.divider()

        # Graphiques Ops
        col_o5, col_o6 = st.columns(2)
        
        with col_o5:
            st.subheader("⚠️ Motifs d'Annulation (Cancellation Reasons)")
            df_cancel = df[df['cancellation reason '].notna() & (df['cancellation reason '] != ' ') & (df['cancellation reason '] != 'N/A')]
            if not df_cancel.empty:
                cancel_stats = df_cancel['cancellation reason '].value_counts().reset_index()
                cancel_stats.columns = ['Motif', 'Nombre']
                fig_cancel = px.pie(cancel_stats, values='Nombre', names='Motif', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_cancel, use_container_width=True)
            else:
                st.info("Pas assez de données sur les motifs d'annulation.")

        with col_o6:
            st.subheader("🛵 Performance par Type de Coursier")
            driver_stats = df.groupby('Driver Type').agg(
                Commandes=('order id', 'count'),
                Temps_Moyen=('delivery time(M)', 'mean')
            ).reset_index()
            fig_driver = px.bar(driver_stats, x='Driver Type', y=['Commandes', 'Temps_Moyen'], barmode='group', title="Volume vs Temps de livraison par Contrat")
            st.plotly_chart(fig_driver, use_container_width=True)

        st.subheader("⏱️ Distribution des Temps de Livraison")
        fig_time = px.histogram(df, x='delivery time(M)', nbins=40, title="Répartition du temps de livraison (en minutes)", color_discrete_sequence=['#1ABC9C'])
        st.plotly_chart(fig_time, use_container_width=True)

else:
    st.info("Veuillez uploader un fichier CSV pour générer l'analyse complète (Sales, Marketing, Ops).")

import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Dashboard Yassir | BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FONCTION DE CHARGEMENT OPTIMISÉE (CACHE) ---
# Le cache permet de ne pas recharger le fichier lourd à chaque clic
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, low_memory=False)
    # Nettoyage des données numériques
    df['item total'] = pd.to_numeric(df['item total'], errors='coerce').fillna(0)
    df['delivery time(M)'] = pd.to_numeric(df['delivery time(M)'], errors='coerce')
    df['Discount Amount'] = pd.to_numeric(df['Discount Amount'], errors='coerce').fillna(0)
    return df

# --- 3. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("Veuillez uploader votre export Admin pour mettre à jour le tableau de bord.")
    uploaded_file = st.file_uploader("Export CSV", type=['csv'], label_visibility="collapsed")
    st.divider()
    st.markdown("💡 **Astuce :** Naviguez entre les onglets pour voir les données spécifiques à chaque département.")

# --- 4. CORPS DE L'APPLICATION ---
if uploaded_file is None:
    # UX : Message d'accueil propre quand aucun fichier n'est chargé
    st.title("Bienvenue sur votre Dashboard de Business Intelligence 👋")
    st.info("👈 Commencez par importer votre fichier de données dans la barre latérale pour générer les analyses.")
else:
    # Chargement des données
    df = load_data(uploaded_file)
    
    # En-tête principal
    st.title("📊 Tableau de Bord Opérationnel & Stratégique")
    st.markdown(f"**Données analysées :** {len(df):,} commandes au total.")
    st.write("") # Espace

    # Création des onglets
    tab_sales, tab_marketing, tab_ops = st.tabs([
        "💰 Sales & Performances", 
        "🎯 Marketing & Acquisition", 
        "⚙️ Logistique & Opérations"
    ])

    # ==========================================
    # ONGLET 1 : SALES
    # ==========================================
    with tab_sales:
        st.subheader("Indicateurs Clés de Performance (KPIs)")
        
        # Calculs KPIs
        requests = len(df)
        delivered = len(df[df['status'] == 'Delivered'])
        gmv = df['item total'].sum()
        aov = gmv / requests if requests > 0 else 0
        
        # Affichage KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Requests (Commandes)", f"{requests:,}")
        col2.metric("Delivered (Livrées)", f"{delivered:,}")
        col3.metric("GMV (Chiffre d'Affaires)", f"{gmv:,.0f} MAD")
        col4.metric("AOV (Panier Moyen)", f"{aov:,.2f} MAD")
        
        st.markdown("---")

        # --- Ligne 1 : Villes et Quartiers ---
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            city_stats = df.groupby('city').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
            fig_city = px.bar(city_stats, x='city', y=['GMV', 'Requests'], barmode='group', 
                              title="Performance globale par Ville", template="plotly_white")
            st.plotly_chart(fig_city, use_container_width=True)
            
        with col_c2:
            area_stats = df.groupby('Area').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
            area_stats['AOV'] = area_stats['GMV'] / area_stats['Requests']
            fig_area = px.scatter(area_stats, x='Requests', y='GMV', size='AOV', color='Area', 
                                  title="Performance par Quartier (Taille = AOV)", template="plotly_white")
            st.plotly_chart(fig_area, use_container_width=True)

        # --- Ligne 2 : Top Restaurants ---
        st.subheader("🏆 Classement des Restaurants")
        rest_stats = df.groupby('restaurant name').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
        rest_stats['AOV'] = rest_stats['GMV'] / rest_stats['Requests']

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            fig_r1 = px.bar(rest_stats.nlargest(10, 'GMV'), x='GMV', y='restaurant name', orientation='h', 
                            title="Top 10 par GMV", template="plotly_white", color_discrete_sequence=['#2E86C1'])
            fig_r1.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r1, use_container_width=True)
            
        with col_r2:
            fig_r2 = px.bar(rest_stats.nlargest(10, 'AOV'), x='AOV', y='restaurant name', orientation='h', 
                            title="Top 10 par AOV", template="plotly_white", color_discrete_sequence=['#27AE60'])
            fig_r2.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r2, use_container_width=True)

        with col_r3:
            fig_r3 = px.bar(rest_stats.nlargest(10, 'Requests'), x='Requests', y='restaurant name', orientation='h', 
                            title="Top 10 par Volume", template="plotly_white", color_discrete_sequence=['#E67E22'])
            fig_r3.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r3, use_container_width=True)

        st.markdown("---")

        # --- Ligne 3 : Tableau interactif ---
        st.subheader("📋 Répertoire Détaillé des Restaurants")
        
        # UX : Filtres dans un Expander pour ne pas polluer l'écran
        with st.expander("🔍 Ouvrir les filtres du tableau"):
            col_f1, col_f2 = st.columns(2)
            ville_filter = col_f1.multiselect("Filtrer par Ville", options=df['city'].dropna().unique())
            area_filter = col_f2.multiselect("Filtrer par Quartier", options=df['Area'].dropna().unique())
        
        df_filtered = df.copy()
        if ville_filter: df_filtered = df_filtered[df_filtered['city'].isin(ville_filter)]
        if area_filter: df_filtered = df_filtered[df_filtered['Area'].isin(area_filter)]

        table_rest = df_filtered.groupby(['restaurant name', 'city', 'Area']).agg(
            Requests=('order id', 'count'),
            Delivered=('status', lambda x: (x == 'Delivered').sum()),
            GMV=('item total', 'sum')
        ).reset_index()
        table_rest['AOV (MAD)'] = (table_rest['GMV'] / table_rest['Requests']).round(2)
        table_rest['Taux Livraison (%)'] = ((table_rest['Delivered'] / table_rest['Requests']) * 100).round(1)
        
        st.dataframe(table_rest.sort_values(by='GMV', ascending=False), use_container_width=True, hide_index=True)


    # ==========================================
    # ONGLET 2 : MARKETING
    # ==========================================
    with tab_marketing:
        st.subheader("Acquisition & Rétention")
        
        unique_users = df['customer Phone'].nunique()
        total_coupons_used = len(df[df['coupon'].notna() & (df['coupon'] != ' ')])
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("👥 Utilisateurs Uniques", f"{unique_users:,}")
        col_m2.metric("🎟️ Commandes Promo", f"{total_coupons_used:,}")
        col_m3.metric("📉 Taux d'utilisation Promo", f"{(total_coupons_used / requests * 100):.1f} %")
        
        st.markdown("---")
        
        df_coupons = df[df['coupon'].notna() & (df['coupon'] != ' ')]
        if not df_coupons.empty:
            coupon_stats = df_coupons.groupby('coupon').agg(
                Utilisations=('order id', 'count'),
                Total_Discount=('Discount Amount', 'sum')
            ).reset_index()
            
            col_m4, col_m5 = st.columns(2)
            with col_m4:
                fig_coup1 = px.bar(coupon_stats.nlargest(10, 'Utilisations'), x='Utilisations', y='coupon', orientation='h', 
                                   title="Coupons les plus utilisés", template="plotly_white", color_discrete_sequence=['#8E44AD'])
                fig_coup1.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_coup1, use_container_width=True)
            with col_m5:
                fig_coup2 = px.bar(coupon_stats.nlargest(10, 'Total_Discount'), x='Total_Discount', y='coupon', orientation='h', 
                                   title="Coût par Coupon (MAD)", template="plotly_white", color_discrete_sequence=['#C0392B'])
                fig_coup2.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_coup2, use_container_width=True)
        else:
            st.info("Aucune donnée de code promo (coupon) trouvée.")


    # ==========================================
    # ONGLET 3 : OPÉRATIONS
    # ==========================================
    with tab_ops:
        st.subheader("Performance Logistique de la Flotte")
        
        avg_delivery_time = df['delivery time(M)'].mean()
        cancellations = len(df[df['status'] == 'Cancelled'])
        cancel_rate = (cancellations / requests * 100) if requests > 0 else 0
        
        col_o1, col_o2, col_o3, col_o4 = st.columns(4)
        col_o1.metric("⏱️ Temps de Livraison", f"{avg_delivery_time:.1f} min")
        col_o2.metric("📏 Distance Moyenne", f"{df['Distance travel'].mean():.2f} km")
        col_o3.metric("❌ Commandes Annulées", f"{cancellations:,}")
        col_o4.metric("📉 Taux d'Annulation", f"{cancel_rate:.2f} %")
        
        st.markdown("---")

        col_o5, col_o6 = st.columns(2)
        with col_o5:
            df_cancel = df[df['cancellation reason '].notna() & (df['cancellation reason '] != ' ') & (df['cancellation reason '] != 'N/A')]
            if not df_cancel.empty:
                cancel_stats = df_cancel['cancellation reason '].value_counts().reset_index()
                cancel_stats.columns = ['Motif', 'Nombre']
                fig_cancel = px.pie(cancel_stats, values='Nombre', names='Motif', hole=0.4, 
                                    title="Répartition des motifs d'annulation", template="plotly_white")
                st.plotly_chart(fig_cancel, use_container_width=True)

        with col_o6:
            driver_stats = df.groupby('Driver Type').agg(
                Commandes=('order id', 'count'),
                Temps_Moyen=('delivery time(M)', 'mean')
            ).reset_index()
            fig_driver = px.bar(driver_stats, x='Driver Type', y='Commandes', color='Temps_Moyen', 
                                title="Volume vs Temps par Contrat Livreurs", template="plotly_white")
            st.plotly_chart(fig_driver, use_container_width=True)

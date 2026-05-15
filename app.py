import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Dashboard Yassir | BI & Supply",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FONCTION DE CHARGEMENT OPTIMISÉE (CACHE) ---
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, low_memory=False)
    # Nettoyage des données
    df['item total'] = pd.to_numeric(df['item total'], errors='coerce').fillna(0)
    df['delivery time(M)'] = pd.to_numeric(df['delivery time(M)'], errors='coerce')
    df['Discount Amount'] = pd.to_numeric(df['Discount Amount'], errors='coerce').fillna(0)
    df['Distance travel'] = pd.to_numeric(df['Distance travel'], errors='coerce')
    return df

# --- 3. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Configuration")
    uploaded_file = st.file_uploader("Uploadez l'Export CSV", type=['csv'], label_visibility="collapsed")
    st.divider()
    st.markdown("💡 **Astuce :** Le tableau de bord est divisé en 3 piliers stratégiques.")

# --- 4. CORPS DE L'APPLICATION ---
if uploaded_file is None:
    st.title("Bienvenue sur votre Dashboard de Business Intelligence 👋")
    st.info("👈 Veuillez uploader votre fichier CSV dans la barre latérale pour commencer.")
else:
    df = load_data(uploaded_file)
    
    st.title("📊 Tableau de Bord Stratégique & Opérationnel")
    st.write("") # Espace

    tab_sales, tab_marketing, tab_ops = st.tabs([
        "💰 Sales & Performances", 
        "🎯 Marketing & Acquisition", 
        "⚙️ Supply & Logistique (Ops)"
    ])

    # ==========================================
    # ONGLET 1 : SALES
    # ==========================================
    with tab_sales:
        st.subheader("Indicateurs Clés de Performance (KPIs)")
        
        requests = len(df)
        delivered = len(df[df['status'] == 'Delivered'])
        gmv = df['item total'].sum()
        aov = gmv / requests if requests > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Requests (Total)", f"{requests:,}")
        col2.metric("Delivered (Livrées)", f"{delivered:,}")
        col3.metric("GMV (Chiffre d'Affaires)", f"{gmv:,.0f} MAD")
        col4.metric("AOV (Panier Moyen)", f"{aov:,.2f} MAD")
        st.markdown("---")

        # --- City Charts ---
        st.subheader("📍 Performance par Ville (City)")
        city_stats = df.groupby('city').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
        city_stats['AOV'] = city_stats['GMV'] / city_stats['Requests']

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            fig_c1 = px.bar(city_stats.sort_values('GMV', ascending=False), x='city', y='GMV', title="GMV by City", template="plotly_white", color_discrete_sequence=['#2980B9'])
            st.plotly_chart(fig_c1, use_container_width=True)
        with col_c2:
            fig_c2 = px.bar(city_stats.sort_values('AOV', ascending=False), x='city', y='AOV', title="AOV by City", template="plotly_white", color_discrete_sequence=['#27AE60'])
            st.plotly_chart(fig_c2, use_container_width=True)
        with col_c3:
            fig_c3 = px.bar(city_stats.sort_values('Requests', ascending=False), x='city', y='Requests', title="Requests by City", template="plotly_white", color_discrete_sequence=['#E67E22'])
            st.plotly_chart(fig_c3, use_container_width=True)

        st.markdown("---")

        # --- Area Charts ---
        st.subheader("🏘️ Performance par Quartier (Area) - Top 15")
        area_stats = df.groupby('Area').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
        area_stats['AOV'] = area_stats['GMV'] / area_stats['Requests']
        # Top 15 pour garder les graphiques lisibles
        top_areas = area_stats.nlargest(15, 'Requests')

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            fig_a1 = px.bar(top_areas.sort_values('GMV', ascending=False), x='Area', y='GMV', title="GMV by Area", template="plotly_white", color_discrete_sequence=['#3498DB'])
            st.plotly_chart(fig_a1, use_container_width=True)
        with col_a2:
            fig_a2 = px.bar(top_areas.sort_values('AOV', ascending=False), x='Area', y='AOV', title="AOV by Area", template="plotly_white", color_discrete_sequence=['#2ECC71'])
            st.plotly_chart(fig_a2, use_container_width=True)
        with col_a3:
            fig_a3 = px.bar(top_areas.sort_values('Requests', ascending=False), x='Area', y='Requests', title="Requests by Area", template="plotly_white", color_discrete_sequence=['#F39C12'])
            st.plotly_chart(fig_a3, use_container_width=True)

        st.markdown("---")

        # --- Top 10 Restaurants Charts ---
        st.subheader("🏆 Classement des Restaurants")
        rest_stats = df.groupby('restaurant name').agg(Requests=('order id', 'count'), GMV=('item total', 'sum')).reset_index()
        rest_stats['AOV'] = rest_stats['GMV'] / rest_stats['Requests']

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            fig_r1 = px.bar(rest_stats.nlargest(10, 'GMV'), x='GMV', y='restaurant name', orientation='h', title="Top 10 by GMV", template="plotly_white", color_discrete_sequence=['#8E44AD'])
            fig_r1.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r1, use_container_width=True)
        with col_r2:
            fig_r2 = px.bar(rest_stats.nlargest(10, 'AOV'), x='AOV', y='restaurant name', orientation='h', title="Top 10 by AOV", template="plotly_white", color_discrete_sequence=['#16A085'])
            fig_r2.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r2, use_container_width=True)
        with col_r3:
            fig_r3 = px.bar(rest_stats.nlargest(10, 'Requests'), x='Requests', y='restaurant name', orientation='h', title="Top 10 by Requests", template="plotly_white", color_discrete_sequence=['#D35400'])
            fig_r3.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_r3, use_container_width=True)

        st.markdown("---")

        # --- Tableau des Restaurants ---
        st.subheader("📋 Répertoire Détaillé des Restaurants")
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
        col_m1.metric("👥 New / Unique Users (Reach)", f"{unique_users:,}")
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
                fig_coup1 = px.bar(coupon_stats.nlargest(10, 'Utilisations'), x='Utilisations', y='coupon', orientation='h', title="Coupons les plus utilisés", template="plotly_white", color_discrete_sequence=['#8E44AD'])
                fig_coup1.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_coup1, use_container_width=True)
            with col_m5:
                fig_coup2 = px.bar(coupon_stats.nlargest(10, 'Total_Discount'), x='Total_Discount', y='coupon', orientation='h', title="Coût par Coupon (MAD)", template="plotly_white", color_discrete_sequence=['#C0392B'])
                fig_coup2.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_coup2, use_container_width=True)


    # ==========================================
    # ONGLET 3 : SUPPLY & OPÉRATIONS (Enrichi)
    # ==========================================
    with tab_ops:
        st.subheader("Performance de la Flotte (Supply)")
        
        avg_delivery_time = df['delivery time(M)'].mean()
        cancellations = len(df[df['status'] == 'Cancelled'])
        cancel_rate = (cancellations / requests * 100) if requests > 0 else 0
        total_payout = df['driver payout'].sum()
        
        col_o1, col_o2, col_o3, col_o4 = st.columns(4)
        col_o1.metric("⏱️ Temps de Livraison Moyen", f"{avg_delivery_time:.1f} min")
        col_o2.metric("📏 Distance Moyenne", f"{df['Distance travel'].mean():.2f} km")
        col_o3.metric("📉 Taux d'Annulation", f"{cancel_rate:.2f} %")
        col_o4.metric("💸 Total Driver Payout", f"{total_payout:,.0f} MAD")
        st.markdown("---")

        # --- LIGNE 1 : Rush Hours & Distribution du temps ---
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            # Commandes par heure
            df['hour'] = pd.to_datetime(df['order time'], format='%H:%M:%S', errors='coerce').dt.hour
            hour_stats = df['hour'].value_counts().sort_index().reset_index()
            hour_stats.columns = ['Heure', 'Commandes']
            fig_rush = px.bar(hour_stats, x='Heure', y='Commandes', title="Rush Hours (Commandes par Heure)", template="plotly_white", color_discrete_sequence=['#E74C3C'])
            st.plotly_chart(fig_rush, use_container_width=True)
            
        with col_s2:
            # Distribution des temps de livraison
            fig_time_dist = px.histogram(df, x='delivery time(M)', nbins=40, title="Distribution des Temps de Livraison (min)", template="plotly_white", color_discrete_sequence=['#1ABC9C'])
            st.plotly_chart(fig_time_dist, use_container_width=True)

        st.markdown("---")

        # --- LIGNE 2 : Top Livreurs & Efficacité ---
        col_s3, col_s4 = st.columns(2)
        with col_s3:
            # Top 10 Livreurs
            top_drivers = df['driver name'].value_counts().head(10).reset_index()
            top_drivers.columns = ['Livreur', 'Courses']
            fig_drivers = px.bar(top_drivers, x='Courses', y='Livreur', orientation='h', title="Top 10 Livreurs (par Volume de courses)", template="plotly_white", color_discrete_sequence=['#F39C12'])
            fig_drivers.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_drivers, use_container_width=True)

        with col_s4:
            # Efficacité : Distance vs Temps
            fig_scatter = px.scatter(df, x='Distance travel', y='delivery time(M)', color='Driver Type', title="Efficacité : Temps de Trajet vs Distance", template="plotly_white")
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("---")

        # --- LIGNE 3 : Annulations & Type de Contrat ---
        col_s5, col_s6 = st.columns(2)
        with col_s5:
            # Motifs d'annulation
            df_cancel = df[df['cancellation reason '].notna() & (df['cancellation reason '] != ' ') & (df['cancellation reason '] != 'N/A')]
            if not df_cancel.empty:
                cancel_stats = df_cancel['cancellation reason '].value_counts().reset_index()
                cancel_stats.columns = ['Motif', 'Nombre']
                fig_cancel = px.pie(cancel_stats, values='Nombre', names='Motif', hole=0.4, title="Répartition des motifs d'annulation", template="plotly_white")
                st.plotly_chart(fig_cancel, use_container_width=True)

        with col_s6:
            # Performance par contrat
            driver_contract = df.groupby('Driver Type').agg(Commandes=('order id', 'count'), Temps_Moyen=('delivery time(M)', 'mean')).reset_index()
            fig_contract = px.bar(driver_contract, x='Driver Type', y='Commandes', color='Temps_Moyen', title="Volume par Type de Contrat (Couleur = Temps Moyen)", template="plotly_white")
            st.plotly_chart(fig_contract, use_container_width=True)

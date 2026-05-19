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
    
    # Création d'une colonne de date au format datetime pour les calculs Week over Week
    df['_date'] = pd.to_datetime(df['order day'], errors='coerce')
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
    
    # --- PREPARATION DES DONNEES WoW (Week over Week) ---
    max_d = df['_date'].max()
    # Semaine en cours (7 derniers jours)
    cw_start = max_d - pd.Timedelta(days=6)
    cw_df = df[df['_date'] >= cw_start]
    
    # Semaine précédente (les 7 jours d'avant)
    pw_start = max_d - pd.Timedelta(days=13)
    pw_df = df[(df['_date'] >= pw_start) & (df['_date'] < cw_start)]

    # Fonction pour calculer le pourcentage de croissance
    def wow_delta(cw_val, pw_val):
        if pd.isna(pw_val) or pw_val == 0:
            return "0.0% WoW"
        pct = ((cw_val - pw_val) / pw_val) * 100
        return f"{pct:.1f}% WoW"

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
        
        # Calculs Totaux
        requests = len(df)
        delivered = len(df[df['status'] == 'Delivered'])
        gmv = df['item total'].sum()
        aov = gmv / requests if requests > 0 else 0
        
        # Calculs WoW
        cw_req, pw_req = len(cw_df), len(pw_df)
        cw_del, pw_del = len(cw_df[cw_df['status'] == 'Delivered']), len(pw_df[pw_df['status'] == 'Delivered'])
        cw_gmv, pw_gmv = cw_df['item total'].sum(), pw_df['item total'].sum()
        cw_aov = cw_gmv / cw_req if cw_req > 0 else 0
        pw_aov = pw_gmv / pw_req if pw_req > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Requests (Total)", f"{requests:,}", wow_delta(cw_req, pw_req))
        col2.metric("Delivered (Livrées)", f"{delivered:,}", wow_delta(cw_del, pw_del))
        col3.metric("GMV (Chiffre d'Affaires)", f"{gmv:,.0f} MAD", wow_delta(cw_gmv, pw_gmv))
        col4.metric("AOV (Panier Moyen)", f"{aov:,.2f} MAD", wow_delta(cw_aov, pw_aov))
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
        
        # Calculs Totaux
        unique_users = df['customer Phone'].nunique()
        total_coupons_used = len(df[df['coupon'].notna() & (df['coupon'] != ' ')])
        
        # Calculs WoW
        cw_users, pw_users = cw_df['customer Phone'].nunique(), pw_df['customer Phone'].nunique()
        cw_coup, pw_coup = len(cw_df[cw_df['coupon'].notna() & (cw_df['coupon'] != ' ')]), len(pw_df[pw_df['coupon'].notna() & (pw_df['coupon'] != ' ')])
        cw_coup_rate = cw_coup / cw_req if cw_req > 0 else 0
        pw_coup_rate = pw_coup / pw_req if pw_req > 0 else 0
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("👥 New / Unique Users (Reach)", f"{unique_users:,}", wow_delta(cw_users, pw_users))
        col_m2.metric("🎟️ Commandes Promo", f"{total_coupons_used:,}", wow_delta(cw_coup, pw_coup))
        col_m3.metric("📉 Taux d'utilisation Promo", f"{(total_coupons_used / requests * 100):.1f} %", wow_delta(cw_coup_rate, pw_coup_rate))
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
        
        # Calculs Totaux
        avg_delivery_time = df['delivery time(M)'].mean()
        cancellations = len(df[df['status'] == 'Cancelled'])
        cancel_rate = (cancellations / requests * 100) if requests > 0 else 0
        total_payout = pd.to_numeric(df['driver payout'], errors='coerce').sum()
        
        # Calculs WoW
        cw_del_time, pw_del_time = cw_df['delivery time(M)'].mean(), pw_df['delivery time(M)'].mean()
        cw_dist, pw_dist = cw_df['Distance travel'].mean(), pw_df['Distance travel'].mean()
        cw_canc, pw_canc = len(cw_df[cw_df['status'] == 'Cancelled']), len(pw_df[pw_df['status'] == 'Cancelled'])
        cw_canc_rate = cw_canc / cw_req if cw_req > 0 else 0
        pw_canc_rate = pw_canc / pw_req if pw_req > 0 else 0
        cw_pay = pd.to_numeric(cw_df['driver payout'], errors='coerce').sum()
        pw_pay = pd.to_numeric(pw_df['driver payout'], errors='coerce').sum()
        
        col_o1, col_o2, col_o3, col_o4 = st.columns(4)
        
        # NOTE : Utilisation de delta_color="inverse" car ici, une HAUSSE de temps, distance ou d'annulation est NÉGATIVE
        col_o1.metric("⏱️ Temps de Livraison Moyen", f"{avg_delivery_time:.1f} min", wow_delta(cw_del_time, pw_del_time), delta_color="inverse")
        col_o2.metric("📏 Distance Moyenne", f"{df['Distance travel'].mean():.2f} km", wow_delta(cw_dist, pw_dist), delta_color="inverse")
        col_o3.metric("📉 Taux d'Annulation", f"{cancel_rate:.2f} %", wow_delta(cw_canc_rate, pw_canc_rate), delta_color="inverse")
        
        # Pour les paiements (Payout), une hausse est normale si le volume augmente, donc delta normal
        col_o4.metric("💸 Total Driver Payout", f"{total_payout:,.0f} MAD", wow_delta(cw_pay, pw_pay))
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

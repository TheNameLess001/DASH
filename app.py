import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration de la page ---
st.set_page_config(page_title="Dashboard Yassir/Commandes", layout="wide")
st.title("📊 Tableau de Bord Stratégique")

# --- Zone d'upload ---
uploaded_file = st.file_uploader("Uploadez votre fichier CSV (Export Admin)", type=['csv'])

if uploaded_file is not None:
    # Lecture des données
    df = pd.read_csv(uploaded_file, low_memory=False)
    
    # Création des 3 onglets principaux
    tab_sales, tab_marketing, tab_ops = st.tabs(["💰 Sales (Ventes)", "🎯 Marketing", "⚙️ Opérations (Logistique)"])

    # ==========================================
    # ONGLET 1 : SALES (VENTES & FINANCES)
    # ==========================================
    with tab_sales:
        st.header("Performance des Ventes & Chiffre d'Affaires")
        
        # KPIs Sales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Commandes", len(df))
        col2.metric("Chiffre d'Affaires Global", f"{df['item total'].sum():,.2f} MAD")
        col3.metric("Revenus Admin Nets", f"{df['admin earnings'].sum():,.2f} MAD")
        col4.metric("Panier Moyen", f"{df['item total'].mean():,.2f} MAD")
        
        st.divider()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📈 Évolution du CA par Jour")
            df_revenue = df.groupby('order day')['item total'].sum().reset_index()
            fig_ca = px.line(df_revenue, x='order day', y='item total', markers=True, color_discrete_sequence=['#2E86C1'])
            st.plotly_chart(fig_ca, use_container_width=True)

        with col_b:
            st.subheader("🏆 Top 10 Restaurants (par volume de commandes)")
            top_rests = df['restaurant name'].value_counts().head(10).reset_index()
            top_rests.columns = ['Restaurant', 'Commandes']
            fig_rests = px.bar(top_rests, x='Commandes', y='Restaurant', orientation='h', color='Commandes', color_continuous_scale='Blues')
            fig_rests.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_rests, use_container_width=True)

        st.subheader("💳 Méthodes de Paiement")
        payment_counts = df['Payment Method'].value_counts().reset_index()
        payment_counts.columns = ['Méthode', 'Total']
        fig_pay = px.pie(payment_counts, values='Total', names='Méthode', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pay, use_container_width=True)


    # ==========================================
    # ONGLET 2 : MARKETING (CLIENTS, PROMOS, ZONES)
    # ==========================================
    with tab_marketing:
        st.header("Analyse Marketing & Acquisition")
        
        # Remplacer les valeurs nulles pour les réductions
        df['Discount Amount'] = df['Discount Amount'].fillna(0)
        
        # KPIs Marketing
        col1, col2, col3 = st.columns(3)
        col1.metric("Commandes avec Réduction", len(df[df['Discount Amount'] > 0]))
        col2.metric("Total des Réductions Accordées", f"{df['Discount Amount'].sum():,.2f} MAD")
        col3.metric("Abonnements Yassir+ (Commandes)", len(df[df['Yassir+ Subscription Fee'] > 0]))
        
        st.divider()

        col_c, col_d = st.columns(2)
        with col_c:
            st.subheader("📍 Top Quartiers (Acquisition par zone)")
            top_areas = df['Area'].value_counts().head(10).reset_index()
            top_areas.columns = ['Quartier', 'Commandes']
            fig_areas = px.bar(top_areas, x='Commandes', y='Quartier', orientation='h', color='Commandes', color_continuous_scale='Purples')
            fig_areas.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_areas, use_container_width=True)

        with col_d:
            st.subheader("🍔 Top Catégories de Repas")
            # Nettoyage rapide de la colonne catégorie
            df_food = df['Food Category'].dropna().value_counts().head(10).reset_index()
            df_food.columns = ['Catégorie', 'Total']
            fig_food = px.bar(df_food, x='Total', y='Catégorie', orientation='h', color_discrete_sequence=['#9B59B6'])
            fig_food.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_food, use_container_width=True)


    # ==========================================
    # ONGLET 3 : OPÉRATIONS (LOGISTIQUE & LIVRAISONS)
    # ==========================================
    with tab_ops:
        st.header("Logistique & Performance de Livraison")
        
        # KPIs Ops
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temps de Livraison Moyen", f"{df['delivery time(M)'].mean():,.0f} min")
        col2.metric("Distance Moyenne", f"{df['Distance travel'].mean():,.1f} km")
        col3.metric("Total Dépenses Livreurs", f"{df['driver payout'].sum():,.2f} MAD")
        col4.metric("Taux d'Annulation", f"{(len(df[df['status'] == 'Cancelled']) / len(df) * 100):.1f} %")
        
        st.divider()

        col_e, col_f = st.columns(2)
        with col_e:
            st.subheader("📦 Entonnoir des Statuts de Commande")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Statut', 'Total']
            fig_status = px.funnel(status_counts, x='Total', y='Statut', color_discrete_sequence=['#E67E22'])
            st.plotly_chart(fig_status, use_container_width=True)

        with col_f:
            st.subheader("⏰ Heures de Pointe (Rush Hours)")
            df['hour'] = pd.to_datetime(df['order time'], format='%H:%M:%S', errors='coerce').dt.hour
            hour_counts = df['hour'].value_counts().sort_index().reset_index()
            hour_counts.columns = ['Heure', 'Commandes']
            fig_rush = px.bar(hour_counts, x='Heure', y='Commandes', color_discrete_sequence=['#F1C40F'])
            st.plotly_chart(fig_rush, use_container_width=True)

        col_g, col_h = st.columns(2)
        with col_g:
            st.subheader("🛵 Profils de la Flotte (Type de Livreurs)")
            driver_types = df['Driver Type'].value_counts().reset_index()
            driver_types.columns = ['Type', 'Total']
            fig_drivers = px.pie(driver_types, values='Total', names='Type', hole=0.3, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_drivers, use_container_width=True)
            
        with col_h:
            st.subheader("⚠️ Top Raisons d'Annulation")
            df_cancel = df[df['cancellation reason '].notna() & (df['cancellation reason '] != ' ')]
            cancel_reasons = df_cancel['cancellation reason '].value_counts().head(5).reset_index()
            cancel_reasons.columns = ['Raison', 'Total']
            fig_cancel = px.bar(cancel_reasons, x='Total', y='Raison', orientation='h', color_discrete_sequence=['#E74C3C'])
            fig_cancel.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_cancel, use_container_width=True)

else:
    st.info("Veuillez uploader un fichier CSV pour générer les tableaux de bord (Sales, Marketing, Ops).")

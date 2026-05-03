import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import geopandas as gpd
import requests, zipfile, io, os
import warnings
warnings.filterwarnings('ignore')

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClimateIQ",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.session_state["sidebar_state"] = "expanded"

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1a0533 0%, #0d1b4b 50%, #0a2a3d 100%);
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] * { color: #e8e0f5 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    padding: 6px 0;
    cursor: pointer;
}

/* Main background */
.main { background: #f7f4ff; }

/* Page banner */
.page-banner {
    padding: 28px 36px;
    border-radius: 18px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.page-banner h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.1rem;
    margin: 0 0 6px 0;
    color: white;
}
.page-banner p {
    font-size: 1.05rem;
    margin: 0;
    color: rgba(255,255,255,0.82);
    font-weight: 300;
}

/* Stat cards */
.stat-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    border-left: 5px solid;
    margin-bottom: 12px;
}
.stat-card .stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-card .stat-label {
    font-size: 0.82rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Graph cards */
.graph-card {
    background: white;
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}

/* Section divider */
.section-tag {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

h2, h3 { font-family: 'Syne', sans-serif; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Color palette ──────────────────────────────────────────────────────────────
COLORS = {
    'indigo':  '#4f46e5',
    'purple':  '#7c3aed',
    'pink':    '#db2777',
    'teal':    '#0d9488',
    'amber':   '#d97706',
    'rose':    '#e11d48',
    'blue':    '#2563eb',
    'violet':  '#8b5cf6',
    'fuchsia': '#c026d3',
    'cyan':    '#0891b2',
    'yellow':  '#ca8a04',
    'emerald': '#059669',
}

BANNER_GRADIENTS = {
    '🏠 Home':               'linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%)',
    '📈 Global Emissions':   'linear-gradient(135deg, #dc2626 0%, #d97706 100%)',
    '🗺️ World Map & Rankings':'linear-gradient(135deg, #0d9488 0%, #2563eb 100%)',
    '🔥 Emission Patterns':  'linear-gradient(135deg, #7c3aed 0%, #c026d3 100%)',
    '⚖️ Climate Justice':    'linear-gradient(135deg, #0891b2 0%, #4f46e5 100%)',
    '🇹🇳 Tunisia Focus':     'linear-gradient(135deg, #dc2626 0%, #ca8a04 100%)',
    '🤖 AI & Data Centers':  'linear-gradient(135deg, #1e1b4b 0%, #4f46e5 60%, #0891b2 100%)',
    '📚 References':         'linear-gradient(135deg, #059669 0%, #0d9488 100%)',
}

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    BASE = ''
    owid      = pd.read_csv(BASE + 'owid_clean.csv')
    nasa      = pd.read_csv(BASE + 'nasa_clean.csv')
    sea       = pd.read_csv(BASE + 'sea_clean.csv')
    disasters = pd.read_csv(BASE + 'disasters_clean.csv')
    global_df = pd.read_csv(BASE + 'global_merged.csv')
    return owid, nasa, sea, disasters, global_df

try:
    owid, nasa, sea, disasters, global_df = load_data()
    latest_year = int(owid['Year'].max())
    DATA_LOADED = True
except:
    DATA_LOADED = False

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <div style='font-family:Syne,sans-serif; font-size:1.6rem; font-weight:800;
                    background: linear-gradient(90deg,#a78bfa,#f472b6);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            🌱 ClimateIQ
        </div>
        <div style='font-size:0.75rem; color:rgba(255,255,255,0.5); margin-top:4px;'>
            Climate Change Analysis
        </div>
    </div>
    <hr style='border:1px solid rgba(255,255,255,0.08); margin: 8px 0 20px 0;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ['🏠 Home', '📈 Global Emissions', '🗺️ World Map & Rankings',
         '🔥 Emission Patterns', '⚖️ Climate Justice',
         '🇹🇳 Tunisia Focus', '🤖 AI & Data Centers', '📚 References'],
        label_visibility='collapsed'
    )

    st.markdown("""
    <hr style='border:1px solid rgba(255,255,255,0.08); margin: 20px 0 12px 0;'>
    <div style='font-size:0.72rem; color:rgba(255,255,255,0.35); text-align:center; padding-bottom:10px;'>
        Data: OWID · NASA · EPA · EMDAT<br>Last updated 2022–2023
    </div>
    """, unsafe_allow_html=True)

# ── Helper functions ───────────────────────────────────────────────────────────
def banner(title, subtitle):
    grad = BANNER_GRADIENTS.get(page, 'linear-gradient(135deg,#4f46e5,#7c3aed)')
    st.markdown(f"""
    <div class='page-banner' style='background:{grad};'>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def stat_card(value, label, color, prefix='', suffix=''):
    st.markdown(f"""
    <div class='stat-card' style='border-left-color:{color};'>
        <div class='stat-value' style='color:{color};'>{prefix}{value}{suffix}</div>
        <div class='stat-label'>{label}</div>
    </div>
    """, unsafe_allow_html=True)

def graph_card(fig, height=420):
    st.plotly_chart(fig, use_container_width=True)

def interp(text):
    with st.expander("📌 What does this tell us?"):
        st.markdown(f"<p style='color:#444; font-size:0.93rem; line-height:1.6;'>{text}</p>",
                    unsafe_allow_html=True)

def plotly_layout(fig, title='', bg='white'):
    fig.update_layout(
        title=dict(text=title, font=dict(family='Syne', size=15, color='#1e1b4b')),
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family='DM Sans', color='#374151'),
        legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0),
        margin=dict(t=50, b=40, l=40, r=20),
    )
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0', zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f0f0f0', zeroline=False)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# 🏠 HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == '🏠 Home':
    st.markdown("""
    <div style='background: linear-gradient(135deg,#4f46e5,#7c3aed,#db2777);
                border-radius:22px; padding:48px 44px 40px; margin-bottom:32px; position:relative; overflow:hidden;'>
        <div style='position:absolute;top:-40px;right:-40px;width:220px;height:220px;
                    background:rgba(255,255,255,0.05);border-radius:50%;'></div>
        <div style='position:absolute;bottom:-60px;left:60%;width:300px;height:300px;
                    background:rgba(255,255,255,0.04);border-radius:50%;'></div>
        <div style='font-family:Syne,sans-serif;font-size:0.8rem;font-weight:700;
                    letter-spacing:0.15em;color:rgba(255,255,255,0.6);
                    text-transform:uppercase;margin-bottom:12px;'>
            Academic Project · 2025–2026
        </div>
        <h1 style='font-family:Syne,sans-serif;font-weight:800;font-size:3rem;
                   color:white;margin:0 0 16px;line-height:1.1;'>
            Climate Change<br>& CO₂ Emissions
        </h1>
        <div style='background:rgba(255,255,255,0.12);border-left:3px solid rgba(255,255,255,0.6);
                    border-radius:0 10px 10px 0;padding:14px 20px;max-width:700px;margin-bottom:24px;'>
            <p style='font-family:DM Sans,sans-serif;font-size:1.05rem;color:rgba(255,255,255,0.92);
                      margin:0;font-style:italic;line-height:1.5;'>
                "How have global CO₂ emissions evolved since 1980 — and what are their measurable
                consequences on temperature, sea level rise, and climate equity?"
            </p>
        </div>
        <p style='color:rgba(255,255,255,0.72);font-size:0.97rem;max-width:640px;line-height:1.6;margin:0;'>
            This dashboard explores four decades of climate data across 190+ countries,
            linking CO₂ emissions to rising temperatures, sea level change, and the unequal
            burden carried by the world's most vulnerable nations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if DATA_LOADED:
        # Quick stats
        global_co2 = owid.groupby('Year')['co2'].sum().reset_index()
        g_last = global_co2[global_co2['Year'] == latest_year]['co2'].values[0]
        g1980  = global_co2[global_co2['Year'] == 1980]['co2'].values[0]
        slope, _, r, _, _ = stats.linregress(nasa['Year'], nasa['temp_anomaly'])
        total_rise = sea['sea_level_mm'].max() - sea['sea_level_mm'].min()

        c1, c2, c3, c4 = st.columns(4)
        with c1: stat_card(f"{g_last:.0f} Gt", f"Global CO₂ in {latest_year}", COLORS['rose'])
        with c2: stat_card(f"+{(g_last-g1980)/g1980*100:.0f}%", "Emissions growth since 1980", COLORS['amber'])
        with c3: stat_card(f"+{slope*10:.2f}°C", "Warming per decade (NASA)", COLORS['purple'])
        with c4: stat_card(f"{total_rise:.0f} mm", "Total sea level rise", COLORS['cyan'])

        st.markdown("<br>", unsafe_allow_html=True)

        # Mini preview charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=global_co2['Year'], y=global_co2['co2'],
                fill='tozeroy', fillcolor='rgba(220,38,38,0.15)',
                line=dict(color='#dc2626', width=2), name='CO₂ (Gt)'
            ))
            plotly_layout(fig, 'Global CO₂ Emissions since 1980')
            fig.update_layout(height=280, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            fig2 = go.Figure()
            colors_bar = ['#dc2626' if x > 0 else '#2563eb' for x in nasa['temp_anomaly']]
            fig2.add_trace(go.Bar(
                x=nasa['Year'], y=nasa['temp_anomaly'],
                marker_color=colors_bar, name='Anomaly'
            ))
            nasa_smooth = nasa['temp_anomaly'].rolling(5, center=True).mean()
            fig2.add_trace(go.Scatter(
                x=nasa['Year'], y=nasa_smooth,
                line=dict(color='#1e1b4b', width=2.5), name='5yr mean'
            ))
            plotly_layout(fig2, 'Temperature Anomaly (°C)')
            fig2.update_layout(height=280, showlegend=False)
            fig2.add_hline(y=0, line_color='gray', line_width=0.8)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='background:linear-gradient(135deg,#fdf4ff,#eff6ff);
                    border-radius:14px;padding:20px 28px;margin-top:8px;
                    border:1px solid rgba(139,92,246,0.2);'>
            <span style='font-family:Syne,sans-serif;font-weight:700;color:#7c3aed;'>
                👈 Use the sidebar
            </span>
            <span style='color:#555;'> to explore each chapter of this analysis.</span>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 📈 GLOBAL EMISSIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == '📈 Global Emissions':
    banner("Global CO₂ Emissions",
           "How have emissions evolved since 1980 — and did international agreements change anything?")

    if DATA_LOADED:
        global_co2 = owid.groupby('Year')['co2'].sum().reset_index()
        global_co2['co2_5yr'] = global_co2['co2'].rolling(5, center=True).mean()

        year_min, year_max = st.select_slider(
            "Filter year range", options=list(range(1980, latest_year+1)),
            value=(1980, latest_year)
        )
        gco2_f = global_co2[(global_co2['Year'] >= year_min) & (global_co2['Year'] <= year_max)]

        # CO2 trend with milestones
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=gco2_f['Year'], y=gco2_f['co2'],
            fill='tozeroy', fillcolor='rgba(220,38,38,0.12)',
            line=dict(color='#dc2626', width=1.5), name='Annual', opacity=0.7
        ))
        fig.add_trace(go.Scatter(
            x=gco2_f['Year'], y=gco2_f['co2_5yr'],
            line=dict(color='#7c3aed', width=3), name='5-year mean'
        ))
        events = {1988:'IPCC founded', 1997:'Kyoto Protocol', 2008:'Financial crisis',
                  2015:'Paris Agreement', 2020:'COVID dip'}
        for yr, lbl in events.items():
            if year_min <= yr <= year_max:
                fig.add_vline(x=yr, line_dash='dash', line_color='gray', line_width=1,
                              annotation_text=lbl, annotation_position='top',
                              annotation_font_size=10, annotation_font_color='gray')
        plotly_layout(fig, f'Global CO₂ Emissions {year_min}–{year_max}')
        fig.update_layout(height=400)
        fig.update_yaxes(title_text='CO₂ (Gt)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        interp("Global CO₂ has risen continuously since 1980. The two visible dips — 2008 (financial crisis) and 2020 (COVID) — were both short-lived. Despite the Kyoto Protocol and Paris Agreement, the trend has never reversed. This confirms that political commitments alone, without structural economic change, are insufficient.")

        # CO2 by source
        st.markdown("<br>", unsafe_allow_html=True)
        source_cols = [c for c in ['coal_co2','oil_co2','gas_co2','cement_co2'] if c in owid.columns]
        source_labels = {'coal_co2':'Coal','oil_co2':'Oil','gas_co2':'Gas','cement_co2':'Cement'}
        sources = owid.groupby('Year')[source_cols].sum().reset_index()
        sources_f = sources[(sources['Year'] >= year_min) & (sources['Year'] <= year_max)]

        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            fig2 = go.Figure()
            src_colors = ['#1c1c1c','#92400e','#3b82f6','#9ca3af']
            for i, col in enumerate(source_cols):
                fig2.add_trace(go.Scatter(
                    x=sources_f['Year'], y=sources_f[col],
                    name=source_labels[col], stackgroup='one',
                    fillcolor=src_colors[i], line=dict(width=0),
                    mode='lines'
                ))
            plotly_layout(fig2, 'CO₂ by Source — Stacked Area')
            fig2.update_layout(height=350)
            fig2.update_yaxes(title_text='CO₂ (Gt)')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            latest_src = sources[sources['Year'] == latest_year][source_cols].iloc[0]
            fig3 = go.Figure(go.Pie(
                labels=[source_labels[c] for c in source_cols],
                values=latest_src.values,
                marker_colors=src_colors,
                hole=0.4,
                textinfo='label+percent'
            ))
            plotly_layout(fig3, f'Source Breakdown ({latest_year})')
            fig3.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        interp("Coal is still the largest single source (~43%), but oil and gas together make up over half of emissions. Gas has grown the most since 1980, promoted as a 'cleaner' alternative — but it still contributes significantly to warming. Cement (~4%) is small but impossible to replace with renewables. All three fossil fuels need to be targeted simultaneously.")

# ══════════════════════════════════════════════════════════════════════════════
# 🗺️ WORLD MAP & RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == '🗺️ World Map & Rankings':
    banner("World Map & Rankings",
           "Which countries are responsible — today and throughout history?")

    if DATA_LOADED:
        sel_year = st.slider("Select year", 1980, latest_year, latest_year)
        year_data = owid[owid['Year'] == sel_year].dropna(subset=['co2'])

        # Choropleth
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        fig = px.choropleth(
            year_data, locations='Code', color='co2',
            hover_name='Entity', hover_data={'co2': ':.2f'},
            color_continuous_scale=[
                [0,'#f0f4ff'],[0.2,'#818cf8'],[0.5,'#7c3aed'],
                [0.75,'#db2777'],[1,'#dc2626']
            ],
            labels={'co2': 'CO₂ (Gt)'},
            title=f'Global CO₂ Emissions by Country ({sel_year})'
        )
        fig.update_layout(
            height=480, paper_bgcolor='white',
            font=dict(family='DM Sans'),
            coloraxis_colorbar=dict(title='CO₂ (Gt)', thickness=14),
            geo=dict(showframe=False, showcoastlines=True,
                     coastlinecolor='#e5e7eb', bgcolor='#f7f9ff',
                     showland=True, landcolor='#f0f4ff',
                     showocean=True, oceancolor='#dbeafe'),
            margin=dict(t=50,b=0,l=0,r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        interp("The map reveals extreme geographic concentration — a handful of countries dominate while most of Africa, Central Asia and South America remain nearly invisible. The regions that appear lightest are often the most vulnerable to climate consequences. This is the core of climate injustice.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Top 10 side by side
        col1, col2 = st.columns(2)
        top10 = year_data.nlargest(10, 'co2')
        with col1:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            fig2 = go.Figure(go.Bar(
                x=top10['co2'], y=top10['Entity'],
                orientation='h',
                marker_color=px.colors.sequential.Plasma_r[:10],
                text=[f"{v:.2f} Gt" for v in top10['co2']],
                textposition='outside'
            ))
            plotly_layout(fig2, f'Top 10 Annual Emitters ({sel_year})')
            fig2.update_layout(height=400, yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            if 'cumulative_co2' in owid.columns:
                st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
                top10_cum = year_data.dropna(subset=['cumulative_co2']).nlargest(10, 'cumulative_co2')
                total_cum = year_data['cumulative_co2'].sum()
                fig3 = go.Figure(go.Bar(
                    x=top10_cum['cumulative_co2']/1e3,
                    y=top10_cum['Entity'],
                    orientation='h',
                    marker_color=px.colors.sequential.Inferno_r[:10],
                    text=[f"{row['cumulative_co2']/total_cum*100:.1f}%" for _, row in top10_cum.iterrows()],
                    textposition='outside'
                ))
                plotly_layout(fig3, 'Top 10 — Cumulative Historical Responsibility')
                fig3.update_layout(height=400, yaxis=dict(autorange='reversed'))
                fig3.update_xaxes(title_text='Cumulative CO₂ (thousand Gt)')
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        interp("Annual vs historical rankings tell two different stories. China leads today, but the USA leads historically — and CO₂ stays in the atmosphere for centuries. Past emissions from wealthy nations continue driving warming today, forming the basis of the climate justice debate.")

# ══════════════════════════════════════════════════════════════════════════════
# 🔥 EMISSION PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == '🔥 Emission Patterns':
    banner("Emission Patterns",
           "What does 40 years of data reveal about how countries actually changed?")

    if DATA_LOADED:
        # Heatmap
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        top20 = (owid[owid['Year'] == latest_year].dropna(subset=['co2'])
                 .nlargest(20, 'co2')['Entity'].tolist())
        hmap = (owid[owid['Entity'].isin(top20)]
                .pivot_table(index='Entity', columns='Year', values='co2'))
        years_show = [y for y in hmap.columns if y % 2 == 0]
        hmap = hmap[years_show]
        hmap = hmap.loc[hmap[hmap.columns[-1]].sort_values(ascending=False).index]

        fig = go.Figure(go.Heatmap(
            z=hmap.values, x=[str(y) for y in hmap.columns],
            y=hmap.index,
            colorscale=[[0,'#f0f4ff'],[0.3,'#a78bfa'],[0.6,'#7c3aed'],[0.85,'#db2777'],[1,'#dc2626']],
            colorbar=dict(title='CO₂ (Gt)', thickness=14),
            hoverongaps=False
        ))
        plotly_layout(fig, 'CO₂ Emissions Heatmap — Top 20 Emitters (1980–2022)')
        fig.update_layout(height=560)
        fig.update_xaxes(tickangle=45, tickfont=dict(size=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        interp("Read left to right to see each country's story. China: pale to deep red — the fastest industrialization in history. Russia: sharp lightening after 1991 — the Soviet collapse. Germany and UK: gradual lightening — real decarbonization. No country shows a sharp, sustained drop — global emissions have never seriously decreased.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Paris Agreement
        st.markdown("""
<div style='background:linear-gradient(135deg,#eff6ff,#fdf4ff);
            border-radius:14px;padding:22px 28px;margin-bottom:20px;
            border-left:4px solid #4f46e5;'>
    <p style='font-family:Syne,sans-serif;font-weight:700;color:#1e1b4b;
              font-size:1rem;margin:0 0 10px;'>What is the Paris Agreement?</p>
    <p style='color:#374151;font-size:0.93rem;line-height:1.7;margin:0;'>
        In December 2015, 196 countries signed a historic treaty committing to limit 
        global warming to <b>well below 2°C</b>. Each country submitted a pledge — called 
        an NDC — to cut their CO₂ emissions by a specific percentage by 2030.
        Examples: 🇺🇸 USA pledged <b>-51% vs 2005</b> · 🇪🇺 EU pledged <b>-55% vs 1990</b> · 
        🇹🇳 Tunisia pledged <b>-41% vs business-as-usual</b>.
        The chart below asks the uncomfortable question: <b>are they actually on track?</b>
    </p>
</div>
""", unsafe_allow_html=True)
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        paris_targets = {
            'United States': ('USA', 2005, 0.51),
            'China':         ('CHN', 2005, 0.65),
            'India':         ('IND', 2005, 0.45),
            'United Kingdom':('GBR', 1990, 0.68),
            'Germany':       ('DEU', 1990, 0.65),
            'France':        ('FRA', 1990, 0.40),
            'Canada':        ('CAN', 2005, 0.40),
            'Australia':     ('AUS', 2005, 0.43),
            'South Africa':  ('ZAF', 2005, 0.28),
            'Brazil':        ('BRA', 2005, 0.37),
            'Tunisia':       ('TUN', 2010, 0.41),
        }
        records = []
        for country, (code, ref_year, reduction) in paris_targets.items():
            ref_d = owid[(owid['Code'] == code) & (owid['Year'] == ref_year)]['co2']
            cur_d = owid[(owid['Code'] == code) & (owid['Year'] == latest_year)]['co2']
            if len(ref_d) == 0 or len(cur_d) == 0: continue
            ref_val, cur_val = ref_d.values[0], cur_d.values[0]
            records.append({'Country': country, 'Current': cur_val,
                            'Target': ref_val*(1-reduction), 'Gap': cur_val - ref_val*(1-reduction)})
        paris_df = pd.DataFrame(records).sort_values('Gap', ascending=False)

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name=f'Current ({latest_year})', x=paris_df['Country'],
                              y=paris_df['Current'], marker_color='#dc2626', opacity=0.85))
        fig2.add_trace(go.Bar(name='2030 Paris Target', x=paris_df['Country'],
                              y=paris_df['Target'], marker_color='#3b82f6', opacity=0.85))
        plotly_layout(fig2, 'Paris Agreement: Current Emissions vs 2030 Targets')
        fig2.update_layout(barmode='group', height=400)
        fig2.update_xaxes(tickangle=30)
        fig2.update_yaxes(title_text='CO₂ (Gt)')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        off_track = paris_df[paris_df['Gap'] > 0]['Country'].tolist()
        interp(f"Countries where current emissions exceed their 2030 target: <b>{', '.join(off_track)}</b>. Most major emitters are not on track. Tunisia, despite being a minor emitter, has committed to significant reductions — reflecting the moral seriousness of vulnerable nations toward a crisis they did not cause.")

# ══════════════════════════════════════════════════════════════════════════════
# ⚖️ CLIMATE JUSTICE
# ══════════════════════════════════════════════════════════════════════════════
elif page == '⚖️ Climate Justice':
    banner("Climate Justice",
           "Is the warming shared equally — or do the least responsible suffer the most?")

    if DATA_LOADED:
        # Temperature anomaly
        nasa['temp_5yr'] = nasa['temp_anomaly'].rolling(5, center=True).mean()
        slope, intercept, r, p, _ = stats.linregress(nasa['Year'], nasa['temp_anomaly'])
        nasa['trend'] = slope * nasa['Year'] + intercept

        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        fig = go.Figure()
        colors_bar = ['#dc2626' if x > 0 else '#3b82f6' for x in nasa['temp_anomaly']]
        fig.add_trace(go.Bar(x=nasa['Year'], y=nasa['temp_anomaly'],
                             marker_color=colors_bar, name='Annual', opacity=0.75))
        fig.add_trace(go.Scatter(x=nasa['Year'], y=nasa['temp_5yr'],
                                 line=dict(color='#1e1b4b', width=3), name='5-year mean'))
        fig.add_trace(go.Scatter(x=nasa['Year'], y=nasa['trend'],
                                 line=dict(color='#f59e0b', width=2, dash='dash'),
                                 name=f'Trend (+{slope*10:.2f}°C/decade)'))
        fig.add_hline(y=0, line_color='gray', line_width=0.8)
        plotly_layout(fig, 'Global Temperature Anomaly (°C vs 1951–1980 baseline)')
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        interp(f"Every year since the mid-1970s has been above baseline. The trend shows +{slope*10:.2f}°C per decade — accelerating, not slowing. The 5 warmest years on record all occurred after 2015.")

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        # Sea level vs CO2
        with col1:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            global_co2 = owid.groupby('Year')['co2'].sum().reset_index()
            sea_co2 = sea.merge(global_co2, on='Year', how='inner').dropna()

            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(go.Scatter(
                x=sea_co2['Year'], y=sea_co2['sea_level_mm'],
                fill='tozeroy', fillcolor='rgba(8,145,178,0.15)',
                line=dict(color='#0891b2', width=2), name='Sea level (mm)'
            ), secondary_y=False)
            fig2.add_trace(go.Scatter(
                x=sea_co2['Year'], y=sea_co2['co2'],
                line=dict(color='#dc2626', width=2, dash='dash'), name='CO₂ (Gt)'
            ), secondary_y=True)
            fig2.update_yaxes(title_text='Sea level change (mm)', secondary_y=False,
                               color='#0891b2')
            fig2.update_yaxes(title_text='Global CO₂ (Gt)', secondary_y=True,
                               color='#dc2626')
            fig2.update_layout(height=350, paper_bgcolor='white', plot_bgcolor='white',
                                font=dict(family='DM Sans'),
                                title=dict(text='Sea Level Rise vs CO₂', font=dict(family='Syne',size=14)),
                                legend=dict(bgcolor='rgba(0,0,0,0)'),
                                margin=dict(t=50,b=40,l=40,r=60))
            fig2.update_xaxes(showgrid=True, gridcolor='#f0f0f0')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            interp("The two curves move in near-perfect parallel. As CO₂ rises, sea levels follow — confirming emissions are the primary driver of sea level rise.")

        # Regional bubble chart
        with col2:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            reg = (owid[(owid['Year'] == latest_year) & owid['region'].notna()]
                   .groupby('region')[['co2_per_capita','temperature_change_from_co2','co2']]
                   .mean().reset_index().dropna())

            fig3 = go.Figure()
            pal = ['#4f46e5','#db2777','#0891b2','#d97706','#059669','#7c3aed']
            for i, row in reg.iterrows():
                fig3.add_trace(go.Scatter(
                    x=[row['co2_per_capita']], y=[row['temperature_change_from_co2']],
                    mode='markers+text', name=row['region'],
                    text=[row['region']], textposition='top right',
                    textfont=dict(size=9, family='DM Sans'),
                    marker=dict(size=max(row['co2']*0.4, 12),
                                color=pal[i % len(pal)], opacity=0.85,
                                line=dict(color='white', width=2))
                ))
            plotly_layout(fig3, 'Climate Justice: Emissions vs Warming by Region')
            fig3.update_layout(height=350, showlegend=False)
            fig3.update_xaxes(title_text='CO₂ per capita (t/person)')
            fig3.update_yaxes(title_text='Temp change from CO₂ (°C)')
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            interp("High-emitting regions sit far right. Low-emitting regions like Africa sit bottom left — yet face the severest consequences. The burden of climate change is NOT proportional to its cause. This is climate injustice, visible in data.")

# ══════════════════════════════════════════════════════════════════════════════
# 🇹🇳 TUNISIA FOCUS
# ══════════════════════════════════════════════════════════════════════════════
elif page == '🇹🇳 Tunisia Focus':
    banner("Tunisia Focus",
           "A country that emits almost nothing — yet faces everything.")

    if DATA_LOADED:
        tun = owid[owid['Code'] == 'TUN'].sort_values('Year')
        world_avg = owid.groupby('Year')[['co2_per_capita','temperature_change_from_co2']].mean().reset_index()

        tun_pc   = tun[tun['Year'] == latest_year]['co2_per_capita'].values
        world_pc = world_avg[world_avg['Year'] == latest_year]['co2_per_capita'].values

        if len(tun_pc) > 0 and len(world_pc) > 0:
            ratio = world_pc[0] / tun_pc[0]
            c1, c2, c3 = st.columns(3)
            with c1: stat_card(f"{tun_pc[0]:.2f} t", "Tunisia CO₂/person", COLORS['rose'])
            with c2: stat_card(f"{world_pc[0]:.2f} t", "World average CO₂/person", COLORS['purple'])
            with c3: stat_card(f"{ratio:.1f}×", "Tunisia emits LESS than world avg", COLORS['teal'])

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=tun['Year'], y=tun['co2'],
                fill='tozeroy', fillcolor='rgba(220,38,38,0.12)',
                line=dict(color='#dc2626', width=2.5), name='Tunisia CO₂'
            ))
            plotly_layout(fig, 'Tunisia Total CO₂ Emissions (Gt)')
            fig.update_layout(height=300)
            fig.update_yaxes(title_text='Gt CO₂')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=world_avg['Year'], y=world_avg['co2_per_capita'],
                line=dict(color='#9ca3af', width=2, dash='dash'), name='World average'
            ))
            fig2.add_trace(go.Scatter(
                x=tun['Year'], y=tun['co2_per_capita'],
                line=dict(color='#3b82f6', width=2.5), name='Tunisia'
            ))
            plotly_layout(fig2, 'CO₂ per Capita vs World Average')
            fig2.update_layout(height=300)
            fig2.update_yaxes(title_text='tonnes/person')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)

        with col3:
            if 'temperature_change_from_co2' in tun.columns:
                st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=world_avg['Year'], y=world_avg['temperature_change_from_co2'],
                    line=dict(color='#9ca3af', width=2, dash='dash'), name='World average'
                ))
                fig3.add_trace(go.Scatter(
                    x=tun['Year'], y=tun['temperature_change_from_co2'],
                    line=dict(color='#f97316', width=2.5), name='Tunisia'
                ))
                plotly_layout(fig3, 'Temperature Change Attributed to CO₂')
                fig3.update_layout(height=300)
                fig3.update_yaxes(title_text='°C')
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with col4:
            st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=tun['Year'], y=tun['share_global_co2'],
                fill='tozeroy', fillcolor='rgba(124,58,237,0.12)',
                line=dict(color='#7c3aed', width=2.5), name='Share %'
            ))
            plotly_layout(fig4, "Tunisia's Share of Global CO₂ (%)")
            fig4.update_layout(height=300)
            fig4.update_yaxes(title_text='%')
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        interp("Tunisia's total emissions are growing gradually but remain under 1% of global output. Per capita, Tunisians emit several times less than the world average. The temperature change attributed to Tunisia's own emissions is negligible — the warming it experiences is almost entirely caused by others. This is climate injustice in a single country's data.")

# ══════════════════════════════════════════════════════════════════════════════
# 🤖 AI & DATA CENTERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == '🤖 AI & Data Centers':
    banner("AI & Data Centers",
           "The invisible carbon cost of the technology you use every day.")

    st.markdown("""
    <div style='background:linear-gradient(135deg,#1e1b4b,#1e3a5f);
                border-radius:16px;padding:24px 30px;margin-bottom:24px;
                border:1px solid rgba(99,102,241,0.3);'>
        <p style='color:rgba(255,255,255,0.88);font-size:0.97rem;line-height:1.7;margin:0;'>
            Every AI query, generated image, or model inference runs on a <b style='color:#a78bfa;'>data center</b>
            consuming enormous electricity. Most of that electricity still comes from fossil fuels.
            What makes this worse is <b style='color:#f472b6;'>how these centers are cooled</b> — companies
            like Microsoft, Meta and Google are placing servers in <b style='color:#67e8f9;'>Arctic regions and cold seas</b>,
            releasing heat that accelerates permafrost thaw, releasing methane (80× more potent than CO₂),
            and directly contributing to <b style='color:#86efac;'>sea level rise</b>.
            The AI boom is not just an energy problem — it is becoming a direct climate accelerator.
        </p>
    </div>
    """, unsafe_allow_html=True)

    
    # IEA hardcoded data
    years   = list(range(2020, 2036))
    central = [250,280,370,415,500,590,660,730,800,870,950,1010,1060,1110,1160,1200]
    low     = [250,270,350,390,460,530,580,630,680,730,780,830,870,910,950,980]
    high    = [250,300,400,450,560,670,770,870,970,1070,1180,1270,1360,1440,1520,1580]

    ai_events = {2020:'GPT-3', 2022:'ChatGPT launch', 2023:'GPT-4 / Gemini', 2025:'AI everywhere'}

    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years+years[::-1], y=high+low[::-1],
        fill='toself', fillcolor='rgba(99,102,241,0.12)',
        line=dict(width=0), showlegend=True, name='IEA uncertainty range'
    ))
    fig.add_trace(go.Scatter(
        x=years, y=central,
        line=dict(color='#4f46e5', width=3), mode='lines+markers',
        marker=dict(size=6, color='#4f46e5'), name='Central estimate'
    ))
    fig.add_trace(go.Scatter(
        x=years[:6], y=central[:6],
        line=dict(color='#0891b2', width=3), name='Historical (2020–2024)',
        showlegend=True
    ))
    for yr, lbl in ai_events.items():
        if yr in years:
            fig.add_vline(x=yr, line_dash='dash', line_color='#db2777', line_width=1.5,
                          annotation_text=lbl, annotation_position='top',
                          annotation_font_size=10, annotation_font_color='#db2777')
    fig.add_vrect(x0=2024, x1=2035, fillcolor='rgba(251,191,36,0.06)',
                  line_width=0, annotation_text='Projected →',
                  annotation_position='top left',
                  annotation_font_color='#d97706', annotation_font_size=10)

    plotly_layout(fig, 'Electricity Consumption by Data Centres, 2020–2035  (Source: IEA, April 2026)')
    fig.update_layout(height=450, paper_bgcolor='white')
    fig.update_yaxes(title_text='Electricity consumption (TWh)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
<p style='color:#6b7280;font-size:0.8rem;margin:4px 0 16px 4px;'>
    📏 <b>Note:</b> TWh = Terawatt-hours per year. 1 TWh = 1 billion kilowatt-hours — 
    enough to power ~300,000 homes for a year.
</p>
""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: stat_card("250 TWh", "Data center usage in 2020", COLORS['indigo'])
    with col2: stat_card("~500 TWh", "Estimated usage in 2024 (+100%)", COLORS['pink'])
    with col3: stat_card("~1200 TWh", "Projected 2035 (+380% vs 2020)", COLORS['rose'])

    interp("Data center electricity consumption has nearly doubled since 2020, driven almost entirely by AI. By 2035 the IEA projects ~1200 TWh/year — equivalent to Japan's entire electricity use today. The Arctic cooling strategy transfers heat into cold environments, directly accelerating the ice melt that our sea level data shows is already at an alarming rate. Using AI responsibly starts with being aware of its true cost.")

    #cooling cycle 
    st.markdown("""
<div style='background:linear-gradient(135deg,#1e1b4b,#0c1445);
            border-radius:14px;padding:20px 28px;margin-bottom:20px;
            border-left:4px solid #818cf8;'>
    <p style='color:#a5b4fc;font-weight:700;font-size:0.95rem;margin:0 0 10px;'>
        🔄 The Cooling Cycle Problem
    </p>
    <p style='color:rgba(255,255,255,0.8);font-size:0.9rem;line-height:1.8;margin:0;'>
        🖥️ Servers generate heat → 
        ❄️ Companies place data centers in Arctic/cold seas → 
        🌡️ Local temperatures rise → 
        🧊 Permafrost thaws → 
        💨 Methane released (80× more potent than CO₂) → 
        🌊 Ice melts → Sea levels rise →
        🔁 Climate crisis accelerates
    </p>
</div>
""", unsafe_allow_html=True)
    
    with st.expander("📌 What does this tell us?"):
        st.markdown("""
        <p style='color:#444;font-size:0.93rem;line-height:1.7;'>
        Data center electricity consumption has <b>nearly doubled since 2020</b>, driven almost 
        entirely by the AI boom. By 2035, the IEA projects data centers will consume 
        <b>~1200 TWh/year</b> — roughly the entire electricity consumption of Japan today.
        A TWh (Terawatt-hour) is 1 billion kilowatt-hours — enough to power ~300,000 homes 
        for a year. Most of this electricity still comes from fossil fuels.<br><br>
        The <b>Arctic cooling strategy</b> makes this worse: by transferring heat into cold 
        environments, tech companies are directly accelerating ice melt — which our sea level 
        analysis showed is already rising at an alarming rate. The very technology people use 
        casually every day is quietly amplifying the crisis this entire dashboard has been measuring.<br><br>
        <b>Using AI responsibly starts with being aware of its true cost.</b>
        </p>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 📚 REFERENCES
# ══════════════════════════════════════════════════════════════════════════════
elif page == '📚 References':
    banner("References & Data Sources",
           "Where the data comes from — and how to access it.")

    st.markdown("""
    <div style='background:white;border-radius:18px;padding:32px;
                box-shadow:0 4px 24px rgba(0,0,0,0.06);'>
    """, unsafe_allow_html=True)

    refs = pd.DataFrame([
        {
            'Dataset': 'OWID CO₂ & Greenhouse Gas Emissions',
            'Source': 'Our World in Data / Global Carbon Project',
            'Period': '1750–2022',
            'Key Variables': 'CO₂, GDP, population, energy, cumulative emissions',
            'Link': 'https://github.com/owid/co2-data'
        },
        {
            'Dataset': 'GISS Surface Temperature Analysis (GISTEMP v4)',
            'Source': 'NASA Goddard Institute for Space Studies',
            'Period': '1880–2023',
            'Key Variables': 'Global surface temperature anomaly (°C)',
            'Link': 'https://data.giss.nasa.gov/gistemp/'
        },
        {
            'Dataset': 'Global Mean Sea Level Rise',
            'Source': 'EPA / CSIRO + NOAA satellite data',
            'Period': '1880–2013',
            'Key Variables': 'Global mean sea level change (mm)',
            'Link': 'https://datahub.io/core/sea-level-rise'
        },
        {
            'Dataset': 'Natural Disasters 1900–2019',
            'Source': 'EM-DAT Emergency Events Database / OWID',
            'Period': '1900–2019',
            'Key Variables': 'Number of natural disasters per year',
            'Link': 'https://github.com/owid/owid-datasets'
        },
        {
            'Dataset': 'Electricity Consumption by Data Centres 2020–2035',
            'Source': 'International Energy Agency (IEA)',
            'Period': '2020–2035',
            'Key Variables': 'TWh consumption, uncertainty range',
            'Link': 'https://www.iea.org/energy-system/buildings/data-centres-and-data-transmission-networks'
        },
    ])

    st.dataframe(
        refs,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Link': st.column_config.LinkColumn('Link', display_text='Open ↗')
        }
    )

    st.markdown("""
    <br>
    <div style='background:linear-gradient(135deg,#f0fdf4,#eff6ff);
                border-radius:14px;padding:20px 28px;
                border:1px solid rgba(5,150,105,0.2);'>
        <p style='color:#065f46;font-weight:600;font-size:0.95rem;margin:0 0 6px;'>
            📌 Data Quality Notes
        </p>
        <ul style='color:#374151;font-size:0.9rem;margin:0;padding-left:20px;line-height:1.8;'>
            <li>GDP and energy data are sparse for ~30% of low-income countries in OWID</li>
            <li>Sea level data ends in 2013 — adequate for trend analysis but not latest values</li>
            <li>Disaster data is aggregated globally — per-country breakdown not available in this version</li>
            <li>Temperature anomaly baseline is 1951–1980 (NASA standard)</li>
            <li>IEA data center figures are hardcoded from the April 2026 IEA report</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

"""
Utilidades y configuración de estilo CLARO v2.0
"""
import streamlit as st
import base64
from io import BytesIO
import pandas as pd

# Colores corporativos CLARO
CLARO_COLORS = {
    'primary': '#E31837',      # Rojo CLARO
    'secondary': '#FF6B6B',   # Rojo claro
    'accent': '#C41230',        # Rojo oscuro
    'background': '#FFFFFF',    # Blanco
    'text': '#333333',          # Negro suave
    'success': '#28a745',       # Verde éxito
    'warning': '#ffc107',     # Amarillo advertencia
    'danger': '#dc3545',        # Rojo peligro
    'info': '#17a2b8',        # Azul info
    'hfc_blue': '#0066CC'       # Azul HFC
}

def aplicar_estilo_claro():
    """Aplica CSS corporativo CLARO completo"""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Titillium Web', sans-serif;
    }}
    
    /* Header principal */
    .main-header {{
        background: linear-gradient(135deg, {CLARO_COLORS['primary']} 0%, {CLARO_COLORS['accent']} 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(227,24,55,0.3);
    }}
    
    .main-header h1 {{
        color: white !important;
        font-weight: 700;
        margin: 0;
        font-size: 2.8rem;
        letter-spacing: -0.5px;
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.95) !important;
        margin: 0.8rem 0 0 0;
        font-size: 1.2rem;
        font-weight: 400;
    }}
    
    /* Botones primarios */
    .stButton > button {{
        background-color: {CLARO_COLORS['primary']} !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(227,24,55,0.3) !important;
        font-size: 1rem !important;
    }}
    
    .stButton > button:hover {{
        background-color: {CLARO_COLORS['accent']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(227,24,55,0.4) !important;
    }}
    
    .stButton > button:disabled {{
        background-color: #cccccc !important;
        color: #666666 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        margin-bottom: 1rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
        color: {CLARO_COLORS['text']};
        border: none;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {CLARO_COLORS['primary']} !important;
        color: white !important;
        box-shadow: 0 -4px 8px rgba(227,24,55,0.2);
    }}
    
    /* Métricas */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 5px solid {CLARO_COLORS['primary']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }}
    
    [data-testid="metric-container"] label {{
        color: {CLARO_COLORS['primary']} !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    [data-testid="metric-container"] .metric-value {{
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #333 !important;
    }}
    
    /* Cards */
    .claro-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }}
    
    .claro-card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }}
    
    .claro-card h3 {{
        color: {CLARO_COLORS['primary']};
        margin-top: 0;
        border-bottom: 3px solid {CLARO_COLORS['secondary']};
        padding-bottom: 0.5rem;
        font-weight: 700;
    }}
    
    /* Cajas de estado */
    .success-box {{
        background-color: #d4edda;
        border-left: 5px solid {CLARO_COLORS['success']};
        padding: 1.2rem;
        border-radius: 8px;
        color: #155724;
        margin: 1rem 0;
    }}
    
    .warning-box {{
        background-color: #fff3cd;
        border-left: 5px solid {CLARO_COLORS['warning']};
        padding: 1.2rem;
        border-radius: 8px;
        color: #856404;
        margin: 1rem 0;
    }}
    
    .error-box {{
        background-color: #f8d7da;
        border-left: 5px solid {CLARO_COLORS['danger']};
        padding: 1.2rem;
        border-radius: 8px;
        color: #721c24;
        margin: 1rem 0;
    }}
    
    .info-box {{
        background-color: #d1ecf1;
        border-left: 5px solid {CLARO_COLORS['info']};
        padding: 1.2rem;
        border-radius: 8px;
        color: #0c5460;
        margin: 1rem 0;
    }}
    
    /* Barra de progreso */
    .stProgress > div > div > div > div {{
        background-color: {CLARO_COLORS['primary']} !important;
        border-radius: 10px;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #f8f9fa;
        border-right: 2px solid #e9ecef;
    }}
    
    [data-testid="stSidebar"] h1 {{
        color: {CLARO_COLORS['primary']};
        font-size: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    /* File uploader */
    .stFileUploader {{
        border: 2px dashed {CLARO_COLORS['secondary']};
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .stFileUploader:hover {{
        border-color: {CLARO_COLORS['primary']};
        background-color: #fff5f5;
    }}
    
    /* DataFrames */
    .dataframe {{
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border: none;
    }}
    
    .dataframe th {{
        background-color: {CLARO_COLORS['primary']} !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 14px !important;
        font-size: 0.9rem;
    }}
    
    .dataframe td {{
        padding: 12px !important;
        border-bottom: 1px solid #e0e0e0;
        font-size: 0.9rem;
    }}
    
    .dataframe tr:hover {{
        background-color: #f5f5f5;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: #666;
        border-top: 3px solid {CLARO_COLORS['primary']};
        margin-top: 3rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 16px;
    }}
    
    /* Animaciones */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .animate-fade-in {{
        animation: fadeIn 0.6s ease-out;
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    .pulse {{
        animation: pulse 2s infinite;
    }}
    
    /* Spinners y estados de carga */
    .stSpinner > div {{
        border-top-color: {CLARO_COLORS['primary']} !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        border-radius: 8px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {CLARO_COLORS['primary']} !important;
        box-shadow: 0 0 0 3px rgba(227,24,55,0.1) !important;
    }}
    
    /* Radio buttons */
    .stRadio > div {{
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
    }}
    
    .stRadio > div > div > label {{
        font-weight: 600;
        color: #333;
    }}
    </style>
    """, unsafe_allow_html=True)

def crear_card(titulo, contenido, tipo="default"):
    """Crea una card HTML estilizada"""
    colores = {
        "default": CLARO_COLORS['primary'],
        "success": CLARO_COLORS['success'],
        "warning": CLARO_COLORS['warning'],
        "danger": CLARO_COLORS['danger'],
        "info": CLARO_COLORS['info'],
        "hfc": CLARO_COLORS['hfc_blue']
    }
    color = colores.get(tipo, colores['default'])
    
    return f"""
    <div class="claro-card" style="border-top: 4px solid {color};">
        <h3 style="color: {color}; margin-top: 0;">{titulo}</h3>
        {contenido}
    </div>
    """

def crear_download_link(df, filename="resultado.xlsx", texto="📥 Descargar Excel"):
    """Genera link de descarga para DataFrame con estilo CLARO"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cobertura')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    
    return f"""
    <div style="text-align: center; margin: 1rem 0;">
        <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
           download="{filename}" 
           style="
               display: inline-block;
               background: linear-gradient(135deg, {CLARO_COLORS['primary']} 0%, {CLARO_COLORS['accent']} 100%);
               color: white;
               padding: 14px 28px;
               text-decoration: none;
               border-radius: 10px;
               font-weight: 600;
               font-size: 1.1rem;
               transition: all 0.3s ease;
               box-shadow: 0 4px 8px rgba(227,24,55,0.3);
           "
           onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(227,24,55,0.4)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 8px rgba(227,24,55,0.3)';"
        >
            {texto}
        </a>
    </div>
    """

def mostrar_resumen_analisis(resumen):
    """Muestra métricas del análisis en 4 columnas"""
    cols = st.columns(4)
    
    with cols[0]:
        st.metric(
            "Total Puntos", 
            f"{resumen['total']:,}",
            help="Total de órdenes analizadas"
        )
    with cols[1]:
        delta_ftth = f"{resumen['con_ftth']/resumen['total']*100:.1f}%" if resumen['total'] > 0 else "0%"
        st.metric(
            "Con FTTH", 
            f"{resumen['con_ftth']:,}", 
            delta=delta_ftth,
            delta_color="normal",
            help="Órdenes con cobertura de fibra óptica"
        )
    with cols[2]:
        delta_hfc = f"{resumen['con_hfc']/resumen['total']*100:.1f}%" if resumen['total'] > 0 else "0%"
        st.metric(
            "Con HFC", 
            f"{resumen['con_hfc']:,}",
            delta=delta_hfc,
            delta_color="normal",
            help="Órdenes con cobertura HFC (cable)"
        )
    with cols[3]:
        delta_sin = f"{resumen['sin_cobertura']/resumen['total']*100:.1f}%" if resumen['total'] > 0 else "0%"
        st.metric(
            "Sin Cobertura", 
            f"{resumen['sin_cobertura']:,}",
            delta=delta_sin,
            delta_color="inverse",
            help="Órdenes sin cobertura identificada"
        )

def mostrar_estado_carga(mensaje, tipo="info"):
    """Muestra mensaje de estado estilizado"""
    estilos = {
        "info": ("ℹ️", CLARO_COLORS['info']),
        "success": ("✅", CLARO_COLORS['success']),
        "warning": ("⚠️", CLARO_COLORS['warning']),
        "error": ("❌", CLARO_COLORS['danger'])
    }
    icono, color = estilos.get(tipo, estilos["info"])
    
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {color};
        background-color: {color}15;
        margin: 1rem 0;
    ">
        <span style="font-weight: 600; color: {color};">{icono} {mensaje}</span>
    </div>
    """, unsafe_allow_html=True)
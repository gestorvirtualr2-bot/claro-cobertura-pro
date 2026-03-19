"""
CLARO COBERTURA PRO v2.0
Sistema Profesional de Análisis y Consulta de Redes FTTH/HFC
Optimizado para Streamlit Cloud - Despliegue Gratuito
"""
import streamlit as st
import pandas as pd
import tempfile
import os
from core_analyzer import ClaroCoverageAnalyzer
from map_viewer import MapaCobertura
from utils import (
    aplicar_estilo_claro, crear_card, crear_download_link, 
    mostrar_resumen_analisis, CLARO_COLORS, mostrar_estado_carga
)

# ==================== CONFIGURACIÓN PÁGINA ====================
st.set_page_config(
    page_title="CLARO - Análisis de Cobertura Pro",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos corporativos CLARO
aplicar_estilo_claro()

# ==================== INICIALIZACIÓN SESSION STATE ====================
def init_session_state():
    defaults = {
        'kmz_uploaded': None,
        'kmz_path': None,
        'analisis_completado': False,
        'df_resultado': None,
        'resumen': None,
        'mapa_cobertura': None,
        'procesando': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== HEADER CORPORATIVO ====================
st.markdown("""
<div class="main-header animate-fade-in">
    <h1>📡 CLARO COBERTURA PRO</h1>
    <p>Sistema Profesional de Análisis y Consulta de Redes FTTH/HFC</p>
    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0 0.3rem;">
            ✓ FTTH Propio + Redes Neutras
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0 0.3rem;">
            ✓ HFC
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0 0.3rem;">
            ✓ Tolerancia 50m
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR - CONFIGURACIÓN ====================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="background: linear-gradient(135deg, #E31837 0%, #C41230 100%); 
                    color: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700;">📡 CLARO</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Sistema de Cobertura</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload KMZ - OBLIGATORIO PARA TODO EL SISTEMA
    st.markdown("### 🗂️ Archivo de Coberturas (KMZ)")
    st.markdown("<p style='font-size: 0.85rem; color: #666; margin-bottom: 1rem;'>"
                "Cargue primero el archivo KMZ con los polígonos de cobertura FTTH y HFC. "
                "Este archivo es necesario para todas las funcionalidades.</p>", unsafe_allow_html=True)
    
    kmz_file = st.file_uploader(
        "Cargar Red Fija (KMZ)", 
        type=['kmz'],
        help="Archivo KMZ con polígonos de cobertura FTTH y HFC",
        key="kmz_uploader"
    )
    
    if kmz_file is not None and st.session_state.kmz_uploaded is None:
        # Guardar temporalmente con nombre único pero mantener referencia
        with tempfile.NamedTemporaryFile(delete=False, suffix='.kmz', prefix='cobertura_claro_') as tmp_file:
            tmp_file.write(kmz_file.getvalue())
            st.session_state.kmz_path = tmp_file.name
            st.session_state.kmz_uploaded = True
        
        st.success("✅ Archivo KMZ cargado correctamente")
        
        # Inicializar mapa para consultas con spinner profesional
        with st.spinner("🗺️ Cargando coberturas en memoria..."):
            try:
                st.session_state.mapa_cobertura = MapaCobertura(st.session_state.kmz_path)
                st.success(f"🎯 Mapas listos: {len(st.session_state.mapa_cobertura.coberturas_ftth)} FTTH, "
                         f"{len(st.session_state.mapa_cobertura.coberturas_hfc)} HFC")
            except Exception as e:
                st.error(f"❌ Error cargando KMZ: {str(e)}")
                st.session_state.kmz_uploaded = None
    
    elif st.session_state.kmz_uploaded:
        st.info("🗺️ KMZ ya cargado en memoria")
    
    st.markdown("---")
    
    # Información del sistema
    with st.expander("ℹ️ Información del Sistema"):
        st.markdown("""
        **Versión:** 2.0 PRO  
        **Motor:** Streamlit Cloud  
        **Geocodificación:** Nominatim (OpenStreetMap)  
        **Tolerancia:** 50 metros  
        
        **Soporta:**
        - FTTH Greenfield/Brownfield
        - Redes Neutras
        - HFC tradicional
        """)
    
    st.markdown("""
    <div style="font-size: 0.75rem; color: #666; text-align: center; margin-top: 2rem;">
        <p>© 2024 CLARO Colombia</p>
        <p style="font-size: 0.7rem;">Sistema de Gestión de Redes</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== CONTENIDO PRINCIPAL ====================

if st.session_state.kmz_uploaded is None:
    # Pantalla de bienvenida cuando no hay KMZ
    st.markdown("""
    <div style="text-align: center; padding: 5rem 2rem; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                border-radius: 16px; margin: 2rem 0; border: 2px dashed #E31837;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
        <h2 style="color: #E31837; margin-bottom: 1rem; font-size: 2rem;">Bienvenido al Sistema CLARO</h2>
        <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            Para comenzar a utilizar el sistema de análisis de cobertura, 
            por favor cargue el archivo de coberturas (KMZ) en el panel lateral.
        </p>
        
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 3rem;">
            <div style="background: white; padding: 2rem; border-radius: 12px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 280px; 
                        border-top: 4px solid #E31837; transition: transform 0.3s;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                <h4 style="color: #E31837; margin-bottom: 0.5rem;">Análisis Masivo</h4>
                <p style="font-size: 0.9rem; color: #666; line-height: 1.5;">
                    Procese archivos Excel con múltiples coordenadas de órdenes de trabajo
                </p>
            </div>
            
            <div style="background: white; padding: 2rem; border-radius: 12px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 280px;
                        border-top: 4px solid #0066CC; transition: transform 0.3s;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
                <h4 style="color: #0066CC; margin-bottom: 0.5rem;">Consultas Tiempo Real</h4>
                <p style="font-size: 0.9rem; color: #666; line-height: 1.5;">
                    Busque por nodo, coordenadas exactas o dirección geocodificada
                </p>
            </div>
            
            <div style="background: white; padding: 2rem; border-radius: 12px; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 280px;
                        border-top: 4px solid #28a745; transition: transform 0.3s;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🗺️</div>
                <h4 style="color: #28a745; margin-bottom: 0.5rem;">Visualización</h4>
                <p style="font-size: 0.9rem; color: #666; line-height: 1.5;">
                    Mapas interactivos con polígonos de cobertura y ubicaciones
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # KMZ cargado - Mostrar tabs principales
    tab1, tab2 = st.tabs([
        "📊 ANÁLISIS MASIVO DE ÓRDENES", 
        "🔍 CONSULTAS DE COBERTURA"
    ])
    
    # ==================== TAB 1: ANÁLISIS MASIVO ====================
    with tab1:
        st.markdown("### 📊 Análisis de Órdenes del Día Siguiente")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="claro-card" style="border-left: 4px solid #E31837;">
                <h3 style="color: #E31837;">📁 Cargar Archivo de Órdenes</h3>
                <p style="color: #666; margin-bottom: 1rem; line-height: 1.6;">
                    Seleccione el archivo Excel con las órdenes a analizar.<br>
                    <strong>El sistema automáticamente:</strong><br>
                    • Renombrará el archivo internamente como <code>Exporte_Dia_Siguiente.xlsx</code><br>
                    • Procesará solo actividades: Instalaciones y Traslados<br>
                    • Filtrará estado: Pendiente
                </p>
                <div style="background: #fff5f5; padding: 0.8rem; border-radius: 6px; font-size: 0.85rem; color: #666;">
                    <strong>Columnas requeridas:</strong> Tipo de Actividad, Estado, Coordenada X, Coordenada Y
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            excel_file = st.file_uploader(
                "Seleccionar archivo Excel de órdenes",
                type=['xlsx', 'xls'],
                help="Cualquier nombre de archivo será procesado correctamente",
                key="excel_uploader"
            )
            
            if excel_file:
                # Validar columnas antes de procesar
                try:
                    df_check = pd.read_excel(excel_file, nrows=5)
                    columnas_requeridas = ['Tipo de Actividad', 'Estado', 'Coordenada X', 'Coordenada Y']
                    columnas_faltantes = [col for col in columnas_requeridas if col not in df_check.columns]
                    
                    if columnas_faltantes:
                        st.error(f"❌ Columnas faltantes: {', '.join(columnas_faltantes)}")
                        st.info("💡 Asegúrese de que el archivo tenga el formato correcto de exporte de órdenes")
                    else:
                        st.success("✅ Formato de archivo válido detectado")
                        
                        # Guardar temporalmente RENOMBRANDO internamente
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', prefix='Exporte_Dia_Siguiente_') as tmp_excel:
                            tmp_excel.write(excel_file.getvalue())
                            excel_path = tmp_excel.name
                        
                        # Botón de análisis prominente
                        st.markdown("---")
                        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                        
                        with col_btn2:
                            if st.button("🚀 INICIAR ANÁLISIS DE COBERTURA", 
                                       use_container_width=True, 
                                       type="primary",
                                       disabled=st.session_state.procesando):
                                
                                st.session_state.procesando = True
                                
                                # Contenedor de progreso
                                progress_container = st.container()
                                with progress_container:
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                                    detalle_text = st.empty()
                                    
                                    def update_progress(porcentaje, mensaje):
                                        progress_bar.progress(min(porcentaje, 100))
                                        status_text.markdown(
                                            f"<h4 style='text-align: center; color: #E31837; margin: 0;'>{mensaje}</h4>", 
                                            unsafe_allow_html=True
                                        )
                                        if porcentaje >= 60:
                                            detalle_text.markdown(
                                                f"<p style='text-align: center; color: #666; font-size: 0.9rem;'>"
                                                f"Procesando {porcentaje}% - Esto puede tomar varios minutos dependiendo del volumen</p>",
                                                unsafe_allow_html=True
                                            )
                                    
                                    try:
                                        analyzer = ClaroCoverageAnalyzer(excel_path, st.session_state.kmz_path)
                                        df_resultado, resumen = analyzer.analizar(update_progress)
                                        
                                        st.session_state.df_resultado = df_resultado
                                        st.session_state.resumen = resumen
                                        st.session_state.analisis_completado = True
                                        
                                        status_text.markdown(
                                            "<div class='success-box' style='text-align: center;'>"
                                            "<h4>✅ Análisis completado exitosamente</h4>"
                                            "</div>", 
                                            unsafe_allow_html=True
                                        )
                                        
                                    except Exception as e:
                                        st.error(f"❌ Error en el análisis: {str(e)}")
                                        st.session_state.analisis_completado = False
                                    
                                    finally:
                                        st.session_state.procesando = False
                                        # Limpiar archivo temporal
                                        try:
                                            os.unlink(excel_path)
                                        except:
                                            pass
                
                except Exception as e:
                    st.error(f"❌ Error leyendo archivo: {str(e)}")
        
        with col2:
            st.markdown(f"""
            <div class="claro-card" style="background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%); border: 2px solid {CLARO_COLORS['primary']};">
                <h3 style="color: {CLARO_COLORS['primary']};">⚙️ Configuración Activa</h3>
                <div style="font-size: 0.9rem; color: #333; line-height: 2;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 0.3rem 0;">
                        <span><strong>Tolerancia:</strong></span>
                        <span style="color: {CLARO_COLORS['primary']}; font-weight: 600;">50 metros</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 0.3rem 0;">
                        <span><strong>Actividades:</strong></span>
                        <span>Instalaciones, Traslados</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 0.3rem 0;">
                        <span><strong>Estado:</strong></span>
                        <span>Pendiente</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 0.3rem 0;">
                        <span><strong>Sistemas:</strong></span>
                        <span style="text-align: right;">FTTH + HFC +<br>Redes Neutras</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.analisis_completado:
                st.markdown("""
                <div class="claro-card" style="background: #d4edda; border-left: 4px solid #28a745;">
                    <h4 style="color: #155724; margin-top: 0;">✅ Estado</h4>
                    <p style="color: #155724; margin: 0; font-size: 0.9rem;">
                        Análisis completado.<br>Resultados disponibles para descarga.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Mostrar resultados si existen
        if st.session_state.analisis_completado and st.session_state.resumen:
            st.markdown("---")
            st.markdown("### 📈 Resultados del Análisis")
            
            # Métricas principales
            mostrar_resumen_analisis(st.session_state.resumen)
            
            # Gráfico de distribución
            import plotly.graph_objects as go
            
            labels = ['FTTH', 'HFC', 'Ambas', 'Sin Cobertura']
            values = [
                st.session_state.resumen['con_ftth'] - st.session_state.resumen['con_ambas'],
                st.session_state.resumen['con_hfc'] - st.session_state.resumen['con_ambas'],
                st.session_state.resumen['con_ambas'],
                st.session_state.resumen['sin_cobertura']
            ]
            colors = [CLARO_COLORS['primary'], CLARO_COLORS['hfc_blue'], '#9932CC', '#CCCCCC']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.4,
                marker_colors=colors,
                textinfo='percent+label',
                textfont_size=12
            )])
            
            fig.update_layout(
                title_text="Distribución de Cobertura",
                annotations=[dict(
                    text=f"{st.session_state.resumen['total']:,}<br>Total", 
                    x=0.5, y=0.5, 
                    font_size=18, 
                    showarrow=False,
                    font=dict(color='#333')
                )],
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            
            col_chart, col_table = st.columns([1, 2])
            
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            
            with col_table:
                # Filtros dinámicos
                st.markdown("#### 📋 Filtros de Visualización")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    filtro_cobertura = st.selectbox(
                        "Cobertura", 
                        ["Todos", "Sí - Con cobertura", "No - Sin cobertura"]
                    )
                with col_f2:
                    if 'NODO FTTH' in st.session_state.df_resultado.columns:
                        nodos = ["Todos"] + sorted([n for n in st.session_state.df_resultado['NODO FTTH'].dropna().unique() if n and str(n) != 'nan'])
                        filtro_nodo = st.selectbox("Nodo FTTH", nodos[:20])  # Limitar para performance
                
                # Aplicar filtros
                df_display = st.session_state.df_resultado.copy()
                if filtro_cobertura == "Sí - Con cobertura":
                    df_display = df_display[df_display['COBERTURA'] == 'Si']
                elif filtro_cobertura == "No - Sin cobertura":
                    df_display = df_display[df_display['COBERTURA'] == 'No']
                
                if 'filtro_nodo' in locals() and filtro_nodo != "Todos":
                    df_display = df_display[df_display['NODO FTTH'] == filtro_nodo]
                
                # Mostrar tabla con scroll
                st.dataframe(
                    df_display, 
                    use_container_width=True, 
                    height=350,
                    column_config={
                        "COBERTURA": st.column_config.Column(
                            "COBERTURA",
                            help="Indica si tiene cobertura FTTH o HFC",
                            width="medium"
                        )
                    }
                )
            
            # Botón de descarga prominente
            st.markdown("---")
            col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
            with col_d2:
                output = crear_download_link(
                    st.session_state.df_resultado, 
                    filename=f"Resultado_Cobertura_CLARO_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    texto="📥 DESCARGAR RESULTADO COMPLETO (Excel)"
                )
                st.markdown(output, unsafe_allow_html=True)
                st.markdown(
                    "<p style='text-align: center; color: #666; font-size: 0.8rem; margin-top: 0.5rem;'>"
                    "Incluye todas las columnas originales + Nodo HFC + Nodo FTTH + Estado Cobertura</p>",
                    unsafe_allow_html=True
                )
    
    # ==================== TAB 2: CONSULTAS ====================
    with tab2:
        st.markdown("### 🔍 Consultas de Cobertura en Tiempo Real")
        st.markdown("<p style='color: #666; margin-bottom: 1.5rem;'>"
                   "Seleccione el tipo de consulta para verificar cobertura instantáneamente</p>", 
                   unsafe_allow_html=True)
        
        # Sub-tabs para los 3 tipos de consulta
        consulta_tab1, consulta_tab2, consulta_tab3 = st.tabs([
            "🏷️ Consulta por Nodo",
            "📍 Consulta por Coordenadas", 
            "🏠 Consulta por Dirección"
        ])
        
        # ---- CONSULTA POR NODO ----
        with consulta_tab1:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                <div class="claro-card">
                    <h3>Buscar por Nodo</h3>
                    <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">
                        Ingrese el nombre del nodo para visualizar su polígono de cobertura.
                        El sistema buscará coincidencias parciales (no es case-sensitive).
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                tipo_nodo = st.radio(
                    "Tipo de Red", 
                    ["FTTH", "HFC"], 
                    horizontal=True,
                    help="FTTH = Fibra óptica hasta el hogar (Rojo), HFC = Cable coaxial (Azul)"
                )
                
                nombre_busqueda = st.text_input(
                    "Nombre del Nodo", 
                    placeholder="Ej: NODO_CENTRO_01 o CENTRO",
                    help="Puede ingresar parte del nombre"
                )
                
                if st.button("🔍 Buscar Nodo", type="primary", use_container_width=True):
                    if nombre_busqueda and st.session_state.mapa_cobertura:
                        with st.spinner(f"Buscando {tipo_nodo}..."):
                            resultado = st.session_state.mapa_cobertura.buscar_por_nodo(
                                nombre_busqueda, 
                                tipo=tipo_nodo
                            )
                        
                        if resultado is not None:
                            st.success(f"✅ Encontrado: {resultado['nombre']}")
                            
                            # Calcular centro del polígono
                            centro = resultado.geometry.centroid
                            
                            # Crear mapa destacando el polígono
                            mapa = st.session_state.mapa_cobertura.crear_mapa_consulta(
                                centro=[centro.y, centro.x],
                                zoom=15,
                                poligono_destacado=resultado['nombre'],
                                tipo_destacado=tipo_nodo
                            )
                            
                            # Agregar marcador en el centro
                            color = 'red' if tipo_nodo == "FTTH" else 'blue'
                            mapa = st.session_state.mapa_cobertura.agregar_marcador(
                                mapa, centro.y, centro.x,
                                f"<b>{resultado['nombre']}</b><br>Tipo: {tipo_nodo}<br>"
                                f"Coordenadas: {centro.y:.6f}, {centro.x:.6f}",
                                color=color
                            )
                            
                            with col2:
                                from streamlit_folium import st_folium
                                st_folium(mapa, width=800, height=600, returned_objects=[])
                        else:
                            st.error(f"❌ No se encontró '{nombre_busqueda}' en red {tipo_nodo}")
                            # Sugerencias si hay similares
                            coberturas = (st.session_state.mapa_cobertura.coberturas_ftth 
                                        if tipo_nodo == "FTTH" 
                                        else st.session_state.mapa_cobertura.coberturas_hfc)
                            if coberturas is not None and len(coberturas) > 0:
                                similares = coberturas[coberturas['nombre'].str.contains(nombre_busqueda[:3], case=False, na=False)]
                                if len(similares) > 0:
                                    st.info(f"💡 Nodos similares: {', '.join(similares['nombre'].head(5).tolist())}")
                    else:
                        st.warning("⚠️ Ingrese un nombre de nodo para buscar")
            
            with col2:
                if not nombre_busqueda:
                    # Mapa por defecto mostrando todos los polígonos
                    mapa_default = st.session_state.mapa_cobertura.crear_mapa_consulta(
                        centro=[4.6097, -74.0817],
                        zoom=11
                    )
                    from streamlit_folium import st_folium
                    st_folium(mapa_default, width=800, height=600, returned_objects=[])
        
        # ---- CONSULTA POR COORDENADAS ----
        with consulta_tab2:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                <div class="claro-card">
                    <h3>Buscar por Coordenadas</h3>
                    <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">
                        Ingrese latitud y longitud en grados decimales (WGS84).
                        El sistema verificará si el punto cae dentro de algún polígono de cobertura.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Inputs con formato específico
                col_lat, col_lon = st.columns(2)
                with col_lat:
                    lat = st.number_input(
                        "Latitud", 
                        value=4.6097, 
                        format="%.6f",
                        help="Ejemplo: 4.609711 (Bogotá centro)",
                        step=0.000001
                    )
                with col_lon:
                    lon = st.number_input(
                        "Longitud", 
                        value=-74.0817, 
                        format="%.6f",
                        help="Ejemplo: -74.081749 (Bogotá centro)",
                        step=0.000001
                    )
                
                if st.button("📍 Verificar Cobertura", type="primary", use_container_width=True):
                    with st.spinner("Analizando cobertura..."):
                        resultado = st.session_state.mapa_cobertura.buscar_por_coordenadas(lat, lon)
                    
                    # Mostrar resultados con estilos
                    if resultado['tiene_cobertura']:
                        mensaje = f"""
                        <div class='success-box' style='border-left: 4px solid #28a745; background: #d4edda; padding: 1rem; border-radius: 4px;'>
                            <h4 style='color: #155724; margin: 0 0 0.5rem 0;'>✅ COBERTURA DISPONIBLE</h4>
                            <div style='color: #155724; font-size: 0.9rem;'>
                        """
                        if resultado['ftth']:
                            mensaje += f"<p style='margin: 0.2rem 0;'><strong>🔴 FTTH:</strong> {resultado['ftth']}</p>"
                        if resultado['hfc']:
                            mensaje += f"<p style='margin: 0.2rem 0;'><strong>🔵 HFC:</strong> {resultado['hfc']}</p>"
                        mensaje += "</div></div>"
                        st.markdown(mensaje, unsafe_allow_html=True)
                        color_marcador = 'green'
                    else:
                        st.markdown("""
                        <div class='error-box' style='border-left: 4px solid #dc3545; background: #f8d7da; padding: 1rem; border-radius: 4px;'>
                            <h4 style='color: #721c24; margin: 0 0 0.5rem 0;'>❌ SIN COBERTURA CLARO</h4>
                            <p style='color: #721c24; margin: 0; font-size: 0.9rem;'>
                                Esta ubicación no está dentro de ningún polígono de cobertura activa.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        color_marcador = 'red'
                    
                    # Crear mapa centrado en el punto
                    mapa = st.session_state.mapa_cobertura.crear_mapa_consulta(
                        centro=[lat, lon],
                        zoom=17
                    )
                    
                    # Preparar popup
                    popup_text = f"""
                    <b>Coordenadas Consultadas</b><br>
                    Lat: {lat:.6f}<br>
                    Lon: {lon:.6f}<br>
                    <hr style='margin: 0.5rem 0;'>
                    """
                    if resultado['ftth']:
                        popup_text += f"<span style='color: #E31837;'>🔴 FTTH: {resultado['ftth']}</span><br>"
                    if resultado['hfc']:
                        popup_text += f"<span style='color: #0066CC;'>🔵 HFC: {resultado['hfc']}</span><br>"
                    if not resultado['tiene_cobertura']:
                        popup_text += "<span style='color: #dc3545;'>❌ Sin cobertura</span>"
                    
                    mapa = st.session_state.mapa_cobertura.agregar_marcador(
                        mapa, lat, lon, popup_text, color=color_marcador
                    )
                    
                    with col2:
                        from streamlit_folium import st_folium
                        st_folium(mapa, width=800, height=600, returned_objects=[])
                else:
                    with col2:
                        mapa_default = st.session_state.mapa_cobertura.crear_mapa_consulta(
                            centro=[4.6097, -74.0817],
                            zoom=11
                        )
                        from streamlit_folium import st_folium
                        st_folium(mapa_default, width=800, height=600, returned_objects=[])
        
        # ---- CONSULTA POR DIRECCIÓN ----
        with consulta_tab3:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("""
                <div class="claro-card">
                    <h3>Buscar por Dirección Colombia</h3>
                    <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">
                        Soporta formatos de dirección colombianos estándar.
                        Utiliza geocodificación vía Nominatim (OpenStreetMap).
                    </p>
                    <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 6px; font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                        <strong>Ejemplos válidos:</strong><br>
                        • Calle 80 # 22-10, Bogotá<br>
                        • Carrera 15 # 45-32, Medellín<br>
                        • Avenida Chile 23-45, Cali<br>
                        • Calle 26 # 10-45, Bogotá, Colombia
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                direccion = st.text_input(
                    "Dirección completa",
                    placeholder="Ej: Calle 80 # 22-10, Bogotá",
                    help="Incluya ciudad para mejor precisión"
                )
                
                if st.button("🏠 Geocodificar y Verificar", type="primary", use_container_width=True):
                    if direccion:
                        with st.spinner("🔍 Geocodificando dirección..."):
                            geo_result = st.session_state.mapa_cobertura.geocodificar_direccion(direccion)
                        
                        if geo_result:
                            lat, lon = geo_result['latitud'], geo_result['longitud']
                            
                            st.success(f"✅ Ubicación encontrada")
                            st.info(f"📍 {geo_result['direccion'][:80]}...")
                            st.markdown(f"<p style='font-size: 0.9rem; color: #666;'>"
                                       f"<strong>Coordenadas:</strong> {lat:.6f}, {lon:.6f}</p>", 
                                       unsafe_allow_html=True)
                            
                            # Verificar cobertura
                            with st.spinner("Verificando cobertura..."):
                                resultado = st.session_state.mapa_cobertura.buscar_por_coordenadas(lat, lon)
                            
                            if resultado['tiene_cobertura']:
                                mensaje = "<div class='success-box' style='border-left: 4px solid #28a745; background: #d4edda; padding: 1rem; border-radius: 4px; margin-top: 1rem;'>"
                                mensaje += "<h4 style='color: #155724; margin: 0 0 0.5rem 0;'>✅ COBERTURA DISPONIBLE</h4>"
                                if resultado['ftth']:
                                    mensaje += f"<p style='margin: 0.2rem 0; color: #155724;'><strong>🔴 FTTH:</strong> {resultado['ftth']}</p>"
                                if resultado['hfc']:
                                    mensaje += f"<p style='margin: 0.2rem 0; color: #155724;'><strong>🔵 HFC:</strong> {resultado['hfc']}</p>"
                                mensaje += "</div>"
                                st.markdown(mensaje, unsafe_allow_html=True)
                                color_marcador = 'green'
                            else:
                                st.markdown("""
                                <div class='error-box' style='border-left: 4px solid #dc3545; background: #f8d7da; padding: 1rem; border-radius: 4px; margin-top: 1rem;'>
                                    <h4 style='color: #721c24; margin: 0 0 0.5rem 0;'>❌ SIN COBERTURA</h4>
                                    <p style='color: #721c24; margin: 0;'>Esta dirección no cuenta con cobertura CLARO.</p>
                                </div>
                                """, unsafe_allow_html=True)
                                color_marcador = 'red'
                            
                            # Mapa
                            mapa = st.session_state.mapa_cobertura.crear_mapa_consulta(
                                centro=[lat, lon],
                                zoom=17
                            )
                            
                            popup_text = f"<b>{direccion}</b><br>Lat: {lat:.6f}<br>Lon: {lon:.6f}<hr>"
                            if resultado['ftth']:
                                popup_text += f"🔴 FTTH: {resultado['ftth']}<br>"
                            if resultado['hfc']:
                                popup_text += f"🔵 HFC: {resultado['hfc']}"
                            
                            mapa = st.session_state.mapa_cobertura.agregar_marcador(
                                mapa, lat, lon, popup_text, color=color_marcador
                            )
                            
                            with col2:
                                from streamlit_folium import st_folium
                                st_folium(mapa, width=800, height=600, returned_objects=[])
                        else:
                            st.error("❌ No se pudo geocodificar la dirección. Intente:")
                            st.markdown("""
                            <ul style='color: #666; font-size: 0.9rem;'>
                                <li>Incluir la ciudad (ej: ', Bogotá')</li>
                                <li>Usar formato: Calle/Carrera # Num - Num</li>
                                <li>Verificar que la dirección exista</li>
                                <li>Usar coordenadas exactas en la pestaña anterior</li>
                            </ul>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ Ingrese una dirección para buscar")
                else:
                    with col2:
                        mapa_default = st.session_state.mapa_cobertura.crear_mapa_consulta(
                            centro=[4.6097, -74.0817],
                            zoom=11
                        )
                        from streamlit_folium import st_folium
                        st_folium(mapa_default, width=800, height=600, returned_objects=[])

# ==================== FOOTER ====================
st.markdown("""
<div class="footer" style="text-align: center; padding: 2rem; 
                          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                          border-radius: 12px; margin-top: 3rem; border-top: 3px solid #E31837;">
    <p style="margin: 0; color: #E31837; font-weight: 600; font-size: 1.1rem;">
        <strong>CLARO Colombia</strong>
    </p>
    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">
        Sistema de Análisis de Cobertura v2.0 PRO
    </p>
    <p style="margin: 0.5rem 0 0 0; color: #999; font-size: 0.8rem;">
        Desplegado en Streamlit Cloud | Procesamiento local seguro
    </p>
</div>
""", unsafe_allow_html=True)
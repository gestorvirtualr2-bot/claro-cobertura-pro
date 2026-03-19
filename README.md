# 📡 CLARO COBERTURA PRO

Sistema profesional de análisis y consulta de cobertura de redes FTTH/HFC para CLARO Colombia.

## 🚀 Despliegue en Streamlit Cloud (Gratuito)

1. **Crear repositorio GitHub** con estos archivos
2. **Ir a** [share.streamlit.io](https://share.streamlit.io)
3. **Conectar cuenta GitHub** y seleccionar el repositorio
4. **Archivo principal:** `app.py`
5. **Deploy!** La app estará online en segundos

## 📋 Funcionalidades

### 1. Análisis Masivo de Órdenes
- Carga archivo Excel (Exporte_Dia_Siguiente.xlsx)
- Renombra automáticamente el archivo recibido
- Procesa FTTH (Propio + Redes Neutras) + HFC
- Tolerancia: 50 metros
- Descarga resultados en Excel
- Dashboard con métricas y gráficos

### 2. Consultas en Tiempo Real
- **Por Nodo:** Busca HFC o FTTH y visualiza polígono
- **Por Coordenadas:** Lat/Lng con verificación instantánea
- **Por Dirección:** Geocodificación Colombia (Calle/Carrera format)

## 🎨 Diseño Corporativo
- Paleta de colores CLARO (Rojo #E31837)
- Interfaz profesional y responsive
- Mapas interactivos con Folium
- Visualizaciones con Plotly

## 📦 Dependencias
Ver `requirements.txt`

## 🔒 Notas
- Los archivos KMZ y Excel se procesan en memoria temporal
- No se almacenan datos entre sesiones
- Compatible con Redes Neutras del KMZ
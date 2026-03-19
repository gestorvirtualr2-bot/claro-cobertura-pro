"""
Módulo de visualización de mapas - Consultas en tiempo real v2.0
Optimizado para performance en Streamlit Cloud
"""
import folium
from folium.plugins import Draw, Fullscreen, LocateControl, MarkerCluster
import geopandas as gpd
from shapely.geometry import Point
import streamlit as st
import zipfile
import tempfile
import os
import xml.etree.ElementTree as ET
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class MapaCobertura:
    def __init__(self, kmz_file=None):
        self.kmz_file = kmz_file
        self.coberturas_ftth = None
        self.coberturas_hfc = None
        # User agent único para evitar bloqueos
        self.geolocator = Nominatim(
            user_agent="claro_cobertura_pro_app_v2_0",
            timeout=10
        )
        
        if kmz_file:
            self._cargar_kmz()
    
    def _cargar_kmz(self):
        """Carga coberturas del KMZ con manejo de errores robusto"""
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(self.kmz_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            kml_path = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file == 'doc.kml':
                        kml_path = os.path.join(root, file)
                        break
                if kml_path:
                    break

            if kml_path:
                self._extraer_poligonos(kml_path)
        except Exception as e:
            st.error(f"Error cargando KMZ: {e}")
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _extraer_poligonos(self, kml_path):
        """Extrae polígonos del KML de forma optimizada"""
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        try:
            tree = ET.parse(kml_path)
            root = tree.getroot()
            
            ftth_list = []
            hfc_list = []
            
            for folder in root.findall('.//kml:Folder', ns):
                name_elem = folder.find('kml:name', ns)
                if name_elem is None:
                    continue
                
                folder_name = name_elem.text or ""
                folder_upper = folder_name.upper()
                
                # FTTH - Redes Neutras y Propio
                if any(x in folder_upper for x in ["COBERTURAS FTT", "RED NEUTRA", "NEUTRAS", "GREENFIELD", "BROWNFIELD"]) and "NO_APLICA" not in folder_upper:
                    for placemark in folder.findall('.//kml:Placemark', ns):
                        pm_name = self._extraer_nombre_placemark(placemark, ns)
                        coords = self._extraer_coordenadas_placemark(placemark, ns)
                        
                        if coords:
                            from shapely.geometry import Polygon
                            try:
                                poly = Polygon(coords)
                                if poly.is_valid and poly.area > 0:  # Validar área no nula
                                    ftth_list.append({
                                        "nombre": pm_name,
                                        "geometry": poly,
                                        "tipo": "FTTH"
                                    })
                            except:
                                continue
                
                # HFC
                if folder_upper == "HFC":
                    for placemark in folder.findall('.//kml:Placemark', ns):
                        pm_name = self._extraer_nombre_placemark(placemark, ns)
                        coords = self._extraer_coordenadas_placemark(placemark, ns)
                        
                        if coords:
                            from shapely.geometry import Polygon
                            try:
                                poly = Polygon(coords)
                                if poly.is_valid and poly.area > 0:
                                    hfc_list.append({
                                        "nombre": pm_name,
                                        "geometry": poly,
                                        "tipo": "HFC"
                                    })
                            except:
                                continue
            
            if ftth_list:
                self.coberturas_ftth = gpd.GeoDataFrame(ftth_list, crs="EPSG:4326")
            if hfc_list:
                self.coberturas_hfc = gpd.GeoDataFrame(hfc_list, crs="EPSG:4326")
                
        except Exception as e:
            print(f"Error extrayendo polígonos: {e}")
    
    def _extraer_nombre_placemark(self, placemark, ns):
        """Extrae nombre del placemark buscando también en descripción"""
        pm_name_elem = placemark.find('kml:name', ns)
        pm_name = pm_name_elem.text if pm_name_elem is not None else "SIN_NOMBRE"
        
        desc_elem = placemark.find('kml:description', ns)
        desc = desc_elem.text if desc_elem is not None else ""
        
        # Buscar NOMBRE_TK en descripción (formato común en KMZ de CLARO)
        if desc and "NOMBRE_TK" in desc:
            match = re.search(r'NOMBRE_TK[^>]*>([^<]+)', desc)
            if match:
                return match.group(1).strip()
        return pm_name
    
    def _extraer_coordenadas_placemark(self, placemark, ns):
        """Extrae coordenadas del placemark de múltiples geometrías posibles"""
        coords = None
        
        # Polygon simple
        poly_elem = placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
        if poly_elem is not None and poly_elem.text:
            coords = self._parsear_coordenadas(poly_elem.text)
        
        # MultiGeometry (para MultiPolygon)
        if coords is None:
            multigeom = placemark.find('.//kml:MultiGeometry', ns)
            if multigeom is not None:
                poly_elem = multigeom.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
                if poly_elem is not None and poly_elem.text:
                    coords = self._parsear_coordenadas(poly_elem.text)
        return coords
    
    def _parsear_coordenadas(self, coords_text):
        """Parsea coordenadas KML a lista de tuplas (lon, lat)"""
        coords = []
        for punto in coords_text.strip().split():
            partes = punto.split(',')
            if len(partes) >= 2:
                try:
                    lon = float(partes[0])
                    lat = float(partes[1])
                    coords.append((lon, lat))
                except ValueError:
                    continue
        return coords if len(coords) >= 3 else None
    
    def buscar_por_nodo(self, nombre_nodo, tipo="FTTH"):
        """Busca polígono por nombre de nodo (búsqueda parcial case-insensitive)"""
        coberturas = self.coberturas_ftth if tipo == "FTTH" else self.coberturas_hfc
        if coberturas is None or len(coberturas) == 0:
            return None
        
        # Búsqueda parcial case-insensitive
        mask = coberturas['nombre'].str.contains(nombre_nodo, case=False, na=False, regex=False)
        resultado = coberturas[mask]
        
        if len(resultado) > 0:
            return resultado.iloc[0]
        return None
    
    def buscar_por_coordenadas(self, lat, lon):
        """Busca cobertura por coordenadas exactas"""
        punto = Point(lon, lat)
        resultado = {
            "punto": (lat, lon),
            "ftth": None,
            "hfc": None,
            "tiene_cobertura": False
        }
        
        # Revisar FTTH (vectorizado es más rápido, pero iteramos para nombre específico)
        if self.coberturas_ftth is not None and len(self.coberturas_ftth) > 0:
            contiene = self.coberturas_ftth[self.coberturas_ftth.contains(punto)]
            if len(contiene) > 0:
                resultado["ftth"] = contiene.iloc[0]['nombre']
                resultado["tiene_cobertura"] = True
        
        # Revisar HFC
        if self.coberturas_hfc is not None and len(self.coberturas_hfc) > 0:
            contiene = self.coberturas_hfc[self.coberturas_hfc.contains(punto)]
            if len(contiene) > 0:
                resultado["hfc"] = contiene.iloc[0]['nombre']
                resultado["tiene_cobertura"] = True
        
        return resultado
    
    def geocodificar_direccion(self, direccion):
        """Geocodifica dirección colombiana con manejo de errores robusto"""
        try:
            # Limpiar y preparar dirección
            direccion_limpia = direccion.strip()
            if not direccion_limpia.lower().endswith('colombia'):
                direccion_completa = f"{direccion_limpia}, Colombia"
            else:
                direccion_completa = direccion_limpia
            
            # Geocodificar con timeout
            location = self.geolocator.geocode(direccion_completa, timeout=10)
            
            if location:
                return {
                    "direccion": location.address,
                    "latitud": location.latitude,
                    "longitud": location.longitude,
                    "raw": location.raw
                }
            return None
            
        except GeocoderTimedOut:
            st.warning("⏱️ Tiempo de espera agotado geocodificando. Intente nuevamente.")
            return None
        except GeocoderServiceError as e:
            st.error(f"❌ Error del servicio de geocodificación: {e}")
            return None
        except Exception as e:
            st.error(f"❌ Error inesperado: {e}")
            return None
    
    def crear_mapa_consulta(self, centro=None, zoom=12, mostrar_poligonos=True, 
                           poligono_destacado=None, tipo_destacado="FTTH"):
        """Crea mapa base optimizado para consultas"""
        if centro is None:
            centro = [4.6097, -74.0817]  # Bogotá por defecto
        
        # Mapa base limpio y profesional
        m = folium.Map(
            location=centro,
            zoom_start=zoom,
            tiles='CartoDB positron',
            control_scale=True
        )
        
        # Capas adicionales
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
                       name='Satélite',
            control=True
        ).add_to(m)
        
        # Mostrar polígonos FTTH (rojos - color CLARO) - Optimizado: solo mostrar si no son demasiados
        if mostrar_poligonos and self.coberturas_ftth is not None and len(self.coberturas_ftth) > 0:
            # Si hay muchos polígonos, solo mostrar el destacado o limitar
            ftth_mostrar = self.coberturas_ftth
            if poligono_destacado:
                ftth_mostrar = self.coberturas_ftth[self.coberturas_ftth['nombre'] == poligono_destacado]
            
            for _, row in ftth_mostrar.iterrows():
                es_destacado = poligono_destacado and row['nombre'] == poligono_destacado
                color = '#E31837' if es_destacado else '#FF6B6B'
                weight = 4 if es_destacado else 1.5
                fill_opacity = 0.4 if es_destacado else 0.1
                
                folium.GeoJson(
                    row.geometry.__geo_interface__,
                    name=f"FTTH: {row['nombre']}",
                    style_function=lambda x, c=color, w=weight, f=fill_opacity: {
                        'fillColor': c,
                        'color': c,
                        'weight': w,
                        'fillOpacity': f
                    },
                    tooltip=f"FTTH: {row['nombre']}",
                    popup=folium.Popup(f"<b>FTTH:</b> {row['nombre']}", max_width=200)
                ).add_to(m)
        
        # Mostrar polígonos HFC (azul)
        if mostrar_poligonos and self.coberturas_hfc is not None and len(self.coberturas_hfc) > 0:
            hfc_mostrar = self.coberturas_hfc
            if poligono_destacado and tipo_destacado == "HFC":
                hfc_mostrar = self.coberturas_hfc[self.coberturas_hfc['nombre'] == poligono_destacado]
            
            for _, row in hfc_mostrar.iterrows():
                es_destacado = poligono_destacado and row['nombre'] == poligono_destacado and tipo_destacado == "HFC"
                color = '#0066CC' if es_destacado else '#4DA6FF'
                weight = 4 if es_destacado else 1.5
                fill_opacity = 0.4 if es_destacado else 0.1
                
                folium.GeoJson(
                    row.geometry.__geo_interface__,
                    name=f"HFC: {row['nombre']}",
                    style_function=lambda x, c=color, w=weight, f=fill_opacity: {
                        'fillColor': c,
                        'color': c,
                        'weight': w,
                        'fillOpacity': f
                    },
                    tooltip=f"HFC: {row['nombre']}",
                    popup=folium.Popup(f"<b>HFC:</b> {row['nombre']}", max_width=200)
                ).add_to(m)
        
        # Controles
        folium.LayerControl(collapsed=False).add_to(m)
        Fullscreen().add_to(m)
        LocateControl(auto_start=False).add_to(m)
        
        return m
    
    def agregar_marcador(self, mapa, lat, lon, popup_text, color='red'):
        """Agrega marcador personalizado al mapa"""
        icon_colors = {
            'red': 'red',
            'blue': 'blue', 
            'green': 'green',
            'orange': 'orange',
            'purple': 'purple'
        }
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(
                color=icon_colors.get(color, 'red'),
                icon='info-sign',
                prefix='glyphicon'
            )
        ).add_to(mapa)
        return mapa
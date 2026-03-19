"""
Módulo de análisis de cobertura - Core del sistema CLARO v2.0
CORREGIDO: Error de sintaxis en línea 170 (gpd.to_crs -> gdf.to_crs)
"""
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import os
import zipfile
import shutil
import xml.etree.ElementTree as ET
import re
import tempfile

# Constantes
TOLERANCIA_METROS = 50
TOLERANCIA_GRADOS = TOLERANCIA_METROS / 111000  # Conversión aproximada

class ClaroCoverageAnalyzer:
    def __init__(self, excel_file, kmz_file):
        self.excel_file = excel_file
        self.kmz_file = kmz_file
        self.df_resultado = None
        self.gdf_puntos = None
        self.coberturas_ftth = None
        self.coberturas_hfc = None
        self.resumen = {}
        
    def analizar(self, progress_callback=None):
        """Ejecuta el análisis completo manteniendo la lógica original robusta"""
        
        # 1. Leer Excel
        if progress_callback:
            progress_callback(10, "📊 Leyendo archivo Excel...")
        
        try:
            df = pd.read_excel(self.excel_file)
        except Exception as e:
            raise ValueError(f"Error leyendo Excel: {str(e)}")
        
        total_registros = len(df)
        
        if total_registros == 0:
            raise ValueError("El archivo Excel está vacío")
        
        # Validar columnas requeridas
        columnas_requeridas = ['Tipo de Actividad', 'Estado', 'Coordenada X', 'Coordenada Y']
        for col in columnas_requeridas:
            if col not in df.columns:
                raise ValueError(f"Columna requerida no encontrada: {col}")
        
        # Filtrar actividades válidas (case insensitive)
        actividades_validas = ["Instalaciones", "INSTALACIONES FTTH", "TRASLADO FTTH", "Traslados"]
        df["Tipo de Actividad"] = df["Tipo de Actividad"].astype(str).str.strip().str.upper()
        df["Estado"] = df["Estado"].astype(str).str.strip().str.upper()

        df_filtered = df[
            (df["Tipo de Actividad"].isin([a.upper() for a in actividades_validas])) &
            (df["Estado"] == "PENDIENTE") &
            (df["Coordenada X"].notna()) & (df["Coordenada X"] != "") &
            (df["Coordenada Y"].notna()) & (df["Coordenada Y"] != "")
        ].copy()

        if len(df_filtered) == 0:
            raise ValueError("No hay registros válidos para analizar (verifique actividades pendientes y coordenadas)")
        
        # 2. Crear geometrías
        if progress_callback:
            progress_callback(20, f"📍 Creando geometrías de {len(df_filtered)} puntos...")
            
        df_filtered["LATITUD"] = pd.to_numeric(df_filtered["Coordenada Y"], errors="coerce")
        df_filtered["LONGITUD"] = pd.to_numeric(df_filtered["Coordenada X"], errors="coerce")
        df_filtered = df_filtered[(df_filtered["LATITUD"].notna()) & (df_filtered["LONGITUD"].notna())].copy()

        if len(df_filtered) == 0:
            raise ValueError("No hay coordenadas numéricas válidas")

        geometry = [
            Point(lon, lat) if pd.notnull(lat) and pd.notnull(lon) else None
            for lon, lat in zip(df_filtered["LONGITUD"], df_filtered["LATITUD"])
        ]

        self.gdf_puntos = gpd.GeoDataFrame(df_filtered, geometry=geometry, crs="EPSG:4326")
        
        # 3. Extraer KMZ
        if progress_callback:
            progress_callback(30, "🗂️ Extrayendo archivo KMZ...")
            
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

            if not kml_path:
                raise ValueError("No se encontró doc.kml en el archivo KMZ")
            
            # 4. Cargar coberturas
            if progress_callback:
                progress_callback(40, "🔍 Cargando coberturas FTTH y HFC...")
                
            self._cargar_coberturas(kml_path, progress_callback)
            
            if len(self.coberturas_ftth) == 0 and len(self.coberturas_hfc) == 0:
                raise ValueError("No se encontraron coberturas válidas (FTTH ni HFC) en el KMZ")
            
            # 5. Análisis punto por punto
            if progress_callback:
                progress_callback(60, f"🔎 Analizando cobertura de {len(self.gdf_puntos)} puntos...")
                
            nodo_hfc_result = []
            nodo_ftth_result = []
            
            total = len(self.gdf_puntos)
            for i, row in self.gdf_puntos.iterrows():
                punto = row.geometry
                
                if punto is None or punto.is_empty:
                    nodo_hfc_result.append(None)
                    nodo_ftth_result.append(None)
                    continue
                
                # FTTH
                res_ftth = self._buscar_nodo(punto, self.coberturas_ftth)
                nodo_ftth_result.append(res_ftth[0] if res_ftth else None)
                
                # HFC
                res_hfc = self._buscar_nodo(punto, self.coberturas_hfc)
                nodo_hfc_result.append(res_hfc[0] if res_hfc else None)
                
                # Progreso cada 10%
                if progress_callback and (i + 1) % max(1, total // 10) == 0:
                    progreso = 60 + int(((i + 1) / total) * 30)
                    progress_callback(progreso, f"Analizando {i+1}/{total} puntos ({((i+1)/total*100):.0f}%)")
            
            # 6. Guardar resultados
            if progress_callback:
                progress_callback(90, "💾 Guardando resultados...")
                
            self.gdf_puntos["NODO HFC"] = nodo_hfc_result
            self.gdf_puntos["NODO FTTH"] = nodo_ftth_result
            self.gdf_puntos["COBERTURA"] = self.gdf_puntos.apply(
                lambda r: "Si" if (r["NODO HFC"] or r["NODO FTTH"]) else "No", axis=1
            )
            
            # Calcular resumen
            con_ftth = sum(1 for n in nodo_ftth_result if n)
            con_hfc = sum(1 for n in nodo_hfc_result if n)
            con_ambas = sum(1 for i in range(len(nodo_ftth_result)) 
                          if nodo_ftth_result[i] and nodo_hfc_result[i])
            sin_cob = sum(1 for i in range(len(nodo_ftth_result)) 
                         if not nodo_ftth_result[i] and not nodo_hfc_result[i])
            
            self.resumen = {
                "total": len(self.gdf_puntos),
                "con_ftth": con_ftth,
                "con_hfc": con_hfc,
                "con_ambas": con_ambas,
                "sin_cobertura": sin_cob,
                "porcentaje_cobertura": ((con_ftth + con_hfc - con_ambas) / len(self.gdf_puntos) * 100) 
                                        if len(self.gdf_puntos) > 0 else 0
            }
            
            self.df_resultado = pd.DataFrame(self.gdf_puntos.drop(columns=["geometry"]))
            
            if progress_callback:
                progress_callback(100, "✅ Análisis completado")
                
        finally:
            # Limpieza segura del directorio temporal
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        
        return self.df_resultado, self.resumen
    
    def _cargar_coberturas(self, kml_path, progress_callback=None):
        """Carga coberturas FTTH y HFC del KML con manejo robusto de errores"""
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        # FTTH Propio (vía GeoPandas/Fiona)
        ftth_propio = []
        try:
            import fiona
            capas = fiona.listlayers(kml_path)
            
            for capa in capas:
                capa_upper = capa.upper()
                if "FTTH" in capa_upper and any(x in capa_upper for x in ["GREENFIELD", "BROWNFIELD", "DESCONOCIDO"]):
                    if "NO_APLICA" not in capa_upper:
                        try:
                            gdf = gpd.read_file(kml_path, layer=capa)
                            if len(gdf) > 0:
                                if gdf.crs is None:
                                    gdf.set_crs("EPSG:4326", inplace=True)
                                gdf = gdf.to_crs("EPSG:4326")
                                
                                nombre_col = "NOMBRE_TK" if "NOMBRE_TK" in gdf.columns else "Name"
                                gdf["NOMBRE_TK"] = gdf[nombre_col].astype(str)
                                
                                for _, row in gdf.iterrows():
                                    if row.geometry and not row.geometry.is_empty:
                                        ftth_propio.append({"nombre": row["NOMBRE_TK"], "geometry": row.geometry})
                        except Exception as e:
                            print(f"Error en capa {capa}: {e}")
                            continue
        except Exception as e:
            print(f"Error cargando FTTH propio: {e}")
        
        # Redes Neutras - Extracción manual XML (más robusto para KML complejos)
        redes_neutras = []
        try:
            tree = ET.parse(kml_path)
            root = tree.getroot()
            
            for folder in root.findall('.//kml:Folder', ns):
                name_elem = folder.find('kml:name', ns)
                if name_elem is None:
                    continue
                
                folder_name = name_elem.text or ""
                folder_upper = folder_name.upper()
                
                if any(x in folder_upper for x in ["COBERTURAS FTT", "RED NEUTRA", "NEUTRAS"]) and "NO_APLICA" not in folder_upper:
                    for placemark in folder.findall('.//kml:Placemark', ns):
                        pm_name_elem = placemark.find('kml:name', ns)
                        pm_name = pm_name_elem.text if pm_name_elem is not None else "SIN_NOMBRE"
                        
                        desc_elem = placemark.find('kml:description', ns)
                        desc = desc_elem.text if desc_elem is not None else ""
                        
                        nombre_tk = pm_name
                        if desc and "NOMBRE_TK" in desc:
                            match = re.search(r'NOMBRE_TK[^>]*>([^<]+)', desc)
                            if match:
                                nombre_tk = match.group(1).strip()
                        
                        coords = self._extraer_coordenadas_placemark(placemark, ns)
                        
                        if coords and len(coords) >= 3:
                            try:
                                poly = Polygon(coords)
                                if poly.is_valid:
                                    redes_neutras.append({"nombre": nombre_tk, "geometry": poly})
                            except:
                                continue
        except Exception as e:
            print(f"Error extrayendo redes neutras: {e}")
        
        todas_ftth = ftth_propio + redes_neutras
        self.coberturas_ftth = gpd.GeoDataFrame(todas_ftth, crs="EPSG:4326") if todas_ftth else gpd.GeoDataFrame(columns=["nombre", "geometry"], crs="EPSG:4326")
        
        # HFC
        capas_hfc = []
        try:
            for capa in capas:
                if capa.upper() == "HFC":
                    try:
                        gdf = gpd.read_file(kml_path, layer=capa)
                        if len(gdf) > 0:
                            if gdf.crs is None:
                                gdf.set_crs("EPSG:4326", inplace=True)
                            # CORRECCIÓN CRÍTICA AQUÍ: Era gpd.to_crs, debe ser gdf.to_crs
                            gdf = gdf.to_crs("EPSG:4326")
                            
                            nombre_col = "Name" if "Name" in gdf.columns else "NOMBRE"
                            gdf["NOMBRE_TK"] = gdf[nombre_col].astype(str)
                            
                            for _, row in gdf.iterrows():
                                if row.geometry and not row.geometry.is_empty:
                                    capas_hfc.append({"nombre": row["NOMBRE_TK"], "geometry": row.geometry})
                    except Exception as e:
                        print(f"Error en capa HFC {capa}: {e}")
                        continue
        except Exception as e:
            print(f"Error cargando HFC: {e}")
        
        self.coberturas_hfc = gpd.GeoDataFrame(capas_hfc, crs="EPSG:4326") if capas_hfc else gpd.GeoDataFrame(columns=["nombre", "geometry"], crs="EPSG:4326")
    
    def _extraer_coordenadas_placemark(self, placemark, ns):
        """Extrae coordenadas de un placemark KML"""
        coords = None
        
        # Intentar Polygon simple
        poly_elem = placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
        if poly_elem is not None and poly_elem.text:
            coords = self._parsear_coordenadas(poly_elem.text)
        
        # Intentar MultiGeometry
        if coords is None:
            multigeom = placemark.find('.//kml:MultiGeometry', ns)
            if multigeom is not None:
                poly_elem = multigeom.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
                if poly_elem is not None and poly_elem.text:
                    coords = self._parsear_coordenadas(poly_elem.text)
        
        return coords
    
    def _parsear_coordenadas(self, coords_text):
        """Parsea texto de coordenadas KML a lista de tuplas (lon, lat)"""
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
        return coords
    
    def _buscar_nodo(self, punto, coberturas):
        """Busca nodo con tolerancia de 50 metros"""
        if len(coberturas) == 0:
            return None
        
        nodo_encontrado = None
        distancia_minima = float('inf')
        
        for _, pol in coberturas.iterrows():
            try:
                geom = pol.geometry
                if geom is None or geom.is_empty:
                    continue
                
                # Verificar contención exacta primero
                if geom.contains(punto):
                    return pol["nombre"], 0
                
                # Calcular distancia si no está contenido
                distancia = geom.distance(punto)
                if distancia <= TOLERANCIA_GRADOS and distancia < distancia_minima:
                    distancia_minima = distancia
                    nodo_encontrado = pol["nombre"]
                    
            except Exception:
                continue
        
        return (nodo_encontrado, distancia_minima) if nodo_encontrado else None
    
    def exportar_excel(self, output_path):
        """Exporta resultados a Excel"""
        if self.df_resultado is not None:
            self.df_resultado.to_excel(output_path, index=False)
            return output_path
        return None
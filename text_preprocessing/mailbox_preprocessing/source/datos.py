import pandas as pd
from pandas import DataFrame
from utils.funciones_estandar_V2_2 import describe_el_error, seleccionar_csv, seleccionar_carpeta
from typing import List, Dict, Any, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import numpy as np

""" RESPONSABILIDADES
• Obtener los datos desde una carpeta (interfaz gráfica).
• Imprimir los datos y metadatos, el histograma, la forma de los datos nuevos.
• Obtener el dataframe que usaremos para el preprocesamiento. 
"""
    
class Data:
    """Clase para manejar un DataFrame de pandas."""
    def __init__(self, datos: Optional[DataFrame] = None, nombre: Optional[str] = 'Dataframe'):
        """
        Inicializa la clase Datos.

        Args:
            datos (DataFrame, optional): DataFrame de pandas. Defaults to None.
        """
        self.data = datos if datos is not None else pd.DataFrame()
        self.nombre = nombre

    def agregar_datos(self, nuevos_datos: DataFrame):
        """Agrega nuevos data al DataFrame existente."""
        self.data = pd.concat([self.data, nuevos_datos], ignore_index=True) # Resetea el índice

    def eliminar_datos(self, indices: List[int]):
        """Elimina filas del DataFrame por índice."""
        self.data = self.data.drop(indices).reset_index(drop=True)

    def filtrar_filas(self, condiciones: Dict[str, Any] = None,
                            eliminar_duplicados: bool = False,
                            eliminar_vacios: bool = False,
                            columnas_vacias: Optional[List[str]] = None,
                            reset_index: bool = True) -> 'Data':
        """
        Método versátil para filtrar y limpiar datos con múltiples opciones.

        Args:
            condiciones (Dict[str, Any]): Condiciones de filtrado. Si None, no filtra.
            eliminar_duplicados (bool): Si True, elimina filas duplicadas.
            eliminar_vacios (bool): Si True, elimina filas con valores vacíos.
            columnas_vacias (Optional[List[str]]): Columnas donde buscar valores vacíos.
            reset_index (bool): Si True, resetea índices al final.

        Returns:
            DataFrame: DataFrame procesado según las opciones especificadas.

        Examples:
            >>> df = pd.DataFrame({
            ...     'nombre': ['Ana', 'Luis', 'Ana', 'María', None],
            ...     'edad': [25, 30, 25, 25, 30],
            ...     'ciudad': ['Madrid', 'Barcelona', 'Madrid', None, 'Valencia']
            ... })
            >>> processor = DataProcessor(df)
            
            >>> # Filtrar, eliminar vacíos y duplicados
            >>> resultado = processor.filtrar_datos_avanzado(
            ...     condiciones={'edad': 25},
            ...     eliminar_vacios=True,
            ...     eliminar_duplicados=True
            ... )
            >>> print(resultado)
            nombre  edad  ciudad
            0    Ana  25.0  Madrid
            
            >>> # Solo eliminar duplicados completos
            >>> resultado = processor.filtrar_datos_avanzado(
            ...     eliminar_duplicados=True
            ... )
            >>> print(resultado)
            nombre  edad     ciudad
            0    Ana  25.0     Madrid
            1   Luis  30.0  Barcelona
            2  María  25.0       None
            3   None  30.0   Valencia
        """
        df_resultado = self.data.copy()
        
        # Paso 1: Aplicar condiciones de filtrado
        if condiciones:
            for columna, valor in condiciones.items():
                df_resultado = df_resultado[df_resultado[columna] == valor]
        
        # Paso 2: Eliminar filas vacías
        if eliminar_vacios:
            if columnas_vacias:
                df_resultado = df_resultado.dropna(subset=columnas_vacias)
            else:
                df_resultado = df_resultado.dropna()
        
        # Paso 3: Eliminar duplicados
        if eliminar_duplicados:
            df_resultado = df_resultado.drop_duplicates()
        
        # Paso 4: Resetear índices
        if reset_index:
            df_resultado = df_resultado.reset_index(drop=True)
        
        return Data(df_resultado)

    
    def filtrar_columnas(self, columnas: List[str]) -> DataFrame:
        """
        Filtra el DataFrame para mantener solo las columnas especificadas.

        Args:
            columnas (List[str]): Lista de nombres de columnas a mantener.

        Returns:
            DataFrame: DataFrame con solo las columnas especificadas.
        """
        columnas_faltantes = set(columnas) - set(self.data.columns)
        
        if columnas_faltantes:
            raise KeyError(f"Columnas no encontradas: {columnas_faltantes}")
        
        return self.data[columnas].copy()
    
    def obtener_datos(self) -> DataFrame:
        """Devuelve el DataFrame actual."""
        return self.data
    
    def __deepcopy__(self, memo):
        """
        Implementación personalizada de deepcopy.
        
        Args:
            memo: Diccionario de objetos ya copiados (para evitar loops infinitos).
            
        Returns:
            Data: Nueva instancia copiada.
        """
        # Crear nueva instancia
        nueva_instancia = Data()
        
        # Copiar DataFrame usando pandas copy
        nueva_instancia.data = self.data.copy(deep=True)
        
        # Copiar nombre
        nueva_instancia.nombre = copy.deepcopy(self.nombre, memo)
        
        return nueva_instancia
    


class CargaDatos:
    """Clase abstracta para cargar datos desde diferentes fuentes."""
    def cargar_datos(self) -> Data:
        """Método abstracto para cargar datos."""
        raise NotImplementedError("Este método debe ser implementado por subclases.")
    

class CargaDatosCSV(CargaDatos):
    """
    Clase para cargar datos desde un archivo CSV. Permite cargar directamente al crear.    
    """
    def __init__(self, ruta_archivo: Optional[Path] = None):
        self.ruta_archivo = ruta_archivo
        self.datos = None
        self.cargar_datos()


    def cargar_datos(self, nuevo_archivo: bool = True) -> None:
        """
        Carga los datos desde un archivo CSV, si ya se seleccionó un archivo carga el 

        Args:
            nuevo_archivo: opción para cargar un nuevo archivo, si es falso carga el link actual.
        """
        try:
            # Cargamos de manera manual si no se proporcionó una ruta inicial o queremos un nuevo archivo
            if not self.ruta_archivo or nuevo_archivo:
                self.ruta_archivo = seleccionar_csv(directorio_inicial=Path.cwd())

            df = pd.read_csv(self.ruta_archivo)
            nombre_archivo = self.ruta_archivo.name
            self.datos = Data(df, nombre_archivo)
        except FileNotFoundError:
            print(f"Error: El archivo {self.ruta_archivo} no se encuentra.")
            return None
        except pd.errors.EmptyDataError:
            print(f"Error: El archivo {self.ruta_archivo} está vacío.")
            return None
        except Exception as e:
            print(f"Error: Ocurrió un error inesperado al cargar el archivo {self.ruta_archivo}.")
            describe_el_error(e)
            return None
        
class VisualizadorDatos:
    """Clase para visualizar datos con gráficas mejoradas."""
    def __init__(self, datos: Data):
        self.datos = datos.obtener_datos()
        self.nombre_archivo = datos.nombre
        if self.datos.empty:
            print("Error: No hay datos para mostrar.")
            return
        
    def agregar_nuevos_datos(self, datos: Data):
        """Agrega nuevos datos al visualizador."""
        self.datos = datos.obtener_datos()
        self.nombre_archivo = datos.nombre
        if self.datos.empty:
            print("Error: No hay datos para mostrar.")
            return

    def mostrar_primeros_datos(self):
        """Muestra los primeros 5 registros de los datos."""
        print(self.datos.head())
    
    def mostrar_datos(self):
        """Muestra todos los datos."""
        print(self.datos)

    def mostrar_info(self):
        """Muestra información general de los datos."""
        print("\n=== Mostrando información general ===")
        print('Archivo: ', self.nombre_archivo)
        print(self.datos.info())
    
    def mostrar_descripcion(self):
        """Muestra estadísticas descriptivas de los datos."""
        print("\n=== Mostrando descripción ===")
        print(self.datos.describe())
    
    def mostrar_columnas(self):
        """
        Muestra información sobre las columnas de los datos (DataFrame o Series).
        Funciona tanto con DataFrame como con Series de pandas.
        """
        print("\n" + "="*50)
        
        # Verificar si es Series o DataFrame
        if isinstance(self.datos, pd.Series):
            print("INFORMACIÓN DE LA SERIE")
            print("="*50)
            
            # Para Series: mostrar nombre, tipo y estadísticas básicas
            nombre_serie = self.datos.name if self.datos.name is not None else "Sin nombre"
            tipo_serie = str(self.datos.dtype)
            longitud = len(self.datos)
            valores_unicos = self.datos.nunique()
            valores_nulos = self.datos.isnull().sum()
            
            print(f"Nombre:           {nombre_serie}")
            print(f"Tipo de dato:     {tipo_serie}")
            print(f"Longitud:         {longitud:,} elementos")
            print(f"Valores únicos:   {valores_unicos:,}")
            print(f"Valores nulos:    {valores_nulos:,}")
            print(f"Porcentaje nulos: {(valores_nulos/longitud)*100:.2f}%")
            
            print("\n" + "-"*30)
            print("MUESTRA DE VALORES:")
            print("-"*30)
            
            # Mostrar muestra de valores
            if len(self.datos) > 10:
                print("Primeros 5 valores:")
                for i, valor in enumerate(self.datos.head(5)):
                    print(f"  {i+1}. {valor}")
                print("  ...")
                print("Últimos 5 valores:")
                for i, valor in enumerate(self.datos.tail(5)):
                    idx = len(self.datos) - 5 + i + 1
                    print(f"  {idx}. {valor}")
            else:
                print("Todos los valores:")
                for i, valor in enumerate(self.datos):
                    print(f"  {i+1}. {valor}")
            
            # Información específica según el tipo de datos
            print("\n" + "-"*30)
            if pd.api.types.is_numeric_dtype(self.datos):
                print("ESTADÍSTICAS NUMÉRICAS:")
                print("-"*30)
                print(f"Mínimo:    {self.datos.min()}")
                print(f"Máximo:    {self.datos.max()}")
                print(f"Media:     {self.datos.mean():.2f}")
                print(f"Mediana:   {self.datos.median():.2f}")
                print(f"Desv. Std: {self.datos.std():.2f}")
            
            elif pd.api.types.is_categorical_dtype(self.datos) or self.datos.dtype == 'object':
                print("INFORMACIÓN CATEGÓRICA:")
                print("-"*30)
                if valores_unicos <= 20:  # Solo mostrar si no son demasiados valores
                    conteos = self.datos.value_counts().head(10)
                    print("Valores más frecuentes:")
                    for valor, frecuencia in conteos.items():
                        porcentaje = (frecuencia/longitud)*100
                        print(f"  '{valor}': {frecuencia:,} ({porcentaje:.1f}%)")
                else:
                    print(f"Demasiados valores únicos para mostrar ({valores_unicos:,})")
            
            elif pd.api.types.is_datetime64_any_dtype(self.datos):
                print("INFORMACIÓN DE FECHAS:")
                print("-"*30)
                print(f"Fecha mínima: {self.datos.min()}")
                print(f"Fecha máxima: {self.datos.max()}")
                print(f"Rango:        {self.datos.max() - self.datos.min()}")
        
        elif isinstance(self.datos, pd.DataFrame):
            print("COLUMNAS DISPONIBLES")
            print("="*50)
            
            # Mostrar información básica del DataFrame
            filas, columnas = self.datos.shape
            memoria_mb = self.datos.memory_usage(deep=True).sum() / (1024*1024)
            print(f"Dimensiones: {filas:,} filas × {columnas} columnas")
            print(f"Memoria utilizada: {memoria_mb:.2f} MB")
            print("\n" + "-"*50)
            
            # Mostrar cada columna con información detallada
            for i, col in enumerate(self.datos.columns):
                tipo = str(self.datos[col].dtype)
                nulos = self.datos[col].isnull().sum()
                unicos = self.datos[col].nunique()
                porcentaje_nulos = (nulos/filas)*100 if filas > 0 else 0
                
                # Crear string de información adicional
                info_extra = []
                if nulos > 0:
                    info_extra.append(f"{nulos} nulos ({porcentaje_nulos:.1f}%)")
                if unicos < filas and unicos > 1:
                    info_extra.append(f"{unicos} únicos")
                elif unicos == 1:
                    info_extra.append("valor constante")
                elif unicos == filas:
                    info_extra.append("todos únicos")
                
                info_str = " | " + " | ".join(info_extra) if info_extra else ""
                
                print(f"{i+1:2}. {col:25} | {tipo:15}{info_str}")
            
            print("="*50)
            
            # Mostrar columnas categóricas recomendadas
            columnas_categoricas = self.datos.select_dtypes(include=['object', 'category']).columns
            if len(columnas_categoricas) > 0:
                print(f"\nColumnas categóricas recomendadas para análisis:")
                for col in columnas_categoricas:
                    unique_vals = self.datos[col].nunique()
                    nulos = self.datos[col].isnull().sum()
                    info_nulos = f" ({nulos} nulos)" if nulos > 0 else ""
                    print(f"  • {col} ({unique_vals} valores únicos{info_nulos})")
            else:
                print("\nNo se encontraron columnas categóricas.")
            
            # Mostrar columnas numéricas
            columnas_numericas = self.datos.select_dtypes(include=[np.number]).columns
            if len(columnas_numericas) > 0:
                print(f"\nColumnas numéricas disponibles:")
                for col in columnas_numericas:
                    nulos = self.datos[col].isnull().sum()
                    rango = f"{self.datos[col].min():.2f} a {self.datos[col].max():.2f}" if not self.datos[col].empty else "N/A"
                    info_nulos = f" ({nulos} nulos)" if nulos > 0 else ""
                    print(f"  • {col} (rango: {rango}{info_nulos})")
            
            # Mostrar columnas de fecha
            columnas_fecha = self.datos.select_dtypes(include=['datetime64']).columns
            if len(columnas_fecha) > 0:
                print(f"\nColumnas de fecha/tiempo:")
                for col in columnas_fecha:
                    nulos = self.datos[col].isnull().sum()
                    if not self.datos[col].empty:
                        fecha_min = self.datos[col].min()
                        fecha_max = self.datos[col].max()
                        rango = f"{fecha_min.strftime('%Y-%m-%d')} a {fecha_max.strftime('%Y-%m-%d')}"
                    else:
                        rango = "N/A"
                    info_nulos = f" ({nulos} nulos)" if nulos > 0 else ""
                    print(f"  • {col} (rango: {rango}{info_nulos})")
            
            print("="*50)
        
        else:
            print("TIPO DE DATOS NO SOPORTADO")
            print("="*50)
            print(f"Tipo recibido: {type(self.datos)}")
            print("Esta función solo soporta pandas DataFrame o Series.")
            print("="*50)

    def histograma(self, columna=None, mostrar_valores='encima', estilo='moderno', color_palette='viridis'):
        """
        Genera una gráfica de frecuencias mejorada con información adicional.
        
        Parámetros:
        - columna: nombre de la columna a analizar (si es None, usa la primera columna categórica)
        - mostrar_valores: 'encima', 'centro', 'abajo' - donde mostrar los números
        - estilo: 'moderno', 'clasico', 'minimalista' - estilo de la gráfica
        - color_palette: paleta de colores para las barras
        """
        # Configurar el estilo
        if estilo == 'moderno':
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette(color_palette)
        elif estilo == 'minimalista':
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("husl")
        else:
            plt.style.use('classic')
        
        # Preparar los datos
        df = self.datos.copy()
        
        # Determinar qué columna usar
        if columna is None:
            # Buscar la primera columna categórica o de texto
            columnas_categoricas = df.select_dtypes(include=['object', 'category']).columns
            if len(columnas_categoricas) == 0:
                print("Error: No se encontraron columnas categóricas en los datos.")
                print(f"Columnas disponibles: {list(df.columns)}")
                return
            columna = columnas_categoricas[-1] # Usar la última columna categórica encontrada
            print(f"Usando columna automática: '{columna}'")
        
        # Verificar que la columna existe
        if columna not in df.columns:
            print(f"Error: La columna '{columna}' no existe en los datos.")
            print(f"Columnas disponibles: {list(df.columns)}")
            return
        
        # Convertir a categórico y obtener frecuencias
        df[columna] = df[columna].astype('category')
        frecuencias = df[columna].value_counts()
        
        # Crear la figura con mejor tamaño
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Crear las barras con gradiente y mejor diseño
        barras = ax.bar(frecuencias.index, frecuencias.values, 
                       color=sns.color_palette(color_palette, len(frecuencias)),
                       edgecolor='white', linewidth=1.5, alpha=0.8)
        
        # Agregar efectos visuales a las barras
        for i, barra in enumerate(barras):
            # Gradiente sutil
            barra.set_alpha(0.9)
            # Sombra sutil
            ax.bar(frecuencias.index[i], frecuencias.values[i], 
                  color='gray', alpha=0.1, zorder=0,
                  width=barra.get_width() * 1.02)
        
        # Agregar los valores según la posición especificada
        for i, (categoria, valor) in enumerate(frecuencias.items()):
            if mostrar_valores == 'encima':
                ax.text(i, valor + max(frecuencias.values) * 0.01, str(valor),
                       ha='center', va='bottom', fontweight='bold', fontsize=11)
            elif mostrar_valores == 'centro':
                ax.text(i, valor / 2, str(valor),
                       ha='center', va='center', fontweight='bold', 
                       fontsize=12, color='white', 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
            elif mostrar_valores == 'abajo':
                ax.text(i, -max(frecuencias.values) * 0.05, str(valor),
                       ha='center', va='top', fontweight='bold', fontsize=11)
        
        # Personalizar la gráfica
        ax.set_title(f'Distribución de Frecuencias - {columna}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(f'{columna}', fontsize=14, fontweight='bold')
        ax.set_ylabel('Frecuencia', fontsize=14, fontweight='bold')
        
        # Mejorar las etiquetas del eje x
        ax.set_xticks(range(len(frecuencias)))
        ax.set_xticklabels(frecuencias.index, rotation=45, ha='right', fontsize=12)
        ax.tick_params(axis='y', labelsize=12)
        
        # Agregar información estadística
        total_datos = len(df)
        num_categorias = len(frecuencias)
        categoria_mas_frecuente = frecuencias.index[0]
        freq_maxima = frecuencias.values[0]
        
        # Texto informativo en la esquina
        info_text = f"""Estadísticas ({columna}):
        • Total de datos: {total_datos:,}
        • Número de categorías: {num_categorias}
        • Categoría más frecuente: {categoria_mas_frecuente}
        • Frecuencia máxima: {freq_maxima:,}
        • Porcentaje máximo: {(freq_maxima/total_datos)*100:.1f}%"""
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
               verticalalignment='top', fontsize=10,
               bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
        
        # Agregar línea de promedio
        promedio = frecuencias.mean()
        ax.axhline(y=promedio, color='red', linestyle='--', alpha=0.7, linewidth=2)
        ax.text(len(frecuencias)-1, promedio + max(frecuencias.values) * 0.02, 
               f'Promedio: {promedio:.1f}', ha='right', va='bottom', 
               color='red', fontweight='bold')
        
        # Mejorar el diseño general
        plt.tight_layout()
        
        # Agregar grid sutil
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Mostrar la gráfica
        plt.show()
        
        # Imprimir resumen en consola
        print("\n" + "="*60)
        print(f"RESUMEN DE FRECUENCIAS - {columna.upper()}")
        print("="*60)
        for categoria, freq in frecuencias.items():
            porcentaje = (freq / total_datos) * 100
            print(f"{str(categoria)[:25]:25} | {freq:6,} ({porcentaje:5.1f}%)")
        print("="*60)
        print(f"{'Total':25} | {total_datos:6,} (100.0%)")
        print("="*60)

    def histograma_comparativo(self, columnas=['Type'], orientacion='vertical'):
        """
        Crea gráficas de frecuencia comparativas para múltiples columnas.
        """
        num_cols = len(columnas)
        fig, axes = plt.subplots(1, num_cols, figsize=(6*num_cols, 6))
        
        if num_cols == 1:
            axes = [axes]
        
        for i, columna in enumerate(columnas):
            df_temp = self.datos.copy()
            df_temp[columna] = df_temp[columna].astype('category')
            frecuencias = df_temp[columna].value_counts()
            
            if orientacion == 'vertical':
                barras = axes[i].bar(range(len(frecuencias)), frecuencias.values,
                                   color=sns.color_palette("Set2", len(frecuencias)))
                axes[i].set_xticks(range(len(frecuencias)))
                axes[i].set_xticklabels(frecuencias.index, rotation=45, ha='right')
            else:
                barras = axes[i].barh(range(len(frecuencias)), frecuencias.values,
                                    color=sns.color_palette("Set2", len(frecuencias)))
                axes[i].set_yticks(range(len(frecuencias)))
                axes[i].set_yticklabels(frecuencias.index)
            
            # Agregar valores en las barras
            for j, valor in enumerate(frecuencias.values):
                if orientacion == 'vertical':
                    axes[i].text(j, valor + max(frecuencias.values) * 0.01, str(valor),
                               ha='center', va='bottom', fontweight='bold')
                else:
                    axes[i].text(valor + max(frecuencias.values) * 0.01, j, str(valor),
                               ha='left', va='center', fontweight='bold')
            
            axes[i].set_title(f'Frecuencias - {columna}', fontweight='bold')
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
class AlmacenDatos:
    """Clase para almacenar datos, y guardar el DataFrame en un archivo CSV."""
    def __init__(self, datos: Optional[Data] = None):
        self.almacen = {datos.nombre: datos} if datos else {}

    def agregar_datos(self, datos: Data):
        """Agrega un nuevo DataFrame al almacenamiento."""
        if datos.nombre in self.almacen:
            print(f"Advertencia: Ya existe un DataFrame con el nombre '{datos.nombre}'.")
        self.almacen[datos.nombre] = datos
    
    def obtener_datos(self, nombre: str) -> Optional[Data]:
        """Obtiene un DataFrame por su nombre."""
        return self.almacen.get(nombre, None)
    
    def guardar_datos(self, nombre: str, ruta: Optional[Path] = None) -> bool:
        """
        Guarda el DataFrame en un archivo CSV.

        Args:
            nombre (str): Nombre del DataFrame a guardar.
            ruta (Path, optional): Ruta donde guardar el archivo. Si es None, usa el nombre del DataFrame.

        Returns:
            bool: True si se guardó correctamente, False si hubo un error.
        """
        datos = self.obtener_datos(nombre)
        if datos is None:
            print(f"Error: No se encontró el DataFrame '{nombre}'.")
            return False
        
        if ruta is None:
            ruta = seleccionar_carpeta()

        ruta_final = ruta / f"{nombre}.csv"  # <- Combina carpeta con nombre

        try:
            datos.data.to_csv(ruta_final, index=False)
            print(f"Datos guardados correctamente en {ruta_final}")
            return True
        except Exception as e:
            print(f"Error al guardar los datos: {e}")
            return False
        
    def existen_datos(self, nombre: str) -> bool:
        """Verifica si un DataFrame con el nombre dado ya existe en el almacenamiento."""
        return nombre in self.almacen
    
    def mostrar_almacenados(self):
        """Muestra los nombres de los DataFrames almacenados."""
        if not self.almacen:
            print("No hay DataFrames almacenados.")
            return
        print("DataFrames almacenados:")
        for nombre in self.almacen.keys():
            print(f" - {nombre}")
        
# Responsabilidades del coordinador:
# • Cargar los datos desde un CSV cuando lo pida el módulo de procesamiento, si ya lo almacenamos se copia si no, se carga.
# • Mostrar los datos y metadatos, el histograma, la forma de los datos nuevos al cargarlo por primera vez.
# • Filtrar los datos según las condiciones dadas y almacenarlos.
# • Guardar los datos que se soliciten en un .csv en una carpeta seleccionada por el usuario.
# • Tener un método para guardar embbedings en construccion (aun no implementado).
class CoordinadorDatos:
    """
    Clase coordinadora para manejar la carga, visualización y almacenamiento de datos.
    """
    def __init__(self):
        self.cargador = CargaDatosCSV()
        self.visualizador = VisualizadorDatos(self.cargador.datos)
        self.almacen = AlmacenDatos(self.cargador.datos)

    def cargar_datos(self, ruta: Optional[Path] = None, nombre_archivo: Optional[str] = None) -> Data:
        """
        Carga los datos, desde una ruta o con un nombre desde el almacenamiento si ya existe.
        Si no se proporcionan, se selecciona desde el explorador de archivos.
        
        Args:
            nombre_archivo (str, optional): Nombre del archivo CSV a cargar. Si es None, se permite seleccionar uno de una carpeta.
        """
        if ruta:
            try:
                self.cargador.ruta_archivo = ruta
                self.cargador.cargar_datos(nuevo_archivo=False)
                if self.cargador.datos is not None:
                    self.almacen.agregar_datos(self.cargador.datos)
                    self.visualizador.agregar_nuevos_datos(self.cargador.datos)
                    return copy.deepcopy(self.cargador.datos)
                else:
                    print("Error: No se pudieron cargar los datos desde el archivo CSV.")
                    return None
            except Exception as e:
                print(f"Error al cargar datos desde la ruta proporcionada: {e}")
                return None
        if nombre_archivo:
            if self.almacen.existen_datos(nombre_archivo):
                datos =  copy.deepcopy(self.almacen.obtener_datos(nombre_archivo))
                self.visualizador.agregar_nuevos_datos(datos)
                return datos
            else:
                print(f"Error: No se encontró el DataFrame '{nombre_archivo}' en el almacenamiento.")
                return None     
        else:
            self.cargador.cargar_datos()
            if self.cargador.datos is not None:
                self.almacen.agregar_datos(self.cargador.datos)
                self.visualizador.agregar_nuevos_datos(self.cargador.datos)
                return copy.deepcopy(self.cargador.datos)
            else:
                print("Error: No se pudieron cargar los datos desde el archivo CSV.")
                return None
            
    def obtener_datos(self) -> Data:
        """Obtiene los datos cargados."""
        if self.cargador.datos is not None:
            return copy.deepcopy(self.cargador.datos)
        else:
            print("Error: No hay datos cargados.")
            return None
        
    def obtener_dataframe(self) -> pd.DataFrame:
        """Obtiene una copia del DataFrame cargado."""
        if self.cargador.datos is not None:
            return self.cargador.datos.obtener_datos().copy()
        else:
            print("Error: No hay datos cargados.")
            return pd.DataFrame()

    def mostrar_datos(self):
        """Muestra los datos y metadatos."""
        self.visualizador.mostrar_info()
        self.visualizador.mostrar_columnas()
        self.visualizador.mostrar_primeros_datos()
        self.visualizador.mostrar_descripcion()
        if isinstance(self.cargador.datos.obtener_datos(), pd.DataFrame):
            self.visualizador.histograma()

    def filtrar_filas_y_almacenar(self, condiciones: Dict[str, Any], nombre: str):
        """Filtra las filas y los almacena en el almacenamiento volatil.
        Args:
            condiciones (Dict[str, Any]): Condiciones de filtrado.
            nombre (str): Nombre para el nuevo DataFrame filtrado.
        Examples:
            condiciones = {'Type': 'Reputacion'}

        """
        df_filtrado = self.cargador.datos.filtrar_filas(condiciones)
        data_filtrada = Data(df_filtrado, nombre)
        self.almacen.agregar_datos(data_filtrada)
        self.visualizador.agregar_nuevos_datos(data_filtrada)

    def filtrar_columnas_y_almacenar(self, columnas: List[str], nombre: str):
        """Filtra las columnas y los almacena en el almacenamiento volatil.
        Args:
            columnas (List[str]): Lista de columnas a mantener.
            nombre (str): Nombre para el nuevo DataFrame filtrado.
        Examples:
            columnas = ['Type', 'Content']

        """
        try:
            df_filtrado = self.cargador.datos.filtrar_columnas(columnas)
            data_filtrada = Data(df_filtrado, nombre)
            self.almacen.agregar_datos(data_filtrada)
            self.visualizador.agregar_nuevos_datos(data_filtrada)
        except KeyError as e:
            print(f"Error al filtrar columnas: {e}")
            return
    
    def guardar_dataframe(self, dataframe: DataFrame, nombre: str, ruta: Optional[Path] = None) -> bool:
        """
        Guarda un DataFrame proporcionado en un archivo CSV.

        Args:
            dataframe (DataFrame): DataFrame de pandas a guardar.
            nombre (str): Nombre del DataFrame a guardar.
            ruta (Path, optional): Ruta donde guardar el archivo. Si es None, se permite seleccionar una carpeta.

        Returns:
            bool: True si se guardó correctamente, False si hubo un error.
        """
        if dataframe is None or dataframe.empty:
            print("Error: El DataFrame proporcionado está vacío o no es válido.")
            return False
        else:
            datos = Data(dataframe, nombre)
            self.almacen.agregar_datos(datos)
            return self.almacen.guardar_datos(nombre, ruta)


    def guardar_datos(self, nombre: str, ruta: Optional[Path] = None) -> bool:
        """
        Guarda los datos filtrados en un archivo CSV.

        Args:
            nombre (str): Nombre del DataFrame a guardar.
            ruta (Path, optional): Ruta donde guardar el archivo. Si es None, se permite seleccionar una carpeta.

        Returns:
            bool: True si se guardó correctamente, False si hubo un error.
        """
        return self.almacen.guardar_datos(nombre, ruta)
    
    def actualizar_datos(self, nuevos_datos: Data):
        """Actualiza los datos en el visualizador y almacenamiento."""
        if nuevos_datos is None or nuevos_datos.obtener_datos().empty or not isinstance(nuevos_datos, Data) or nuevos_datos is self.cargador.datos:
            print("Error: Los nuevos datos no son válidos o están vacíos o son iguales a los actuales.")
            return False            
        else:
            self.cargador.datos = nuevos_datos
            self.visualizador.agregar_nuevos_datos(nuevos_datos)
            self.almacen.agregar_datos(nuevos_datos)

    def guardar_como_nuevo(self, nombre: str, ruta: Optional[Path] = None) -> bool:
        """
        Guarda los datos actuales como un nuevo archivo CSV.

        Args:
            nombre (str): Nombre del nuevo DataFrame a guardar.
            ruta (Path, optional): Ruta donde guardar el archivo. Si es None, se permite seleccionar una carpeta.

        Returns:
            bool: True si se guardó correctamente, False si hubo un error.
        """
        if self.cargador.datos is None or self.cargador.datos.obtener_datos().empty:
            print("Error: No hay datos para guardar.")
            return False
        else:
            nuevos_datos = Data(self.cargador.datos.obtener_datos(), nombre)
            self.almacen.agregar_datos(nuevos_datos)
            return self.almacen.guardar_datos(nombre, ruta)



if __name__ == '__main__':
    """ cargador = CargaDatosCSV()
    visualizador = VisualizadorDatos(cargador.datos)
    visualizador.mostrar_info()
    visualizador.histograma(
        columna='Type',
        mostrar_valores='encima',
        estilo='minimalista'        
    )
    Almacen = AlmacenDatos(cargador.datos)
    df_filtrado = cargador.datos.filtrar_filas({'Type': 'Reputacion'})
    Data_filtrada = Data(df_filtrado, 'reputacion')
    Almacen.agregar_datos(Data_filtrada)
    Almacen.guardar_datos('reputacion', Path.cwd()) """

    coordinador = CoordinadorDatos()
    coordinador.mostrar_datos()
    coordinador.filtrar_filas_y_almacenar({'Type': 'Reputacion'}, 'reputacion_filtrada')
    coordinador.guardar_datos('reputacion_filtrada', Path.cwd())
    coordinador.obtener_datos()
    coordinador.mostrar_datos()
    coordinador.almacen.mostrar_almacenados()
    coordinador.filtrar_filas_y_almacenar({'Type': 'Reputacion'}, 'reputacion_original')
    coordinador.guardar_datos('reputacion_original', Path.cwd())

    
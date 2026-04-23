
import spacy
from spacy.lang.es.stop_words import STOP_WORDS as STOP_WORDS_ES # Stopwords en español por defecto
from spacy.lang.en.stop_words import STOP_WORDS as STOP_WORDS_EN # Ejemplo para inglés
import string
from unidecode import unidecode
from typing import List, Set, Union, Optional, Callable
from source.datos import Data
from pandas import DataFrame

class ProcesadorTextos:
    """Clase que formatea y procesa textos para su uso en modelos de lenguaje."""
    def __init__(self, data: Optional[Data] = None):
        """
        Inicializa el procesador de textos con los datos proporcionados.

        :param data: Instancia de la clase Data que contiene los textos a procesar.
        """
        self.data = data

    def quitar_lineas_repetidas(self, data: Optional[Data] = None) -> Optional[Data]:
        """
        Elimina las líneas repetidas de los textos, si recibe datos los quita de los mismos,
        si no entonces los quita de los datos guardados en el procesador.

        :param data: (opcional) Instancia de la clase Data que contiene los textos a procesar.
        :return: (opcional) Instancia de Data con las líneas repetidas eliminadas.
        """
        if data is None:
            data = self.data

        if data is None:
            print("No se proporcionaron datos para procesar.")
            return None
        
        def quitar_lineas_repetidas(texto: str) -> str:
            """
            Elimina las líneas repetidas de un texto.

            :param texto: Texto del cual se eliminarán las líneas repetidas.
            :return: Texto con las líneas repetidas eliminadas.
            """
            lineas = texto.split('\n')
            # Evitamos unir lineas vacías y eliminamos espacios en blanco
            lineas = [linea.strip() for linea in lineas if linea.strip()]
            lineas_unicas = []
            lineas_minusculas = []
            for linea in lineas:
                # Para que no se repitan las líneas siempre se guardan las últimas 
                if linea.lower() not in lineas_minusculas:
                    lineas_minusculas.append(linea.lower())
                    lineas_unicas.append(linea)
                else:
                    # Sustituimos la línea repetida por la que estaba para que la útima línea repetida sea la que se quede
                    indice = lineas_unicas.index(linea)
                    lineas_unicas[indice] = linea

            return '\n'.join(lineas_unicas)
        
        data.data.apply(lambda x: quitar_lineas_repetidas(x) if isinstance(x, str) else x)

        return data
    
    def quitar_saltos_linea(self, data: Optional[Data] = None) -> Optional[Data]:
        """
        Elimina los saltos de línea de los textos, si recibe datos los quita de los mismos,
        si no entonces los quita de los datos guardados en el procesador.

        :param data: (opcional) Instancia de la clase Data que contiene los textos a procesar.
        :return: (opcional) Instancia de Data con los saltos de línea eliminados.
        """
        if data is None:
            data = self.data

        if data is None:
            print("No se proporcionaron datos para procesar.")
            return None
        
        def quitar_saltos_linea(texto: str) -> str:
            """
            Elimina los saltos de línea de un texto.

            :param texto: Texto del cual se eliminarán los saltos de línea.
            :return: Texto sin saltos de línea.
            """
            return texto.replace('\n', ' ').replace('\r', ' ')
        
        data.data = data.data.apply(lambda x: quitar_saltos_linea(x) if isinstance(x, str) else x)

        return data



class PreprocesadorTextoAvanzado:
    """
    Clase robusta y configurable para el preprocesamiento de texto,
    combinando funcionalidades de limpieza, normalización, tokenización y lematización.
    Utiliza spaCy para tareas lingüísticas avanzadas y unidecode para la transliteración.
    """

    def __init__(
        self,
        idioma_spacy: str = "es_core_news_sm",
        stopwords_personalizadas: Optional[Set[str]] = None,
        caracteres_prohibidos_adicionales: Optional[Set[str]] = None
    ):
        """
        Inicializa el preprocesador.

        Args:
            idioma_spacy (str): Nombre del modelo de spaCy a cargar.
                                 Ejemplos: "es_core_news_sm", "en_core_web_sm".
                                 Asegúrate de haber descargado el modelo:
                                 python -m spacy download es_core_news_sm
            stopwords_personalizadas (Optional[Set[str]]): Un conjunto de stopwords
                                                            adicionales o para reemplazar
                                                            las de spaCy. Si es None, usa
                                                            las de spaCy para el idioma.
            caracteres_prohibidos_adicionales (Optional[Set[str]]): Un conjunto de
                                                                    caracteres o cadenas
                                                                    adicionales a eliminar
                                                                    además de la puntuación estándar.
        """
        try:
            self.nlp = spacy.load(idioma_spacy)
        except OSError:
            print(f"Error: Modelo de spaCy '{idioma_spacy}' no encontrado.")
            print(f"Por favor, descárgalo ejecutando: python -m spacy download {idioma_spacy}")
            # Podrías optar por levantar una excepción aquí o tener un comportamiento de fallback.
            # Por simplicidad, continuaremos pero algunas funciones fallarán.
            self.nlp = None # Marcar que nlp no está disponible

        # Configuración de stopwords
        if stopwords_personalizadas is not None:
            self.stopwords = stopwords_personalizadas
        else:
            # Intentar obtener stopwords del modelo de spaCy si está cargado
            if self.nlp and self.nlp.Defaults.stop_words:
                 self.stopwords = self.nlp.Defaults.stop_words
            elif "es" in idioma_spacy.lower(): # Fallback a una lista predefinida si es español
                self.stopwords = STOP_WORDS_ES
            elif "en" in idioma_spacy.lower(): # Fallback para inglés
                self.stopwords = STOP_WORDS_EN
            else:
                self.stopwords = set() # Sin stopwords por defecto si no se pueden determinar

        # Configuración de caracteres de puntuación y prohibidos
        self.puntuacion_estandar = set(string.punctuation)
        self.caracteres_prohibidos = self.puntuacion_estandar.copy()
        if caracteres_prohibidos_adicionales:
            self.caracteres_prohibidos.update(caracteres_prohibidos_adicionales)
        
        # Añadir algunos caracteres comunes que a veces no están en string.punctuation
        self.caracteres_prohibidos.update(["¿", "¡", "“", "”", "‘", "’", "...", "–", "—"])


    def _validar_texto_entrada(self, texto: any) -> str:
        """Valida y convierte la entrada a string."""
        if not isinstance(texto, str):
            if texto is None:
                return ""
            try:
                return str(texto)
            except:
                # Si no se puede convertir a string, retornar cadena vacía
                # o podrías levantar un ValueError
                print(f"Advertencia: La entrada de tipo {type(texto)} no pudo ser convertida a string. Se usará ''.")
                return ""
        return texto

    def a_minusculas(self, texto: str) -> str:
        """Convierte el texto a minúsculas."""
        texto = self._validar_texto_entrada(texto)
        return texto.lower()

    def quitar_acentos_y_diacriticos(self, texto: str) -> str:
        """
        Elimina acentos y otros diacríticos del texto usando unidecode.
        Ejemplo: "canción" -> "cancion", "Crème brûlée" -> "Creme brulee".
        """
        texto = self._validar_texto_entrada(texto)
        return unidecode(texto)

    def quitar_puntuacion_y_simbolos(self, texto: str, conservar_espacios_internos: bool = True) -> str:
        """
        Elimina signos de puntuación y símbolos definidos en self.caracteres_prohibidos.

        Args:
            texto (str): El texto a limpiar.
            conservar_espacios_internos (bool): Si es True, los signos de puntuación se reemplazan
                                                por un espacio para no unir palabras.
                                                Si es False, se eliminan directamente.
        Returns:
            str: Texto sin puntuación ni símbolos.
        """
        texto = self._validar_texto_entrada(texto)
        caracter_reemplazo = ' ' if conservar_espacios_internos else ''
        # Usamos join para construir la nueva cadena, es más eficiente para muchas operaciones
        return "".join(caracter_reemplazo if char in self.caracteres_prohibidos else char for char in texto)

    def quitar_numeros(self, texto: str, conservar_espacios_internos: bool = True) -> str:
        """
        Elimina todos los dígitos numéricos del texto.

        Args:
            texto (str): El texto a limpiar.
            conservar_espacios_internos (bool): Si es True, los números se reemplazan
                                                por un espacio para no unir palabras.
                                                Si es False, se eliminan directamente.
        Returns:
            str: Texto sin números.
        """
        texto = self._validar_texto_entrada(texto)
        caracter_reemplazo = ' ' if conservar_espacios_internos else ''
        return "".join(caracter_reemplazo if char.isdigit() else char for char in texto)
    
    def quitar_lineas_repetidas(self, texto: str) -> str:
        """
        Versión simplificada usando OrderedDict.
        Mantiene la última ocurrencia de cada línea.
        
        :param texto: Texto del cual se eliminarán las líneas repetidas.
        :return: Texto con las líneas repetidas eliminadas.
        """
        from collections import OrderedDict
        
        texto = self._validar_texto_entrada(texto)
        lineas = texto.split('\n')
        
        # Filtrar líneas vacías
        lineas = [linea.strip() for linea in lineas if linea.strip()]
        
        # Usar OrderedDict para mantener orden y eliminar duplicados
        lineas_unicas = OrderedDict()
        
        for linea in lineas:
            # La clave es lowercase, el valor es la línea original
            # Si ya existe, se sobrescribe (mantiene la última)
            lineas_unicas[linea.lower()] = linea
        
        return '\n'.join(lineas_unicas.values())

    def quitar_saltos_linea(self, texto: str) -> str:
        """
        Elimina los saltos de línea de un texto.

        :param texto: Texto del cual se eliminarán los saltos de línea.
        :return: Texto sin saltos de línea.
        """
        texto = self._validar_texto_entrada(texto)
        return texto.replace('\n', ' ').replace('\r', ' ')

    def tokenizar(self, texto: str) -> List[str]:
        """
        Tokeniza el texto utilizando spaCy.
        Devuelve una lista de strings (tokens).
        Requiere que el modelo spaCy (self.nlp) esté cargado.
        """
        if not self.nlp:
            print("Error: El modelo spaCy no está cargado. No se puede tokenizar.")
            # Dividir por espacios como fallback muy básico si no hay spaCy
            return texto.split() 
            
        texto = self._validar_texto_entrada(texto)
        doc = self.nlp(texto)
        # Podrías añadir más filtros aquí, ej. token.is_alpha, token.is_stop, etc.
        # Por ahora, devolvemos el texto de cada token.
        return [token.text for token in doc]

    def quitar_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Elimina las stopwords de una lista de tokens.
        Los tokens y las stopwords se comparan en minúsculas.
        """
        if not isinstance(tokens, list):
            print("Advertencia: la entrada para quitar_stopwords no es una lista. Se devolverá una lista vacía.")
            return []
        
        # Asegurarse de que las stopwords estén en minúsculas para la comparación
        stopwords_lower = {sw.lower() for sw in self.stopwords}
        
        return [token for token in tokens if token.lower() not in stopwords_lower]

    def lematizar(self, tokens: List[str], solo_alfabeticos: bool = True) -> List[str]:
        """
        Lematiza una lista de tokens utilizando spaCy.
        Devuelve una lista de lemas (strings).
        Requiere que el modelo spaCy (self.nlp) esté cargado.

        Args:
            tokens (List[str]): Lista de tokens a lematizar.
            solo_alfabeticos (bool): Si es True, solo se procesan y devuelven
                                     lemas que consisten en caracteres alfabéticos.
        Returns:
            List[str]: Lista de lemas.
        """
        if not self.nlp:
            print("Error: El modelo spaCy no está cargado. No se puede lematizar.")
            return tokens # Devolver tokens originales como fallback

        if not isinstance(tokens, list):
            print("Advertencia: la entrada para lematizar no es una lista. Se devolverán los tokens originales.")
            return tokens

        # Unir los tokens en un string para procesarlos eficientemente con spaCy
        # Es mucho más rápido procesar un documento completo que token por token.
        texto_para_lematizar = " ".join(tokens)
        doc = self.nlp(texto_para_lematizar)
        
        lemas = []
        for token_spacy in doc:
            if solo_alfabeticos:
                if token_spacy.is_alpha:
                    lemas.append(token_spacy.lemma_)
            else:
                lemas.append(token_spacy.lemma_)
        return lemas
        
    def limpiar_tokens_vacios_y_espacios_extra(self, entrada: Union[List[str], str]) -> Union[List[str], str]:
        """
        Si la entrada es una lista de tokens, elimina los tokens vacíos o que son solo espacios.
        Si la entrada es un string, elimina espacios múltiples y espacios al inicio/final.
        """
        if isinstance(entrada, list):
            return [token.strip() for token in entrada if token and not token.isspace()]
        elif isinstance(entrada, str):
            texto = self._validar_texto_entrada(entrada)
            return " ".join(texto.split()) # Elimina espacios múltiples y al inicio/final
        else:
            print(f"Advertencia: Tipo de entrada no soportado para limpiar_tokens_vacios_y_espacios_extra: {type(entrada)}")
            return entrada


    def procesar(
        self,
        texto: str,
        a_minusculas_flag: bool = True,
        quitar_acentos_flag: bool = True,
        quitar_puntuacion_flag: bool = True,
        quitar_numeros_flag: bool = False, # Por defecto no quitamos números
        tokenizar_flag: bool = True,
        quitar_stopwords_flag: bool = True,
        lematizar_flag: bool = True,
        devolver_como_string: bool = False,
        limpiar_vacios_flag: bool = True,
        quitar_lineas_repetidas_flag: bool = False,
        quitar_saltos_linea_flag: bool = False
    ) -> Union[List[str], str]:
        """
        Aplica una secuencia de pasos de preprocesamiento al texto.

        Args:
            texto (str): El texto a procesar.
            a_minusculas_flag (bool): Aplicar conversión a minúsculas.
            quitar_acentos_flag (bool): Aplicar eliminación de acentos.
            quitar_puntuacion_flag (bool): Aplicar eliminación de puntuación.
            quitar_numeros_flag (bool): Aplicar eliminación de números.
            tokenizar_flag (bool): Aplicar tokenización. Si es False y se lematiza o
                                   quitan stopwords, se tokenizará internamente de forma básica.
            quitar_stopwords_flag (bool): Aplicar eliminación de stopwords (requiere tokenización).
            lematizar_flag (bool): Aplicar lematización (requiere tokenización).
            devolver_como_string (bool): Si es True, los tokens procesados se unen en un string.
                                         Si es False, se devuelve una lista de tokens.
            limpiar_vacios_flag (bool): Aplicar limpieza de tokens vacíos o espacios extra.

        Returns:
            Union[List[str], str]: El texto procesado, como lista de tokens o string.
        """
        texto_procesado = self._validar_texto_entrada(texto)

        if quitar_lineas_repetidas_flag:
            texto_procesado = self.quitar_lineas_repetidas(texto_procesado)
        
        if quitar_saltos_linea_flag:
            texto_procesado = self.quitar_saltos_linea(texto_procesado)

        if a_minusculas_flag:
            texto_procesado = self.a_minusculas(texto_procesado)
        
        if quitar_acentos_flag:
            texto_procesado = self.quitar_acentos_y_diacriticos(texto_procesado)

        if quitar_puntuacion_flag:
            texto_procesado = self.quitar_puntuacion_y_simbolos(texto_procesado)

        if quitar_numeros_flag:
            texto_procesado = self.quitar_numeros(texto_procesado)
        
        # La tokenización es necesaria para stopwords y lematización
        # Si no se pide tokenizar explícitamente pero sí las operaciones siguientes,
        # el texto se tokenizará internamente en esos pasos.
        # Si se pide tokenizar, el resultado será una lista de tokens.
        
        resultado_final: Union[List[str], str]

        if tokenizar_flag or quitar_stopwords_flag or lematizar_flag:
            # Si el texto aún no es una lista de tokens (porque tokenizar_flag era False
            # pero se activó quitar_stopwords_flag o lematizar_flag), lo tokenizamos ahora.
            if isinstance(texto_procesado, str):
                # Si spaCy no está disponible, tokenizar() usa split()
                # Si spaCy está disponible, usa la tokenización avanzada
                tokens_actuales = self.tokenizar(texto_procesado)
            else: # Ya debería ser una lista de tokens si tokenizar_flag fue True y se ejecutó antes
                  # Esto es un caso poco probable dado el flujo actual, pero es una salvaguarda.
                tokens_actuales = texto_procesado if isinstance(texto_procesado, list) else self.tokenizar(str(texto_procesado))


            if lematizar_flag: # Lematizar primero puede ayudar a la unificación antes de quitar stopwords
                tokens_actuales = self.lematizar(tokens_actuales)
            
            if quitar_stopwords_flag:
                tokens_actuales = self.quitar_stopwords(tokens_actuales)
            
            if limpiar_vacios_flag:
                tokens_actuales = self.limpiar_tokens_vacios_y_espacios_extra(tokens_actuales)
            
            resultado_final = tokens_actuales
        else:
            # Si no se tokeniza, ni se quitan stopwords, ni se lematiza,
            # el texto_procesado sigue siendo un string.
            if limpiar_vacios_flag and isinstance(texto_procesado, str):
                 texto_procesado = self.limpiar_tokens_vacios_y_espacios_extra(texto_procesado)
            resultado_final = texto_procesado


        if devolver_como_string:
            if isinstance(resultado_final, list):
                return " ".join(resultado_final)
            return str(resultado_final) # Ya es un string o se convierte
        else:
            if isinstance(resultado_final, str) and not tokenizar_flag:
                # Si el usuario no quería tokenizar pero quiere una lista,
                # se devuelve el string procesado como una lista de un solo elemento.
                # O podríamos tokenizarlo aquí como último paso si es lo deseado.
                # Por coherencia, si no se pidió tokenizar, y se pide lista,
                # se devuelve el string completo en una lista.
                # Si se pidió tokenizar, ya será una lista.
                return [resultado_final] if resultado_final else []
            elif isinstance(resultado_final, str) and tokenizar_flag:
                # Caso donde tokenizar_flag era true, pero por alguna razón el resultado es string
                # (ej. todos los tokens fueron eliminados y se unió una cadena vacía).
                # Se re-tokeniza o se devuelve lista vacía.
                return self.tokenizar(resultado_final) if resultado_final else []

            return resultado_final if isinstance(resultado_final, list) else [str(resultado_final)]


    def procesar_archivo(
        self,
        ruta_archivo: str,
        encoding: str = 'utf-8',
        **kwargs  # Para pasar argumentos a self.procesar
    ) -> Union[List[str], str]:
        """
        Lee un archivo de texto y lo procesa utilizando el método `procesar`.

        Args:
            ruta_archivo (str): La ruta al archivo de texto.
            encoding (str): La codificación del archivo.
            **kwargs: Argumentos adicionales para pasar al método `procesar`
                      (ej. a_minusculas_flag=True, lematizar_flag=False).

        Returns:
            Union[List[str], str]: El contenido del archivo procesado.
                                   Devuelve lista vacía o string vacío si hay error.
        """
        try:
            with open(ruta_archivo, 'r', encoding=encoding) as archivo:
                texto_archivo = archivo.read()
            return self.procesar(texto_archivo, **kwargs)
        except FileNotFoundError:
            print(f"Error: Archivo no encontrado en la ruta: {ruta_archivo}")
        except Exception as e:
            print(f"Error al procesar el archivo '{ruta_archivo}': {e}")
        
        # Determinar el tipo de retorno en caso de error basado en devolver_como_string
        devolver_como_string = kwargs.get('devolver_como_string', False)
        return "" if devolver_como_string else []

    def procesar_dataframe(
        self,
        df: DataFrame,  
        columna_texto: str,
        inplace: bool = False,
        **kwargs  # Para pasar argumentos a self.procesar
    ) -> Optional[DataFrame]:
        """
        Procesa una columna de texto en un DataFrame de pandas.

        Args:
            df (pd.DataFrame): El DataFrame que contiene la columna de texto.
            columna_texto (str): El nombre de la columna que contiene los textos a procesar.
            inplace (bool): Si es True, modifica el DataFrame original. Si es False, devuelve una copia modificada.
            **kwargs: Argumentos adicionales para pasar al método `procesar`
                      (ej. a_minusculas_flag=True, lematizar_flag=False).

        Returns:
            Optional[pd.DataFrame]: El DataFrame con la columna procesada.
                                     Devuelve None si hay error y inplace es True.
        """
        if columna_texto not in df.columns:
            print(f"Error: La columna '{columna_texto}' no existe en el DataFrame.")
            return None if inplace else df.copy()

        df_a_procesar = df if inplace else df.copy()

        # Aplicar el procesamiento a cada fila de la columna especificada
        df_a_procesar[columna_texto] = df_a_procesar[columna_texto].apply(
            lambda x: self.procesar(x, **kwargs)
        )

        return df_a_procesar if not inplace else None

    def limpiar_resultados_vacios(self, df: DataFrame, columna_texto: str) -> DataFrame:
        """
        Elimina filas donde el texto procesado quedó vacío.
        
        Args:
            df: DataFrame a limpiar
            columna_texto: Nombre de la columna de texto
            
        Returns:
            DataFrame sin filas vacías
        """
        from pandas import isna
        def es_valido(texto):
            if isna(texto):
                return False
            if isinstance(texto, str):
                return len(texto.strip()) > 0
            if isinstance(texto, list):
                return len(texto) > 0
            return False
        
        df_limpio = df[df[columna_texto].apply(es_valido)].reset_index(drop=True)
        
        filas_eliminadas = len(df) - len(df_limpio)
        if filas_eliminadas > 0:
            print(f"Filas eliminadas por estar vacías: {filas_eliminadas}")
        
        return df_limpio


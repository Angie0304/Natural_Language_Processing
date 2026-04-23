""" 
Cambio de la versión V2_1
1. input_validado: ahora para los rangos no devuelve un tuple(bool, int | float), sino el valor si está dentro del rango o False si no lo está.


"""

import platform
import traceback
from pathlib import Path
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, Union, List
import time
import tkinter as tk
from tkinter import filedialog
import os
import sys
import inspect
import re
from typing import Optional, Dict, Any
import datetime
import logging



def cronometro(func):
    """
    Decorador para medir el tiempo de ejecución de una función.
    
    Args:
        func: Función a medir
        
    Returns:
        Función decorada
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        print(f"{func.__name__} tomó {fin - inicio:.6f} segundos")
        return resultado
    return wrapper

def try_except(func):
    """
    Decorador para manejar excepciones en funciones.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada
    """
    @wraps(func)
    def wrapper(*arg, **args):
        try:
            return func(*arg, **args)
        except Exception as e:
            describe_el_error(e)
            return None
    return wrapper


def print_buf(text: str = "", output_lines: list = None):
    """
    Función auxiliar para imprimir y almacenar líneas de salida.
    
    Args:
        text: Texto a imprimir y almacenar
        output_lines: Lista donde almacenar las líneas (se modifica in-place)
    """
    if output_lines is not None:
        output_lines.append(text)
    print(text)


def describe_el_error(
    e: Exception, 
    tb_frame=None,
    max_depth: int = None, 
    mostrar_libs: bool = False, 
    colorizar: bool = True,
    capturar_variables: bool = True,
    archivo_log: str = None,
    debug_mode: bool = False
):
    """
    Muestra un árbol visual de la cadena de llamadas que llevó al error,
    priorizando el código del usuario sobre el código de librerías.
    
    Args:
        e: Excepción a describir
        tb_frame: Frame del traceback (obtener con sys.exc_info()[2] para capturar variables reales)
        max_depth: Control del árbol de llamadas:
                  - None: Muestra solo puntos probables del error (código de usuario)
                  - -1: Muestra el árbol completo sin límite
                  - número > 0: Muestra hasta esa profundidad
        mostrar_libs: Si es True, muestra también las llamadas a librerías
        colorizar: Si es True, coloriza la salida para mejor visualización
        capturar_variables: Si es True, muestra las variables locales en cada frame
        archivo_log: Si se proporciona, guarda el error en este archivo
    
    Examples:
        # Uso básico (sin captura de variables, solo puntos probables)
        try:
            resultado = 10 / 0
        except Exception as e:
            describe_el_error(e)
        
        # Uso avanzado con captura de variables reales
        try:
            x = 5
            y = 0
            resultado = x / y
        except Exception as e:
            import sys
            describe_el_error(e, sys.exc_info()[2])
        
        # Mostrar árbol completo sin límite
        try:
            mi_funcion_compleja()
        except Exception as e:
            import sys
            describe_el_error(e, tb_frame=sys.exc_info()[2], max_depth=-1)
        
        # Mostrar árbol con profundidad limitada
        try:
            procesar_datos()
        except Exception as e:
            describe_el_error(e, max_depth=5, capturar_variables=True)
        
        # Solo mostrar código del usuario, sin variables
        try:
            procesar_datos()
        except Exception as e:
            describe_el_error(e, capturar_variables=False)
    """
    
    # Colores ANSI
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"
    
    # Deshabilitar colores si no se quieren
    if not colorizar:
        RESET = BOLD = RED = YELLOW = BLUE = GREEN = MAGENTA = CYAN = GRAY = ""
    
    # Símbolos para el árbol
    TREE_BRANCH = "├── "
    TREE_CORNER = "└── "
    TREE_VERTICAL = "│   "
    TREE_SPACE = "    "
    ERROR_SYMBOL = "🔴 "
    USER_CODE_SYMBOL = "👉 "
    LIB_CODE_SYMBOL = "📚 "
    VAR_SYMBOL = "💾 "
    
    # Determinar directorios de usuario vs. librerías - CORREGIDO
    script_dir = os.path.abspath(os.getcwd())

    # Preparar buffer para output
    output_lines = []
    debug_mode = False  # Cambiar a True para diagnósticos
    
    def print_buf_local(text: str = ""):
        print_buf(text, output_lines)
    
    # DIAGNÓSTICO ADICIONAL: Verificar detección de directorio
    if debug_mode:
        print_buf_local(f"{GRAY}   Directorio actual (getcwd): {script_dir}{RESET}")

    # Obtener información del traceback - MEJORADO PARA DIAGNÓSTICO
    frames_summary = traceback.extract_tb(e.__traceback__)

    # Si no hay frames de usuario detectados, usar el directorio del primer frame como referencia
    if frames_summary:
        primer_archivo = frames_summary[0].filename
        if os.path.exists(primer_archivo):
            directorio_primer_frame = os.path.dirname(os.path.abspath(primer_archivo))
            if debug_mode:
                print_buf_local(f"{GRAY}   Directorio del primer frame: {directorio_primer_frame}{RESET}")
            # Usar el directorio que contenga archivos .py del proyecto
            if directorio_primer_frame != script_dir and primer_archivo.endswith('.py'):
                script_dir = directorio_primer_frame
                if debug_mode:
                    print_buf_local(f"{GRAY}   CORRIGIENDO directorio de trabajo a: {script_dir}{RESET}")
    
    site_packages_dirs = [p for p in sys.path if 'site-packages' in p or 'dist-packages' in p]
    
    # Extraer información del error
    error_type = type(e).__name__
    error_msg = str(e)
    
    # Función para determinar si un archivo es del usuario - MEJORADA
    def es_codigo_usuario(filename: str) -> bool:
        if not filename:
            return False
        
        # Convertir a ruta absoluta
        try:
            abs_path = os.path.abspath(filename)
        except:
            return False
        
        # Verificar si está en el directorio del script
        es_del_directorio = abs_path.startswith(script_dir)
        
        # Verificar si NO está en site-packages
        no_es_libreria = not any(abs_path.startswith(lib_dir) for lib_dir in site_packages_dirs if lib_dir)
        
        # Verificar extensiones de archivos de usuario comunes
        es_archivo_python_usuario = filename.endswith(('.py', '.pyw')) and not filename.startswith('<')
        
        # Excluir archivos temporales o internos
        no_es_temporal = not any(x in filename.lower() for x in ['<stdin>', '<string>', '<frozen', '__pycache__'])
        
        resultado = es_del_directorio and no_es_libreria and es_archivo_python_usuario and no_es_temporal
        
        # DEBUG: Mostrar decisión para diagnóstico (solo en modo debug)
        if debug_mode:
            print_buf_local(f"{GRAY}   DEBUG: {os.path.basename(filename)} -> Usuario: {resultado} "
                     f"(dir: {es_del_directorio}, no_lib: {no_es_libreria}, py: {es_archivo_python_usuario}, no_temp: {no_es_temporal}){RESET}")
        
        return resultado
    
    # DIAGNÓSTICO: Mostrar información completa del traceback
    if debug_mode:
        print_buf_local(f"\n{GRAY}🔬 DIAGNÓSTICO DEL TRACEBACK:{RESET}")
        print_buf_local(f"{GRAY}   Total de frames en traceback: {len(frames_summary)}{RESET}")
        print_buf_local(f"{GRAY}   Traceback completo disponible: {'Sí' if tb_frame else 'No'}{RESET}")
        
        # Mostrar todos los archivos en el traceback para diagnóstico
        archivos_en_traceback = [os.path.basename(frame.filename) for frame in frames_summary]
        print_buf_local(f"{GRAY}   Archivos en el traceback: {', '.join(archivos_en_traceback)}{RESET}")
        
        print_buf_local(f"{GRAY}   Directorio de trabajo final: {os.path.basename(script_dir)}{RESET}")
        print_buf_local(f"{GRAY}{'='*50}{RESET}")
    
    # Verificar si hay frames de usuario en cualquier lugar
    archivos_usuario = [frame.filename for frame in frames_summary if es_codigo_usuario(frame.filename)]
    if debug_mode:
        print_buf_local(f"{GRAY}   Archivos de usuario detectados: {len(archivos_usuario)}{RESET}")
        if archivos_usuario:
            print_buf_local(f"{GRAY}   -> {[os.path.basename(f) for f in archivos_usuario]}{RESET}")
    
    # Formatear la línea del frame para mostrar
    def formatear_linea(frame: traceback.FrameSummary, es_ultimo: bool, es_usuario: bool) -> str:
        filename = os.path.basename(frame.filename)
        function = frame.name
        lineno = frame.lineno
        line = frame.line
        
        # Decidir el estilo según el tipo de frame
        if es_ultimo:
            prefix = BOLD + RED + ERROR_SYMBOL
        elif es_usuario:
            prefix = BOLD + BLUE + USER_CODE_SYMBOL
        else:
            prefix = GRAY + LIB_CODE_SYMBOL
        
        # Formatear la ubicación y el código
        color = BOLD + (BLUE if es_usuario else GRAY)
        ubicacion = f"{color}{filename}:{lineno}{RESET} en {BOLD}{function}(){RESET}"
        codigo = f"{GREEN}'{line.strip() if line else ''}'{RESET}" if line else ""
        
        # Etiquetar según origen
        if es_usuario:
            etiqueta = f"{RED}[TU CÓDIGO] {RESET}"
        elif not es_ultimo:
            etiqueta = f"{GRAY}[LIBRERÍA] {RESET}"
        else:
            etiqueta = ""
        
        return f"{prefix}{etiqueta}{ubicacion} → {codigo}"
    
    # Función para formatear valores multilínea con indentación correcta
    def formatear_valor_multilinea(valor_str: str, linea_completa: str, es_ultimo_item: bool) -> str:
        """
        Formatea valores multilínea manteniendo la indentación del árbol.
        
        Args:
            valor_str: El valor a formatear (puede ser multilínea)
            linea_completa: La línea completa que se va a imprimir (para calcular alineación)
            es_ultimo_item: Si es True, no continúa el árbol (└──), si es False continúa (├──)
        """
        lineas = valor_str.split('\n')
        if len(lineas) <= 1:
            return valor_str
        
        # Primera línea sin modificación
        resultado = [lineas[0]]
        
        # Calcular la posición donde debe alinearse el contenido multilínea
        # Buscar la posición del '=' en la línea completa
        pos_igual = linea_completa.find(' = ')
        if pos_igual == -1:
            return valor_str  # Si no hay '=', no formatear
        
        # Calcular los espacios hasta el inicio del contenido
        # Incluir el ' = ' (3 caracteres)
        espacios_hasta_contenido = pos_igual + 3
        
        # Detectar si el valor empieza con caracteres que sugieren alineación especial
        primera_linea = lineas[0].strip()
        
        # Para arrays/matrices: alinear con el segundo '['
        if primera_linea.startswith('[[') or primera_linea.startswith('array([['):
            # Buscar el segundo '[' para alinear ahí
            if primera_linea.startswith('array([['):
                # Para numpy arrays: "array([[..."
                pos_segundo_bracket = primera_linea.find('[[') + 1
            else:
                # Para listas simples: "[[..."
                pos_segundo_bracket = 1
            alineacion_contenido = espacios_hasta_contenido + pos_segundo_bracket
        else:
            # Para otros tipos: alinear después del primer espacio tras '='
            # O directamente después del '=' si no hay espacios adicionales
            alineacion_contenido = espacios_hasta_contenido
        
        # Generar la indentación base (mantener estructura del árbol si no es el último)
        if es_ultimo_item:
            # Si es el último item (└──), no continuar las líneas del árbol
            indentacion_base = " " * alineacion_contenido
        else:
            # Si continúa el árbol (├──), mantener las líneas verticales
            # Contar cuántas líneas verticales hay en la indentación original
            indentacion_original = linea_completa[:espacios_hasta_contenido]
            
            # Reconstruir la indentación manteniendo las líneas verticales
            nueva_indentacion = ""
            i = 0
            while i < len(indentacion_original):
                if indentacion_original[i:i+1] == "│":
                    nueva_indentacion += "│"
                    i += 1
                elif indentacion_original[i:i+4] == "├── " or indentacion_original[i:i+4] == "└── ":
                    # Reemplazar el símbolo del árbol con espacios, pero mantener │ si es necesario
                    nueva_indentacion += "│" + " " * 3
                    i += 4
                elif indentacion_original[i:i+4] == "    ":
                    nueva_indentacion += "    "
                    i += 4
                else:
                    nueva_indentacion += " "
                    i += 1
            
            # Completar hasta la posición de alineación
            while len(nueva_indentacion) < alineacion_contenido:
                nueva_indentacion += " "
            
            indentacion_base = nueva_indentacion
        
        # Procesar las líneas restantes
        for linea in lineas[1:]:
            if linea.strip():  # Solo procesar líneas no vacías
                resultado.append(indentacion_base + linea.strip())
            else:
                # AGREGAR AQUÍ: Para líneas vacías, mantener la estructura del árbol si no es el último item
                if not es_ultimo_item:
                    # Mantener solo las líneas verticales del árbol para líneas vacías
                    lineas_verticales = ""
                    for char in indentacion_base:
                        if char == "│":
                            lineas_verticales += "│"
                        else:
                            break
                    resultado.append(lineas_verticales)
                else:
                    resultado.append("")
        
        return '\n'.join(resultado)
    
    # Obtener variables locales del traceback - MEJORADO
    def obtener_variables_locales(tb_obj, frame_index: int) -> Dict[str, Tuple[str, str]]:
        if not capturar_variables or not tb_obj:
            return {}
        
        # Navegar al frame específico
        current_tb = tb_obj
        for _ in range(frame_index):
            if current_tb.tb_next:
                current_tb = current_tb.tb_next
            else:
                break
        
        if not current_tb:
            return {}
        
        variables = {}
        frame = current_tb.tb_frame
        
        for key, value in frame.f_locals.items():
            # Filtrar variables internas y módulos
            if not key.startswith('__') and not inspect.ismodule(value):
                try:
                    str_value = str(value)
                    if len(str_value) > 100:  # Aumentamos el límite para mejor visualización
                        str_value = str_value[:97] + "..."
                    
                    tipo = type(value).__name__
                    variables[key] = (str_value, tipo)
                except Exception:
                    variables[key] = ("ERROR_AL_CONVERTIR", "desconocido")
        
        return variables
    
    # Analizar y explicar errores comunes
    def explicar_error(tipo: str, mensaje: str) -> str:
        explicacion = ""
        
        # Patrones de errores comunes
        if tipo == "TypeError":
            # Error de número de argumentos
            match = re.search(r"(\w+)\(\) takes (\d+) positional arguments? but (\d+) (?:was|were) given", mensaje)
            if match:
                func, esperados, dados = match.groups()
                explicacion = f"La función {func}() esperaba {esperados} argumentos pero recibió {dados}"
            
            # Error de tipo de argumento
            match = re.search(r"([\w\.]+)\(\) argument '(\w+)' must be ([\w\.]+), not ([\w\.]+)", mensaje)
            if match:
                func, param, tipo_esperado, tipo_dado = match.groups()
                explicacion = f"En {func}(), el parámetro '{param}' esperaba {tipo_esperado} pero recibió {tipo_dado}"
                
            # Error de operación no soportada
            match = re.search(r"unsupported operand type\(s\) for (.+): '(.+)' and '(.+)'", mensaje)
            if match:
                operacion, tipo1, tipo2 = match.groups()
                explicacion = f"No se puede realizar la operación {operacion} entre {tipo1} y {tipo2}"
        
        elif tipo == "AttributeError":
            match = re.search(r"'([\w\.]+)' object has no attribute '(\w+)'", mensaje)
            if match:
                obj_tipo, atributo = match.groups()
                explicacion = f"El objeto de tipo '{obj_tipo}' no tiene el atributo '{atributo}'"
        
        elif tipo == "IndexError":
            match = re.search(r"(list|tuple) index out of range", mensaje)
            if match:
                tipo_contenedor = match.group(1)
                explicacion = f"Intentaste acceder a un índice fuera del rango del {tipo_contenedor}"
        
        elif tipo == "KeyError":
            explicacion = f"La clave {mensaje} no existe en el diccionario"
        
        elif tipo == "NameError":
            match = re.search(r"name '(\w+)' is not defined", mensaje)
            if match:
                var = match.group(1)
                explicacion = f"La variable o función '{var}' no está definida"
        
        elif tipo == "ZeroDivisionError":
            explicacion = "División por cero - verifica que el denominador no sea 0"
        
        elif tipo == "ValueError":
            # Casos específicos de ValueError
            if "n_components" in mensaje and "must be between" in mensaje:
                explicacion = "El número de componentes PCA es inválido - debe ser menor que min(n_samples, n_features)"
            elif "could not convert" in mensaje:
                explicacion = "Error de conversión de tipos - verifica que los datos tengan el formato correcto"
            else:
                explicacion = "Valor inválido - verifica que los parámetros tengan valores válidos"
        
        elif tipo == "FileNotFoundError":
            explicacion = f"No se encontró el archivo especificado"
        
        elif tipo == "ImportError" or tipo == "ModuleNotFoundError":
            explicacion = "Error al importar módulo - verifica que esté instalado y el nombre sea correcto"
        
        # Si hay explicación, formatearla
        if explicacion:
            explicacion = f"{BOLD}{YELLOW}💡 Explicación:{RESET} {explicacion}"
        
        return explicacion
    
    # Imprimir cabecera
    print_buf_local(f"\n{BOLD}{RED}{'='*60}{RESET}")
    print_buf_local(f"{BOLD}{RED}🚨 ERROR DETECTADO: {error_type}{RESET}")
    print_buf_local(f"{BOLD}{RED}📝 Mensaje: {error_msg}{RESET}")
    print_buf_local(f"{BOLD}{RED}{'='*60}{RESET}\n")
    
    # Filtrar frames según configuración - CORREGIDO
    all_frames = list(frames_summary)
    
    # Siempre identificar frames de código del usuario
    frames_usuario = [(i, frame) for i, frame in enumerate(all_frames) if es_codigo_usuario(frame.filename)]
    
    # Mostrar resumen de puntos probables del error (SIEMPRE código del usuario)
    print_buf_local(f"{BOLD}{RED}🎯 Puntos probables del error:{RESET}")
    
    # Encontrar SOLO frames de código del usuario, priorizando el más cercano al error
    frames_usuario_display = [(i, frame) for i, frame in enumerate(all_frames) if es_codigo_usuario(frame.filename)]
    
    if frames_usuario_display:
        # Mostrar los frames de usuario, priorizando los más recientes
        for i, (frame_idx, frame) in enumerate(frames_usuario_display[-3:]):  # Últimos 3 frames de usuario
            simbolo = TREE_CORNER if i == len(frames_usuario_display[-3:]) - 1 else TREE_BRANCH
            linea = formatear_linea(frame, False, True)  # Siempre es código de usuario
            print_buf_local(f"  {simbolo}{linea}")
    else:
        # Solo si NO hay código de usuario, mostrar el frame del error de la librería
        ultimo_frame = all_frames[-1]
        linea = formatear_linea(ultimo_frame, True, False)
        print_buf_local(f"  {TREE_CORNER}{linea}")
        print_buf_local(f"  {YELLOW}⚠️  No se encontró código de usuario en el stack trace.{RESET}")
        print_buf_local(f"  {YELLOW}   El error se originó directamente en una librería.{RESET}")
    
    # Decidir si mostrar el árbol completo basado en max_depth
    mostrar_arbol_completo = False
    if max_depth is None:
        # Comportamiento por defecto: solo puntos probables (ya mostrados arriba)
        mostrar_arbol_completo = False
    elif max_depth == -1:
        # Mostrar árbol completo sin límite
        mostrar_arbol_completo = True
        max_depth = None  # Sin límite
    elif isinstance(max_depth, int) and max_depth > 0:
        # Mostrar árbol con profundidad limitada
        mostrar_arbol_completo = True
    
    # Mostrar árbol completo de llamadas solo si se solicita
    if mostrar_arbol_completo:
        # Decidir qué frames mostrar en el árbol completo
        if mostrar_libs:
            # Mostrar TODO el stack trace
            frames_a_mostrar = [(i, frame) for i, frame in enumerate(all_frames)]
        else:
            # Mostrar código de usuario + el frame del error (aunque sea de librería)
            frames_a_mostrar = frames_usuario.copy()
            
            # Agregar el último frame (donde ocurre el error) si no es de usuario
            ultimo_frame_idx = len(all_frames) - 1
            ultimo_frame = all_frames[-1]
            if not es_codigo_usuario(ultimo_frame.filename):
                frames_a_mostrar.append((ultimo_frame_idx, ultimo_frame))
            
            # Si no hay frames de usuario, mostrar al menos los últimos 3 frames
            if not frames_usuario:
                frames_a_mostrar = [(i, frame) for i, frame in enumerate(all_frames[-3:])]
        
        # Limitar profundidad si es necesario
        if max_depth is not None and max_depth > 0:
            frames_a_mostrar = frames_a_mostrar[-max_depth:]
        
        print_buf_local(f"\n{BOLD}{CYAN}🌳 Árbol completo de llamadas:{RESET}")
        
        # Si no hay frames de usuario, explicar por qué
        if not frames_usuario and not mostrar_libs:
            print_buf_local(f"  {YELLOW}ℹ️  Solo mostrando el punto del error (usar mostrar_libs=True para ver todo):{RESET}")
        
        for i, (frame_idx, frame) in enumerate(frames_a_mostrar):
            es_ultimo_en_lista = (i == len(frames_a_mostrar) - 1)
            es_ultimo_real = (frame_idx == len(all_frames) - 1)  # Es el frame donde ocurre el error
            es_usuario = es_codigo_usuario(frame.filename)
            
            # Calcular indentación para el árbol
            indent = ""
            for j in range(i):
                if j < i - 1:
                    indent += TREE_VERTICAL
                else:
                    indent += ""
            
            # Decidir el símbolo del árbol
            simbolo = TREE_CORNER if es_ultimo_en_lista else TREE_BRANCH
            
            linea = formatear_linea(frame, es_ultimo_real, es_usuario)
            print_buf_local(f"{indent}{simbolo}{linea}")
            
            # Mostrar variables locales si se solicitó - MEJORADO con formato multilínea
            if capturar_variables and tb_frame and es_usuario:  # Solo para código de usuario
                variables = obtener_variables_locales(tb_frame, frame_idx)
                if variables:
                    # Calcular indentación para variables
                    var_indent = indent
                    if not es_ultimo_en_lista:
                        var_indent += TREE_VERTICAL
                    else:
                        var_indent += TREE_SPACE
                    
                    print_buf_local(f"{var_indent}{CYAN}{VAR_SYMBOL}Variables locales:{RESET}")
                    
                    var_items = list(variables.items())
                    for idx, (var_name, (var_value, var_type)) in enumerate(sorted(var_items)):
                        es_ultima_var = idx == len(var_items) - 1
                        var_simbolo = TREE_CORNER if es_ultima_var else TREE_BRANCH
                        
                        # Construir la línea completa primero para calcular alineación
                        linea_var_base = f"{var_indent}{TREE_SPACE}{var_simbolo}{CYAN}{var_name}{RESET} ({YELLOW}{var_type}{RESET}) = {MAGENTA}"
                        linea_var_sin_color = f"{var_indent}{TREE_SPACE}{var_simbolo}{var_name} ({var_type}) = "
                        
                        # Formatear valor con manejo de multilínea
                        valor_formateado = formatear_valor_multilinea(var_value, linea_var_sin_color, es_ultima_var)
                        
                        # Construir la línea final
                        linea_var = linea_var_base + valor_formateado + RESET
                        print_buf_local(linea_var)
    else:
        # Mostrar mensaje informativo sobre cómo ver el árbol completo
        print_buf_local(f"\n{BOLD}{BLUE}ℹ️  Para ver el árbol completo de llamadas:{RESET}")
        print_buf_local(f"   • describe_el_error(e, max_depth=-1) - Árbol completo sin límite")
        print_buf_local(f"   • describe_el_error(e, max_depth=5) - Árbol limitado a 5 niveles")
        print_buf_local(f"   • describe_el_error(e, max_depth=-1, mostrar_libs=True) - Incluir librerías")
    
    # Mostrar explicación del error
    print_buf_local(f"\n{BOLD}{YELLOW}🔍 Análisis del error:{RESET}")
    explicacion = explicar_error(error_type, error_msg)
    if explicacion:
        print_buf_local(f"  {explicacion}")
    else:
        print_buf_local(f"  {GRAY}No hay explicación específica disponible para este tipo de error.{RESET}")
    
    # Mostrar sugerencias específicas según el tipo de error
    print_buf_local(f"\n{BOLD}{GREEN}💡 Sugerencias de solución:{RESET}")
    
    if error_type == "TypeError":
        print_buf_local("  • Verifica el número y tipos de argumentos que pasas a las funciones")
        print_buf_local("  • Usa print(type(variable)) para verificar los tipos de tus variables")
        print_buf_local("  • Revisa la documentación de la función para ver qué espera")
    elif error_type == "AttributeError":
        print_buf_local("  • Verifica que el nombre del atributo sea correcto (mayúsculas/minúsculas)")
        print_buf_local("  • Usa dir(objeto) para ver los atributos disponibles")
        print_buf_local("  • Comprueba que el objeto sea del tipo esperado")
    elif error_type == "IndexError":
        print_buf_local("  • Verifica que el índice esté dentro del rango con len(lista)")
        print_buf_local("  • Recuerda que los índices empiezan en 0")
        print_buf_local("  • Usa try/except para manejar índices fuera de rango")
    elif error_type == "KeyError":
        print_buf_local("  • Verifica que la clave exista con 'clave in diccionario'")
        print_buf_local("  • Usa dict.get(clave, valor_default) para evitar KeyError")
        print_buf_local("  • Revisa que la clave tenga el tipo correcto")
    elif error_type == "ZeroDivisionError":
        print_buf_local("  • Verifica que el denominador no sea cero antes de dividir")
        print_buf_local("  • Usa una condición if para validar antes de la división")
        print_buf_local("  • Considera usar try/except para manejar este caso")
    elif error_type == "ValueError":
        print_buf_local("  • Verifica que los parámetros tengan valores dentro del rango permitido")
        print_buf_local("  • Revisa la documentación para conocer las restricciones de valores")
        print_buf_local("  • Usa validaciones antes de pasar valores a funciones")
        if "n_components" in error_msg:
            print_buf_local("  • Para PCA: usa n_components=min(n_samples, n_features) o menor")
    else:
        print_buf_local("  • Revisa la línea específica donde ocurre el error")
        print_buf_local("  • Verifica que todas las variables estén definidas")
        print_buf_local("  • Usa print() para depurar valores antes del error")
    
    # Mostrar opciones de uso - ACTUALIZADO
    print_buf_local(f"\n{BOLD}{BLUE}🛠️  Opciones avanzadas:{RESET}")
    print_buf_local("  • describe_el_error(e, tb_frame=sys.exc_info()[2]) - Captura variables reales")
    print_buf_local("  • describe_el_error(e, max_depth=-1) - Muestra árbol completo sin límite")
    print_buf_local("  • describe_el_error(e, max_depth=5) - Limita el árbol a 5 niveles")
    print_buf_local("  • describe_el_error(e, mostrar_libs=True) - Incluye llamadas a librerías")
    print_buf_local("  • describe_el_error(e, capturar_variables=False) - Oculta variables")
    print_buf_local("  • describe_el_error(e, archivo_log='error.log') - Guarda en archivo")
    print_buf_local("  • describe_el_error(e, colorizar=False) - Desactiva colores")
    
    # Guardar en archivo si se solicitó
    if archivo_log:
        try:
            # Eliminar códigos ANSI para el archivo
            lineas_limpias = []
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            for linea in output_lines:
                lineas_limpias.append(ansi_escape.sub('', linea))
            
            # Añadir timestamp y contexto
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            encabezado = f"=== ERROR LOG: {timestamp} ===\n"
            encabezado += f"Error Type: {error_type}\n"
            encabezado += f"Error Message: {error_msg}\n"
            encabezado += f"Captured Variables: {'Yes' if capturar_variables and tb_frame else 'No'}\n"
            encabezado += f"Show Libraries: {'Yes' if mostrar_libs else 'No'}\n"
            encabezado += f"Max Depth: {max_depth if max_depth is not None else 'Default (user code only)'}\n"
            encabezado += "=" * 50 + "\n\n"
            
            with open(archivo_log, 'a', encoding='utf-8') as f:
                f.write(encabezado)
                f.write('\n'.join(lineas_limpias))
                f.write('\n\n' + '='*50 + '\n\n')
            
            print_buf_local(f"\n{BOLD}{GREEN}📁 Error guardado en: {archivo_log}{RESET}")
        except Exception as log_error:
            print_buf_local(f"\n{BOLD}{RED}❌ Error al guardar el log: {str(log_error)}{RESET}")
    
    print_buf_local(f"\n{BOLD}{GRAY}{'='*60}{RESET}")
    
    # Mostrar información adicional si no se capturaron variables
    if capturar_variables and not tb_frame:
        print_buf_local(f"\n{YELLOW}ℹ️  Para capturar variables reales, usa:{RESET}")
        print_buf_local(f"   {CYAN}import sys{RESET}")
        print_buf_local(f"   {CYAN}describe_el_error(e, sys.exc_info()[2]){RESET}")
    
def input_validado(texto: str, tipo: str, limites: tuple = None) -> Union[str, int, float, bool]:
    """
    Valida la entrada del usuario según diferentes criterios.
    
    Args:
        texto (str): Mensaje que se mostrará al usuario
        tipo (str): Tipo de validación a realizar
            'entero': Número entero
            'decimal': Número decimal
            'rango_entero': Número entero dentro de un rango
            'texto': Texto no vacío
            'nombre': Nombre (alfanumérico comenzando con letra)
            'rango_decimal': Número decimal dentro de un rango
        limites (tuple, optional): Tupla con (valor_minimo, valor_maximo) para rangos
    
    Returns:
        Union[str, int, float, bool]: Valor validado según el tipo de entrada requerida
    """
    TIPOS_VALIDOS = {
        'entero',
        'decimal', 
        'rango_entero',
        'texto',
        'nombre',
        'rango_decimal'
    }
    
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo de validación no válido. Tipos válidos: {TIPOS_VALIDOS}")
    
    if 'rango' in tipo and limites is None:
        raise ValueError("Se requieren límites para validar rangos")

    MENSAJES_ERROR = {
        'numero': "Error: Debe ingresar un número válido",
        'rango': f"Error: El valor debe estar entre {limites[0]} y {limites[1]}" if limites else "",
        'vacio': "Error: El campo no puede estar vacío",
        'primer_caracter': "Error: El primer caracter debe ser una letra",
        'alfanumerico': "Error: Solo se permiten caracteres alfanuméricos y espacios"
    }

    while True:
        try:
            match tipo:
                case 'entero':
                    valor = int(input(texto + ": "))
                    return valor
                    
                case 'decimal':
                    valor = float(input(texto + ": "))
                    return valor
                    
                case 'rango_entero' | 'rango_decimal':
                    tipo_num = 'entero' if tipo == 'rango_entero' else 'decimal'
                    valor = input_validado(f"{texto} ({limites[0]}, {limites[1]})", 
                                        tipo_num)
                    
                    if limites[0] <= valor <= limites[1]:
                        return valor
                    print(MENSAJES_ERROR['rango'])
                    return False  # Ahora sólo regresa false
                    
                case 'texto':
                    valor = input(texto + ': ').strip()
                    if valor:
                        return valor
                    print(MENSAJES_ERROR['vacio'])
                    
                case 'nombre':
                    valor = input_validado(texto + ': ').strip()
                    
                    if not valor[0].isalpha():
                        print(MENSAJES_ERROR['primer_caracter'])
                        continue
                        
                    if not all(c.isalnum() or c.isspace() for c in valor):
                        print(MENSAJES_ERROR['alfanumerico'])
                        continue
                        
                    return valor
                    
        except ValueError:
            print(MENSAJES_ERROR['numero'])

def eleccion(pregunta: str, por_defecto: bool = True, intentos_maximos: int = None) -> bool:
    """ 
    Función para preguntar al usuario si desea continuar con una acción.
    
    Args:
        pregunta: Texto de la pregunta
        por_defecto: Valor a retornar para entrada vacía
        intentos_maximos: Número máximo de intentos antes de usar el valor por defecto.
                         None para intentos ilimitados.
        
    Returns:
        True si la respuesta es afirmativa, False en caso contrario, 
        o el valor por defecto tras entrada vacía o máximo de intentos alcanzado.
    """
    # Respuestas válidas (más completas y flexibles)
    respuestas_afirmativas = {'s', 'si', 'sí', 'y', 'yes', '1', 'true', 'ok'}
    respuestas_negativas = {'n', 'no', '0', 'false', 'nope'}
    
    leyenda = "(S/n)" if por_defecto else "(s/N)"
    intentos = 0
    
    while True:
        try:
            # Mostrar número de intento si hay límite
            prompt = f"\n{pregunta} {leyenda}"
            if intentos_maximos and intentos > 0:
                prompt += f" (intento {intentos + 1}/{intentos_maximos})"
            
            respuesta = input(f"{prompt}: ").strip()
            
            # Si está vacía, usar valor por defecto
            if not respuesta:
                return por_defecto
            
            # Normalizar respuesta (minúsculas, sin acentos)
            respuesta_normalizada = respuesta.lower().replace('í', 'i')
            
            if respuesta_normalizada in respuestas_afirmativas:
                return True
            elif respuesta_normalizada in respuestas_negativas:
                return False
            else:
                intentos += 1
                
                # Si se alcanzó el máximo de intentos, usar valor por defecto
                if intentos_maximos and intentos >= intentos_maximos:
                    print(f"Máximo de intentos alcanzado. Usando valor por defecto: {'Sí' if por_defecto else 'No'}")
                    return por_defecto
                
                # Mensaje de error más informativo
                print("Respuesta no válida. Use 's/si/sí/y/yes/1' para Sí o 'n/no/0' para No.")
                if intentos_maximos:
                    restantes = intentos_maximos - intentos
                    print(f"Intentos restantes: {restantes}")
                
        except (KeyboardInterrupt, EOFError):
            # Manejar Ctrl+C o EOF graciosamente
            print(f"\nOperación cancelada. Usando valor por defecto: {'Sí' if por_defecto else 'No'}")
            return por_defecto



# Variable global para controlar si ya se configuró DPI
_dpi_configurado = False


def _configurar_sistema_automatico():
    """
    Configura el sistema automáticamente para optimal funcionamiento.
    Se ejecuta una sola vez, la primera vez que se usa cualquier función.
    """
    global _dpi_configurado
    
    if _dpi_configurado:
        return
    
    try:
        sistema = platform.system()
        
        # Configuración específica para Windows
        if sistema == 'Windows':
            _configurar_windows_dpi()
            
        # Configuración específica para macOS
        elif sistema == 'Darwin':
            _configurar_macos()
            
        # Linux y otros sistemas Unix generalmente manejan bien el escalado
        elif sistema == 'Linux':
            _configurar_linux()
            
        _dpi_configurado = True
        
    except Exception as e:
        # Si algo falla, continúa sin configuración especial
        logging.debug(f"No se pudo configurar sistema automáticamente: {e}")
        _dpi_configurado = True  # Marcar como configurado para evitar reintentos


def _configurar_windows_dpi():
    """Configuración específica para Windows."""
    try:
        import ctypes
        import os
        # Obtener versión de Windows
        version = platform.version()
        major_version = int(version.split('.')[0]) if '.' in version else 0
        
        if major_version >= 6:  # Windows Vista o superior
            try:
                # Método más moderno (Windows 8.1+)
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                try:
                    # Método legacy (Windows Vista+)
                    ctypes.windll.user32.SetProcessDPIAware()
                except (AttributeError, OSError):
                    pass
        
        # Variables de entorno para mejorar renderizado
        os.environ.setdefault('QT_AUTO_SCREEN_SCALE_FACTOR', '1')
        os.environ.setdefault('QT_SCALE_FACTOR', '1')
        
    except Exception:
        pass


def _configurar_macos():
    """Configuración específica para macOS."""
    try:
        import os
        # macOS maneja bien el escalado Retina automáticamente
        # Pero podemos optimizar algunas configuraciones
        os.environ.setdefault('TK_SILENCE_DEPRECATION', '1')
    except Exception:
        pass


def _configurar_linux():
    """Configuración específica para Linux."""
    try:
        import os
        # Linux con entornos de escritorio modernos maneja bien el escalado
        # Configuraciones para mejor compatibilidad con diferentes DEs
        os.environ.setdefault('GDK_SCALE', '1')
        os.environ.setdefault('GDK_DPI_SCALE', '1')
    except Exception:
        pass


def _obtener_ventana_tk() -> tk.Tk:
    """
    Obtiene o crea una ventana Tk de manera segura y optimizada.
    
    Returns:
        Instancia de Tk configurada apropiadamente
    """
    # Configurar sistema automáticamente si es la primera vez
    _configurar_sistema_automatico()
    
    try:
        # Intentar obtener la ventana raíz existente
        root = tk._default_root
        if root is None:
            root = tk.Tk()
            _configurar_tkinter_window(root)
        
        # Configurar la ventana para que no sea visible
        root.withdraw()
        
        # Traer al frente (multiplataforma)
        try:
            root.attributes('-topmost', True)
            # En algunos sistemas, necesitamos bajar el topmost después de un momento
            root.after(100, lambda: root.attributes('-topmost', False))
        except tk.TclError:
            # Fallback para sistemas que no soportan -topmost
            try:
                root.lift()
                root.focus_force()
            except tk.TclError:
                pass
        
        return root
        
    except Exception:
        # Fallback: crear nueva ventana
        root = tk.Tk()
        root.withdraw()
        _configurar_tkinter_window(root)
        return root


def _configurar_tkinter_window(root: tk.Tk):
    """Configuraciones específicas para la ventana Tkinter."""
    try:
        # Configurar escalado si está disponible
        if hasattr(tk, 'call'):
            try:
                tk.call('tk', 'scaling', '-displayof', '.', 1.0)
            except tk.TclError:
                pass
        
        # Configuraciones específicas por sistema
        sistema = platform.system()
        
        if sistema == 'Windows':
            try:
                # Mejorar renderizado de fuentes en Windows
                root.tk.call('tk', 'fontchooser', 'configure', '-visible', False)
            except tk.TclError:
                pass
                
        elif sistema == 'Darwin':  # macOS
            try:
                # Configuraciones específicas para macOS
                root.createcommand('::tk::mac::Quit', root.quit)
            except tk.TclError:
                pass
                
    except Exception:
        pass

def seleccionar_carpeta(
    titulo: str = 'Seleccionar carpeta',
    directorio_inicial: Optional[str] = None
) -> Optional[Path]:
    """ 
    Función para seleccionar una carpeta desde el explorador de archivos.
    Compatible con Windows, macOS y Linux.

    Args:
        titulo: Texto para el título de la ventana de diálogo
        directorio_inicial: Directorio donde abrir el diálogo inicialmente

    Returns:
        Path opcional con la ruta de la carpeta seleccionada,
        o None si no se seleccionó nada.
        
    Raises:
        ImportError: Si tkinter no está disponible
        OSError: Si hay problemas de acceso al sistema de archivos
    """
    try:
        root = _obtener_ventana_tk()
        
        # Parámetros del diálogo
        dialog_params = {
            'title': titulo,
            'mustexist': True,
            'parent': root
        }
        
        if directorio_inicial:
            dialog_params['initialdir'] = str(directorio_inicial)
        
        ruta = filedialog.askdirectory(**dialog_params)
        
        return Path(ruta) if ruta else None
        
    except ImportError:
        error_msg = "tkinter no está disponible en este sistema"
        logging.error(error_msg)
        raise ImportError(error_msg)
        
    except Exception as e:
        logging.error(f"Error al seleccionar carpeta: {e}")
        return None
        
    finally:
        if root and root.winfo_exists():
            root.quit()
            root.destroy()

def seleccionar_archivo(
    titulo: str = 'Seleccionar archivo', 
    filetypes: Optional[List[Tuple[str, str]]] = None,
    directorio_inicial: Optional[str] = None,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """ 
    Función para seleccionar archivo(s) desde el explorador de archivos.
    Compatible con Windows, macOS y Linux.

    Args:
        titulo: Texto para el título de la ventana de diálogo
        filetypes: Lista de tuplas con tipos de archivos permitidos.
                  Si es None, usa todos los archivos por defecto.
        directorio_inicial: Directorio donde abrir el diálogo inicialmente
        multiples: Si True, permite seleccionar múltiples archivos

    Returns:
        Path opcional con la ruta del archivo, lista de Path si multiples=True,
        o None/lista vacía si no se seleccionó nada.
        
    Raises:
        ImportError: Si tkinter no está disponible
        OSError: Si hay problemas de acceso al sistema de archivos

    Examples:
        >>> # Archivo único
        >>> archivo = seleccionar_archivo('Seleccionar imagen', [('PNG', '*.png')])
        >>> 
        >>> # Múltiples archivos
        >>> archivos = seleccionar_archivo('Múltiples', multiples=True)
        >>> 
        >>> # Con directorio inicial
        >>> doc = seleccionar_archivo('PDF', [('PDF', '*.pdf')], Path.cwd())
    """
    # Valor por defecto para filetypes
    if filetypes is None:
        filetypes = [('Todos los archivos', '*.*')]
    
    root = None
    try:
        # Obtener ventana Tk configurada
        root = _obtener_ventana_tk()
        
        # Parámetros comunes del diálogo
        dialog_params = {
            'title': titulo,
            'filetypes': filetypes,
            'parent': root
        }
        
        # Agregar directorio inicial si se especifica
        if directorio_inicial:
            dialog_params['initialdir'] = str(directorio_inicial)
        
        # Seleccionar función según si se permiten múltiples archivos
        if multiples:
            rutas = filedialog.askopenfilenames(**dialog_params)
            resultado = [Path(ruta) for ruta in rutas] if rutas else []
        else:
            ruta = filedialog.askopenfilename(**dialog_params)
            resultado = Path(ruta) if ruta else None
        
        return resultado
        
    except ImportError:
        error_msg = "tkinter no está disponible en este sistema"
        logging.error(error_msg)
        raise ImportError(error_msg)
        
    except Exception as e:
        logging.error(f"Error al seleccionar archivo: {e}")
        return [] if multiples else None
        
    finally:
        # Limpieza cuidadosa de la ventana
        if root:
            try:
                if root.winfo_exists():
                    root.quit()
                    root.destroy()
            except (tk.TclError, AttributeError):
                pass


def seleccionar_imagen(
    titulo: str = "Seleccionar imagen",
    directorio_inicial: Optional[str] = None,
    incluir_webp: bool = True,
    incluir_svg: bool = True,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """ 
    Función especializada para seleccionar archivos de imagen.
    
    Args:
        titulo: Título de la ventana de diálogo
        directorio_inicial: Directorio donde iniciar la búsqueda
        incluir_webp: Si incluir formato WebP en los tipos permitidos
        incluir_svg: Si incluir formato SVG en los tipos permitidos
        multiples: Si permitir seleccionar múltiples imágenes
        
    Returns:
        Path con la imagen seleccionada, lista de Path si multiples=True,
        o None si no se seleccionó nada.
    """
    # Tipos de imagen más completos
    formatos_imagen = "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.gif *.ico"
    
    if incluir_webp:
        formatos_imagen += " *.webp"
    if incluir_svg:
        formatos_imagen += " *.svg"
    
    filetypes = [
        ("Archivos de imagen", formatos_imagen),
        ("PNG", "*.png"),
        ("JPEG", "*.jpg *.jpeg"),
        ("GIF", "*.gif"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff *.tif"),
    ]
    
    if incluir_webp:
        filetypes.append(("WebP", "*.webp"))
    if incluir_svg:
        filetypes.append(("SVG", "*.svg"))
        
    filetypes.append(("Todos los archivos", "*.*"))
    
    return seleccionar_archivo(
        titulo=titulo,
        filetypes=filetypes,
        directorio_inicial=directorio_inicial,
        multiples=multiples
    )


def seleccionar_documento(
    titulo: str = "Seleccionar documento",
    directorio_inicial: Optional[str] = None,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """ 
    Función especializada para seleccionar documentos.
    
    Args:
        titulo: Título de la ventana de diálogo
        directorio_inicial: Directorio donde iniciar la búsqueda
        multiples: Si permitir seleccionar múltiples documentos
        
    Returns:
        Path con el documento seleccionado, lista de Path si multiples=True,
        o None si no se seleccionó nada.
    """
    filetypes = [
        ("Documentos", "*.pdf *.doc *.docx *.txt *.rtf *.odt"),
        ("PDF", "*.pdf"),
        ("Word", "*.doc *.docx"),
        ("Texto", "*.txt *.rtf"),
        ("OpenDocument", "*.odt"),
        ("Todos los archivos", "*.*")
    ]
    
    return seleccionar_archivo(
        titulo=titulo,
        filetypes=filetypes,
        directorio_inicial=directorio_inicial,
        multiples=multiples
    )


def seleccionar_csv(
    titulo: str = "Seleccionar archivo CSV",
    directorio_inicial: Optional[str] = None,
    multiples: bool = False
) -> Union[Optional[Path], List[Path]]:
    """
    Función especializada para seleccionar archivos CSV.
    
    Args:
        titulo: Título de la ventana de diálogo
        directorio_inicial: Directorio donde iniciar la búsqueda
        multiples: Si permitir seleccionar múltiples archivos CSV
        
    Returns:
        Path con el CSV seleccionado, lista de Path si multiples=True,
        o None si no se seleccionó nada.
    """
    filetypes = [
        ("Archivos CSV", "*.csv"),
        ("Archivos de texto separado por comas", "*.csv *.txt"),
        ("Todos los archivos", "*.*")
    ]
    
    return seleccionar_archivo(
        titulo=titulo,
        filetypes=filetypes,
        directorio_inicial=directorio_inicial,
        multiples=multiples
    )


# Función de conveniencia para mantener compatibilidad
def cargar_enlace_imagen() -> Optional[Path]:
    """ 
    Función legacy para cargar una imagen.
    Se recomienda usar seleccionar_imagen() directamente.
    """
    return seleccionar_imagen()


def obtener_info_sistema() -> dict:
    """
    Obtiene información del sistema para debugging.
    
    Returns:
        Diccionario con información del sistema
    """
    return {
        'sistema': platform.system(),
        'version': platform.version(),
        'arquitectura': platform.architecture(),
        'python_version': sys.version,
        'dpi_configurado': _dpi_configurado,
        'tkinter_disponible': 'tkinter' in sys.modules
    }



# Función de ejemplo para probar las mejoras
def test_error_examples():
    """
    Función de prueba para demostrar las nuevas funcionalidades
    """
    import numpy as np
    
    def funcion_con_error():
        # Crear algunos datos de prueba con variables multilínea
        matriz_grande = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        lista_larga = [f"elemento_{i}" for i in range(10)]
        array_complejo = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        diccionario_complejo = {
            'datos': matriz_grande,
            'nombres': lista_larga,
            'configuracion': {'param1': 123, 'param2': 'valor_largo_que_se_ve_en_varias_lineas'}
        }
        
        # Más variables para testing
        texto_multilinea = """Esta es una línea muy larga
que continúa en la siguiente línea
y termina aquí"""
        
        # Error intencional
        resultado = 10 / 0
        return resultado
    
    print("=== EJEMPLO 1: Uso básico (solo puntos probables) ===")
    try:
        funcion_con_error()
    except Exception as e:
        describe_el_error(e)
    
    print("\n" + "="*80)
    print("=== EJEMPLO 2: Con captura de variables y árbol completo ===")
    try:
        funcion_con_error()
    except Exception as e:
        import sys
        describe_el_error(e, sys.exc_info()[2], max_depth=-1)
    
    print("\n" + "="*80)
    print("=== EJEMPLO 3: Árbol limitado a 3 niveles ===")
    try:
        funcion_con_error()
    except Exception as e:
        import sys
        describe_el_error(e, sys.exc_info()[2], max_depth=3)


if __name__ == "__main__":
    # Ejecutar ejemplos de prueba
    test_error_examples()

""" # Ejemplo de uso de la selección de archivos
if __name__ == "__main__":
    print("=== Selector de Archivos Universal ===")
    print(f"Sistema: {platform.system()}")
    print("=" * 40)
    
    try:
        # Ejemplo básico
        print("1. Seleccionar cualquier archivo:")
        archivo = seleccionar_archivo("Seleccionar cualquier archivo")
        print(f"   Resultado: {archivo}")
        
        # CSV específico
        print("\n2. Seleccionar archivo CSV:")
        csv_path = seleccionar_csv(
            'Selecciona un CSV',
            directorio_inicial=str(Path.cwd())
        )
        print(f"   CSV elegido: {csv_path}")
        
        # Imagen con opciones avanzadas
        print("\n3. Seleccionar imagen (con WebP y SVG):")
        imagen = seleccionar_imagen(
            "Seleccionar imagen",
            incluir_webp=True,
            incluir_svg=True
        )
        print(f"   Imagen seleccionada: {imagen}")


        # Con directorio inicial
        print('\n4. Selección de un documento en el directorio especializado')
        doc = seleccionar_documento(
            "Seleccionar documento",
            directorio_inicial=str(Path.home() / "Documents")
        )
        print(f"   Documento seleccionado: {doc}")
        
        # Información del sistema
        print("\n5. Información del sistema:")
        info = obtener_info_sistema()
        for clave, valor in info.items():
            print(f"   {clave}: {valor}")
            
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        print("Verifique que tkinter esté instalado correctamente.") """
""" 
Constantes del proyecto, como rutas de archivos y configuraciones generales.
"""
from pathlib import Path
# ==========================================
# RUTAS DEL PROYECTO
# ==========================================

# Ruta genérica de los datos
PROJECT_ROOT = Path.cwd.parent.parent # proyecto/source/constantes.py -> proyecto/
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
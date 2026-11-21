"""
Sistema de Procesamiento y Ordenamiento Masivo de Datos
Punto de entrada:  python main.py
"""

import os
import sys

# Asegura que se importen las librerias propias de ESTA carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def revisar_requisitos():
    if sys.version_info < (3, 8):
        print("Se requiere Python 3.8 o superior.")
        return False
    from importlib.util import find_spec
    faltantes = [m for m in ("openpyxl", "matplotlib") if find_spec(m) is None]
    if faltantes:
        print("Faltan librerías: " + ", ".join(faltantes))
        print("Instálalas con:  python -m pip install -r requirements.txt")
        if "openpyxl" in faltantes:
            print("(Sin openpyxl no se pueden leer ni guardar archivos XLSX.)")
        if "matplotlib" in faltantes:
            print("(Sin matplotlib el programa funciona, pero sin gráficas ni PDF.)")
    return True


if __name__ == "__main__":
    if revisar_requisitos():
        try:
            from interfaz import iniciar
        except ImportError as e:
            print(f"No se pudo iniciar la interfaz: {e}")
            sys.exit(1)
        iniciar()

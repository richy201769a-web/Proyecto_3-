"""
Ejecuta todas las pruebas automaticas del proyecto:

    python ejecutar_pruebas.py

Incluye: ordenamientos internos y externos, busquedas, lectura/escritura de
archivos, seguridad (inyecciones, archivos maliciosos, limites) y la
verificacion de que no se usa .sort() / sorted() en ningun archivo.
"""

import os
import shutil
import sys
import unittest

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    suite = unittest.defaultTestLoader.discover(os.path.join(BASE, "pruebas"), top_level_dir=BASE)
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)
    shutil.rmtree(os.path.join(BASE, "pruebas", "_tmp"), ignore_errors=True)
    total = resultado.testsRun
    fallas = len(resultado.failures) + len(resultado.errors)
    print("\n" + "=" * 60)
    print(f"  Pruebas ejecutadas: {total}   Correctas: {total - fallas}   Fallidas: {fallas}")
    print("=" * 60)
    sys.exit(0 if resultado.wasSuccessful() else 1)

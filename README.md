# Sistema de Procesamiento y Ordenamiento Masivo de Datos

Examen Parcial · **Algoritmos de Ordenamiento y Búsqueda** · Estructura de Datos

Aplicación de escritorio en Python (interfaz gráfica con tkinter) que lee archivos
TXT/XLSX con miles de números enteros, los ordena con **librerías propias**
(ordenamientos internos y externos), busca valores (secuencial, binaria y hash),
muestra resultados con gráficas, exporta el archivo ordenado y, **al terminar todo
el proceso**, genera un **reporte final en PDF** con un botón específico.

![Pantalla de ordenamiento](capturas/2_ordenar.png)

> **Restricción cumplida:** en ningún archivo del proyecto se usa `.sort()`,
> `sorted()` ni bibliotecas automáticas de ordenamiento. Una prueba automática
> (`pruebas/test_seguridad.py`) revisa el código fuente completo para comprobarlo.

---

## 1. Requisitos e instalación

* Python 3.8 o superior (probado con Python 3.14).
* Librerías: `openpyxl` (leer y escribir XLSX) y `matplotlib` (gráficas y PDF).
  `tkinter`, `os` y `time` ya vienen con Python.

```powershell
python -m pip install -r requirements.txt
```

## 2. Ejecución

```powershell
python main.py
```

Pruebas automáticas (110 pruebas: ordenamientos, búsquedas, archivos, seguridad, robustez con datos al azar, restricciones, interfaz y laboratorio):

```powershell
python ejecutar_pruebas.py
```

Las pruebas usan sus propios archivos en `pruebas/datos/`. Para regenerarlos:

```powershell
python herramientas/generar_datasets.py
```

---

## 3. Estructura del repositorio

```
Sistema_Ordenamiento_Masivo/
├── main.py                       Punto de entrada (revisa requisitos e inicia la interfaz)
├── interfaz.py                   Interfaz gráfica (barra lateral con los pasos): solo IMPORTA y USA las librerías
├── librerias/                    ← LIBRERÍAS PROPIAS (reutilizadas de las ADAs anteriores)
│   ├── ordenamiento_interno.py   Burbuja, Inserción, Selección, ShellSort, QuickSort, HeapSort, RadixSort
│   ├── ordenamiento_externo.py   Intercalación, Mezcla Directa, Mezcla Equilibrada (sobre archivos)
│   ├── busquedas.py              Secuencial, Binaria y Hash (tabla hash propia)
│   ├── archivos.py               Lectura/escritura segura de TXT y XLSX
│   ├── validacion.py             Validación de lo que escribe el usuario
│   ├── graficos.py               Gráficas (matplotlib)
│   ├── laboratorio.py            Laboratorio de rendimiento (escalabilidad y escenarios)
│   └── exportacion.py            Reporte final en PDF (portada, gráficas y tablas)
├── pruebas/                      Pruebas automáticas (unittest)
│   └── datos/                    Archivos SOLO para las pruebas automáticas (el programa no los usa)
├── herramientas/generar_datasets.py   Genera los archivos de pruebas/datos/
├── exportaciones/                Carpeta sugerida para guardar lo que exportes
├── capturas/                     Capturas de cada pantalla (para el reporte del examen)
└── ejecutar_pruebas.py
```

---

## 4. Cumplimiento de cada requerimiento

| # | Requerimiento | Dónde / cómo |
|---|---|---|
| 1 | Leer archivo de 1000 y de 5000 enteros (TXT y XLSX) | **1. Cargar datos** · `librerias/archivos.py` |
| 2 | Reutilizar librerías propias (internos y externos) | `librerias/ordenamiento_interno.py` y `ordenamiento_externo.py`, importadas por `interfaz.py` |
| 3 | Búsqueda secuencial y binaria (+ hash) | **3. Buscar** · `librerias/busquedas.py` |
| 4 | Corrección de código defectuoso | Se documenta en el **reporte PDF de entrega** (los fragmentos los da el docente en clase) |
| 5A | Cargar archivo (TXT o XLSX) | Botón «Seleccionar archivo…» (Ctrl + O): tú eliges tu archivo |
| 5B | Ordenar: elegir algoritmo y orden asc/desc | **2. Ordenar** (interno o externo) |
| 5C | Buscar: secuencial, binaria o hash | **3. Buscar** |
| 5D | Mostrar primeros 20, últimos 20 y total | **1. Cargar datos** y **2. Ordenar** |
| 5E | Exportar archivo ordenado, tiempo y algoritmo | **5. Reporte final** (TXT/XLSX + reporte final PDF) |
| 6 | Comparación básica / algoritmo recomendado | **4. Comparar** (gráfica, tabla y recomendaciones) |

### Flujo del proceso y reporte final
La barra lateral muestra los pasos **1. Cargar → 2. Ordenar → 3. Buscar → 4. Comparar**;
cada uno se marca con ✓ al completarse. El botón **«Generar reporte final PDF»** está
**deshabilitado hasta terminar los 4 pasos** (la página «Reporte final» dice qué falta).
Si se carga otro archivo, el proceso se reinicia. El Laboratorio de rendimiento y la
Intercalación son opcionales y, si se hacen, también aparecen en el reporte.

### Intercalación (ordenamiento externo)
Se cargan en **A** y **B** dos archivos que ya se ordenaron y guardaron antes con
«Guardar archivo ordenado» (TXT o XLSX). Si los dos están ordenados de la misma forma,
se intercalan archivo contra archivo, línea por línea. Si alguno no está ordenado, o uno
es ascendente y el otro descendente, el programa avisa cuál es el problema.

### Separación interno / externo
* **Interno:** los datos están en una lista en memoria.
* **Externo:** los datos se escriben en un archivo `F` y se ordenan leyendo y
  escribiendo **línea por línea** con archivos auxiliares (`F1`, `F2`, `F3`), sin
  cargarlos completos en memoria. Los temporales se borran al terminar,
  aunque ocurra un error o se cancele.

### Qué se exporta
* **Archivo ordenado TXT:** un número por línea. Al inicio lleva el algoritmo, el
  tiempo, etc. como comentarios `# ...`, que el propio sistema ignora al volver a leerlo.
* **Archivo ordenado XLSX:** hoja «Datos ordenados» y hoja «Resumen» (algoritmo, tiempo, comparaciones…).
* **Reporte final PDF** (solo al terminar el proceso): portada con indicadores y estado
  de cada paso · carga de datos con gráfica de distribución · algoritmo utilizado,
  tiempo de ejecución y primeros/últimos 20 · evidencia gráfica antes/después ·
  búsquedas realizadas con gráfica de comparaciones · comparación entre algoritmos ·
  recomendaciones y conclusiones automáticas · laboratorio de rendimiento e
  intercalación (si se hicieron).

---

## 5. Comparación básica (requerimiento 6)

| Escenario | Algoritmo recomendado | Motivo |
|---|---|---|
| Datos pequeños | **Inserción / ShellSort** | Sin sobrecosto; ShellSort (inserción con saltos) fue el más rápido medido. |
| Datos masivos | **QuickSort** (general) / **RadixSort** (enteros) | O(n log n) promedio; Radix fue el más rápido con enteros. |
| Archivos externos | **Mezcla Equilibrada** | Usa tramos naturales y necesita menos pasadas que la Mezcla Directa. |
| Datos parcialmente ordenados | **Inserción** | Casi O(n) cuando cada elemento se mueve poco. |
| Búsquedas frecuentes | **Hash** | Tabla construida una vez; cada búsqueda revisa una cubeta, O(1) promedio. |

Tiempos medidos en esta computadora con un archivo de 20,000 enteros (orden ascendente):

| Algoritmo | Tiempo aprox. |
|---|---|
| RadixSort | 9 ms |
| QuickSort | 43 ms |
| ShellSort | 47 ms |
| HeapSort | 59 ms |
| Mezcla Equilibrada (externo) | 172 ms |
| Mezcla Directa (externo) | 287 ms |
| Inserción | 7.2 s |
| Selección | 7.6 s |
| Burbuja | 15.1 s |

---

## 6. Agregado: Laboratorio de rendimiento

El requerimiento 6 pide **indicar** el algoritmo recomendado para cada escenario. El
laboratorio lo **comprueba con mediciones reales** sobre los datos cargados
(`librerias/laboratorio.py`, herramienta «Laboratorio de rendimiento»):

1. **Escalabilidad:** mide cada algoritmo con n = 250, 500, 1000, 2000, 5000… y calcula
   el **exponente de crecimiento b** (t ≈ n^b) con mínimos cuadrados sobre log n y log t.
   Resultado típico: Burbuja/Inserción/Selección **b ≈ 2.0** (O(n²)); QuickSort/HeapSort
   **b ≈ 1.1** (O(n log n)); RadixSort **b ≈ 1.0** (lineal). Gráfica en escala logarítmica.
2. **Escenarios:** datos pequeños, masivos, casi ordenados, orden inverso y muchos
   duplicados → mapa de calor con el ganador de cada uno.
3. **Búsquedas frecuentes:** costo de 1,000 búsquedas con cada método, incluyendo la
   preparación (ordenar una vez para la binaria, construir la tabla hash).
4. **Recomendación comprobada:** compara el ganador medido con la tabla teórica.
   Con los tres datasets del proyecto coinciden **5 de 5**.

Respeta las restricciones: no usa `.sort()`/`sorted()`; ordena solo con las librerías
propias; mide con `time`; los datos de prueba se generan con un **generador
congruencial lineal propio** (no `random`) y el logaritmo con una **serie propia**
(no `math`). Tarda ≈ 15 s con 5,000 datos y ≈ 20 s con 20,000 (se puede cancelar).
Si se ejecuta, se agrega al reporte final (2 páginas).

## 7. Validaciones y seguridad

El sistema **no usa base de datos**, así que la inyección SQL no puede ejecutarse.
Aun así, toda entrada se valida con **lista blanca** (solo enteros) y se probó
contra textos de ataque:

* **Campo de búsqueda:** solo deja escribir un signo opcional y dígitos ASCII
  (máx. 15). Inyecciones SQL (`' OR 1=1 --`), comandos (`; rm -rf /`), rutas
  (`../../etc/passwd`), scripts, fórmulas de Excel, `1e5`, `0x1F`, `1_000`,
  dígitos Unicode, bytes nulos y textos gigantes se rechazan.
* **Archivos:** solo `.txt` y `.xlsx`. Se revisa el contenido real: un ejecutable
  o ZIP renombrado a `.txt`, un TXT renombrado a `.xlsx`, un XLSX dañado o
  protegido con contraseña se rechazan. Límites: 20 MB y 500,000 números.
* **Datos inválidos** (letras, decimales, notación científica, signos sueltos,
  números de más de 15 dígitos, celdas con fecha o VERDADERO/FALSO): el archivo
  **no se carga a medias**; se indica la línea o celda exacta del error.
* **Tolera** líneas vacías, espacios, tabulaciones, saltos de línea Windows/Mac,
  UTF-8 con BOM, UTF-16, signos `+`/`-`, ceros a la izquierda y encabezado en XLSX.
* **Exportación:** escritura atómica (temporal + reemplazo), no permite sobrescribir
  el archivo de origen, avisa si el destino está abierto en Excel y protege los
  XLSX contra **inyección de fórmulas**.
* **Código:** no usa `eval`, `exec`, `os.system`, `subprocess` ni `pickle`
  (lo comprueba una prueba automática).
* **Interfaz:** los botones se bloquean mientras se procesa (no se pueden lanzar
  dos procesos a la vez); todo proceso largo muestra progreso y se puede **cancelar**.
  Los métodos O(n²) piden confirmación con más de 20,000 datos. Se adapta a la
  pantalla (zoom de Windows, laptops pequeñas): los indicadores se reacomodan y
  aparece desplazamiento en lugar de aplastar las gráficas.
* El tiempo medido **no incluye** el tiempo que la ventana usa para refrescarse.

---

## 8. Guía rápida para la demostración en clase

1. `python main.py` → **1. Cargar datos** → **Seleccionar archivo…** y elegir tu archivo de
   1,000 (TXT) y luego el de 5,000 (XLSX). «Caso del examen» muestra ✓.
2. **2. Ordenar**: *Interno → QuickSort → Ascendente* → **Ordenar datos**. Mostrar la
   gráfica antes/después, los primeros/últimos 20 y el total. Repetir con
   *Externo → Mezcla Equilibrada → Descendente*.
3. **3. Buscar**: buscar un valor con Binaria y luego **Comparar los 3 métodos**
   (comparaciones: n vs log n vs 1).
4. **4. Comparar**: **Ejecutar comparación** y explicar la tabla de recomendaciones.
5. **5. Reporte final**: mostrar que el botón del PDF solo se habilitó al terminar,
   **Guardar archivo ordenado** (TXT/XLSX) y **Generar reporte final PDF**.
6. **Intercalación**: cargar en A y B dos archivos ordenados que guardaste antes.
7. **Laboratorio de rendimiento**: **Ejecutar laboratorio** y explicar el exponente b
   (n² contra n log n) y la tabla «Recomendación comprobada» (5 de 5).
8. Uso de librerías propias: abrir `interfaz.py` y mostrar los `from librerias import ...`.

---

## 9. Lista de verificación contra el PDF del examen

| Pide el examen | Estado |
|---|---|
| Leer 1 archivo de 1000 y 1 de 5000 enteros, en TXT y XLSX | ✔ el usuario elige su archivo; validación completa |
| Reutilizar librerías propias de ordenamiento internos y externos | ✔ 7 internos + 3 externos en `librerias/` |
| Búsqueda secuencial y binaria (y hash en el punto C) | ✔ las tres, con tabla hash propia |
| Corrección de código defectuoso (índices, recursividad, intercambio, archivos, búsquedas) | Va en el reporte PDF de entrega (error, corrección y explicación de cada fragmento) |
| A) Cargar TXT o XLSX | ✔ |
| B) Ordenar eligiendo algoritmo y asc/desc | ✔ interno o externo |
| C) Buscar con secuencial, binaria o hash | ✔ |
| D) Primeros 20, últimos 20 y total | ✔ |
| E) Guardar archivo ordenado, tiempo y algoritmo | ✔ TXT/XLSX con metadatos + reporte PDF |
| 6) Tabla de algoritmo recomendado por escenario | ✔ y comprobada con el laboratorio |
| Restricciones: sin `.sort()`, `sorted()` ni bibliotecas de ordenamiento | ✔ verificado por prueba automática (análisis del código) |
| Repositorio: código, librerías, README, instrucciones | ✔ listo para subir (`.gitignore` incluido) |
| Reporte PDF de entrega (portada, introducción, desarrollo, resultados, conclusiones) | Lo redacta el alumno; el programa aporta capturas (`capturas/`) y el reporte de resultados en PDF |

**Nota sobre librerías:** para ordenar y buscar solo se usan las librerías propias.
Además de `os`, `time` y `openpyxl` (permitidas), el programa usa `tkinter` (interfaz
gráfica, incluida en Python) y `matplotlib` (solo para **dibujar** gráficas y el PDF;
no ordena nada). Si el profesor no las permitiera, el núcleo (`librerias/`) funciona
igual sin ellas.

"""
INTERFAZ GRAFICA - Sistema de Procesamiento y Ordenamiento Masivo de Datos

Usa tkinter (incluido en Python) y matplotlib para las graficas.
Toda la logica vive en las librerias propias de la carpeta "librerias";
esta interfaz solo las IMPORTA y las usa (reutilizacion real).

Flujo del proceso (barra lateral):
    1. Cargar datos  ->  2. Ordenar  ->  3. Buscar  ->  4. Comparar
    ->  5. Reporte final (el boton del PDF se habilita solo al completar 1-4)
Herramientas adicionales: Laboratorio de rendimiento e Intercalacion de archivos.
"""

import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont

from librerias import ordenamiento_interno as oi
from librerias import ordenamiento_externo as oe
from librerias import busquedas as bq
from librerias import archivos as ar
from librerias import validacion as val
from librerias import graficos as gr
from librerias import exportacion as ex
from librerias import laboratorio as lab

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAY_MATPLOTLIB = True
except ImportError:                                   # el sistema funciona aun sin graficas
    HAY_MATPLOTLIB = False

BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_INICIAL = os.path.join(os.path.expanduser("~"), "Downloads")   # donde abre el dialogo la 1a vez
CARPETA_EXPORT = os.path.join(BASE, "exportaciones")
CARPETA_TEMP = os.path.join(BASE, "temp_externo")

LIMITE_CUADRATICO = 20_000          # arriba de esto se pide confirmacion para O(n^2)

# ----------------------------------------------------------------------
# Sistema de diseno
# ----------------------------------------------------------------------
LATERAL = "#0f172a"
LATERAL_HOVER = "#1e293b"
LATERAL_TEXTO = "#cbd5e1"
LATERAL_TENUE = "#64748b"
FONDO = "#f1f5f9"
TARJETA = "#ffffff"
BORDE = "#e2e8f0"
BORDE_FUERTE = "#cbd5e1"
TEXTO = "#0f172a"
TEXTO_2 = "#475569"
TEXTO_3 = "#94a3b8"
PRIMARIO = "#2563eb"
PRIMARIO_HOVER = "#1d4ed8"
PRIMARIO_SUAVE = "#eff6ff"
PRIMARIO_CLARO = "#60a5fa"
OK = "#15803d"
OK_VIVO = "#22c55e"
OK_SUAVE = "#f0fdf4"
ERROR = "#b91c1c"
ERROR_SUAVE = "#fef2f2"
AVISO = "#b45309"
AVISO_SUAVE = "#fffbeb"
CODIGO_FONDO = "#0b1220"
CODIGO_TEXTO = "#e2e8f0"

ESCALA = 1.0
FUENTE = "Segoe UI"
FUENTE_B = "Segoe UI Semibold"
MONO = "Consolas"


def px(n):
    """Pixeles "logicos" -> pixeles reales segun el zoom de la pantalla."""
    return int(n * ESCALA)


def fuente(tam, negrita=False):
    """Tk solo acepta tamanos enteros: 9.5 se redondea a 10, etc."""
    return (FUENTE_B if negrita else FUENTE, int(tam + 0.5))


def elegir_fuentes(raiz):
    """Usa las fuentes modernas de Windows si existen; si no, alternativas."""
    global FUENTE, FUENTE_B, MONO
    familias = set(tkfont.families(raiz))

    def primera(opciones, defecto):
        for nombre in opciones:
            if nombre in familias:
                return nombre
        return defecto
    FUENTE = primera(("Segoe UI", "Helvetica", "Arial"), "TkDefaultFont")
    FUENTE_B = primera(("Segoe UI Semibold", "Segoe UI"), FUENTE)
    MONO = primera(("Cascadia Mono", "Consolas", "Courier New"), "TkFixedFont")


def miles(n):
    return f"{n:,}"


DESCRIPCIONES = {
    "Burbuja": "Compara vecinos y los intercambia si están en desorden. Simple, pero lento con muchos datos.",
    "Inserción": "Inserta cada elemento en su lugar dentro de la parte ya ordenada. Muy rápido si los datos "
                 "ya vienen casi ordenados.",
    "Selección": "Busca el menor (o mayor) y lo coloca al inicio. Pocos intercambios, pero siempre n²/2 "
                 "comparaciones.",
    "ShellSort": "Inserción con saltos decrecientes (Knuth: 1, 4, 13, 40…). Mueve los datos lejos en pocos pasos.",
    "QuickSort": "Divide con un pivote (mediana de tres) y agrupa los iguales. Usa una pila propia en vez "
                 "de recursión.",
    "HeapSort": "Construye un montículo dentro de la misma lista y extrae la raíz repetidamente.",
    "RadixSort": "No compara: reparte por dígitos (unidades, decenas…) en 10 cubetas. Ideal para enteros.",
    "Mezcla Directa": "Externo: particiona el archivo en bloques de 1, 2, 4, 8… y los fusiona con los "
                      "archivos auxiliares F1 y F2.",
    "Mezcla Equilibrada": "Externo: reparte los tramos que ya vienen ordenados en 4 archivos y los fusiona "
                          "hasta que queda uno solo.",
}

COMPLEJIDAD_CORTA = {
    "Burbuja": "O(n²)", "Inserción": "O(n²) · O(n) casi ordenado", "Selección": "O(n²)",
    "ShellSort": "≈ O(n^1.5)", "QuickSort": "O(n log n) promedio", "HeapSort": "O(n log n)",
    "RadixSort": "O(d·n) · sin comparaciones", "Mezcla Directa": "⌈log₂ n⌉ pasadas en disco",
    "Mezcla Equilibrada": "Aprovecha tramos naturales",
}

RECOMENDACIONES = [
    ("Datos pequeños", "Inserción / ShellSort",
     "Con pocos datos (decenas) los métodos simples sin sobrecosto ganan: Inserción es estable y ordena en "
     "el mismo arreglo, y ShellSort (inserción con saltos) fue el más rápido en nuestras mediciones."),
    ("Datos masivos", "QuickSort / RadixSort",
     "QuickSort es O(n log n) en promedio y con mediana de tres y partición de 3 vías no se degrada con "
     "duplicados. Para enteros, RadixSort fue el más rápido en nuestras pruebas."),
    ("Archivos externos", "Mezcla Equilibrada",
     "Trabaja por tramos naturales sin cargar todo en memoria y necesita menos pasadas que la Mezcla "
     "Directa, porque aprovecha el orden que ya traen los datos."),
    ("Datos parcialmente ordenados", "Inserción",
     "Si los datos están casi ordenados cada elemento se mueve poco: su costo baja a casi O(n). En "
     "archivos externos, la Mezcla Equilibrada aprovecha lo mismo."),
    ("Búsquedas frecuentes", "Hash",
     "Se construye la tabla una sola vez (O(n)) y cada búsqueda revisa una sola cubeta, O(1) en "
     "promedio. Alternativa: ordenar una vez y usar Búsqueda Binaria (O(log n))."),
]

PAGINAS = {
    "cargar": ("Cargar datos", "Selecciona un archivo TXT o XLSX con números enteros."),
    "ordenar": ("Ordenar", "Elige el tipo de procesamiento, el algoritmo y el orden."),
    "buscar": ("Buscar un valor", "Búsqueda secuencial, binaria o hash sobre los datos."),
    "comparar": ("Comparar algoritmos", "Mide todos los algoritmos con los mismos datos."),
    "intercalacion": ("Intercalación de archivos", "Une dos archivos ya ordenados leyéndolos de forma secuencial."),
    "reporte": ("Reporte final", "Exporta el archivo ordenado y genera el reporte PDF de todo el proceso."),
    "laboratorio": ("Laboratorio de rendimiento", "Comprueba con mediciones reales cómo crece cada algoritmo y "
                                                  "cuál conviene en cada escenario."),
}
PASOS_OBLIGATORIOS = ("cargar", "ordenar", "buscar", "comparar")
PASOS_OPCIONALES = ("laboratorio", "intercalacion")


class Cancelado(Exception):
    """El usuario presiono Cancelar."""


# ======================================================================
# Componentes visuales
# ======================================================================
def _al_hacer_clic(widget, funcion):
    widget.bind("<Button-1>", lambda e: funcion())
    for hijo in widget.winfo_children():
        _al_hacer_clic(hijo, funcion)


def etiqueta_seccion(padre, texto, bg=TARJETA, arriba=14):
    tk.Label(padre, text=texto.upper(), bg=bg, fg=TEXTO_3, font=fuente(8, True)).pack(
        anchor="w", pady=(px(arriba), px(6)))


class Boton(tk.Label):
    """Boton plano con estado 'hover' y deshabilitado."""
    ESTILOS = {
        "primario": (PRIMARIO, "white", PRIMARIO_HOVER, PRIMARIO),
        "secundario": ("white", TEXTO, "#f8fafc", BORDE_FUERTE),
        "suave": (PRIMARIO_SUAVE, PRIMARIO, "#dbeafe", PRIMARIO_SUAVE),
        "peligro": ("white", ERROR, ERROR_SUAVE, "#fecaca"),
        "exito": (OK, "white", "#166534", OK),
    }

    def __init__(self, padre, texto, comando, tipo="primario", grande=False, pequeno=False):
        bg, fg, hover, borde = self.ESTILOS[tipo]
        tam = 11 if grande else (9 if pequeno else 10)
        super().__init__(padre, text=texto, bg=bg, fg=fg, font=fuente(tam, True), cursor="hand2",
                         padx=px(12 if pequeno else 18), pady=px(13 if grande else (5 if pequeno else 9)),
                         highlightthickness=1, highlightbackground=borde, highlightcolor=borde)
        self.tipo = tipo
        self.comando = comando
        self.habilitado = True
        self.encima = False
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<ButtonRelease-1>", self._clic)

    def _hover(self, encima):
        self.encima = encima
        self._pintar()

    def _clic(self, evento):
        if self.habilitado and 0 <= evento.x <= self.winfo_width() and 0 <= evento.y <= self.winfo_height():
            self.comando()

    def _pintar(self):
        bg, fg, hover, borde = self.ESTILOS[self.tipo]
        if not self.habilitado:
            self.config(bg="#e2e8f0" if self.tipo in ("primario", "exito") else "white", fg=TEXTO_3,
                        highlightbackground=BORDE, cursor="arrow")
        else:
            self.config(bg=hover if self.encima else bg, fg=fg, highlightbackground=borde, cursor="hand2")

    def habilitar(self, valor=True):
        self.habilitado = bool(valor)
        self._pintar()


class Tarjeta(tk.Frame):
    """Recuadro blanco con titulo y subtitulo opcional."""

    def __init__(self, padre, titulo=None, subtitulo=None, relleno=18):
        super().__init__(padre, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
        if titulo:
            cab = tk.Frame(self, bg=TARJETA)
            cab.pack(fill="x", padx=px(relleno), pady=(px(16), px(2)))
            tk.Label(cab, text=titulo, bg=TARJETA, fg=TEXTO, font=fuente(11.5, True)).pack(anchor="w")
            if subtitulo:
                sub = tk.Label(cab, text=subtitulo, bg=TARJETA, fg=TEXTO_2, font=fuente(9), justify="left",
                               anchor="w", wraplength=px(320))
                sub.pack(fill="x", pady=(px(2), 0))
                ajustar_ancho_texto(sub)
        self.cuerpo = tk.Frame(self, bg=TARJETA)
        self.cuerpo.pack(fill="both", expand=True, padx=px(relleno), pady=(px(10), px(relleno)))


class Segmentado(tk.Frame):
    """Control segmentado (como en iOS/Windows 11) para 2-3 opciones."""

    def __init__(self, padre, opciones, variable, comando=None):
        super().__init__(padre, bg="#e2e8f0", padx=px(3), pady=px(3))
        self.var = variable
        self.comando = comando
        self.habilitado = True
        self.etiquetas = []
        for i, (valor, texto) in enumerate(opciones):
            l = tk.Label(self, text=texto, font=fuente(9.5, True), padx=px(10), pady=px(6), cursor="hand2")
            l.grid(row=0, column=i, sticky="nsew")
            self.columnconfigure(i, weight=1, uniform="seg")
            l.bind("<Button-1>", lambda e, v=valor: self._elegir(v))
            self.etiquetas.append((valor, l))
        variable.trace_add("write", lambda *a: self._refrescar())
        self._refrescar()

    def _elegir(self, valor):
        if self.habilitado and self.var.get() != valor:
            self.var.set(valor)
            if self.comando:
                self.comando()

    def _refrescar(self):
        for valor, l in self.etiquetas:
            if valor == self.var.get():
                l.config(bg="white", fg=TEXTO)
            else:
                l.config(bg="#e2e8f0", fg=TEXTO_2)


class ListaOpciones(tk.Frame):
    """Lista de opciones tipo "tarjeta" con circulo de seleccion."""

    def __init__(self, padre, variable, comando=None, compacta=False):
        super().__init__(padre, bg=TARJETA)
        self.var = variable
        self.comando = comando
        self.compacta = compacta
        self.items = []
        variable.trace_add("write", lambda *a: self._refrescar())

    def poner_opciones(self, opciones):
        for hijo in self.winfo_children():
            hijo.destroy()
        self.items = []
        for valor, titulo, subtitulo in opciones:
            item = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground=BORDE, cursor="hand2")
            item.pack(fill="x", pady=(0, px(6)))
            lado = px(16)
            c = tk.Canvas(item, width=lado, height=lado, bg="white", highlightthickness=0)
            c.pack(side="left", padx=(px(12), px(10)))
            textos = tk.Frame(item, bg="white")
            textos.pack(side="left", fill="x", expand=True, pady=px(6 if self.compacta else 8))
            t = tk.Label(textos, text=titulo, bg="white", fg=TEXTO, font=fuente(10, True), anchor="w")
            t.pack(fill="x")
            etiquetas = [t]
            if subtitulo:
                s = tk.Label(textos, text=subtitulo, bg="white", fg=TEXTO_2, font=fuente(8.5), anchor="w")
                s.pack(fill="x")
                etiquetas.append(s)
            _al_hacer_clic(item, lambda v=valor: self._elegir(v))
            self.items.append((valor, item, c, textos, etiquetas))
        self._refrescar()

    def _elegir(self, valor):
        if self.var.get() != valor:
            self.var.set(valor)
            if self.comando:
                self.comando()

    def _refrescar(self):
        for valor, item, c, textos, etiquetas in self.items:
            sel = valor == self.var.get()
            bg = PRIMARIO_SUAVE if sel else "white"
            item.config(bg=bg, highlightbackground=PRIMARIO if sel else BORDE)
            for w in [c, textos] + etiquetas:
                w.config(bg=bg)
            lado = int(c.cget("width"))
            c.delete("all")
            c.create_oval(1, 1, lado - 1, lado - 1, outline=PRIMARIO if sel else BORDE_FUERTE, width=2, fill=bg)
            if sel:
                m = lado * 0.3
                c.create_oval(m, m, lado - m, lado - m, fill=PRIMARIO, outline="")


class Chip(tk.Label):
    """Etiqueta que se activa / desactiva (seleccion multiple)."""

    def __init__(self, padre, texto, variable):
        super().__init__(padre, text=texto, font=fuente(9.5, True), padx=px(10), pady=px(6), cursor="hand2",
                         highlightthickness=1)
        self.var = variable
        self.bind("<Button-1>", lambda e: self.var.set(not self.var.get()))
        variable.trace_add("write", lambda *a: self._pintar())
        self._pintar()

    def _pintar(self):
        if self.var.get():
            self.config(text="✓ " + self.cget("text").lstrip("✓ "), bg=PRIMARIO_SUAVE, fg=PRIMARIO,
                        highlightbackground=PRIMARIO)
        else:
            self.config(text=self.cget("text").lstrip("✓ "), bg="white", fg=TEXTO_2, highlightbackground=BORDE)


class FichaDatos(tk.Frame):
    """Filas "Concepto  valor" separadas por lineas finas."""

    def __init__(self, padre, conceptos, ancho_valor=260):
        super().__init__(padre, bg=TARJETA)
        self.valores = {}
        self.columnconfigure(1, weight=1)
        for i, concepto in enumerate(conceptos):
            if i > 0:
                tk.Frame(self, bg=BORDE, height=1).grid(row=2 * i - 1, column=0, columnspan=2, sticky="ew")
            tk.Label(self, text=concepto, bg=TARJETA, fg=TEXTO_2, font=fuente(9.5)).grid(
                row=2 * i, column=0, sticky="nw", pady=px(7))
            v = tk.Label(self, text="—", bg=TARJETA, fg=TEXTO, font=fuente(10, True), anchor="w",
                         justify="left", wraplength=px(ancho_valor))
            v.grid(row=2 * i, column=1, sticky="w", padx=(px(14), 0), pady=px(7))
            self.valores[concepto] = v

    def poner(self, concepto, texto, color=TEXTO):
        self.valores[concepto].config(text=texto, fg=color)

    def limpiar(self):
        for v in self.valores.values():
            v.config(text="—", fg=TEXTO)


class Indicadores(tk.Frame):
    """Fila de mosaicos KPI: etiqueta pequena arriba y valor grande abajo."""

    def __init__(self, padre, conceptos, ancho_minimo=175):
        super().__init__(padre, bg=FONDO)
        self.valores = {}
        self.cajas = []
        self.columnas = 0
        self.ancho_minimo = ancho_minimo
        for concepto in conceptos:
            caja = tk.Frame(self, bg=TARJETA, highlightbackground=BORDE, highlightthickness=1)
            tk.Label(caja, text=concepto.upper(), bg=TARJETA, fg=TEXTO_3, font=fuente(8, True)).pack(
                anchor="w", padx=px(16), pady=(px(12), 0))
            v = tk.Label(caja, text="—", bg=TARJETA, fg=TEXTO, font=fuente(15, True), anchor="w")
            v.pack(anchor="w", padx=px(16), pady=(px(2), px(12)))
            self.valores[concepto] = v
            self.cajas.append(caja)
        self._acomodar(len(conceptos))
        self.bind("<Configure>", lambda e: self._acomodar(max(1, min(len(self.cajas),
                                                                     e.width // px(self.ancho_minimo)))))

    def _acomodar(self, columnas):
        """Si no caben todos en una fila, se reparten en varias filas."""
        if columnas == self.columnas:
            return
        filas = (len(self.cajas) + columnas - 1) // columnas
        columnas = (len(self.cajas) + filas - 1) // filas          # filas parejas (3+3, no 4+2)
        if columnas == self.columnas:
            return
        self.columnas = columnas
        for i in range(len(self.cajas)):
            self.columnconfigure(i, weight=0, uniform="")
        for i in range(columnas):
            self.columnconfigure(i, weight=1, uniform="kpi")
        for i, caja in enumerate(self.cajas):
            fila, col = divmod(i, columnas)
            caja.grid(row=fila, column=col, sticky="nsew", padx=(0 if col == 0 else px(12), 0),
                      pady=(0 if fila == 0 else px(12), 0))

    def poner(self, concepto, texto, color=TEXTO):
        self.valores[concepto].config(text=texto, fg=color)

    def limpiar(self):
        for v in self.valores.values():
            v.config(text="—", fg=TEXTO)


class Aviso(tk.Frame):
    """Franja de estado con color (exito / error / aviso / informacion)."""
    COLORES = {"ok": (OK_SUAVE, OK), "error": (ERROR_SUAVE, ERROR), "aviso": (AVISO_SUAVE, AVISO),
               "info": (PRIMARIO_SUAVE, PRIMARIO), "neutro": ("#f8fafc", TEXTO_2)}

    def __init__(self, padre):
        super().__init__(padre, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDE)
        self.barra = tk.Frame(self, bg=TEXTO_3, width=px(4))
        self.barra.pack(side="left", fill="y")
        cuerpo = tk.Frame(self, bg="#f8fafc")
        cuerpo.pack(side="left", fill="both", expand=True, padx=px(16), pady=px(12))
        self.cuerpo = cuerpo
        self.titulo = tk.Label(cuerpo, text="", bg="#f8fafc", fg=TEXTO, font=fuente(13, True), anchor="w")
        self.titulo.pack(fill="x")
        self.detalle = tk.Label(cuerpo, text="", bg="#f8fafc", fg=TEXTO_2, font=fuente(9.5), anchor="w",
                                justify="left")
        self.detalle.pack(fill="x")

    def poner(self, tipo, titulo, detalle=""):
        fondo, color = self.COLORES[tipo]
        for w in (self, self.cuerpo, self.titulo, self.detalle):
            w.config(bg=fondo)
        self.config(highlightbackground=fondo)
        self.barra.config(bg=color)
        self.titulo.config(text=titulo, fg=color if tipo != "neutro" else TEXTO)
        self.detalle.config(text=detalle)


class Grafica(tk.Frame):
    """Figura de matplotlib dentro de tkinter."""

    def __init__(self, padre, ancho=6.4, alto=3.2):
        super().__init__(padre, bg=TARJETA)
        if HAY_MATPLOTLIB:
            self.figura = Figure(figsize=(ancho, alto), dpi=96)
            self.figura.patch.set_facecolor(TARJETA)
            self.lienzo = FigureCanvasTkAgg(self.figura, master=self)
            self.lienzo.get_tk_widget().configure(bg=TARJETA, highlightthickness=0)
            self.lienzo.get_tk_widget().pack(fill="both", expand=True)
        else:
            self.figura = None
            tk.Label(self, text="Instala matplotlib para ver las gráficas:\npython -m pip install matplotlib",
                     bg=TARJETA, fg=TEXTO_2).pack(expand=True)

    def dibujar(self, funcion, *args, **kw):
        if self.figura is None:
            return
        try:
            funcion(self.figura, *args, **kw)
            self.lienzo.draw_idle()
        except Exception:
            pass                                      # una grafica nunca debe tumbar el programa


class ColumnaDesplazable(tk.Frame):
    """Columna de ancho fijo con barra de desplazamiento que aparece solo si
    el contenido no cabe (pantallas pequenas o con zoom)."""

    def __init__(self, padre, ancho):
        super().__init__(padre, bg=FONDO)
        self.lienzo = tk.Canvas(self, bg=FONDO, highlightthickness=0, borderwidth=0, width=ancho)
        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        self.interior = tk.Frame(self.lienzo, bg=FONDO)
        self._ventana = self.lienzo.create_window((0, 0), window=self.interior, anchor="nw", width=ancho)
        self.lienzo.configure(yscrollcommand=self.barra.set)
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.interior.bind("<Configure>", self._ajustar)
        self.lienzo.bind("<Configure>", self._ajustar)
        self.bind("<Enter>", lambda e: self.bind_all("<MouseWheel>", self._rueda))
        self.bind("<Leave>", lambda e: self.unbind_all("<MouseWheel>"))

    def _ajustar(self, _evento=None):
        self.lienzo.configure(scrollregion=self.lienzo.bbox("all"))
        if self.interior.winfo_reqheight() > self.lienzo.winfo_height() + 2:
            if not self.barra.winfo_ismapped():
                self.barra.pack(side="right", fill="y", padx=(px(4), 0))
        elif self.barra.winfo_ismapped():
            self.barra.pack_forget()
            self.lienzo.yview_moveto(0)

    def _rueda(self, evento):
        if self.interior.winfo_reqheight() > self.lienzo.winfo_height():
            self.lienzo.yview_scroll(int(-evento.delta / 120), "units")


class PanelDesplazable(tk.Frame):
    """Area que llena la ventana; si el contenido no cabe (pantalla pequena)
    aparece una barra de desplazamiento en lugar de aplastar las graficas."""

    def __init__(self, padre):
        super().__init__(padre, bg=FONDO)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.lienzo = tk.Canvas(self, bg=FONDO, highlightthickness=0, borderwidth=0)
        self.lienzo.grid(row=0, column=0, sticky="nsew")
        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        self.interior = tk.Frame(self.lienzo, bg=FONDO)
        self._ventana = self.lienzo.create_window((0, 0), window=self.interior, anchor="nw")
        self.lienzo.configure(yscrollcommand=self.barra.set)
        self.interior.bind("<Configure>", self._ajustar)
        self.lienzo.bind("<Configure>", self._ajustar)
        self.bind("<Enter>", lambda e: self.bind_all("<MouseWheel>", self._rueda))
        self.bind("<Leave>", lambda e: self.unbind_all("<MouseWheel>"))

    def _ajustar(self, _evento=None):
        ancho = self.lienzo.winfo_width()
        requerido = self.interior.winfo_reqheight()
        alto = max(requerido, self.lienzo.winfo_height())
        self.lienzo.itemconfigure(self._ventana, width=ancho, height=alto)
        self.lienzo.configure(scrollregion=(0, 0, ancho, alto))
        if requerido > self.lienzo.winfo_height() + 2:
            if not self.barra.winfo_ismapped():
                self.barra.grid(row=0, column=1, sticky="ns", padx=(px(4), 0))
        elif self.barra.winfo_ismapped():
            self.barra.grid_remove()
            self.lienzo.yview_moveto(0)

    def _rueda(self, evento):
        if self.interior.winfo_reqheight() > self.lienzo.winfo_height():
            self.lienzo.yview_scroll(int(-evento.delta / 120), "units")


class ElementoMenu(tk.Frame):
    """Opcion de la barra lateral con circulo de paso (numero o ✓)."""

    def __init__(self, padre, simbolo, texto, comando):
        super().__init__(padre, bg=LATERAL, cursor="hand2")
        self.simbolo = simbolo
        self.activo = self.hecho = self.encima = False
        self.barra = tk.Frame(self, bg=LATERAL, width=px(3))
        self.barra.pack(side="left", fill="y")
        lado = px(26)
        self.circulo = tk.Canvas(self, width=lado, height=lado, bg=LATERAL, highlightthickness=0)
        self.circulo.pack(side="left", padx=(px(17), px(12)), pady=px(8))
        self.texto = tk.Label(self, text=texto, bg=LATERAL, fg=LATERAL_TEXTO, font=fuente(10.5), anchor="w")
        self.texto.pack(side="left", fill="x", expand=True)
        for w in (self, self.circulo, self.texto):
            w.bind("<Enter>", lambda e: self._hover(True))
            w.bind("<Leave>", lambda e: self._hover(False))
            w.bind("<Button-1>", lambda e: comando())
        self.refrescar()

    def _hover(self, valor):
        self.encima = valor
        self.refrescar()

    def poner(self, activo=None, hecho=None):
        if activo is not None:
            self.activo = activo
        if hecho is not None:
            self.hecho = hecho
        self.refrescar()

    def refrescar(self):
        bg = LATERAL_HOVER if (self.activo or self.encima) else LATERAL
        for w in (self, self.circulo, self.texto):
            w.config(bg=bg)
        self.barra.config(bg=PRIMARIO_CLARO if self.activo else bg)
        self.texto.config(fg="white" if self.activo else LATERAL_TEXTO,
                          font=fuente(10.5, True) if self.activo else fuente(10.5))
        c = self.circulo
        lado = int(c.cget("width"))
        c.delete("all")
        if self.hecho:
            c.create_oval(1, 1, lado - 1, lado - 1, fill=OK_VIVO, outline="")
            c.create_text(lado / 2, lado / 2, text="✓", fill="white", font=fuente(10, True))
        elif self.activo:
            c.create_oval(1, 1, lado - 1, lado - 1, fill=PRIMARIO, outline="")
            c.create_text(lado / 2, lado / 2, text=self.simbolo, fill="white", font=fuente(9, True))
        else:
            c.create_oval(1, 1, lado - 1, lado - 1, outline="#475569", width=1.5, fill=bg)
            c.create_text(lado / 2, lado / 2, text=self.simbolo, fill="#94a3b8", font=fuente(9, True))


def crear_tabla(padre, columnas, alto=8):
    """columnas: lista de (id, titulo, ancho, alineacion). Regresa el Treeview."""
    marco = tk.Frame(padre, bg=TARJETA, highlightthickness=1, highlightbackground=BORDE)
    arbol = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", height=alto,
                         style="Tabla.Treeview")
    for cid, titulo, ancho, alin in columnas:
        arbol.heading(cid, text=titulo, anchor=alin)
        arbol.column(cid, width=px(ancho), anchor=alin, stretch=True)
    barra = ttk.Scrollbar(marco, orient="vertical", command=arbol.yview)
    arbol.configure(yscrollcommand=barra.set)
    arbol.tag_configure("par", background="#f8fafc")
    arbol.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    arbol.marco = marco
    return arbol


def llenar_tabla(arbol, filas):
    arbol.delete(*arbol.get_children())
    for i, fila in enumerate(filas):
        arbol.insert("", "end", values=fila, tags=("par",) if i % 2 else ())


def filas_valores(lista, inicio):
    return [(miles(inicio + i + 1), miles(v)) for i, v in enumerate(lista)]


def ajustar_ancho_texto(etiqueta, minimo=200):
    """El texto de la etiqueta se acomoda al ancho disponible."""
    etiqueta.bind("<Configure>", lambda e: etiqueta.config(wraplength=max(px(minimo), e.width - px(6))))


# ======================================================================
# Aplicacion
# ======================================================================
class Aplicacion(tk.Tk):

    def __init__(self):
        super().__init__()
        global ESCALA
        ESCALA = max(1.0, self.winfo_fpixels("1i") / 96.0)
        elegir_fuentes(self)
        self.title("Sistema de Procesamiento y Ordenamiento Masivo de Datos")
        self.configure(bg=FONDO)
        self.geometry(f"{px(1320)}x{px(820)}")
        self.minsize(px(1080), px(660))
        try:
            self.state("zoomed")                          # maximizada en Windows
        except tk.TclError:
            pass

        # Estado de los datos
        self.info = None
        self.originales = []
        self.stats = None
        self.resultado = None
        self.historial = []
        self.busquedas = []
        self.comparacion_busquedas = None
        self.comparacion = []
        self.comparacion_orden = "Ascendente"
        self.intercalacion = None
        self.laboratorio = None
        self.tabla_hash = None
        self.lista_hash = None
        self.seg_tabla = 0.0
        self.hecho = {"cargar": False, "ordenar": False, "buscar": False, "comparar": False,
                      "intercalacion": False, "laboratorio": False}
        # Estado de la interfaz
        self.ocupado = False
        self.cancelar = False
        self.cerrar_pendiente = False
        self.pausa = 0.0
        self.ultimo_refresco = 0.0
        self.botones = []
        self.exportados = []
        self.pagina_actual = None
        self.ultima_carpeta = None

        self._estilos()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._barra_lateral()
        principal = tk.Frame(self, bg=FONDO)
        principal.grid(row=0, column=1, sticky="nsew")
        principal.columnconfigure(0, weight=1)
        principal.rowconfigure(1, weight=1)
        self._cabecera(principal)
        self.contenedor = tk.Frame(principal, bg=FONDO)
        self.contenedor.grid(row=1, column=0, sticky="nsew", padx=px(28), pady=(0, px(18)))
        self.contenedor.rowconfigure(0, weight=1)
        self.contenedor.columnconfigure(0, weight=1)
        self._barra_estado(principal)

        self.paginas = {}
        self._pagina_cargar()
        self._pagina_ordenar()
        self._pagina_buscar()
        self._pagina_comparar()
        self._pagina_intercalacion()
        self._pagina_laboratorio()
        self._pagina_reporte()
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)
        self.bind("<Control-o>", lambda e: self._abrir_archivo())
        self.mostrar("cargar")
        self._refrescar_proceso()
        self._estado("Listo. Empieza cargando un archivo TXT o XLSX.", "neutro")

    # ------------------------------------------------------------------
    # Estilos ttk
    # ------------------------------------------------------------------
    def _estilos(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure(".", font=fuente(10), background=FONDO)
        st.configure("Tabla.Treeview", background=TARJETA, fieldbackground=TARJETA, foreground=TEXTO,
                     rowheight=px(26), font=fuente(10), borderwidth=0, relief="flat")
        st.configure("Tabla.Treeview.Heading", background="#f8fafc", foreground=TEXTO_2, font=fuente(9, True),
                     relief="flat", borderwidth=0, padding=(px(8), px(6)))
        st.map("Tabla.Treeview.Heading", background=[("active", "#f1f5f9")])
        st.map("Tabla.Treeview", background=[("selected", PRIMARIO_SUAVE)], foreground=[("selected", TEXTO)])
        st.layout("Tabla.Treeview", [("Tabla.Treeview.treearea", {"sticky": "nswe"})])
        st.configure("Vertical.TScrollbar", troughcolor=FONDO, background="#cbd5e1", bordercolor=FONDO,
                     arrowcolor=TEXTO_2, lightcolor="#cbd5e1", darkcolor="#cbd5e1", gripcount=0, relief="flat",
                     arrowsize=px(12))
        st.map("Vertical.TScrollbar", background=[("active", "#94a3b8")])
        st.configure("Delgada.Horizontal.TProgressbar", troughcolor="#e2e8f0", background=PRIMARIO,
                     bordercolor="#e2e8f0", lightcolor=PRIMARIO, darkcolor=PRIMARIO, thickness=px(6))

    # ------------------------------------------------------------------
    # Estructura: barra lateral, cabecera, barra de estado
    # ------------------------------------------------------------------
    def _barra_lateral(self):
        lat = tk.Frame(self, bg=LATERAL, width=px(258))
        lat.grid(row=0, column=0, sticky="ns")
        lat.pack_propagate(False)

        marca = tk.Frame(lat, bg=LATERAL)
        marca.pack(fill="x", padx=px(20), pady=(px(24), px(22)))
        lado = px(40)
        logo = tk.Canvas(marca, width=lado, height=lado, bg=LATERAL, highlightthickness=0)
        logo.pack(side="left")
        logo.create_rectangle(0, 0, lado, lado, fill=PRIMARIO, outline="")
        for i, alto in enumerate((0.35, 0.55, 0.75)):
            x0 = lado * (0.2 + i * 0.22)
            logo.create_rectangle(x0, lado * (0.85 - alto), x0 + lado * 0.15, lado * 0.85, fill="white", outline="")
        txt = tk.Frame(marca, bg=LATERAL)
        txt.pack(side="left", padx=(px(12), 0))
        tk.Label(txt, text="Ordenamiento", bg=LATERAL, fg="white", font=fuente(12.5, True)).pack(anchor="w")
        tk.Label(txt, text="Masivo de Datos", bg=LATERAL, fg="#94a3b8", font=fuente(9.5)).pack(anchor="w")

        self.menu = {}

        def seccion(texto):
            tk.Label(lat, text=texto, bg=LATERAL, fg=LATERAL_TENUE, font=fuente(8, True)).pack(
                anchor="w", padx=px(22), pady=(px(14), px(4)))

        seccion("PROCESO")
        for clave, simbolo, texto in (("cargar", "1", "Cargar datos"), ("ordenar", "2", "Ordenar"),
                                      ("buscar", "3", "Buscar"), ("comparar", "4", "Comparar")):
            self.menu[clave] = ElementoMenu(lat, simbolo, texto, lambda c=clave: self.mostrar(c))
            self.menu[clave].pack(fill="x")
        seccion("RESULTADOS")
        self.menu["reporte"] = ElementoMenu(lat, "5", "Reporte final", lambda: self.mostrar("reporte"))
        self.menu["reporte"].pack(fill="x")
        seccion("HERRAMIENTAS")
        for clave, simbolo, texto in (("laboratorio", "↗", "Laboratorio de rendimiento"),
                                      ("intercalacion", "⇄", "Intercalación")):
            self.menu[clave] = ElementoMenu(lat, simbolo, texto, lambda c=clave: self.mostrar(c))
            self.menu[clave].pack(fill="x")

        caja = tk.Frame(lat, bg=LATERAL_HOVER)
        caja.pack(side="bottom", fill="x", padx=px(16), pady=px(18))
        tk.Label(caja, text="ARCHIVO ACTIVO", bg=LATERAL_HOVER, fg=LATERAL_TENUE, font=fuente(8, True)).pack(
            anchor="w", padx=px(14), pady=(px(12), 0))
        self.lbl_lat_archivo = tk.Label(caja, text="Ninguno", bg=LATERAL_HOVER, fg="white", font=fuente(10, True),
                                        anchor="w", justify="left", wraplength=px(200))
        self.lbl_lat_archivo.pack(fill="x", padx=px(14))
        self.lbl_lat_detalle = tk.Label(caja, text="Carga un archivo para empezar", bg=LATERAL_HOVER,
                                        fg="#94a3b8", font=fuente(9), anchor="w")
        self.lbl_lat_detalle.pack(fill="x", padx=px(14), pady=(0, px(12)))

    def _cabecera(self, padre):
        cab = tk.Frame(padre, bg=FONDO)
        cab.grid(row=0, column=0, sticky="ew", padx=px(28), pady=(px(22), px(16)))
        cab.columnconfigure(0, weight=1)
        self.lbl_titulo = tk.Label(cab, text="", bg=FONDO, fg=TEXTO, font=fuente(20, True))
        self.lbl_titulo.grid(row=0, column=0, sticky="w")
        self.lbl_desc = tk.Label(cab, text="", bg=FONDO, fg=TEXTO_2, font=fuente(10))
        self.lbl_desc.grid(row=1, column=0, sticky="w")
        self.pastilla = tk.Label(cab, text="", bg="white", fg=TEXTO_2, font=fuente(9.5, True), padx=px(14),
                                 pady=px(7), highlightthickness=1, highlightbackground=BORDE)
        self.pastilla.grid(row=0, column=1, rowspan=2, sticky="e")

    def _barra_estado(self, padre):
        barra = tk.Frame(padre, bg="white", highlightthickness=1, highlightbackground=BORDE)
        barra.grid(row=2, column=0, sticky="ew")
        lado = px(10)
        self.punto_estado = tk.Canvas(barra, width=lado, height=lado, bg="white", highlightthickness=0)
        self.punto_estado.pack(side="left", padx=(px(28), px(8)), pady=px(12))
        self.lbl_estado = tk.Label(barra, text="", bg="white", fg=TEXTO_2, anchor="w", font=fuente(9.5))
        self.lbl_estado.pack(side="left", fill="x", expand=True)
        self.btn_cancelar = Boton(barra, "Cancelar", self._pedir_cancelar, "peligro", pequeno=True)
        self.barra = ttk.Progressbar(barra, length=px(220), mode="determinate",
                                     style="Delgada.Horizontal.TProgressbar")

    def _estado(self, texto, tipo="neutro"):
        color = {"ok": OK_VIVO, "error": "#ef4444", "aviso": "#f59e0b", "info": PRIMARIO,
                 "neutro": TEXTO_3}[tipo]
        lado = int(self.punto_estado.cget("width"))
        self.punto_estado.delete("all")
        self.punto_estado.create_oval(0, 0, lado, lado, fill=color, outline="")
        self.lbl_estado.config(text=texto, fg=TEXTO if tipo != "neutro" else TEXTO_2)

    def mostrar(self, clave):
        self.paginas[clave].tkraise()
        self.pagina_actual = clave
        titulo, desc = PAGINAS[clave]
        self.lbl_titulo.config(text=titulo)
        self.lbl_desc.config(text=desc)
        for c, elem in self.menu.items():
            elem.poner(activo=(c == clave))
        if clave == "reporte":
            self._refrescar_proceso()

    def _nueva_pagina(self, clave, ancho_izq=340):
        p = tk.Frame(self.contenedor, bg=FONDO)
        p.grid(row=0, column=0, sticky="nsew")
        p.columnconfigure(1 if ancho_izq else 0, weight=1)
        p.rowconfigure(0, weight=1)
        self.paginas[clave] = p
        izq = None
        if ancho_izq:
            col = ColumnaDesplazable(p, px(ancho_izq))
            col.grid(row=0, column=0, sticky="nsw", padx=(0, px(20)))
            izq = col.interior
        panel = PanelDesplazable(p)
        panel.grid(row=0, column=1 if ancho_izq else 0, columnspan=1 if ancho_izq else 2, sticky="nsew")
        der = panel.interior
        der.columnconfigure(0, weight=1)
        return izq, der

    def _boton(self, padre, texto, comando, tipo="primario", **kw):
        b = Boton(padre, texto, comando, tipo, **kw)
        self.botones.append(b)
        return b

    # ------------------------------------------------------------------
    # Procesos largos: progreso, cancelacion y bloqueo de botones
    # ------------------------------------------------------------------
    def _iniciar_proceso(self, texto):
        self.ocupado = True
        self.cancelar = False
        self.pausa = 0.0
        self.ultimo_refresco = 0.0
        for b in self.botones:
            b.habilitar(False)
        self.barra["value"] = 0
        self.btn_cancelar.pack(side="right", padx=(px(8), px(20)), pady=px(6))
        self.barra.pack(side="right", padx=px(8))
        self._estado(texto, "info")
        self.config(cursor="watch")
        self.update()

    def _terminar_proceso(self):
        self.ocupado = False
        for b in self.botones:
            b.habilitar(True)
        self.btn_cancelar.pack_forget()
        self.barra.pack_forget()
        self.config(cursor="")
        self._refrescar_proceso()
        if self.cerrar_pendiente:
            self.after_idle(self.destroy)                 # se cierra cuando termine de actualizar la pantalla

    def _progreso(self, hechos, total):
        """Se llama desde los algoritmos. Refresca la ventana como maximo cada
        80 ms; el tiempo que se pasa refrescando NO se cuenta en la medicion."""
        if self.cancelar:
            raise Cancelado()
        ahora = time.perf_counter()
        if ahora - self.ultimo_refresco >= 0.08:
            self.barra["value"] = 100.0 * hechos / max(1, total)
            self.update()
            self.ultimo_refresco = time.perf_counter()
            self.pausa += self.ultimo_refresco - ahora
            if self.cancelar:
                raise Cancelado()

    def _pedir_cancelar(self):
        if self.ocupado:
            self.cancelar = True
            self._estado("Cancelando…", "aviso")

    def _al_cerrar(self):
        if self.ocupado:
            self.cancelar = True
            self.cerrar_pendiente = True
        else:
            self.update_idletasks()                       # termina dibujos pendientes de las graficas
            self.destroy()

    def _hay_datos(self):
        if not self.originales:
            messagebox.showwarning("Sin datos", "Primero carga un archivo TXT o XLSX en «Cargar datos».",
                                   parent=self)
            return False
        return True

    def _medir(self, funcion, *args, **kw):
        """Ejecuta 'funcion' y regresa (resultado, segundos) sin contar el
        tiempo usado para refrescar la ventana."""
        self.pausa = 0.0
        inicio = time.perf_counter()
        resultado = funcion(*args, **kw)
        segundos = time.perf_counter() - inicio - self.pausa
        return resultado, max(segundos, 0.0)

    def _ordenar(self, nombre, tipo, descendente):
        """Ordena self.originales con la libreria correspondiente."""
        if tipo == "Interno":
            funcion = oi.ALGORITMOS_INTERNOS[nombre]
            (lista, est), seg = self._medir(funcion, self.originales, descendente, self._progreso)
        else:
            (lista, est), seg = self._medir(oe.ordenar_externo, self.originales, nombre, CARPETA_TEMP,
                                            descendente, self._progreso)
        verificado = len(lista) == len(self.originales) and oi.esta_ordenada(lista, descendente)
        return {
            "lista": lista, "algoritmo": nombre, "tipo": tipo, "descendente": descendente,
            "orden": "Descendente" if descendente else "Ascendente", "segundos": seg,
            "comparaciones": est.get("comparaciones", 0), "movimientos": est.get("movimientos", 0),
            "pasadas": est.get("pasadas", 0), "verificado": verificado, "n": len(lista),
        }

    def _confirmar_cuadratico(self, nombres):
        lentos = [n for n in nombres if n in oi.CUADRATICOS]
        if lentos and len(self.originales) > LIMITE_CUADRATICO:
            return messagebox.askyesno(
                "Puede tardar",
                f"{', '.join(lentos)} es O(n²) y hay {miles(len(self.originales))} registros.\n"
                "Puede tardar varios minutos (puedes cancelar en cualquier momento).\n\n¿Continuar?",
                parent=self)
        return True

    def _registrar_historial(self, r):
        for i, h in enumerate(self.historial):
            if h["algoritmo"] == r["algoritmo"] and h["orden"] == r["orden"]:
                self.historial[i] = r
                return
        self.historial.append(r)

    # ------------------------------------------------------------------
    # Seguimiento del proceso
    # ------------------------------------------------------------------
    def _detalle_paso(self, paso):
        if paso == "cargar":
            return (f'{self.info["nombre"]} · {miles(len(self.originales))} registros' if self.info
                    else "Selecciona un archivo TXT o XLSX")
        if paso == "ordenar":
            r = self.resultado
            return (f'{r["algoritmo"]} · {r["orden"].lower()} · {ex.formato_tiempo(r["segundos"])}' if r
                    else "Ordena los datos con cualquier algoritmo")
        if paso == "buscar":
            n = len(self.busquedas)
            return f"{n} búsqueda(s) realizada(s)" if n else "Busca al menos un valor"
        if paso == "comparar":
            n = len(self.comparacion)
            return f"{n} algoritmo(s) comparados" if n else "Ejecuta la comparación de algoritmos"
        if paso == "laboratorio":
            if self.laboratorio:
                ok = sum(1 for r in self.laboratorio["recomendaciones"] if r["coincide"])
                return f'{ok} de {len(self.laboratorio["recomendaciones"])} recomendaciones comprobadas'
            return "Opcional · comprueba la tabla de recomendaciones con mediciones"
        if paso == "intercalacion":
            return (f'{miles(self.intercalacion["n"])} registros intercalados' if self.intercalacion
                    else "Opcional")
        return ""

    def _refrescar_proceso(self):
        hechos = sum(1 for p in PASOS_OBLIGATORIOS if self.hecho[p])
        listo = hechos == len(PASOS_OBLIGATORIOS)
        for paso in PASOS_OBLIGATORIOS + PASOS_OPCIONALES:
            if paso in self.menu:
                self.menu[paso].poner(hecho=self.hecho[paso])
        self.menu["reporte"].poner(hecho=False)
        if listo:
            self.pastilla.config(text="✓  Proceso completo", fg=OK, bg=OK_SUAVE, highlightbackground="#bbf7d0")
        else:
            self.pastilla.config(text=f"Proceso: {hechos} de {len(PASOS_OBLIGATORIOS)} pasos", fg=TEXTO_2,
                                 bg="white", highlightbackground=BORDE)
        if not hasattr(self, "filas_proceso"):
            return
        for paso, (circulo, detalle) in self.filas_proceso.items():
            hecho = self.hecho[paso]
            lado = int(circulo.cget("width"))
            circulo.delete("all")
            if hecho:
                circulo.create_oval(1, 1, lado - 1, lado - 1, fill=OK_VIVO, outline="")
                circulo.create_text(lado / 2, lado / 2, text="✓", fill="white", font=fuente(10, True))
            else:
                circulo.create_oval(1, 1, lado - 1, lado - 1, outline=BORDE_FUERTE, width=1.5, fill="white")
            detalle.config(text=self._detalle_paso(paso), fg=TEXTO_2 if hecho else TEXTO_3)
        if not self.ocupado:
            self.btn_pdf.habilitar(listo and HAY_MATPLOTLIB)
            self.btn_guardar_datos.habilitar(self.resultado is not None)
        faltan = [PAGINAS[p][0] for p in PASOS_OBLIGATORIOS if not self.hecho[p]]
        if listo:
            self.aviso_reporte.poner("ok", "Todo listo para el reporte final",
                                     "Se completaron los 4 pasos del proceso. Genera el PDF cuando quieras.")
        else:
            self.aviso_reporte.poner("aviso", "El reporte se habilita al terminar el proceso",
                                     "Pasos pendientes: " + ", ".join(faltan) + ".")

    # ==================================================================
    # 1. CARGAR DATOS (requerimiento A)
    # ==================================================================
    def _pagina_cargar(self):
        izq, der = self._nueva_pagina("cargar")
        t = Tarjeta(izq, "Origen de datos", "Formatos permitidos: TXT y XLSX, con un número entero por "
                                            "línea o por celda.")
        t.pack(fill="x")
        self._boton(t.cuerpo, "Seleccionar archivo…", self._abrir_archivo, grande=True).pack(fill="x")
        tk.Label(t.cuerpo, text="Atajo: Ctrl + O", bg=TARJETA, fg=TEXTO_3, font=fuente(8.5)).pack(
            anchor="w", pady=(px(4), 0))
        etiqueta_seccion(t.cuerpo, "El archivo debe cumplir", arriba=16)
        for requisito in ("Formato .txt o .xlsx (Excel).",
                          "Solo números enteros: uno por línea en TXT, uno por celda en XLSX.",
                          "En Excel puede tener un encabezado en la primera fila (p. ej. «Numero»).",
                          "Sin decimales, letras ni fórmulas. Se indica la línea o celda exacta si algo falla.",
                          f"Hasta {ar.MAX_REGISTROS:,} números y {ar.MAX_BYTES // 1048576} MB.",
                          "El examen pide probar uno de 1,000 y uno de 5,000 números."):
            fila = tk.Frame(t.cuerpo, bg=TARJETA)
            fila.pack(fill="x", pady=px(2))
            tk.Label(fila, text="✓", bg=TARJETA, fg=OK, font=fuente(10, True)).pack(side="left", anchor="n")
            l = tk.Label(fila, text=requisito, bg=TARJETA, fg=TEXTO_2, font=fuente(9), justify="left", anchor="w")
            l.pack(side="left", fill="x", expand=True, padx=(px(8), 0))
            ajustar_ancho_texto(l, 150)

        t2 = Tarjeta(izq, "Detalles del archivo")
        t2.pack(fill="x", pady=(px(16), 0))
        self.ficha_carga = FichaDatos(t2.cuerpo, ["Archivo", "Formato", "Hoja / encabezado", "Tamaño",
                                                  "Caso del examen", "Estado inicial", "Lectura y validación"],
                                      ancho_valor=170)
        self.ficha_carga.pack(fill="x")

        der.rowconfigure(1, weight=1, minsize=px(300))
        self.kpi_carga = Indicadores(der, ["Registros", "Mínimo", "Máximo", "Distintos", "Repetidos"])
        self.kpi_carga.grid(row=0, column=0, sticky="ew", pady=(0, px(16)))
        tg = Tarjeta(der, "Distribución de los datos", "Cada punto es un número: su posición en el archivo "
                                                      "y su valor.")
        tg.grid(row=1, column=0, sticky="nsew")
        self.graf_carga = Grafica(tg.cuerpo, 7, 2.8)
        self.graf_carga.pack(fill="both", expand=True)
        self.graf_carga.dibujar(gr.dibujar_datos, [])
        tv = Tarjeta(der, "Datos originales")
        tv.grid(row=2, column=0, sticky="ew", pady=(px(16), 0))
        fila = tk.Frame(tv.cuerpo, bg=TARJETA)
        fila.pack(fill="x")
        fila.columnconfigure(0, weight=1)
        fila.columnconfigure(1, weight=1)
        self.tabla_carga_ini = self._tabla_valores(fila, "Primeros 20", 0)
        self.tabla_carga_fin = self._tabla_valores(fila, "Últimos 20", 1)

    def _tabla_valores(self, padre, titulo, columna, alto=6):
        marco = tk.Frame(padre, bg=TARJETA)
        marco.grid(row=0, column=columna, sticky="nsew", padx=(0 if columna == 0 else px(8), 0))
        tk.Label(marco, text=titulo.upper(), bg=TARJETA, fg=TEXTO_3, font=fuente(8, True)).pack(
            anchor="w", pady=(0, px(6)))
        arbol = crear_tabla(marco, [("pos", "Posición", 90, "e"), ("valor", "Valor", 110, "e")], alto)
        arbol.marco.pack(fill="both", expand=True)
        return arbol

    def _abrir_archivo(self):
        if self.ocupado:
            return
        carpeta = self.ultima_carpeta
        if not carpeta or not os.path.isdir(carpeta):
            carpeta = CARPETA_INICIAL if os.path.isdir(CARPETA_INICIAL) else os.path.expanduser("~")
        ruta = filedialog.askopenfilename(
            parent=self, title="Selecciona tu archivo de números enteros (TXT o XLSX)", initialdir=carpeta,
            filetypes=[("Archivos de datos", "*.txt *.xlsx"), ("Texto", "*.txt"), ("Excel", "*.xlsx")])
        if ruta:
            self.ultima_carpeta = os.path.dirname(ruta)
            self._cargar(ruta)

    def _cargar(self, ruta):
        if self.ocupado:
            return
        self._iniciar_proceso(f"Leyendo {os.path.basename(ruta)}…")
        try:
            info, seg = self._medir(ar.leer_archivo, ruta)
        except ar.ErrorArchivo as e:
            self._terminar_proceso()
            self._estado("No se pudo cargar el archivo.", "error")
            messagebox.showerror("Archivo no válido", str(e), parent=self)
            return
        except Exception as e:
            self._terminar_proceso()
            self._estado("Error inesperado al leer el archivo.", "error")
            messagebox.showerror("Error inesperado", f"No se pudo leer el archivo:\n{type(e).__name__}: {e}",
                                 parent=self)
            return

        datos = info["datos"]
        self.info = info
        self.originales = datos
        self.resultado = None
        self.historial = []
        self.busquedas = []
        self.comparacion_busquedas = None
        self.comparacion = []
        self.tabla_hash = None
        self.lista_hash = None

        menor = mayor = datos[0]
        for v in datos:
            if v < menor:
                menor = v
            if v > mayor:
                mayor = v
        distintos = 0
        for cubeta in bq.construir_tabla_hash(datos)["tabla"]:
            distintos += len(cubeta)
        if oi.esta_ordenada(datos):
            estado = "Ya viene en orden ascendente"
        elif oi.esta_ordenada(datos, True):
            estado = "Ya viene en orden descendente"
        else:
            estado = "Desordenado"
        extra = []
        if info["hoja"]:
            extra.append(f'hoja «{info["hoja"]}»')
        if info["encabezado"]:
            extra.append(f'encabezado «{info["encabezado"]}» omitido')
        detalle_hoja = ", ".join(extra) if extra else "Sin encabezado"
        self.stats = {"nombre": info["nombre"], "formato": info["formato"], "bytes": info["bytes"],
                      "detalle_hoja": detalle_hoja, "n": len(datos), "minimo": menor, "maximo": mayor,
                      "distintos": distintos, "repetidos": len(datos) - distintos, "estado_inicial": estado,
                      "segundos_lectura": seg}

        f = self.ficha_carga
        f.poner("Archivo", info["nombre"])
        f.poner("Formato", info["formato"])
        f.poner("Hoja / encabezado", detalle_hoja)
        f.poner("Tamaño", f'{info["bytes"] / 1024:,.1f} KB')
        if len(datos) in (1000, 5000):
            f.poner("Caso del examen", f"✓ Archivo de {miles(len(datos))} enteros", OK)
        else:
            f.poner("Caso del examen", f"{miles(len(datos))} enteros (también válido)", TEXTO)
        f.poner("Estado inicial", estado)
        f.poner("Lectura y validación", ex.formato_tiempo(seg))
        k = self.kpi_carga
        k.poner("Registros", miles(len(datos)), PRIMARIO)
        k.poner("Mínimo", miles(menor))
        k.poner("Máximo", miles(mayor))
        k.poner("Distintos", miles(distintos))
        k.poner("Repetidos", miles(len(datos) - distintos))
        llenar_tabla(self.tabla_carga_ini, filas_valores(datos[:20], 0))
        ult = datos[-20:] if len(datos) > 20 else []
        llenar_tabla(self.tabla_carga_fin, filas_valores(ult, len(datos) - len(ult)))
        self.graf_carga.dibujar(gr.dibujar_datos, datos)
        self.lbl_lat_archivo.config(text=info["nombre"])
        self.lbl_lat_detalle.config(text=f'{info["formato"]} · {miles(len(datos))} registros')
        self._limpiar_resultados()
        self.hecho.update({"cargar": True, "ordenar": False, "buscar": False, "comparar": False,
                           "laboratorio": False})
        self.laboratorio = None
        self._limpiar_laboratorio()
        self._terminar_proceso()
        self._estado(f'Archivo cargado: {info["nombre"]} ({miles(len(datos))} enteros) en '
                     f'{ex.formato_tiempo(seg)}. Siguiente paso: Ordenar.', "ok")

    def _limpiar_resultados(self):
        self.kpi_orden.limpiar()
        self.kpi_orden.poner("Total de registros", miles(len(self.originales)))
        llenar_tabla(self.tabla_ord_ini, [])
        llenar_tabla(self.tabla_ord_fin, [])
        self.graf_orden.dibujar(gr.dibujar_antes_despues, [], [])
        self.kpi_busqueda.limpiar()
        self.aviso_busqueda.poner("neutro", "Sin búsquedas todavía", "Escribe un valor y presiona Buscar.")
        self._poner_posiciones("—")
        llenar_tabla(self.tabla_historial, [])
        self.graf_busq.dibujar(gr.dibujar_busquedas, [])
        self._actualizar_fuente_busqueda()
        llenar_tabla(self.tabla_comp, [])
        self.graf_comp.dibujar(gr.dibujar_comparacion, [])

    # ==================================================================
    # 2. ORDENAR (requerimientos B y D)
    # ==================================================================
    def _pagina_ordenar(self):
        izq, der = self._nueva_pagina("ordenar")
        t = Tarjeta(izq, "Configuración")
        t.pack(fill="x")
        c = t.cuerpo
        etiqueta_seccion(c, "Tipo de procesamiento", arriba=0)
        self.var_tipo = tk.StringVar(value="Interno")
        Segmentado(c, [("Interno", "Interno · memoria"), ("Externo", "Externo · archivos")], self.var_tipo,
                   self._cambio_tipo).pack(fill="x")
        etiqueta_seccion(c, "Algoritmo")
        self.var_algoritmo = tk.StringVar(value="QuickSort")
        self.lista_alg = ListaOpciones(c, self.var_algoritmo, self._describir_algoritmo, compacta=True)
        self.lista_alg.pack(fill="x")
        etiqueta_seccion(c, "Orden")
        self.var_orden = tk.StringVar(value="asc")
        Segmentado(c, [("asc", "Ascendente ↑"), ("desc", "Descendente ↓")], self.var_orden).pack(fill="x")
        self.lbl_desc_alg = tk.Label(c, text="", bg="#f8fafc", fg=TEXTO_2, font=fuente(9), justify="left",
                                     anchor="w", wraplength=px(280), padx=px(12), pady=px(10))
        self.lbl_desc_alg.pack(fill="x", pady=(px(16), px(16)))
        self._boton(c, "Ordenar datos", self._accion_ordenar, grande=True).pack(fill="x")
        self._cambio_tipo()

        der.rowconfigure(1, weight=1, minsize=px(320))
        self.kpi_orden = Indicadores(der, ["Algoritmo", "Tiempo de ejecución", "Comparaciones", "Movimientos",
                                           "Total de registros", "Verificación"])
        self.kpi_orden.grid(row=0, column=0, sticky="ew", pady=(0, px(16)))
        tg = Tarjeta(der, "Evidencia del ordenamiento", "Los mismos datos antes y después: ordenados forman una "
                                                       "curva continua.")
        tg.grid(row=1, column=0, sticky="nsew")
        self.graf_orden = Grafica(tg.cuerpo, 7, 2.8)
        self.graf_orden.pack(fill="both", expand=True)
        self.graf_orden.dibujar(gr.dibujar_antes_despues, [], [])
        tv = Tarjeta(der, "Resultado ordenado")
        tv.grid(row=2, column=0, sticky="ew", pady=(px(16), 0))
        fila = tk.Frame(tv.cuerpo, bg=TARJETA)
        fila.pack(fill="x")
        fila.columnconfigure(0, weight=1)
        fila.columnconfigure(1, weight=1)
        self.tabla_ord_ini = self._tabla_valores(fila, "Primeros 20 elementos", 0)
        self.tabla_ord_fin = self._tabla_valores(fila, "Últimos 20 elementos", 1)

    def _cambio_tipo(self):
        if self.var_tipo.get() == "Interno":
            nombres = list(oi.ALGORITMOS_INTERNOS.keys())
            defecto = "QuickSort"
        else:
            nombres = list(oe.ALGORITMOS_EXTERNOS.keys())
            defecto = "Mezcla Equilibrada"
        self.lista_alg.poner_opciones([(n, n, COMPLEJIDAD_CORTA[n]) for n in nombres])
        if self.var_algoritmo.get() not in nombres:
            self.var_algoritmo.set(defecto)
        self._describir_algoritmo()

    def _describir_algoritmo(self):
        self.lbl_desc_alg.config(text=DESCRIPCIONES.get(self.var_algoritmo.get(), ""))

    def _accion_ordenar(self):
        if self.ocupado or not self._hay_datos():
            return
        nombre = self.var_algoritmo.get()
        tipo = self.var_tipo.get()
        catalogo = oi.ALGORITMOS_INTERNOS if tipo == "Interno" else oe.ALGORITMOS_EXTERNOS
        if nombre not in catalogo:
            messagebox.showerror("Algoritmo no válido", "Selecciona un algoritmo de la lista.", parent=self)
            return
        if not self._confirmar_cuadratico([nombre]):
            return
        descendente = self.var_orden.get() == "desc"
        self._iniciar_proceso(f"Ordenando {miles(len(self.originales))} registros con {nombre}…")
        try:
            r = self._ordenar(nombre, tipo, descendente)
        except Cancelado:
            self._terminar_proceso()
            self._estado("Ordenamiento cancelado. Los datos no se modificaron.", "aviso")
            return
        except (OSError, oe.ErrorOrdenExterno) as e:
            self._terminar_proceso()
            self._estado("Error al ordenar.", "error")
            messagebox.showerror("Error", f"No se pudo completar el ordenamiento externo:\n{e}", parent=self)
            return
        except Exception as e:
            self._terminar_proceso()
            self._estado("Error inesperado al ordenar.", "error")
            messagebox.showerror("Error inesperado", f"{type(e).__name__}: {e}", parent=self)
            return
        self.resultado = r
        self._registrar_historial(r)
        self._mostrar_resultado(r)
        self.hecho["ordenar"] = True
        self._terminar_proceso()
        self._estado(f'{nombre} ordenó {miles(r["n"])} registros en {ex.formato_tiempo(r["segundos"])}. '
                     "Siguiente paso: Buscar.", "ok")

    def _mostrar_resultado(self, r):
        k = self.kpi_orden
        k.poner("Algoritmo", r["algoritmo"], PRIMARIO)
        k.poner("Tiempo de ejecución", ex.formato_tiempo(r["segundos"]))
        k.poner("Comparaciones", miles(r["comparaciones"]))
        k.poner("Movimientos", miles(r["movimientos"]))
        k.poner("Total de registros", miles(r["n"]))
        if r["verificado"]:
            k.poner("Verificación", "✓ Ordenado", OK)
        else:
            k.poner("Verificación", "✗ Error", ERROR)
        lista = r["lista"]
        llenar_tabla(self.tabla_ord_ini, filas_valores(lista[:20], 0))
        ult = lista[-20:] if len(lista) > 20 else []
        llenar_tabla(self.tabla_ord_fin, filas_valores(ult, len(lista) - len(ult)))
        self.graf_orden.dibujar(gr.dibujar_antes_despues, self.originales, lista)
        self._actualizar_fuente_busqueda()

    # ==================================================================
    # 3. BUSCAR (requerimiento C)
    # ==================================================================
    def _pagina_buscar(self):
        izq, der = self._nueva_pagina("buscar")
        t = Tarjeta(izq, "Buscar un valor")
        t.pack(fill="x")
        c = t.cuerpo
        etiqueta_seccion(c, "Valor entero", arriba=0)
        caja = tk.Frame(c, bg="white", highlightthickness=1, highlightbackground=BORDE_FUERTE)
        caja.pack(fill="x")
        validar = (self.register(val.caracter_permitido_busqueda), "%P")
        self.var_buscar = tk.StringVar()
        self.ent_buscar = tk.Entry(caja, textvariable=self.var_buscar, font=(MONO, 16), relief="flat", bd=0,
                                   bg="white", fg=TEXTO, insertbackground=TEXTO, validate="key",
                                   validatecommand=validar)
        self.ent_buscar.pack(fill="x", padx=px(12), pady=px(9))
        self.ent_buscar.bind("<Return>", lambda e: self._accion_buscar())
        self.ent_buscar.bind("<FocusIn>", lambda e: caja.config(highlightbackground=PRIMARIO))
        self.ent_buscar.bind("<FocusOut>", lambda e: caja.config(highlightbackground=BORDE_FUERTE))
        tk.Label(c, text=f"Solo dígitos y un signo opcional · máximo {val.MAX_DIGITOS} dígitos", bg=TARJETA,
                 fg=TEXTO_3, font=fuente(8.5)).pack(anchor="w", pady=(px(4), 0))

        etiqueta_seccion(c, "Método de búsqueda")
        self.var_metodo = tk.StringVar(value="Binaria")
        lista = ListaOpciones(c, self.var_metodo, compacta=True)
        lista.poner_opciones([("Secuencial", "Secuencial", "O(n) · no requiere orden"),
                              ("Binaria", "Binaria", "O(log n) · requiere datos ordenados"),
                              ("Hash", "Hash", "O(1) promedio · tabla hash propia")])
        lista.pack(fill="x")
        etiqueta_seccion(c, "Buscar en")
        self.var_fuente = tk.StringVar(value="ordenados")
        Segmentado(c, [("ordenados", "Datos ordenados"), ("originales", "Datos originales")], self.var_fuente,
                   self._actualizar_fuente_busqueda).pack(fill="x")
        self.lbl_fuente = tk.Label(c, text="", bg=TARJETA, fg=TEXTO_2, font=fuente(8.5), justify="left",
                                   anchor="w", wraplength=px(290))
        self.lbl_fuente.pack(fill="x", pady=(px(6), px(16)))
        self._boton(c, "Buscar", self._accion_buscar, grande=True).pack(fill="x")
        self._boton(c, "Comparar los 3 métodos", self._accion_comparar_busquedas, "secundario").pack(
            fill="x", pady=(px(8), 0))

        der.rowconfigure(3, weight=1, minsize=px(300))
        self.aviso_busqueda = Aviso(der)
        self.aviso_busqueda.grid(row=0, column=0, sticky="ew", pady=(0, px(16)))
        self.aviso_busqueda.poner("neutro", "Sin búsquedas todavía", "Escribe un valor y presiona Buscar.")
        self.kpi_busqueda = Indicadores(der, ["Método", "Apariciones", "Comparaciones", "Tiempo"])
        self.kpi_busqueda.grid(row=1, column=0, sticky="ew", pady=(0, px(16)))
        tp = Tarjeta(der, "Posiciones donde aparece (contando desde 1)")
        tp.grid(row=2, column=0, sticky="ew", pady=(0, px(16)))
        self.txt_posiciones = tk.Text(tp.cuerpo, height=2, font=(MONO, 10), relief="flat", bg="#f8fafc",
                                      fg=TEXTO, wrap="word", padx=px(10), pady=px(8))
        self.txt_posiciones.pack(fill="x")
        self._poner_posiciones("—")

        abajo = tk.Frame(der, bg=FONDO)
        abajo.grid(row=3, column=0, sticky="nsew")
        abajo.columnconfigure(0, weight=1)
        abajo.columnconfigure(1, weight=1)
        abajo.rowconfigure(0, weight=1)
        tg = Tarjeta(abajo, "Comparaciones por método", "Mismo valor buscado con los 3 métodos.")
        tg.grid(row=0, column=0, sticky="nsew", padx=(0, px(8)))
        self.graf_busq = Grafica(tg.cuerpo, 5, 2.2)
        self.graf_busq.pack(fill="both", expand=True)
        self.graf_busq.dibujar(gr.dibujar_busquedas, [])
        th = Tarjeta(abajo, "Historial de búsquedas")
        th.grid(row=0, column=1, sticky="nsew", padx=(px(8), 0))
        self.tabla_historial = crear_tabla(th.cuerpo, [("valor", "Valor", 75, "e"), ("met", "Método", 90, "w"),
                                                       ("res", "Resultado", 120, "w"),
                                                       ("comp", "Comparaciones", 115, "e")], alto=5)
        self.tabla_historial.marco.pack(fill="both", expand=True)

    def _poner_posiciones(self, texto):
        self.txt_posiciones.config(state="normal")
        self.txt_posiciones.delete("1.0", "end")
        self.txt_posiciones.insert("1.0", texto)
        self.txt_posiciones.config(state="disabled")

    def _lista_busqueda(self):
        """Regresa (lista, descripcion, descendente_o_None)."""
        if self.var_fuente.get() == "ordenados":
            if self.resultado is None:
                return None, "Aún no has ordenado los datos.", None
            r = self.resultado
            return r["lista"], f'datos ordenados con {r["algoritmo"]} ({r["orden"].lower()})', r["descendente"]
        if oi.esta_ordenada(self.originales):
            return self.originales, "datos originales (vienen en orden ascendente)", False
        if oi.esta_ordenada(self.originales, True):
            return self.originales, "datos originales (vienen en orden descendente)", True
        return self.originales, "datos originales (desordenados)", None

    def _actualizar_fuente_busqueda(self):
        if not hasattr(self, "lbl_fuente"):
            return
        if not self.originales:
            self.lbl_fuente.config(text="Carga un archivo para poder buscar.", fg=TEXTO_3)
            return
        lista, desc, orden = self._lista_busqueda()
        if lista is None:
            self.lbl_fuente.config(text="Aún no has ordenado los datos. Ordénalos primero o elige «Datos "
                                        "originales».", fg=AVISO)
        elif orden is None:
            self.lbl_fuente.config(text=f"Buscando en {desc}. La búsqueda binaria no aplica porque no están "
                                        "ordenados.", fg=AVISO)
        else:
            self.lbl_fuente.config(text=f"Buscando en {desc}.", fg=TEXTO_2)

    def _leer_valor_busqueda(self):
        try:
            return val.convertir_entero(self.var_buscar.get(), "El valor a buscar")
        except val.ErrorEntrada as e:
            messagebox.showwarning("Valor no válido", str(e), parent=self)
            self.ent_buscar.focus_set()
            return None

    def _ejecutar_busqueda(self, metodo, lista, objetivo, descendente):
        """Regresa (posiciones, comparaciones, segundos, texto_hash)."""
        texto_hash = ""
        if metodo == "Secuencial":
            (pos, comp), seg = self._medir(bq.busqueda_secuencial, lista, objetivo)
        elif metodo == "Binaria":
            (pos, comp), seg = self._medir(bq.busqueda_binaria, lista, objetivo, descendente)
        else:
            if self.lista_hash is not lista:
                self.tabla_hash, self.seg_tabla = self._medir(bq.construir_tabla_hash, lista)
                self.lista_hash = lista
                construida = "Tabla hash recién construida"
            else:
                construida = "Tabla hash reutilizada"
            th = self.tabla_hash
            texto_hash = (f' · {construida}: {miles(th["tamano"])} cubetas, {miles(th["colisiones"])} '
                          f'colisiones, construcción {ex.formato_tiempo(self.seg_tabla)}')
            (pos, comp), seg = self._medir(bq.busqueda_hash, th, objetivo)
        return pos, comp, seg, texto_hash

    def _registrar_busqueda(self, objetivo, metodo, desc, pos, comp, seg):
        self.busquedas.append({"valor": objetivo, "metodo": metodo, "fuente": desc, "encontrado": bool(pos),
                               "apariciones": len(pos), "comparaciones": comp, "segundos": seg})
        filas = []
        for b in self.busquedas[::-1][:50]:
            filas.append((miles(b["valor"]), b["metodo"], "✓ Encontrado" if b["encontrado"] else "✗ No está",
                          miles(b["comparaciones"])))
        llenar_tabla(self.tabla_historial, filas)
        self.hecho["buscar"] = True
        self._refrescar_proceso()

    def _validar_busqueda(self, metodo):
        """Regresa (objetivo, lista, desc, orden) o None si no se puede buscar."""
        if self.ocupado or not self._hay_datos():
            return None
        objetivo = self._leer_valor_busqueda()
        if objetivo is None:
            return None
        lista, desc, orden = self._lista_busqueda()
        if lista is None:
            messagebox.showinfo("Primero ordena", "Elegiste buscar en los datos ordenados, pero aún no los has "
                                                  "ordenado. Ordénalos en «Ordenar» o elige «Datos originales».",
                                parent=self)
            return None
        if metodo == "Binaria" and orden is None:
            messagebox.showwarning("Búsqueda binaria no aplicable",
                                   "La búsqueda binaria SOLO funciona con datos ordenados y estos datos están "
                                   "desordenados (daría resultados incorrectos).\n\nOrdénalos primero o usa "
                                   "la búsqueda secuencial o hash.", parent=self)
            return None
        return objetivo, lista, desc, orden

    def _accion_buscar(self):
        metodo = self.var_metodo.get()
        datos = self._validar_busqueda(metodo)
        if datos is None:
            return
        objetivo, lista, desc, orden = datos
        pos, comp, seg, texto_hash = self._ejecutar_busqueda(metodo, lista, objetivo, orden)
        if pos:
            self.aviso_busqueda.poner("ok", f"{miles(objetivo)} se encontró {miles(len(pos))} "
                                            f"{'vez' if len(pos) == 1 else 'veces'}",
                                      f"Búsqueda {metodo.lower()} en {desc}{texto_hash}")
        else:
            self.aviso_busqueda.poner("error", f"{miles(objetivo)} no está en los datos",
                                      f"Búsqueda {metodo.lower()} en {desc}{texto_hash}")
        k = self.kpi_busqueda
        k.poner("Método", metodo, PRIMARIO)
        k.poner("Apariciones", miles(len(pos)))
        k.poner("Comparaciones", miles(comp))
        k.poner("Tiempo", ex.formato_tiempo(seg))
        if pos:
            muestra = ", ".join(miles(p + 1) for p in pos[:80])
            if len(pos) > 80:
                muestra += f" … (+{miles(len(pos) - 80)} más)"
            self._poner_posiciones(muestra)
        else:
            self._poner_posiciones("—")
        self._registrar_busqueda(objetivo, metodo, desc, pos, comp, seg)
        self._estado(f"Búsqueda {metodo.lower()} de {miles(objetivo)}: "
                     f"{'encontrado' if pos else 'no encontrado'} con {miles(comp)} comparaciones.",
                     "ok" if pos else "neutro")

    def _accion_comparar_busquedas(self):
        datos = self._validar_busqueda("Binaria")
        if datos is None:
            return
        objetivo, lista, desc, orden = datos
        filas = []
        for m in bq.NOMBRES:
            pos, comp, seg, _ = self._ejecutar_busqueda(m, lista, objetivo, orden)
            filas.append((m, comp, seg, len(pos)))
            self._registrar_busqueda(objetivo, m, desc, pos, comp, seg)
        self.comparacion_busquedas = {"valor": objetivo, "filas": filas}
        self.graf_busq.dibujar(gr.dibujar_busquedas, filas)
        texto = "  ·  ".join(f"{m}: {miles(c)}" for m, c, s, _ in filas)
        encontrado = filas[0][3] > 0
        self.aviso_busqueda.poner("info", f"Comparación de métodos para {miles(objetivo)}",
                                  f"Comparaciones → {texto}. "
                                  f"{'Encontrado' if encontrado else 'No encontrado'} en {desc}.")
        self._estado(f"Comparación de búsquedas para {miles(objetivo)} → {texto}", "ok")

    # ==================================================================
    # 4. COMPARAR (requerimiento 6)
    # ==================================================================
    def _pagina_comparar(self):
        izq, der = self._nueva_pagina("comparar")
        t = Tarjeta(izq, "Algoritmos a comparar", "Todos ordenan los mismos datos en el mismo orden.")
        t.pack(fill="x")
        c = t.cuerpo
        self.vars_comp = {}
        for titulo, catalogo, tipo in (("Internos", oi.ALGORITMOS_INTERNOS, "Interno"),
                                       ("Externos", oe.ALGORITMOS_EXTERNOS, "Externo")):
            etiqueta_seccion(c, titulo, arriba=0 if tipo == "Interno" else 14)
            rejilla = tk.Frame(c, bg=TARJETA)
            rejilla.pack(fill="x")
            rejilla.columnconfigure(0, weight=1, uniform="chip")
            rejilla.columnconfigure(1, weight=1, uniform="chip")
            for i, nombre in enumerate(catalogo):
                v = tk.BooleanVar(value=True)
                Chip(rejilla, nombre, v).grid(row=i // 2, column=i % 2, sticky="ew",
                                              padx=(0 if i % 2 == 0 else px(6), 0), pady=(0, px(6)))
                self.vars_comp[nombre] = (v, tipo)
        fila = tk.Frame(c, bg=TARJETA)
        fila.pack(fill="x", pady=(px(4), 0))
        Boton(fila, "Todos", lambda: [v.set(True) for v, _ in self.vars_comp.values()], "suave",
              pequeno=True).pack(side="left")
        Boton(fila, "Solo rápidos", self._solo_rapidos, "suave", pequeno=True).pack(side="left", padx=px(6))
        Boton(fila, "Ninguno", lambda: [v.set(False) for v, _ in self.vars_comp.values()], "suave",
              pequeno=True).pack(side="left")
        etiqueta_seccion(c, "Orden")
        self.var_orden_comp = tk.StringVar(value="asc")
        Segmentado(c, [("asc", "Ascendente ↑"), ("desc", "Descendente ↓")], self.var_orden_comp).pack(fill="x")
        tk.Frame(c, bg=TARJETA, height=px(16)).pack()
        self._boton(c, "Ejecutar comparación", self._accion_comparar, grande=True).pack(fill="x")

        der.rowconfigure(0, weight=1, minsize=px(380))
        der.columnconfigure(0, weight=1, uniform="comp")
        der.columnconfigure(1, weight=1, uniform="comp")
        tg = Tarjeta(der, "Tiempo de ejecución", "Azul: interno · naranja: externo. Más arriba = más rápido.")
        tg.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.graf_comp = Grafica(tg.cuerpo, 7, 3.2)
        self.graf_comp.pack(fill="both", expand=True)
        self.graf_comp.dibujar(gr.dibujar_comparacion, [])
        tt = Tarjeta(der, "Resultados")
        tt.grid(row=1, column=0, sticky="nsew", padx=(0, px(8)), pady=(px(16), 0))
        self.tabla_comp = crear_tabla(tt.cuerpo, [("alg", "Algoritmo", 140, "w"), ("t", "Tiempo", 95, "e"),
                                                  ("c", "Comparaciones", 115, "e"), ("ok", "✓", 30, "center")],
                                      alto=9)
        self.tabla_comp.marco.pack(fill="both", expand=True)

        tr = Tarjeta(der, "Algoritmo recomendado por escenario", "Selecciona un escenario para ver el motivo.")
        tr.grid(row=1, column=1, sticky="nsew", padx=(px(8), 0), pady=(px(16), 0))
        arbol = crear_tabla(tr.cuerpo, [("esc", "Escenario", 190, "w"), ("alg", "Recomendado", 160, "w")], alto=5)
        llenar_tabla(arbol, [(e, a) for e, a, _ in RECOMENDACIONES])
        arbol.marco.pack(fill="x")
        self.lbl_motivo = tk.Label(tr.cuerpo, text="", bg="#f8fafc", fg=TEXTO_2, font=fuente(9.5), justify="left",
                                   anchor="nw", padx=px(14), pady=px(12))
        self.lbl_motivo.pack(fill="both", expand=True, pady=(px(10), 0))
        ajustar_ancho_texto(self.lbl_motivo)

        def ver_motivo(_e=None):
            sel = arbol.selection()
            i = arbol.index(sel[0]) if sel else 0
            e, a, m = RECOMENDACIONES[i]
            self.lbl_motivo.config(text=f"{e} → {a}\n\n{m}")
        arbol.bind("<<TreeviewSelect>>", ver_motivo)
        ver_motivo()

    def _solo_rapidos(self):
        for nombre, (v, _tipo) in self.vars_comp.items():
            v.set(nombre not in oi.CUADRATICOS)

    def _accion_comparar(self):
        if self.ocupado or not self._hay_datos():
            return
        elegidos = [(n, tipo) for n, (v, tipo) in self.vars_comp.items() if v.get()]
        if not elegidos:
            messagebox.showwarning("Nada que comparar", "Selecciona al menos un algoritmo.", parent=self)
            return
        if not self._confirmar_cuadratico([n for n, _ in elegidos]):
            return
        descendente = self.var_orden_comp.get() == "desc"
        self._iniciar_proceso("Comparando algoritmos…")
        resultados = []
        cancelado = False
        try:
            for i, (nombre, tipo) in enumerate(elegidos):
                self._estado(f"Comparando {i + 1} de {len(elegidos)}: {nombre}…", "info")
                self.update()
                r = self._ordenar(nombre, tipo, descendente)
                resultados.append(r)
                self._registrar_historial(r)
        except Cancelado:
            cancelado = True
        except Exception as e:
            cancelado = True
            messagebox.showerror("Error", f"Falló la comparación:\n{type(e).__name__}: {e}", parent=self)
        self.comparacion = resultados
        self.comparacion_orden = "Descendente" if descendente else "Ascendente"
        llenar_tabla(self.tabla_comp, [(r["algoritmo"], ex.formato_tiempo(r["segundos"]), miles(r["comparaciones"]),
                                        "✓" if r["verificado"] else "✗") for r in resultados])
        self.graf_comp.dibujar(gr.dibujar_comparacion, resultados)
        self.hecho["comparar"] = len(resultados) > 0 and not cancelado
        self._terminar_proceso()
        if cancelado:
            self._estado("Comparación interrumpida: se muestran los algoritmos que terminaron. Ejecútala completa "
                         "para marcar el paso.", "aviso")
        elif resultados:
            mejor = resultados[0]
            for r in resultados:
                if r["segundos"] < mejor["segundos"]:
                    mejor = r
            self._estado(f'Comparación lista. El más rápido fue {mejor["algoritmo"]} '
                         f'({ex.formato_tiempo(mejor["segundos"])}). Ya puedes generar el reporte final.', "ok")

    # ==================================================================
    # 5. REPORTE FINAL (requerimiento E)
    # ==================================================================
    def _pagina_reporte(self):
        izq, der = self._nueva_pagina("reporte", ancho_izq=0)
        der.columnconfigure(0, weight=3)
        der.columnconfigure(1, weight=2)
        der.rowconfigure(1, weight=1)

        self.aviso_reporte = Aviso(der)
        self.aviso_reporte.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, px(16)))

        tp = Tarjeta(der, "Progreso del proceso", "Haz clic en un paso para ir a él.")
        tp.grid(row=1, column=0, sticky="nsew", padx=(0, px(8)))
        self.filas_proceso = {}
        pasos = [("cargar", "1", "Cargar datos", True), ("ordenar", "2", "Ordenar", True),
                 ("buscar", "3", "Buscar", True), ("comparar", "4", "Comparar algoritmos", True),
                 ("laboratorio", "+", "Laboratorio de rendimiento", False),
                 ("intercalacion", "+", "Intercalación", False)]
        for i, (clave, _num, titulo, obligatorio) in enumerate(pasos):
            if i > 0:
                tk.Frame(tp.cuerpo, bg=BORDE, height=1).pack(fill="x")
            fila = tk.Frame(tp.cuerpo, bg=TARJETA, cursor="hand2")
            fila.pack(fill="x")
            lado = px(26)
            circulo = tk.Canvas(fila, width=lado, height=lado, bg=TARJETA, highlightthickness=0)
            circulo.pack(side="left", padx=(0, px(14)), pady=px(12))
            textos = tk.Frame(fila, bg=TARJETA)
            textos.pack(side="left", fill="x", expand=True)
            tk.Label(textos, text=titulo, bg=TARJETA, fg=TEXTO, font=fuente(10.5, True), anchor="w").pack(fill="x")
            detalle = tk.Label(textos, text="", bg=TARJETA, fg=TEXTO_3, font=fuente(9), anchor="w")
            detalle.pack(fill="x")
            tk.Label(fila, text="OBLIGATORIO" if obligatorio else "OPCIONAL", bg=PRIMARIO_SUAVE if obligatorio
                     else "#f1f5f9", fg=PRIMARIO if obligatorio else TEXTO_3, font=fuente(7.5, True),
                     padx=px(8), pady=px(3)).pack(side="right")
            _al_hacer_clic(fila, lambda c=clave: self.mostrar(c))
            self.filas_proceso[clave] = (circulo, detalle)

        lado_der = tk.Frame(der, bg=FONDO)
        lado_der.grid(row=1, column=1, sticky="nsew", padx=(px(8), 0))
        lado_der.columnconfigure(0, weight=1)
        tr = Tarjeta(lado_der, "Reporte final en PDF", "Un solo documento con todo el proceso:")
        tr.grid(row=0, column=0, sticky="ew")
        for linea in ("Portada con resumen y estado de cada paso", "Carga de datos y su distribución",
                      "Algoritmo utilizado y tiempo de ejecución", "Primeros 20, últimos 20 y evidencia gráfica",
                      "Búsquedas realizadas", "Comparación entre algoritmos y recomendaciones",
                      "Laboratorio de rendimiento (si se ejecutó)", "Intercalación (si se realizó)"):
            tk.Label(tr.cuerpo, text="•  " + linea, bg=TARJETA, fg=TEXTO_2, font=fuente(9.5), anchor="w").pack(
                fill="x", pady=px(1))
        self.btn_pdf = self._boton(tr.cuerpo, "Generar reporte final PDF", self._exportar_reporte_final,
                                   "exito", grande=True)
        self.btn_pdf.pack(fill="x", pady=(px(16), 0))

        td = Tarjeta(lado_der, "Archivo ordenado", "Incluye el algoritmo utilizado y el tiempo de ejecución.")
        td.grid(row=2, column=0, sticky="ew", pady=(px(16), 0))
        self.var_formato = tk.StringVar(value=".txt")
        Segmentado(td.cuerpo, [(".txt", "TXT"), (".xlsx", "XLSX (con hoja Resumen)")], self.var_formato).pack(
            fill="x")
        self.btn_guardar_datos = self._boton(td.cuerpo, "Guardar archivo ordenado…", self._exportar_datos,
                                             "secundario")
        self.btn_guardar_datos.pack(fill="x", pady=(px(12), 0))

        te = Tarjeta(lado_der, "Archivos generados")
        te.grid(row=3, column=0, sticky="nsew", pady=(px(16), 0))
        lado_der.rowconfigure(3, weight=1)
        self.lista_export = tk.Listbox(te.cuerpo, height=4, font=fuente(9), relief="flat", bg="#f8fafc",
                                       fg=TEXTO, activestyle="none", highlightthickness=0, borderwidth=0,
                                       selectbackground=PRIMARIO_SUAVE, selectforeground=TEXTO)
        self.lista_export.pack(fill="both", expand=True)
        Boton(te.cuerpo, "Abrir carpeta", self._abrir_carpeta, "suave", pequeno=True).pack(anchor="w",
                                                                                          pady=(px(10), 0))

    def _metadatos(self):
        r = self.resultado
        return [
            ("Sistema", "Sistema de Procesamiento y Ordenamiento Masivo de Datos"),
            ("Archivo de origen", self.info["nombre"]),
            ("Formato de origen", self.info["formato"]),
            ("Total de registros", r["n"]),
            ("Algoritmo utilizado", r["algoritmo"]),
            ("Tipo de ordenamiento", r["tipo"]),
            ("Orden", r["orden"]),
            ("Tiempo de ejecucion (segundos)", round(r["segundos"], 6)),
            ("Tiempo de ejecucion", ex.formato_tiempo(r["segundos"])),
            ("Comparaciones", r["comparaciones"]),
            ("Movimientos", r["movimientos"]),
            ("Verificado como ordenado", "Si" if r["verificado"] else "No"),
            ("Fecha de exportacion", time.strftime("%d/%m/%Y %H:%M:%S")),
        ]

    def _nombre_base(self):
        r = self.resultado
        origen = os.path.splitext(self.info["nombre"])[0]
        alg = r["algoritmo"].replace(" ", "_").replace("ó", "o").replace("ñ", "n").replace("é", "e")
        base = f'{origen}_{alg}_{"desc" if r["descendente"] else "asc"}'
        limpio = "".join(c if (c.isalnum() and c.isascii()) or c in "_-" else "_" for c in base)
        return limpio[:80]

    def _pedir_ruta_guardar(self, base, extension, tipos):
        os.makedirs(CARPETA_EXPORT, exist_ok=True)
        ruta = filedialog.asksaveasfilename(parent=self, title="Guardar como", initialdir=CARPETA_EXPORT,
                                            initialfile=base + extension, defaultextension=extension,
                                            filetypes=tipos)
        if not ruta:
            return None
        if os.path.splitext(ruta)[1].lower() != extension:
            ruta += extension
        if self.info and os.path.normcase(os.path.abspath(ruta)) == os.path.normcase(self.info["ruta"]):
            messagebox.showerror("Operación no permitida", "No puedes sobrescribir el archivo de origen con "
                                                           "los resultados. Elige otro nombre.", parent=self)
            return None
        return ruta

    def _guardar_con_manejo(self, funcion, rutas, texto="Exportando…"):
        self._iniciar_proceso(texto)
        try:
            funcion()
        except ar.ErrorArchivo as e:
            self._terminar_proceso()
            self._estado("No se pudo exportar.", "error")
            messagebox.showerror("No se pudo exportar", str(e), parent=self)
            return False
        except OSError as e:
            self._terminar_proceso()
            self._estado("No se pudo exportar.", "error")
            messagebox.showerror("No se pudo exportar", f"Error del sistema de archivos:\n{e.strerror or e}",
                                 parent=self)
            return False
        except Exception as e:
            self._terminar_proceso()
            self._estado("Error inesperado al exportar.", "error")
            messagebox.showerror("Error inesperado", f"{type(e).__name__}: {e}", parent=self)
            return False
        self._terminar_proceso()
        for ruta in rutas:
            self.exportados.append(ruta)
            self.lista_export.insert("end", "  " + os.path.basename(ruta))
        self._estado("Guardado: " + "  ·  ".join(os.path.basename(r) for r in rutas), "ok")
        return True

    def _exportar_datos(self):
        if self.ocupado or self.resultado is None:
            return
        ext = self.var_formato.get()
        tipos = [("Texto", "*.txt")] if ext == ".txt" else [("Excel", "*.xlsx")]
        ruta = self._pedir_ruta_guardar(self._nombre_base(), ext, tipos)
        if not ruta:
            return
        lista, meta = self.resultado["lista"], self._metadatos()
        if ext == ".txt":
            self._guardar_con_manejo(lambda: ar.guardar_txt(ruta, lista, meta), [ruta])
        else:
            self._guardar_con_manejo(lambda: ar.guardar_xlsx(ruta, lista, meta), [ruta])

    def _conclusiones(self):
        res = self.comparacion
        lineas = []
        if res:
            rapido = lento = res[0]
            for r in res:
                if r["segundos"] < rapido["segundos"]:
                    rapido = r
                if r["segundos"] > lento["segundos"]:
                    lento = r
            lineas.append(f'El algoritmo más rápido fue {rapido["algoritmo"]} ({ex.formato_tiempo(rapido["segundos"])})'
                          f' y el más lento {lento["algoritmo"]} ({ex.formato_tiempo(lento["segundos"])}).')
            if rapido["segundos"] > 0 and lento is not rapido:
                lineas.append(f'Con {miles(len(self.originales))} registros, {lento["algoritmo"]} tardó '
                              f'{lento["segundos"] / rapido["segundos"]:,.0f} veces más que {rapido["algoritmo"]}: '
                              'la diferencia entre O(n²) y O(n log n) crece con el tamaño de los datos.')
            externos = [r for r in res if r["tipo"] == "Externo"]
            if len(externos) == 2:
                a, b = externos
                mejor = a if a["segundos"] <= b["segundos"] else b
                lineas.append(f'Entre los métodos externos, {mejor["algoritmo"]} fue el más rápido; los externos '
                              'son más lentos que los internos porque leen y escriben en disco, pero no necesitan '
                              'tener todos los datos en memoria.')
            todos = all(r["verificado"] for r in res)
            lineas.append("Todos los resultados se verificaron automáticamente como correctamente ordenados."
                          if todos else "Atención: algún resultado no quedó ordenado.")
        if self.comparacion_busquedas:
            f = self.comparacion_busquedas["filas"]
            lineas.append(f'En las búsquedas, la secuencial necesitó {miles(f[0][1])} comparaciones, la binaria '
                          f'{miles(f[1][1])} y la hash {miles(f[2][1])}, lo que confirma O(n), O(log n) y O(1).')
        return lineas

    def _info_reporte_final(self):
        pasos = [(PAGINAS[p][0] if p != "comparar" else "Comparar algoritmos", self.hecho[p], self._detalle_paso(p),
                  p in PASOS_OBLIGATORIOS)
                 for p in PASOS_OBLIGATORIOS + PASOS_OPCIONALES]
        return {"archivo": self.stats, "original": self.originales, "resultado": self.resultado,
                "busquedas": self.busquedas, "comparacion_busquedas": self.comparacion_busquedas,
                "comparacion": self.comparacion, "comparacion_orden": self.comparacion_orden,
                "recomendaciones": RECOMENDACIONES, "conclusiones": self._conclusiones(),
                "intercalacion": self.intercalacion, "pasos": pasos, "laboratorio": self.laboratorio}

    def _exportar_reporte_final(self):
        if self.ocupado:
            return
        faltan = [PAGINAS[p][0] for p in PASOS_OBLIGATORIOS if not self.hecho[p]]
        if faltan:                                       # el boton ya esta deshabilitado; doble seguridad
            messagebox.showinfo("Proceso incompleto", "Completa primero: " + ", ".join(faltan), parent=self)
            return
        ruta = self._pedir_ruta_guardar(f'reporte_final_{self._nombre_base()}', ".pdf", [("Reporte PDF", "*.pdf")])
        if not ruta:
            return
        info = self._info_reporte_final()
        if self._guardar_con_manejo(lambda: ex.reporte_final(ruta, info), [ruta], "Generando el reporte final…"):
            if messagebox.askyesno("Reporte generado", f"Se guardó el reporte:\n{os.path.basename(ruta)}\n\n"
                                                       "¿Quieres abrirlo ahora?", parent=self):
                try:
                    os.startfile(ruta)
                except (AttributeError, OSError):
                    pass

    def _abrir_carpeta(self):
        carpeta = os.path.dirname(self.exportados[-1]) if self.exportados else CARPETA_EXPORT
        os.makedirs(carpeta, exist_ok=True)
        try:
            os.startfile(carpeta)                  # solo Windows
        except (AttributeError, OSError):
            messagebox.showinfo("Carpeta", carpeta, parent=self)

    # ==================================================================
    # INTERCALACION DE ARCHIVOS (ordenamiento externo)
    # ==================================================================
    def _pagina_intercalacion(self):
        izq, der = self._nueva_pagina("intercalacion")
        t = Tarjeta(izq, "Archivos de entrada", "Carga en A y B dos archivos que ya ordenaste y guardaste antes con "
                                               "«Guardar archivo ordenado» (TXT o XLSX). Los dos deben estar "
                                               "ordenados de la misma forma.")
        t.pack(fill="x")
        c = t.cuerpo
        self.rutas_inter = {"A": None, "B": None}
        self.lbl_inter = {}
        for clave in ("A", "B"):
            fila = tk.Frame(c, bg="#f8fafc", highlightthickness=1, highlightbackground=BORDE)
            fila.pack(fill="x", pady=(0, px(8)))
            tk.Label(fila, text=clave, bg=PRIMARIO, fg="white", font=fuente(10, True), width=3, pady=px(8)).pack(
                side="left", padx=px(10), pady=px(10))
            lbl = tk.Label(fila, text="Sin seleccionar", bg="#f8fafc", fg=TEXTO_3, font=fuente(9.5), anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            self._boton(fila, "Elegir…", lambda k=clave: self._elegir_inter(k), "secundario", pequeno=True).pack(
                side="right", padx=px(10))
            self.lbl_inter[clave] = lbl
        tk.Frame(c, bg=TARJETA, height=px(8)).pack()
        self._boton(c, "Intercalar y guardar…", self._accion_intercalar, grande=True).pack(fill="x")

        der.rowconfigure(2, weight=1, minsize=px(300))
        self.kpi_inter = Indicadores(der, ["Registros", "Comparaciones", "Tiempo", "Verificación"])
        self.kpi_inter.grid(row=0, column=0, sticky="ew", pady=(0, px(16)))
        tf = Tarjeta(der, "Archivos")
        tf.grid(row=1, column=0, sticky="ew", pady=(0, px(16)))
        self.ficha_inter = FichaDatos(tf.cuerpo, ["Archivo A", "Archivo B", "Orden", "Resultado"], ancho_valor=600)
        self.ficha_inter.pack(fill="x")
        tg = Tarjeta(der, "Archivo intercalado")
        tg.grid(row=2, column=0, sticky="nsew")
        self.graf_inter = Grafica(tg.cuerpo, 7, 2.6)
        self.graf_inter.pack(fill="both", expand=True)
        self.graf_inter.dibujar(gr.dibujar_datos, [])

    def _elegir_inter(self, clave):
        if self.ocupado:
            return
        anterior = self.rutas_inter[clave]
        if anterior:
            carpeta = os.path.dirname(anterior)
        elif os.path.isdir(CARPETA_EXPORT):
            carpeta = CARPETA_EXPORT
        else:
            carpeta = os.path.expanduser("~")
        ruta = filedialog.askopenfilename(parent=self, title=f"Archivo {clave}: un archivo que ya ordenaste",
                                          initialdir=carpeta, filetypes=[("Archivos de datos", "*.txt *.xlsx")])
        if ruta:
            self.rutas_inter[clave] = ruta
            self.lbl_inter[clave].config(text=os.path.basename(ruta), fg=TEXTO)

    def _leer_ordenado(self, clave):
        """Lee y valida el archivo A o B. Regresa (datos, es_ascendente, es_descendente)."""
        try:
            datos = ar.leer_archivo(self.rutas_inter[clave])["datos"]
        except ar.ErrorArchivo as e:
            raise ar.ErrorArchivo(f"Archivo {clave}: {e}")
        return datos, oi.esta_ordenada(datos), oi.esta_ordenada(datos, True)

    def _accion_intercalar(self):
        if self.ocupado:
            return
        if not self.rutas_inter["A"] or not self.rutas_inter["B"]:
            messagebox.showwarning("Faltan archivos", "Elige los archivos A y B: dos archivos que ya hayas ordenado "
                                                      "y guardado antes.", parent=self)
            return
        if os.path.normcase(os.path.abspath(self.rutas_inter["A"])) == \
                os.path.normcase(os.path.abspath(self.rutas_inter["B"])):
            if not messagebox.askyesno("Mismo archivo", "A y B son el mismo archivo. ¿Intercalarlo consigo "
                                                        "mismo de todas formas?", parent=self):
                return
        # 1) Leer y revisar que los dos esten ordenados (antes de pedir donde guardar)
        try:
            datos_a, asc_a, desc_a = self._leer_ordenado("A")
            datos_b, asc_b, desc_b = self._leer_ordenado("B")
        except ar.ErrorArchivo as e:
            messagebox.showerror("Archivo no válido", str(e), parent=self)
            return
        for clave, asc, desc in (("A", asc_a, desc_a), ("B", asc_b, desc_b)):
            if not asc and not desc:
                messagebox.showerror("Archivo sin ordenar",
                                     f"El archivo {clave} no está ordenado.\n\nCarga un archivo que hayas ordenado "
                                     "y guardado antes con «Guardar archivo ordenado».", parent=self)
                return
        if asc_a and asc_b:
            desc = False
        elif desc_a and desc_b:
            desc = True
        else:
            orden_a = "ascendente" if asc_a else "descendente"
            orden_b = "ascendente" if asc_b else "descendente"
            messagebox.showerror("Órdenes distintos",
                                 f"El archivo A está en orden {orden_a} y el B en orden {orden_b}.\n\n"
                                 "Los dos deben estar ordenados de la misma forma.", parent=self)
            return
        # 2) Donde guardar el resultado
        sufijo = "desc" if desc else "asc"
        ruta = self._pedir_ruta_guardar(f"intercalado_{sufijo}", ".txt", [("Texto", "*.txt")])
        if not ruta:
            return
        for clave in ("A", "B"):
            if os.path.normcase(os.path.abspath(ruta)) == os.path.normcase(os.path.abspath(self.rutas_inter[clave])):
                messagebox.showerror("No permitido", "El resultado no puede sobrescribir A ni B.", parent=self)
                return
        # 3) Intercalacion externa (archivo contra archivo, linea por linea)
        self._iniciar_proceso("Intercalando archivos…")
        os.makedirs(CARPETA_TEMP, exist_ok=True)
        tmp = {"A": os.path.join(CARPETA_TEMP, "inter_A.txt"), "B": os.path.join(CARPETA_TEMP, "inter_B.txt")}
        try:
            oe.escribir_lista(tmp["A"], datos_a)                  # copia limpia, un numero por linea
            oe.escribir_lista(tmp["B"], datos_b)
            est, seg = self._medir(oe.intercalar_archivos, tmp["A"], tmp["B"], ruta, desc)
            resultado = oe.leer_lista(ruta)
        except (oe.ErrorOrdenExterno, OSError) as e:
            self._terminar_proceso()
            self._estado("No se pudo intercalar.", "error")
            detalle = getattr(e, "strerror", None) or str(e)
            messagebox.showerror("No se pudo intercalar", detalle, parent=self)
            try:
                if os.path.isfile(ruta):
                    os.remove(ruta)
            except OSError:
                pass
            return
        finally:
            for r in tmp.values():
                try:
                    if os.path.isfile(r):
                        os.remove(r)
                except OSError:
                    pass
        ok = len(resultado) == len(datos_a) + len(datos_b) and oi.esta_ordenada(resultado, desc)
        self.intercalacion = {"a": os.path.basename(self.rutas_inter["A"]),
                              "b": os.path.basename(self.rutas_inter["B"]), "salida": os.path.basename(ruta),
                              "orden": "Descendente" if desc else "Ascendente", "n": len(resultado),
                              "comparaciones": est["comparaciones"], "segundos": seg, "verificado": ok,
                              "datos": resultado}
        self.hecho["intercalacion"] = True
        self._terminar_proceso()
        k = self.kpi_inter
        k.poner("Registros", miles(len(resultado)), PRIMARIO)
        k.poner("Comparaciones", miles(est["comparaciones"]))
        k.poner("Tiempo", ex.formato_tiempo(seg))
        k.poner("Verificación", "✓ Ordenado" if ok else "✗ Error", OK if ok else ERROR)
        f = self.ficha_inter
        f.poner("Archivo A", f'{self.intercalacion["a"]}  ·  {miles(len(datos_a))} datos')
        f.poner("Archivo B", f'{self.intercalacion["b"]}  ·  {miles(len(datos_b))} datos')
        f.poner("Orden", self.intercalacion["orden"])
        f.poner("Resultado", self.intercalacion["salida"])
        self.graf_inter.dibujar(gr.dibujar_datos, resultado, color=gr.AZUL)
        self.exportados.append(ruta)
        self.lista_export.insert("end", "  " + os.path.basename(ruta))
        self._estado(f"Intercalación lista: {miles(len(resultado))} registros en {ex.formato_tiempo(seg)}.", "ok")


    # ==================================================================
    # LABORATORIO DE RENDIMIENTO (comprueba el requerimiento 6 con datos)
    # ==================================================================
    def _pagina_laboratorio(self):
        izq, der = self._nueva_pagina("laboratorio")
        t = Tarjeta(izq, "¿Qué hace?", "Mide de verdad lo que dice la teoría, con los datos cargados:")
        t.pack(fill="x")
        for linea in ("Escalabilidad: tiempo con n = 250, 500, 1000… y el exponente de crecimiento b "
                      "(b≈2 es n², b≈1 es n log n o lineal).",
                      "Escenarios del requerimiento 6: datos pequeños, masivos, casi ordenados, orden "
                      "inverso y muchos duplicados.",
                      "Búsquedas frecuentes: costo de 1,000 búsquedas con cada método.",
                      "Compara el ganador medido con la recomendación teórica."):
            l = tk.Label(t.cuerpo, text="•  " + linea, bg=TARJETA, fg=TEXTO_2, font=fuente(9), justify="left",
                         anchor="w")
            l.pack(fill="x", pady=px(2))
            ajustar_ancho_texto(l)
        t2 = Tarjeta(izq, "Algoritmos")
        t2.pack(fill="x", pady=(px(16), 0))
        self.vars_lab = {}
        rejilla = tk.Frame(t2.cuerpo, bg=TARJETA)
        rejilla.pack(fill="x")
        rejilla.columnconfigure(0, weight=1, uniform="chip")
        rejilla.columnconfigure(1, weight=1, uniform="chip")
        nombres = list(oi.ALGORITMOS_INTERNOS) + list(oe.ALGORITMOS_EXTERNOS)
        for i, nombre in enumerate(nombres):
            v = tk.BooleanVar(value=True)
            Chip(rejilla, nombre, v).grid(row=i // 2, column=i % 2, sticky="ew",
                                          padx=(0 if i % 2 == 0 else px(6), 0), pady=(0, px(6)))
            self.vars_lab[nombre] = v
        nota = tk.Label(t2.cuerpo, text=f"Para no tardar de más, un algoritmo deja de probar tamaños mayores cuando "
                                        f"una medición pasa de {lab.PRESUPUESTO:g} s, y en los escenarios los O(n²) "
                                        f"se miden hasta {lab.MAX_CUADRATICO:,} datos. Puedes cancelar en cualquier "
                                        "momento.",
                        bg="#f8fafc", fg=TEXTO_2, font=fuente(8.5), justify="left", anchor="w", padx=px(10),
                        pady=px(8))
        nota.pack(fill="x", pady=(px(8), px(14)))
        ajustar_ancho_texto(nota)
        self._boton(t2.cuerpo, "Ejecutar laboratorio", self._accion_laboratorio, grande=True).pack(fill="x")

        der.rowconfigure(1, minsize=px(380))
        der.rowconfigure(3, minsize=px(330))
        self.aviso_lab = Aviso(der)
        self.aviso_lab.grid(row=0, column=0, sticky="ew", pady=(0, px(16)))
        te = Tarjeta(der, "Escalabilidad", "Tiempo contra cantidad de datos en escala logarítmica: la pendiente de "
                                          "cada línea es su exponente de crecimiento b.")
        te.grid(row=1, column=0, sticky="nsew")
        self.graf_escala = Grafica(te.cuerpo, 7, 3.4)
        self.graf_escala.pack(fill="both", expand=True)
        tb = Tarjeta(der, "Exponente de crecimiento medido")
        tb.grid(row=2, column=0, sticky="ew", pady=(px(16), 0))
        self.tabla_exp = crear_tabla(tb.cuerpo, [("alg", "Algoritmo", 150, "w"), ("b", "b medido", 80, "e"),
                                                 ("med", "Crecimiento medido", 230, "w"),
                                                 ("teo", "Complejidad teórica", 260, "w"),
                                                 ("nmax", "n máximo medido", 120, "e")], alto=9)
        self.tabla_exp.marco.pack(fill="x")
        tm = Tarjeta(der, "Tiempo por escenario (ms)", "Claro = rápido, oscuro = lento respecto al mejor de cada "
                                                       "fila. El borde verde marca al ganador.")
        tm.grid(row=3, column=0, sticky="nsew", pady=(px(16), 0))
        self.graf_matriz = Grafica(tm.cuerpo, 7, 3.2)
        self.graf_matriz.pack(fill="both", expand=True)
        tr = Tarjeta(der, "Recomendación comprobada con mediciones")
        tr.grid(row=4, column=0, sticky="ew", pady=(px(16), 0))
        self.tabla_rec = crear_tabla(tr.cuerpo, [("esc", "Escenario", 200, "w"), ("gan", "Ganador medido", 150, "w"),
                                                 ("det", "Tiempo", 210, "w"), ("teo", "Recomendación teórica", 180, "w"),
                                                 ("ok", "¿Coincide?", 90, "center")], alto=5)
        self.tabla_rec.marco.pack(fill="x")
        self._limpiar_laboratorio()

    def _limpiar_laboratorio(self):
        if not hasattr(self, "aviso_lab"):
            return
        self.aviso_lab.poner("neutro", "Laboratorio sin ejecutar",
                             "Carga un archivo y presiona «Ejecutar laboratorio». Es opcional y se incluye en el "
                             "reporte final.")
        self.graf_escala.dibujar(gr.dibujar_escalabilidad, [])
        self.graf_matriz.dibujar(gr.dibujar_matriz, [], [], [])
        llenar_tabla(self.tabla_exp, [])
        llenar_tabla(self.tabla_rec, [])

    def _accion_laboratorio(self):
        if self.ocupado or not self._hay_datos():
            return
        nombres = [n for n, v in self.vars_lab.items() if v.get()]
        if len(nombres) < 2:
            messagebox.showwarning("Faltan algoritmos", "Selecciona al menos dos algoritmos.", parent=self)
            return
        externos = [n for n in oe.ALGORITMOS_EXTERNOS if n not in nombres]
        nombres_matriz = nombres + externos            # los externos siempre, para «Archivos externos»
        self._iniciar_proceso("Laboratorio de rendimiento…")

        def aviso(texto):
            self._estado(texto, "info")

        def pausa():
            return self.pausa
        try:
            series = lab.escalabilidad(self.originales, nombres, CARPETA_TEMP, self._progreso, pausa, aviso)
            escenarios, matriz = lab.matriz_escenarios(self.originales, nombres_matriz, CARPETA_TEMP,
                                                       self._progreso, pausa, aviso)
            busquedas = lab.busquedas_frecuentes(self.originales, aviso=aviso)
        except Cancelado:
            self._terminar_proceso()
            self._estado("Laboratorio cancelado.", "aviso")
            return
        except Exception as e:
            self._terminar_proceso()
            self._estado("Error en el laboratorio.", "error")
            messagebox.showerror("Error", f"{type(e).__name__}: {e}", parent=self)
            return
        teoricas = {e: a for e, a, _m in RECOMENDACIONES}
        recomendaciones = lab.recomendacion_empirica(nombres_matriz, escenarios, matriz, busquedas, teoricas)
        self.laboratorio = {"series": series, "escenarios": escenarios, "matriz": matriz,
                            "nombres": nombres_matriz, "busquedas": busquedas, "recomendaciones": recomendaciones,
                            "n": len(self.originales)}
        self.hecho["laboratorio"] = True
        self._terminar_proceso()
        self._mostrar_laboratorio()

    def _mostrar_laboratorio(self):
        datos = self.laboratorio
        self.graf_escala.dibujar(gr.dibujar_escalabilidad, datos["series"])
        self.graf_matriz.dibujar(gr.dibujar_matriz, datos["escenarios"], datos["nombres"], datos["matriz"])
        llenar_tabla(self.tabla_exp, [(s["algoritmo"],
                                       f'{s["exponente"]:.2f}' if s["exponente"] is not None else "—",
                                       s["interpretacion"], s["teorica"], miles(s["puntos"][-1][0]))
                                      for s in datos["series"]])
        llenar_tabla(self.tabla_rec, [(r["escenario"], r["ganador"], r["detalle"], r["teorica"],
                                       "✓ Sí" if r["coincide"] else "✗ No") for r in datos["recomendaciones"]])
        ok = sum(1 for r in datos["recomendaciones"] if r["coincide"])
        total = len(datos["recomendaciones"])
        self.aviso_lab.poner("ok" if ok == total else "info",
                             f"{ok} de {total} recomendaciones comprobadas con mediciones",
                             f'Medido con {miles(datos["n"])} datos. El exponente b indica cómo crece el tiempo: '
                             "duplicar n multiplica el tiempo por 2^b.")
        self._estado(f"Laboratorio terminado: {ok} de {total} recomendaciones coinciden con lo medido.", "ok")


def activar_alta_resolucion():
    """En Windows evita que la ventana se vea borrosa en pantallas con escala."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def iniciar():
    activar_alta_resolucion()
    app = Aplicacion()
    app.mainloop()

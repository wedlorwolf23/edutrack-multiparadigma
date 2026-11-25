import tkinter as tk
from datetime import date, timedelta
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from analytics import priorizar_pendientes, proyectar_nota_necesaria, resumen_global
from models import Evaluacion, GestorAcademico, Materia, Pendiente
from storage import cargar_datos, crear_datos_ejemplo, exportar_reporte_csv, guardar_datos


class EduTrackApp(tk.Tk):
    """Interfaz gráfica orientada a eventos construida con Tkinter."""

    BG_DARK = "#0f172a"
    BG_CARD = "#1e293b"
    BG_INPUT = "#334155"
    FG_TEXT = "#f8fafc"
    FG_MUTED = "#94a3b8"
    ACCENT = "#38bdf8"
    GREEN = "#22c55e"
    AMBER = "#f59e0b"
    RED = "#ef4444"

    def __init__(self) -> None:
        super().__init__()
        self.title("EduTrack — Gestor Académico Multiparadigma")
        self.geometry("1120x700")
        self.minsize(980, 620)
        self.configure(bg=self.BG_DARK)

        self.gestor: GestorAcademico = cargar_datos()
        self.materia_actual: Optional[str] = None
        self.pendientes_visibles: List[Pendiente] = []

        self.var_meta = tk.StringVar(value="7.0")
        self.var_mostrar_completados = tk.BooleanVar(value=False)

        self._configurar_estilos()
        self._construir_ui()
        self._refrescar_todo()

    def _configurar_estilos(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=self.BG_DARK)
        style.configure("Card.TFrame", background=self.BG_CARD)
        style.configure("TLabel", background=self.BG_DARK, foreground=self.FG_TEXT, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=self.BG_CARD, foreground=self.FG_TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=self.BG_CARD, foreground=self.FG_MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=self.BG_DARK, foreground=self.FG_TEXT, font=("Segoe UI", 16, "bold"))
        style.configure("KPI.TLabel", background=self.BG_CARD, foreground=self.ACCENT, font=("Segoe UI", 18, "bold"))

        style.configure("TNotebook", background=self.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.BG_CARD, foreground=self.FG_MUTED, padding=(16, 8), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.ACCENT)], foreground=[("selected", self.BG_DARK)])

        style.configure(
            "Accent.TButton",
            background=self.ACCENT,
            foreground=self.BG_DARK,
            font=("Segoe UI", 9, "bold"),
            padding=(10, 6),
            borderwidth=0,
        )
        style.map("Accent.TButton", background=[("active", "#7dd3fc")])

        style.configure(
            "Secondary.TButton",
            background=self.BG_INPUT,
            foreground=self.FG_TEXT,
            font=("Segoe UI", 9),
            padding=(10, 6),
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#475569")])

        style.configure(
            "Danger.TButton",
            background="#7f1d1d",
            foreground=self.FG_TEXT,
            font=("Segoe UI", 9),
            padding=(10, 6),
            borderwidth=0,
        )
        style.map("Danger.TButton", background=[("active", self.RED)])

        style.configure(
            "Treeview",
            background=self.BG_CARD,
            foreground=self.FG_TEXT,
            fieldbackground=self.BG_CARD,
            rowheight=28,
            borderwidth=0,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=self.BG_INPUT,
            foreground=self.FG_TEXT,
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", "#0369a1")])

        style.configure("TCheckbutton", background=self.BG_DARK, foreground=self.FG_TEXT, font=("Segoe UI", 9))

    def _construir_ui(self) -> None:
        # Encabezado
        header = ttk.Frame(self, padding=(18, 14, 18, 8))
        header.pack(fill="x")

        ttk.Label(header, text="EduTrack — Gestor de Progreso Académico", style="Title.TLabel").pack(side="left")

        acciones = ttk.Frame(header)
        acciones.pack(side="right")
        ttk.Button(acciones, text="Cargar ejemplo", style="Secondary.TButton", command=self._evento_cargar_ejemplo).pack(side="left", padx=4)
        ttk.Button(acciones, text="Exportar CSV", style="Accent.TButton", command=self._evento_exportar_csv).pack(side="left", padx=4)

        # Barra de indicadores (KPIs) + Selector de meta
        kpi_bar = ttk.Frame(self, padding=(18, 4, 18, 10))
        kpi_bar.pack(fill="x")

        self.lbl_kpi_promedio = self._crear_tarjeta_kpi(kpi_bar, "Promedio General", "0.00")
        self.lbl_kpi_riesgo = self._crear_tarjeta_kpi(kpi_bar, "Materias en Alerta/Riesgo", "0")
        self.lbl_kpi_pendientes = self._crear_tarjeta_kpi(kpi_bar, "Pendientes Activos", "0")

        meta_card = ttk.Frame(kpi_bar, style="Card.TFrame", padding=(14, 10))
        meta_card.pack(side="left", fill="both", expand=True, padx=5)
        ttk.Label(meta_card, text="Calificación Meta (0-10)", style="Muted.TLabel").pack(anchor="w")
        meta_row = ttk.Frame(meta_card, style="Card.TFrame")
        meta_row.pack(anchor="w", pady=(6, 0))
        tk.Entry(
            meta_row,
            textvariable=self.var_meta,
            width=7,
            bg=self.BG_INPUT,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            relief="flat",
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left", padx=(0, 8), ipady=3)
        ttk.Button(meta_row, text="Aplicar", style="Accent.TButton", command=self._evento_actualizar_meta).pack(side="left")

        # Pestañas principales
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        tab_materias = ttk.Frame(notebook, padding=10)
        tab_pendientes = ttk.Frame(notebook, padding=10)
        notebook.add(tab_materias, text="  Materias y Calculadora de Meta  ")
        notebook.add(tab_pendientes, text="  Agenda y Prioridad Inteligente  ")

        self._construir_tab_materias(tab_materias)
        self._construir_tab_pendientes(tab_pendientes)

    def _crear_tarjeta_kpi(self, parent: ttk.Frame, titulo: str, valor_inicial: str) -> ttk.Label:
        card = ttk.Frame(parent, style="Card.TFrame", padding=(14, 10))
        card.pack(side="left", fill="both", expand=True, padx=5)
        ttk.Label(card, text=titulo, style="Muted.TLabel").pack(anchor="w")
        lbl_valor = ttk.Label(card, text=valor_inicial, style="KPI.TLabel")
        lbl_valor.pack(anchor="w", pady=(4, 0))
        return lbl_valor

    def _crear_entry(self, parent: tk.Widget, width: int = 18) -> tk.Entry:
        return tk.Entry(
            parent,
            width=width,
            bg=self.BG_INPUT,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            relief="flat",
            font=("Segoe UI", 10),
        )

    def _construir_tab_materias(self, parent: ttk.Frame) -> None:
        # Columna izquierda: Materias
        izq = ttk.Frame(parent)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

        form_mat = ttk.Frame(izq, style="Card.TFrame", padding=10)
        form_mat.pack(fill="x", pady=(0, 8))
        ttk.Label(form_mat, text="Nueva materia:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=4)
        self.ent_mat_nombre = self._crear_entry(form_mat, width=22)
        self.ent_mat_nombre.grid(row=0, column=1, padx=4, ipady=3)

        ttk.Label(form_mat, text="Profesor / Nota:", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=4)
        self.ent_mat_prof = self._crear_entry(form_mat, width=16)
        self.ent_mat_prof.grid(row=0, column=3, padx=4, ipady=3)

        ttk.Button(form_mat, text="+ Agregar", style="Accent.TButton", command=self._evento_agregar_materia).grid(row=0, column=4, padx=6)

        cols_mat = ("materia", "evaluado", "promedio", "necesario", "estado")
        self.tree_materias = ttk.Treeview(izq, columns=cols_mat, show="headings", selectmode="browse")
        self.tree_materias.heading("materia", text="Materia")
        self.tree_materias.heading("evaluado", text="Eval. %")
        self.tree_materias.heading("promedio", text="Promedio")
        self.tree_materias.heading("necesario", text="Necesitas")
        self.tree_materias.heading("estado", text="Estado")

        self.tree_materias.column("materia", width=185)
        self.tree_materias.column("evaluado", width=70, anchor="center")
        self.tree_materias.column("promedio", width=75, anchor="center")
        self.tree_materias.column("necesario", width=80, anchor="center")
        self.tree_materias.column("estado", width=115, anchor="center")
        self.tree_materias.pack(fill="both", expand=True)

        self.tree_materias.tag_configure("ok", foreground=self.GREEN)
        self.tree_materias.tag_configure("alerta", foreground=self.AMBER)
        self.tree_materias.tag_configure("riesgo", foreground=self.RED)
        self.tree_materias.tag_configure("neutro", foreground=self.FG_MUTED)
        self.tree_materias.bind("<<TreeviewSelect>>", self._evento_seleccionar_materia)

        ttk.Button(izq, text="Eliminar materia seleccionada", style="Danger.TButton", command=self._evento_eliminar_materia).pack(anchor="e", pady=(8, 0))

        # Columna derecha: Evaluaciones de la materia seleccionada
        der = ttk.Frame(parent, width=420)
        der.pack(side="right", fill="both", expand=True)

        resumen_card = ttk.Frame(der, style="Card.TFrame", padding=12)
        resumen_card.pack(fill="x", pady=(0, 8))
        self.lbl_mat_titulo = ttk.Label(resumen_card, text="Selecciona una materia", style="Card.TLabel", font=("Segoe UI", 12, "bold"))
        self.lbl_mat_titulo.pack(anchor="w")
        self.lbl_mat_mensaje = ttk.Label(
            resumen_card,
            text="Haz clic en una materia de la tabla izquierda para registrar sus parciales y ver cuánto necesitas para tu meta.",
            style="Muted.TLabel",
            wraplength=400,
        )
        self.lbl_mat_mensaje.pack(anchor="w", pady=(4, 0))

        form_ev = ttk.Frame(der, style="Card.TFrame", padding=10)
        form_ev.pack(fill="x", pady=(0, 8))
        ttk.Label(form_ev, text="Evaluación:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=4, pady=3)
        self.ent_ev_nombre = self._crear_entry(form_ev, width=18)
        self.ent_ev_nombre.grid(row=0, column=1, padx=4, pady=3, ipady=3)

        ttk.Label(form_ev, text="Calif (0-10):", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=4, pady=3)
        self.ent_ev_calif = self._crear_entry(form_ev, width=7)
        self.ent_ev_calif.grid(row=0, column=3, padx=4, pady=3, ipady=3)

        ttk.Label(form_ev, text="Peso (%):", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=4, pady=3)
        self.ent_ev_peso = self._crear_entry(form_ev, width=8)
        self.ent_ev_peso.grid(row=1, column=1, sticky="w", padx=4, pady=3, ipady=3)

        ttk.Button(form_ev, text="+ Registrar evaluación", style="Accent.TButton", command=self._evento_agregar_evaluacion).grid(
            row=1, column=2, columnspan=2, sticky="e", padx=4, pady=3
        )

        cols_ev = ("nombre", "peso", "calificacion", "aporte")
        self.tree_evaluaciones = ttk.Treeview(der, columns=cols_ev, show="headings", selectmode="browse")
        self.tree_evaluaciones.heading("nombre", text="Evaluación")
        self.tree_evaluaciones.heading("peso", text="Peso %")
        self.tree_evaluaciones.heading("calificacion", text="Calif.")
        self.tree_evaluaciones.heading("aporte", text="Aporte pts")
        self.tree_evaluaciones.column("nombre", width=165)
        self.tree_evaluaciones.column("peso", width=70, anchor="center")
        self.tree_evaluaciones.column("calificacion", width=70, anchor="center")
        self.tree_evaluaciones.column("aporte", width=80, anchor="center")
        self.tree_evaluaciones.pack(fill="both", expand=True)

        ttk.Button(der, text="Eliminar evaluación seleccionada", style="Danger.TButton", command=self._evento_eliminar_evaluacion).pack(anchor="e", pady=(8, 0))

    def _construir_tab_pendientes(self, parent: ttk.Frame) -> None:
        form = ttk.Frame(parent, style="Card.TFrame", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Tarea / Sesión:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=4)
        self.ent_pen_titulo = self._crear_entry(form, width=28)
        self.ent_pen_titulo.grid(row=0, column=1, padx=4, ipady=3)

        ttk.Label(form, text="Materia:", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=4)
        self.cmb_pen_materia = ttk.Combobox(form, width=20)
        self.cmb_pen_materia.grid(row=0, column=3, padx=4)

        ttk.Label(form, text="Fecha (AAAA-MM-DD):", style="Card.TLabel").grid(row=0, column=4, sticky="w", padx=4)
        self.ent_pen_fecha = self._crear_entry(form, width=12)
        self.ent_pen_fecha.insert(0, (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"))
        self.ent_pen_fecha.grid(row=0, column=5, padx=4, ipady=3)

        ttk.Label(form, text="Imp. (1-5):", style="Card.TLabel").grid(row=0, column=6, sticky="w", padx=4)
        self.cmb_pen_imp = ttk.Combobox(form, values=["1", "2", "3", "4", "5"], width=4, state="readonly")
        self.cmb_pen_imp.set("4")
        self.cmb_pen_imp.grid(row=0, column=7, padx=4)

        ttk.Button(form, text="+ Agregar", style="Accent.TButton", command=self._evento_agregar_pendiente).grid(row=0, column=8, padx=6)

        controles = ttk.Frame(parent)
        controles.pack(fill="x", pady=(0, 6))
        ttk.Checkbutton(
            controles,
            text="Mostrar completados",
            variable=self.var_mostrar_completados,
            command=self._refrescar_pendientes,
        ).pack(side="left")

        ttk.Button(controles, text="Eliminar seleccionado", style="Danger.TButton", command=self._evento_eliminar_pendiente).pack(side="right", padx=4)
        ttk.Button(controles, text="Completar / Reactivar", style="Secondary.TButton", command=self._evento_alternar_pendiente).pack(side="right", padx=4)

        cols_pen = ("estado", "urgencia", "tiempo", "titulo", "materia", "fecha", "imp")
        self.tree_pendientes = ttk.Treeview(parent, columns=cols_pen, show="headings", selectmode="browse")
        self.tree_pendientes.heading("estado", text="Estado")
        self.tree_pendientes.heading("urgencia", text="Prioridad")
        self.tree_pendientes.heading("tiempo", text="Plazo")
        self.tree_pendientes.heading("titulo", text="Actividad / Sesión")
        self.tree_pendientes.heading("materia", text="Materia")
        self.tree_pendientes.heading("fecha", text="Fecha límite")
        self.tree_pendientes.heading("imp", text="Imp.")

        self.tree_pendientes.column("estado", width=90, anchor="center")
        self.tree_pendientes.column("urgencia", width=75, anchor="center")
        self.tree_pendientes.column("tiempo", width=110, anchor="center")
        self.tree_pendientes.column("titulo", width=330)
        self.tree_pendientes.column("materia", width=190)
        self.tree_pendientes.column("fecha", width=100, anchor="center")
        self.tree_pendientes.column("imp", width=55, anchor="center")
        self.tree_pendientes.pack(fill="both", expand=True)

        self.tree_pendientes.tag_configure("urgente", foreground=self.RED)
        self.tree_pendientes.tag_configure("media", foreground=self.AMBER)
        self.tree_pendientes.tag_configure("normal", foreground=self.FG_TEXT)
        self.tree_pendientes.tag_configure("hecho", foreground=self.FG_MUTED)

    # --- Helpers ---

    def _obtener_meta(self) -> float:
        try:
            valor = float(self.var_meta.get().replace(",", "."))
            if not (0.0 < valor <= 10.0):
                raise ValueError
            return valor
        except ValueError:
            self.var_meta.set("7.0")
            return 7.0

    def _guardar_y_refrescar(self) -> None:
        guardar_datos(self.gestor)
        self._refrescar_todo()

    def _refrescar_todo(self) -> None:
        meta = self._obtener_meta()
        stats = resumen_global(self.gestor.materias, meta)
        activos = sum(1 for p in self.gestor.pendientes if not p.completado)

        self.lbl_kpi_promedio.config(text=f"{stats['promedio_general']:.2f}")
        self.lbl_kpi_riesgo.config(text=str(stats["materias_en_riesgo"]))
        self.lbl_kpi_pendientes.config(text=str(activos))

        self._refrescar_materias(meta)
        self._refrescar_detalle_materia(meta)
        self._refrescar_pendientes()

        nombres = [m.nombre for m in self.gestor.materias] + ["General"]
        self.cmb_pen_materia["values"] = nombres
        if not self.cmb_pen_materia.get() and nombres:
            self.cmb_pen_materia.set(nombres[0])

    def _refrescar_materias(self, meta: float) -> None:
        self.tree_materias.delete(*self.tree_materias.get_children())
        item_a_seleccionar = None
        for materia in self.gestor.materias:
            proy = proyectar_nota_necesaria(materia.evaluaciones, meta)
            nota_nec = "-" if proy["nota_necesaria"] is None else f"{proy['nota_necesaria']:.2f}"
            iid = self.tree_materias.insert(
                "",
                "end",
                values=(
                    materia.nombre,
                    f"{proy['peso_evaluado']:.0f}%",
                    f"{proy['promedio_actual']:.2f}",
                    nota_nec,
                    proy["estado"],
                ),
                tags=(proy["nivel"],),
            )
            if self.materia_actual and materia.nombre.lower() == self.materia_actual.lower():
                item_a_seleccionar = iid

        if item_a_seleccionar:
            self.tree_materias.selection_set(item_a_seleccionar)

    def _refrescar_detalle_materia(self, meta: float) -> None:
        self.tree_evaluaciones.delete(*self.tree_evaluaciones.get_children())
        materia = self.gestor.obtener_materia(self.materia_actual) if self.materia_actual else None
        if materia is None:
            self.lbl_mat_titulo.config(text="Selecciona una materia")
            self.lbl_mat_mensaje.config(
                text="Haz clic en una materia de la tabla izquierda para registrar sus parciales y ver cuánto necesitas."
            )
            return

        proy = proyectar_nota_necesaria(materia.evaluaciones, meta)
        sufijo = f" · {materia.profesor}" if materia.profesor else ""
        self.lbl_mat_titulo.config(text=f"{materia.nombre}{sufijo}")
        self.lbl_mat_mensaje.config(text=str(proy["mensaje"]))

        for ev in materia.evaluaciones:
            aporte = ev.calificacion * (ev.peso / 100.0)
            self.tree_evaluaciones.insert(
                "",
                "end",
                values=(ev.nombre, f"{ev.peso:.1f}%", f"{ev.calificacion:.2f}", f"{aporte:.2f}"),
            )

    def _refrescar_pendientes(self) -> None:
        self.tree_pendientes.delete(*self.tree_pendientes.get_children())
        priorizados = priorizar_pendientes(
            self.gestor.pendientes,
            incluir_completados=self.var_mostrar_completados.get(),
        )
        self.pendientes_visibles = [item[0] for item in priorizados]

        for pendiente, puntaje, etiqueta in priorizados:
            estado = "Hecho" if pendiente.completado else "Pendiente"
            if pendiente.completado:
                tag = "hecho"
            elif puntaje >= 105:
                tag = "urgente"
            elif puntaje >= 80:
                tag = "media"
            else:
                tag = "normal"

            self.tree_pendientes.insert(
                "",
                "end",
                values=(
                    estado,
                    f"{puntaje} pts",
                    etiqueta,
                    pendiente.titulo,
                    pendiente.materia,
                    pendiente.fecha_limite,
                    f"{pendiente.importancia}/5",
                ),
                tags=(tag,),
            )

    # --- Manejadores de Eventos ---

    def _evento_actualizar_meta(self) -> None:
        self._obtener_meta()
        self._refrescar_todo()

    def _evento_seleccionar_materia(self, _event: tk.Event) -> None:
        sel = self.tree_materias.selection()
        if not sel:
            return
        valores = self.tree_materias.item(sel[0], "values")
        self.materia_actual = str(valores[0])
        self._refrescar_detalle_materia(self._obtener_meta())

    def _evento_agregar_materia(self) -> None:
        try:
            nueva = Materia(nombre=self.ent_mat_nombre.get(), profesor=self.ent_mat_prof.get())
            self.gestor.agregar_materia(nueva)
            self.materia_actual = nueva.nombre
            self.ent_mat_nombre.delete(0, "end")
            self.ent_mat_prof.delete(0, "end")
            self._guardar_y_refrescar()
        except ValueError as err:
            messagebox.showwarning("Dato inválido", str(err))

    def _evento_eliminar_materia(self) -> None:
        if not self.materia_actual:
            messagebox.showinfo("Aviso", "Selecciona primero una materia para eliminar.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{self.materia_actual}' y sus evaluaciones?"):
            self.gestor.eliminar_materia(self.materia_actual)
            self.materia_actual = None
            self._guardar_y_refrescar()

    def _evento_agregar_evaluacion(self) -> None:
        materia = self.gestor.obtener_materia(self.materia_actual) if self.materia_actual else None
        if materia is None:
            messagebox.showinfo("Aviso", "Selecciona primero una materia en la tabla izquierda.")
            return
        try:
            calif = float(self.ent_ev_calif.get().replace(",", "."))
            peso = float(self.ent_ev_peso.get().replace(",", "."))
            ev = Evaluacion(nombre=self.ent_ev_nombre.get(), calificacion=calif, peso=peso)
            materia.agregar_evaluacion(ev)
            self.ent_ev_nombre.delete(0, "end")
            self.ent_ev_calif.delete(0, "end")
            self.ent_ev_peso.delete(0, "end")
            self._guardar_y_refrescar()
        except ValueError as err:
            messagebox.showwarning("Dato inválido", f"Revisa los valores ingresados:\n{err}")

    def _evento_eliminar_evaluacion(self) -> None:
        materia = self.gestor.obtener_materia(self.materia_actual) if self.materia_actual else None
        sel = self.tree_evaluaciones.selection()
        if materia is None or not sel:
            messagebox.showinfo("Aviso", "Selecciona una evaluación para eliminar.")
            return
        indice = self.tree_evaluaciones.index(sel[0])
        materia.eliminar_evaluacion(indice)
        self._guardar_y_refrescar()

    def _evento_agregar_pendiente(self) -> None:
        try:
            nuevo = Pendiente(
                titulo=self.ent_pen_titulo.get(),
                materia=self.cmb_pen_materia.get(),
                fecha_limite=self.ent_pen_fecha.get().strip(),
                importancia=int(self.cmb_pen_imp.get()),
            )
            self.gestor.agregar_pendiente(nuevo)
            self.ent_pen_titulo.delete(0, "end")
            self._guardar_y_refrescar()
        except ValueError as err:
            messagebox.showwarning("Dato inválido", str(err))

    def _evento_alternar_pendiente(self) -> None:
        sel = self.tree_pendientes.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecciona un pendiente de la lista.")
            return
        indice = self.tree_pendientes.index(sel[0])
        self.pendientes_visibles[indice].alternar_estado()
        self._guardar_y_refrescar()

    def _evento_eliminar_pendiente(self) -> None:
        sel = self.tree_pendientes.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecciona un pendiente para eliminar.")
            return
        indice = self.tree_pendientes.index(sel[0])
        self.gestor.eliminar_pendiente(self.pendientes_visibles[indice])
        self._guardar_y_refrescar()

    def _evento_cargar_ejemplo(self) -> None:
        if self.gestor.materias or self.gestor.pendientes:
            if not messagebox.askyesno("Reemplazar datos", "¿Deseas cargar los datos de ejemplo? Se sobrescribirán los actuales."):
                return
        self.gestor = crear_datos_ejemplo()
        self.materia_actual = self.gestor.materias[0].nombre
        self._guardar_y_refrescar()

    def _evento_exportar_csv(self) -> None:
        ruta = filedialog.asksaveasfilename(
            title="Guardar reporte académico",
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            initialfile="reporte_academico.csv",
        )
        if not ruta:
            return
        try:
            exportar_reporte_csv(self.gestor, self._obtener_meta(), ruta)
            messagebox.showinfo("Exportación exitosa", f"Reporte guardado en:\n{ruta}")
        except OSError as err:
            messagebox.showerror("Error al exportar", str(err))
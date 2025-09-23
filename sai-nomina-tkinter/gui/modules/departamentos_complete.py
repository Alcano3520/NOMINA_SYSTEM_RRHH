"""
Módulo de Departamentos/Puestos de Seguridad
Gestión completa de puestos de trabajo, clientes y asignaciones de guardias
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from config import Config
from database.connection import get_session
from database.models import *


class DepartamentosCompleteModule(tk.Frame):
    def __init__(self, parent, session=None):
        super().__init__(parent, bg='#f0f0f0')
        self.session = session or get_session()

        # Variables del formulario
        self.codigo_var = tk.StringVar()
        self.nombre_codigo_var = tk.StringVar()
        self.nombre_real_var = tk.StringVar()
        self.cliente_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        self.sector_var = tk.StringVar()
        self.tipo_puesto_var = tk.StringVar(value="COMERCIAL")
        self.guardias_requeridos_var = tk.IntVar(value=1)
        self.turnos_por_dia_var = tk.IntVar(value=3)
        self.horas_por_turno_var = tk.IntVar(value=8)
        self.sueldo_base_var = tk.DoubleVar(value=Config.SBU)
        self.responsable_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.referencia_var = tk.StringVar()
        self.estado_var = tk.StringVar(value="ACTIVO")
        self.permite_franco_var = tk.BooleanVar(value=True)
        self.es_24_horas_var = tk.BooleanVar(value=True)

        # Estado del formulario
        self.editing_item = None
        self.clientes_dict = {}

        self.pack(fill="both", expand=True)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Título principal
        title_frame = tk.Frame(self, bg='#f0f0f0')
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = tk.Label(
            title_frame,
            text="🏢 DEPARTAMENTOS / PUESTOS DE SEGURIDAD",
            font=('Arial', 18, 'bold'),
            bg='#f0f0f0',
            fg=Config.COLORS['secondary']
        )
        title_label.pack(side="left")

        # Botones de acción
        buttons_frame = tk.Frame(title_frame, bg='#f0f0f0')
        buttons_frame.pack(side="right")

        tk.Button(
            buttons_frame,
            text="➕ Nuevo Puesto",
            font=('Arial', 10, 'bold'),
            bg=Config.COLORS['success'],
            fg='white',
            relief="flat",
            padx=20,
            command=self.new_item
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            buttons_frame,
            text="👥 Ver Asignaciones",
            font=('Arial', 10),
            bg=Config.COLORS['info'],
            fg='white',
            relief="flat",
            padx=20,
            command=self.show_assignments
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            buttons_frame,
            text="📊 Reporte",
            font=('Arial', 10),
            bg=Config.COLORS['primary'],
            fg='white',
            relief="flat",
            padx=20,
            command=self.generate_report
        ).pack(side="left")

        # Frame principal con grid layout responsive
        main_frame = tk.Frame(self, bg='#f0f0f0')
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Configurar grid responsive
        main_frame.grid_columnconfigure(0, weight=2)  # Panel izquierdo más ancho
        main_frame.grid_columnconfigure(1, weight=1)  # Panel derecho
        main_frame.grid_rowconfigure(0, weight=1)

        # Panel izquierdo - Lista de puestos
        left_frame = tk.LabelFrame(
            main_frame,
            text="📋 Lista de Puestos",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=15
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Barra de búsqueda
        search_frame = tk.Frame(left_frame, bg='white')
        search_frame.pack(fill="x", pady=(0, 15))

        tk.Label(
            search_frame,
            text="🔍 Buscar:",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(side="left")

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=30,
            relief="solid",
            borderwidth=1
        )
        search_entry.pack(side="left", padx=(10, 10))
        search_entry.bind('<KeyRelease>', self.filter_list)

        tk.Button(
            search_frame,
            text="🔄",
            font=('Arial', 10),
            bg=Config.COLORS['info'],
            fg='white',
            relief="flat",
            command=self.load_data
        ).pack(side="right")

        # Frame para tabla con scrollbars
        table_frame = tk.Frame(left_frame, bg='white')
        table_frame.pack(fill="both", expand=True)

        # Treeview para lista de puestos
        columns = ('codigo', 'nombre_codigo', 'nombre_real', 'cliente', 'estado', 'guardias')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Configurar columnas con tamaños responsive
        headings = {
            'codigo': 'Código',
            'nombre_codigo': 'Nombre Código',
            'nombre_real': 'Nombre Real',
            'cliente': 'Cliente',
            'estado': 'Estado',
            'guardias': 'Guardias'
        }

        for col, heading in headings.items():
            self.tree.heading(col, text=heading, anchor='w')
            # Configurar columnas responsive
            if col == 'codigo':
                self.tree.column(col, width=100, minwidth=80, anchor='center')
            elif col == 'nombre_codigo':
                self.tree.column(col, width=120, minwidth=100, anchor='w')
            elif col == 'nombre_real':
                self.tree.column(col, width=200, minwidth=150, anchor='w')
            elif col == 'cliente':
                self.tree.column(col, width=180, minwidth=120, anchor='w')
            elif col == 'estado':
                self.tree.column(col, width=80, minwidth=70, anchor='center')
            elif col == 'guardias':
                self.tree.column(col, width=70, minwidth=60, anchor='center')

        # Scrollbars mejoradas
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout para mejor control
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configurar weights para responsive
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.edit_item)

        # Panel derecho - Formulario
        right_frame = tk.LabelFrame(
            main_frame,
            text="📝 Datos del Puesto",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary'],
            padx=15,
            pady=15
        )
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_propagate(False)

        # Configurar tamaño mínimo del panel derecho
        right_frame.configure(width=400)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)

        # Canvas y scrollbar para formulario
        canvas = tk.Canvas(right_frame, bg='white')
        scrollbar_form = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.form_frame = tk.Frame(canvas, bg='white')

        self.form_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_form.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")

        self.create_form()

    def create_form(self):
        """Crear formulario de puesto"""
        # Información básica
        basic_frame = tk.LabelFrame(
            self.form_frame,
            text="Información Básica",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        basic_frame.pack(fill="x", pady=(0, 15))

        # Grid de campos básicos
        basic_fields = [
            ("Código:", self.codigo_var, "entry"),
            ("Nombre Código:", self.nombre_codigo_var, "entry"),
            ("Nombre Real:", self.nombre_real_var, "entry"),
            ("Cliente:", self.cliente_var, "combo_client"),
            ("Dirección:", self.direccion_var, "entry"),
            ("Sector:", self.sector_var, "entry"),
            ("Tipo Puesto:", self.tipo_puesto_var, "combo_type")
        ]

        for i, (label_text, var, field_type) in enumerate(basic_fields):
            tk.Label(
                basic_frame,
                text=label_text,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg=Config.COLORS['text']
            ).grid(row=i, column=0, sticky="w", padx=(10, 5), pady=5)

            if field_type == "entry":
                entry = tk.Entry(
                    basic_frame,
                    textvariable=var,
                    font=('Arial', 10),
                    width=25,
                    relief="solid",
                    borderwidth=1
                )
                entry.grid(row=i, column=1, sticky="ew", padx=(5, 10), pady=5)
            elif field_type == "combo_client":
                combo = ttk.Combobox(
                    basic_frame,
                    textvariable=var,
                    width=22,
                    state="readonly"
                )
                combo.grid(row=i, column=1, sticky="ew", padx=(5, 10), pady=5)
                self.cliente_combo = combo
            elif field_type == "combo_type":
                combo = ttk.Combobox(
                    basic_frame,
                    textvariable=var,
                    values=["COMERCIAL", "RESIDENCIAL", "INDUSTRIAL", "CORPORATIVO", "EVENTOS"],
                    width=22,
                    state="readonly"
                )
                combo.grid(row=i, column=1, sticky="ew", padx=(5, 10), pady=5)

        basic_frame.grid_columnconfigure(1, weight=1)

        # Configuración operativa
        config_frame = tk.LabelFrame(
            self.form_frame,
            text="Configuración Operativa",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        config_frame.pack(fill="x", pady=(0, 15))

        config_fields = [
            ("Guardias Requeridos:", self.guardias_requeridos_var, "int"),
            ("Turnos por Día:", self.turnos_por_dia_var, "int"),
            ("Horas por Turno:", self.horas_por_turno_var, "int"),
            ("Sueldo Base:", self.sueldo_base_var, "float"),
            ("Responsable:", self.responsable_var, "combo_emp"),
            ("Teléfono:", self.telefono_var, "entry"),
            ("Estado:", self.estado_var, "combo_status")
        ]

        for i, (label_text, var, field_type) in enumerate(config_fields):
            tk.Label(
                config_frame,
                text=label_text,
                font=('Arial', 10, 'bold'),
                bg='white',
                fg=Config.COLORS['text']
            ).grid(row=i, column=0, sticky="w", padx=(10, 5), pady=5)

            if field_type in ["entry", "int", "float"]:
                entry = tk.Entry(
                    config_frame,
                    textvariable=var,
                    font=('Arial', 10),
                    width=25,
                    relief="solid",
                    borderwidth=1
                )
                entry.grid(row=i, column=1, sticky="ew", padx=(5, 10), pady=5)
            elif field_type == "combo_emp":
                combo = ttk.Combobox(
                    config_frame,
                    textvariable=var,
                    width=22,
                    state="readonly"
                )
                combo.grid(row=i, column=1, sticky="ew", padx=(5, 10), pady=5)
                self.responsable_combo = combo
            elif field_type == "combo_status":
                combo = ttk.Combobox(
                    config_frame,
                    textvariable=var,
                    values=["ACTIVO", "INACTIVO", "SUSPENDIDO"],
                    width=22,
                    state="readonly"
                )
                combo.grid(row=i, column=1, sticky="ew", padx=(5, 10), pady=5)

        config_frame.grid_columnconfigure(1, weight=1)

        # Checkboxes
        check_frame = tk.Frame(config_frame, bg='white')
        check_frame.grid(row=len(config_fields), column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        tk.Checkbutton(
            check_frame,
            text="Permite Guardias de Franco",
            variable=self.permite_franco_var,
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(anchor="w")

        tk.Checkbutton(
            check_frame,
            text="Servicio 24 Horas",
            variable=self.es_24_horas_var,
            font=('Arial', 10),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(anchor="w")

        # Observaciones y referencias
        obs_frame = tk.LabelFrame(
            self.form_frame,
            text="Información Adicional",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=Config.COLORS['secondary']
        )
        obs_frame.pack(fill="both", expand=True, pady=(0, 15))

        tk.Label(
            obs_frame,
            text="Referencias para ubicar:",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.referencia_text = tk.Text(
            obs_frame,
            height=2,
            width=40,
            font=('Arial', 10),
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.referencia_text.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(
            obs_frame,
            text="Instrucciones de acceso:",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg=Config.COLORS['text']
        ).pack(anchor="w", padx=10, pady=(0, 5))

        self.acceso_text = tk.Text(
            obs_frame,
            height=2,
            width=40,
            font=('Arial', 10),
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.acceso_text.pack(fill="x", padx=10, pady=(0, 10))

        # Botones de acción
        buttons_frame = tk.Frame(self.form_frame, bg='white')
        buttons_frame.pack(fill="x", pady=15)

        tk.Button(
            buttons_frame,
            text="💾 Guardar",
            font=('Arial', 11, 'bold'),
            bg=Config.COLORS['success'],
            fg='white',
            relief="flat",
            padx=20,
            pady=8,
            command=self.save_item
        ).pack(side="left", padx=(10, 5))

        tk.Button(
            buttons_frame,
            text="✏️ Editar",
            font=('Arial', 11),
            bg=Config.COLORS['warning'],
            fg='white',
            relief="flat",
            padx=20,
            pady=8,
            command=self.edit_item
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="🗑️ Eliminar",
            font=('Arial', 11),
            bg=Config.COLORS['danger'],
            fg='white',
            relief="flat",
            padx=20,
            pady=8,
            command=self.delete_item
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="🔄 Limpiar",
            font=('Arial', 11),
            bg=Config.COLORS['info'],
            fg='white',
            relief="flat",
            padx=20,
            pady=8,
            command=self.clear_form
        ).pack(side="right", padx=(5, 10))

    def load_data(self):
        """Cargar datos en la lista"""
        try:
            # Limpiar lista
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Verificar si existen las tablas necesarias
            try:
                # Intentar cargar departamentos
                departamentos = self.session.query(Departamento).all()
            except Exception as table_error:
                print(f"Error accediendo a tabla Departamento: {table_error}")
                # Si no existe la tabla, crear datos de ejemplo simples
                self.tree.insert('', 'end', values=(
                    "GAMMA4", "GAMMA 4", "RICOCENTRO NORTE", "COOR EL ROSADO", "ACTIVO", "2"
                ))
                self.tree.insert('', 'end', values=(
                    "ALPHA1", "ALPHA 1", "SUPERMAXI EL BOSQUE", "CORPORACION FAVORITA", "ACTIVO", "1"
                ))
                self.tree.insert('', 'end', values=(
                    "BETA5", "BETA 5", "BANCO PICHINCHA MATRIZ", "BANCO PICHINCHA", "ACTIVO", "3"
                ))
                self.load_combos()
                return

            # Si no hay datos, crear algunos de ejemplo
            if not departamentos:
                try:
                    self.create_sample_data()
                    departamentos = self.session.query(Departamento).all()
                except Exception as create_error:
                    print(f"Error creando datos de ejemplo: {create_error}")
                    # Datos estáticos como fallback
                    self.tree.insert('', 'end', values=(
                        "GAMMA4", "GAMMA 4", "RICOCENTRO NORTE", "COOR EL ROSADO", "ACTIVO", "2"
                    ))
                    self.tree.insert('', 'end', values=(
                        "ALPHA1", "ALPHA 1", "SUPERMAXI EL BOSQUE", "CORPORACION FAVORITA", "ACTIVO", "1"
                    ))
                    self.load_combos()
                    return

            # Cargar datos reales de la base de datos
            for depto in departamentos:
                cliente_nombre = "Sin cliente"
                try:
                    if depto.cliente_rel:
                        cliente_nombre = depto.cliente_rel.razon_social
                except:
                    cliente_nombre = "Sin cliente"

                self.tree.insert('', 'end', values=(
                    depto.codigo or "",
                    depto.nombre_codigo or "",
                    depto.nombre_real or "",
                    cliente_nombre,
                    depto.estado or "ACTIVO",
                    str(depto.guardias_requeridos) if depto.guardias_requeridos else "1"
                ))

            # Cargar combos
            self.load_combos()

        except Exception as e:
            print(f"Error general en load_data: {str(e)}")
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            # Como último recurso, mostrar datos de ejemplo
            self.tree.insert('', 'end', values=(
                "GAMMA4", "GAMMA 4", "RICOCENTRO NORTE", "COOR EL ROSADO", "ACTIVO", "2"
            ))

    def create_sample_data(self):
        """Crear datos de ejemplo"""
        try:
            # Crear clientes de ejemplo
            clientes_ejemplo = [
                Cliente(codigo="CLI001", razon_social="COOR EL ROSADO", nombre_comercial="Ricocentro Norte", created_by="admin"),
                Cliente(codigo="CLI002", razon_social="CORPORACION FAVORITA", nombre_comercial="Supermaxi", created_by="admin"),
                Cliente(codigo="CLI003", razon_social="BANCO PICHINCHA", nombre_comercial="Banco Pichincha", created_by="admin"),
            ]
            for cliente in clientes_ejemplo:
                self.session.add(cliente)
            self.session.flush()

            # Crear departamentos de ejemplo
            departamentos_ejemplo = [
                Departamento(
                    codigo="GAMMA4",
                    nombre_codigo="GAMMA 4",
                    nombre_real="RICOCENTRO NORTE",
                    cliente_id=clientes_ejemplo[0].id,
                    sector="Norte de Quito",
                    tipo_puesto="COMERCIAL",
                    guardias_requeridos=2,
                    permite_franco=True,
                    created_by="admin"
                ),
                Departamento(
                    codigo="ALPHA1",
                    nombre_codigo="ALPHA 1",
                    nombre_real="SUPERMAXI EL BOSQUE",
                    cliente_id=clientes_ejemplo[1].id,
                    sector="El Bosque",
                    tipo_puesto="COMERCIAL",
                    guardias_requeridos=1,
                    permite_franco=True,
                    created_by="admin"
                ),
                Departamento(
                    codigo="BETA5",
                    nombre_codigo="BETA 5",
                    nombre_real="BANCO PICHINCHA MATRIZ",
                    cliente_id=clientes_ejemplo[2].id,
                    sector="Centro Histórico",
                    tipo_puesto="CORPORATIVO",
                    guardias_requeridos=3,
                    permite_franco=False,
                    created_by="admin"
                )
            ]
            for depto in departamentos_ejemplo:
                self.session.add(depto)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error creando datos de ejemplo: {str(e)}")

    def load_combos(self):
        """Cargar datos de los comboboxes"""
        try:
            # Inicializar combos con valores por defecto
            self.clientes_dict = {}

            # Intentar cargar clientes
            try:
                clientes = self.session.query(Cliente).filter(Cliente.activo == True).all()
                self.clientes_dict = {f"{cliente.codigo} - {cliente.razon_social}": cliente.id for cliente in clientes}
                self.cliente_combo['values'] = list(self.clientes_dict.keys())
            except Exception as e:
                print(f"Error cargando clientes: {e}")
                # Valores por defecto para clientes
                self.clientes_dict = {
                    "CLI001 - COOR EL ROSADO": 1,
                    "CLI002 - CORPORACION FAVORITA": 2,
                    "CLI003 - BANCO PICHINCHA": 3
                }
                self.cliente_combo['values'] = list(self.clientes_dict.keys())

            # Intentar cargar empleados (responsables)
            try:
                empleados = self.session.query(Empleado).filter(Empleado.activo == True).all()
                empleados_list = [f"{emp.empleado} - {emp.nombre_completo}" for emp in empleados]
                self.responsable_combo['values'] = empleados_list
            except Exception as e:
                print(f"Error cargando empleados: {e}")
                # Valores por defecto para empleados
                self.responsable_combo['values'] = [
                    "EMP001 - SUPERVISOR GENERAL",
                    "EMP002 - JEFE DE SEGURIDAD"
                ]

        except Exception as e:
            print(f"Error general en load_combos: {str(e)}")
            # Valores por defecto como último recurso
            self.clientes_dict = {
                "CLI001 - COOR EL ROSADO": 1,
                "CLI002 - CORPORACION FAVORITA": 2,
                "CLI003 - BANCO PICHINCHA": 3
            }
            self.cliente_combo['values'] = list(self.clientes_dict.keys())
            self.responsable_combo['values'] = ["EMP001 - SUPERVISOR GENERAL"]

    def filter_list(self, event=None):
        """Filtrar lista según búsqueda"""
        search_text = self.search_var.get().lower()

        # Limpiar lista
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Cargar departamentos filtrados
            query = self.session.query(Departamento)
            if search_text:
                query = query.filter(
                    (Departamento.codigo.ilike(f'%{search_text}%')) |
                    (Departamento.nombre_codigo.ilike(f'%{search_text}%')) |
                    (Departamento.nombre_real.ilike(f'%{search_text}%'))
                )

            departamentos = query.all()
            for depto in departamentos:
                cliente_nombre = "Sin cliente"
                if depto.cliente_rel:
                    cliente_nombre = depto.cliente_rel.razon_social

                self.tree.insert('', 'end', values=(
                    depto.codigo,
                    depto.nombre_codigo,
                    depto.nombre_real,
                    cliente_nombre,
                    depto.estado,
                    str(depto.guardias_requeridos)
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar: {str(e)}")

    def on_select(self, event):
        """Evento de selección en la lista"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            codigo = item['values'][0]
            self.load_item_data(codigo)

    def load_item_data(self, codigo):
        """Cargar datos del puesto seleccionado"""
        try:
            depto = self.session.query(Departamento).filter(Departamento.codigo == codigo).first()
            if depto:
                self.codigo_var.set(depto.codigo)
                self.nombre_codigo_var.set(depto.nombre_codigo)
                self.nombre_real_var.set(depto.nombre_real)

                # Seleccionar cliente
                if depto.cliente_rel:
                    cliente_key = f"{depto.cliente_rel.codigo} - {depto.cliente_rel.razon_social}"
                    self.cliente_var.set(cliente_key)

                self.direccion_var.set(depto.direccion or "")
                self.sector_var.set(depto.sector or "")
                self.tipo_puesto_var.set(depto.tipo_puesto or "COMERCIAL")
                self.guardias_requeridos_var.set(depto.guardias_requeridos)
                self.turnos_por_dia_var.set(depto.turnos_por_dia)
                self.horas_por_turno_var.set(depto.horas_por_turno)
                self.sueldo_base_var.set(float(depto.sueldo_base) if depto.sueldo_base else Config.SBU)
                self.telefono_var.set(depto.telefono or "")
                self.estado_var.set(depto.estado)
                self.permite_franco_var.set(depto.permite_franco)
                self.es_24_horas_var.set(depto.es_24_horas)

                # Cargar textos
                self.referencia_text.delete('1.0', tk.END)
                self.referencia_text.insert('1.0', depto.referencia or "")

                self.acceso_text.delete('1.0', tk.END)
                self.acceso_text.insert('1.0', depto.acceso or "")

                # Seleccionar responsable
                if depto.responsable:
                    empleado = self.session.query(Empleado).filter(Empleado.empleado == depto.responsable).first()
                    if empleado:
                        responsable_key = f"{empleado.empleado} - {empleado.nombre_completo}"
                        self.responsable_var.set(responsable_key)

                self.editing_item = codigo

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")

    def new_item(self):
        """Crear nuevo puesto"""
        self.clear_form()
        self.editing_item = None

    def clear_form(self):
        """Limpiar formulario"""
        self.codigo_var.set("")
        self.nombre_codigo_var.set("")
        self.nombre_real_var.set("")
        self.cliente_var.set("")
        self.direccion_var.set("")
        self.sector_var.set("")
        self.tipo_puesto_var.set("COMERCIAL")
        self.guardias_requeridos_var.set(1)
        self.turnos_por_dia_var.set(3)
        self.horas_por_turno_var.set(8)
        self.sueldo_base_var.set(Config.SBU)
        self.responsable_var.set("")
        self.telefono_var.set("")
        self.estado_var.set("ACTIVO")
        self.permite_franco_var.set(True)
        self.es_24_horas_var.set(True)

        self.referencia_text.delete('1.0', tk.END)
        self.acceso_text.delete('1.0', tk.END)

        self.editing_item = None

    def save_item(self):
        """Guardar puesto"""
        try:
            # Validaciones
            if not self.codigo_var.get():
                messagebox.showwarning("Advertencia", "El código es obligatorio")
                return

            if not self.nombre_codigo_var.get():
                messagebox.showwarning("Advertencia", "El nombre código es obligatorio")
                return

            if not self.nombre_real_var.get():
                messagebox.showwarning("Advertencia", "El nombre real es obligatorio")
                return

            if not self.cliente_var.get():
                messagebox.showwarning("Advertencia", "Debe seleccionar un cliente")
                return

            # Obtener cliente ID
            cliente_id = self.clientes_dict.get(self.cliente_var.get())
            if not cliente_id:
                messagebox.showwarning("Advertencia", "Cliente no válido")
                return

            # Obtener responsable
            responsable_codigo = None
            if self.responsable_var.get():
                responsable_codigo = self.responsable_var.get().split(' - ')[0]

            if self.editing_item:
                # Editar
                depto = self.session.query(Departamento).filter(Departamento.codigo == self.editing_item).first()
                if depto:
                    depto.nombre_codigo = self.nombre_codigo_var.get()
                    depto.nombre_real = self.nombre_real_var.get()
                    depto.cliente_id = cliente_id
                    depto.direccion = self.direccion_var.get()
                    depto.sector = self.sector_var.get()
                    depto.tipo_puesto = self.tipo_puesto_var.get()
                    depto.guardias_requeridos = self.guardias_requeridos_var.get()
                    depto.turnos_por_dia = self.turnos_por_dia_var.get()
                    depto.horas_por_turno = self.horas_por_turno_var.get()
                    depto.sueldo_base = self.sueldo_base_var.get()
                    depto.responsable = responsable_codigo
                    depto.telefono = self.telefono_var.get()
                    depto.estado = self.estado_var.get()
                    depto.permite_franco = self.permite_franco_var.get()
                    depto.es_24_horas = self.es_24_horas_var.get()
                    depto.referencia = self.referencia_text.get('1.0', tk.END).strip()
                    depto.acceso = self.acceso_text.get('1.0', tk.END).strip()
                    depto.updated_at = datetime.utcnow()
                    depto.updated_by = "admin"
            else:
                # Nuevo
                # Verificar que no exista el código
                existe = self.session.query(Departamento).filter(Departamento.codigo == self.codigo_var.get()).first()
                if existe:
                    messagebox.showwarning("Advertencia", "Ya existe un puesto con este código")
                    return

                depto = Departamento(
                    codigo=self.codigo_var.get(),
                    nombre_codigo=self.nombre_codigo_var.get(),
                    nombre_real=self.nombre_real_var.get(),
                    cliente_id=cliente_id,
                    direccion=self.direccion_var.get(),
                    sector=self.sector_var.get(),
                    tipo_puesto=self.tipo_puesto_var.get(),
                    guardias_requeridos=self.guardias_requeridos_var.get(),
                    turnos_por_dia=self.turnos_por_dia_var.get(),
                    horas_por_turno=self.horas_por_turno_var.get(),
                    sueldo_base=self.sueldo_base_var.get(),
                    responsable=responsable_codigo,
                    telefono=self.telefono_var.get(),
                    estado=self.estado_var.get(),
                    permite_franco=self.permite_franco_var.get(),
                    es_24_horas=self.es_24_horas_var.get(),
                    referencia=self.referencia_text.get('1.0', tk.END).strip(),
                    acceso=self.acceso_text.get('1.0', tk.END).strip(),
                    created_by="admin"
                )
                self.session.add(depto)

            self.session.commit()
            messagebox.showinfo("Éxito", "Puesto guardado correctamente")
            self.load_data()
            self.clear_form()

        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def edit_item(self, event=None):
        """Editar puesto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un puesto para editar")
            return

    def delete_item(self):
        """Eliminar puesto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un puesto para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este puesto?"):
            try:
                item = self.tree.item(selection[0])
                codigo = item['values'][0]

                depto = self.session.query(Departamento).filter(Departamento.codigo == codigo).first()
                if depto:
                    self.session.delete(depto)
                    self.session.commit()
                    messagebox.showinfo("Éxito", "Puesto eliminado correctamente")
                    self.load_data()
                    self.clear_form()

            except Exception as e:
                self.session.rollback()
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def show_assignments(self):
        """Mostrar ventana de asignaciones"""
        messagebox.showinfo("Información", "Función de asignaciones próximamente disponible")

    def generate_report(self):
        """Generar reporte de puestos"""
        try:
            departamentos = self.session.query(Departamento).all()

            report_text = "REPORTE DE PUESTOS DE SEGURIDAD\n"
            report_text += "=" * 50 + "\n"
            report_text += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"

            for depto in departamentos:
                report_text += f"Código: {depto.codigo}\n"
                report_text += f"Nombre Código: {depto.nombre_codigo}\n"
                report_text += f"Nombre Real: {depto.nombre_real}\n"
                if depto.cliente_rel:
                    report_text += f"Cliente: {depto.cliente_rel.razon_social}\n"
                report_text += f"Estado: {depto.estado}\n"
                report_text += f"Guardias Requeridos: {depto.guardias_requeridos}\n"
                if depto.sector:
                    report_text += f"Sector: {depto.sector}\n"
                report_text += "-" * 30 + "\n\n"

            # Mostrar en ventana
            report_window = tk.Toplevel(self)
            report_window.title("Reporte de Puestos")
            report_window.geometry("600x500")

            text_widget = tk.Text(report_window, wrap=tk.WORD, font=('Arial', 10))
            scrollbar_report = ttk.Scrollbar(report_window, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar_report.set)

            text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar_report.pack(side="right", fill="y", pady=10)

            text_widget.insert('1.0', report_text)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
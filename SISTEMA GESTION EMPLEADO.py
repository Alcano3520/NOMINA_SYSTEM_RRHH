import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyodbc
import pandas as pd
from datetime import datetime
import os

class SistemaGestionEmpleados:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Empleados - INSEVIG")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximizar ventana
        
        # Variables para conexión a BD
        self.conn = None
        self.empleado_actual = None
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Conectar a base de datos
        self.conectar_bd()
        
    def configurar_estilo(self):
        """Configurar el estilo visual de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'), background='lightblue')
        
    def conectar_bd(self):
        """Establecer conexión con la base de datos"""
        try:
            server = 'SERVER\\server'
            database = 'insevig'
            username = 'sa'
            password = 'puntosoft123*'
            
            conn_str = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password};'
                f'Encrypt=No;'
                f'TrustServerCertificate=yes;'
            )
            
            self.conn = pyodbc.connect(conn_str)
            self.status_label.config(text="Conectado a base de datos", foreground="green")
            
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
            self.status_label.config(text="Error de conexión", foreground="red")
    
    def crear_interfaz(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - Búsqueda
        self.crear_panel_busqueda(main_frame)
        
        # Frame para contenido principal (lista + pestañas)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Panel izquierdo - Lista de empleados
        self.crear_panel_lista_empleados(content_frame)
        
        # Panel derecho - Pestañas
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.crear_pestaña_datos_generales()
        self.crear_pestaña_ingresos_descuentos()
        self.crear_pestaña_observaciones()
        self.crear_pestaña_otros_datos()
        self.crear_pestaña_certificados()
        self.crear_pestaña_referencias()
        
        # Panel inferior - Botones y estado
        self.crear_panel_botones(main_frame)
        
        # Variables para control de cambios
        self.datos_modificados = False
        self.datos_originales = None
        
    def crear_panel_busqueda(self, parent):
        """Crear panel de búsqueda"""
        search_frame = ttk.LabelFrame(parent, text="Búsqueda de Empleado", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Búsqueda por cédula
        ttk.Label(search_frame, text="Cédula:").grid(row=0, column=0, padx=5, sticky='w')
        self.cedula_var = tk.StringVar()
        cedula_entry = ttk.Entry(search_frame, textvariable=self.cedula_var, width=15)
        cedula_entry.grid(row=0, column=1, padx=5)
        cedula_entry.bind('<Return>', self.buscar_por_cedula)
        
        # Búsqueda por código empleado
        ttk.Label(search_frame, text="Código Empleado:").grid(row=0, column=2, padx=5, sticky='w')
        self.codigo_var = tk.StringVar()
        codigo_entry = ttk.Entry(search_frame, textvariable=self.codigo_var, width=15)
        codigo_entry.grid(row=0, column=3, padx=5)
        codigo_entry.bind('<Return>', self.buscar_por_codigo)
        
        # Botones de búsqueda
        ttk.Button(search_frame, text="Buscar por Cédula", 
                  command=self.buscar_por_cedula).grid(row=0, column=4, padx=5)
        ttk.Button(search_frame, text="Buscar por Código", 
                  command=self.buscar_por_codigo).grid(row=0, column=5, padx=5)
        ttk.Button(search_frame, text="Nuevo Empleado", 
                  command=self.nuevo_empleado).grid(row=0, column=6, padx=5)
        ttk.Button(search_frame, text="Edición Masiva", 
                  command=self.edicion_masiva).grid(row=0, column=7, padx=5)
    
    def crear_panel_lista_empleados(self, parent):
        """Crear panel lateral con lista de empleados"""
        # Frame principal para la lista
        list_frame = ttk.LabelFrame(parent, text="Lista de Empleados", padding=5)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        list_frame.configure(width=350)
        
        # Frame superior con controles
        control_frame = ttk.Frame(list_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Filtro por estado
        ttk.Label(control_frame, text="Empleados:").pack(side=tk.LEFT)
        self.filtro_estado = tk.StringVar(value="Activos")
        estado_combo = ttk.Combobox(control_frame, textvariable=self.filtro_estado, 
                                   values=["Activos", "Inactivos", "Todos"], width=10, state="readonly")
        estado_combo.pack(side=tk.LEFT, padx=(5, 10))
        estado_combo.bind('<<ComboboxSelected>>', self.filtrar_empleados)
        
        # Botones de navegación
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame, text="⏮", width=3, command=self.primer_empleado).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="◀", width=3, command=self.empleado_anterior).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="▶", width=3, command=self.empleado_siguiente).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="⏭", width=3, command=self.ultimo_empleado).pack(side=tk.LEFT, padx=1)
        
        # Treeview para lista de empleados
        columns = ('codigo', 'apellidos', 'nombres')
        self.tree_empleados = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree_empleados.heading('codigo', text='Código')
        self.tree_empleados.heading('apellidos', text='Apellidos')
        self.tree_empleados.heading('nombres', text='Nombres')
        
        self.tree_empleados.column('codigo', width=60, anchor='center')
        self.tree_empleados.column('apellidos', width=120)
        self.tree_empleados.column('nombres', width=120)
        
        # Scrollbar para la lista
        scrollbar_list = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_empleados.yview)
        self.tree_empleados.configure(yscrollcommand=scrollbar_list.set)
        
        # Empaquetar treeview y scrollbar
        self.tree_empleados.pack(side="left", fill="both", expand=True)
        scrollbar_list.pack(side="right", fill="y")
        
        # Evento de selección
        self.tree_empleados.bind('<<TreeviewSelect>>', self.seleccionar_empleado_lista)
        
        # Frame inferior con controles adicionales
        bottom_frame = ttk.Frame(list_frame)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Ordenamiento
        ttk.Label(bottom_frame, text="Ordenar Por:").pack(anchor='w')
        orden_frame = ttk.Frame(bottom_frame)
        orden_frame.pack(fill=tk.X, pady=2)
        
        self.orden_var = tk.StringVar(value="alfabetico")
        ttk.Radiobutton(orden_frame, text="Alfabéticamente", variable=self.orden_var, 
                       value="alfabetico", command=self.ordenar_lista).pack(anchor='w')
        ttk.Radiobutton(orden_frame, text="Departamento", variable=self.orden_var, 
                       value="departamento", command=self.ordenar_lista).pack(anchor='w')
        
        # Botón actualizar y enlace
        ttk.Button(bottom_frame, text="Actualizar Lista", command=self.cargar_lista_empleados).pack(pady=2)
        
        # Enlace estilo link
        link_label = tk.Label(bottom_frame, text="Ver todos los datos generales", 
                             fg="blue", cursor="hand2", font=("Arial", 8, "underline"))
        link_label.pack(pady=2)
        link_label.bind("<Button-1>", lambda e: self.abrir_vista_completa())
        
        # Cargar lista inicial
        self.cargar_lista_empleados()
    
    def cargar_lista_empleados(self):
        """Cargar lista de empleados en el treeview"""
        if not self.conn:
            return
        
        try:
            # Limpiar lista actual
            for item in self.tree_empleados.get_children():
                self.tree_empleados.delete(item)
            
            # Construir query según filtro
            estado_filtro = self.filtro_estado.get()
            if estado_filtro == "Activos":
                where_clause = "WHERE ESTADO = 'ACT'"
            elif estado_filtro == "Inactivos":
                where_clause = "WHERE ESTADO != 'ACT'"
            else:
                where_clause = ""
            
            # Ordenamiento
            if self.orden_var.get() == "alfabetico":
                order_clause = "ORDER BY APELLIDOS, NOMBRES"
            else:
                order_clause = "ORDER BY DEPTO, APELLIDOS, NOMBRES"
            
            query = f"""
            SELECT EMPLEADO, APELLIDOS, NOMBRES, DEPTO 
            FROM RPEMPLEA 
            {where_clause} 
            {order_clause}
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query)
            empleados = cursor.fetchall()
            
            # Llenar treeview
            for empleado in empleados:
                codigo, apellidos, nombres, depto = empleado
                nombres_corto = nombres[:15] + "..." if len(nombres) > 15 else nombres
                apellidos_corto = apellidos[:15] + "..." if len(apellidos) > 15 else apellidos
                
                self.tree_empleados.insert('', 'end', values=(codigo, apellidos_corto, nombres_corto))
            
            cursor.close()
            self.status_label.config(text=f"Lista cargada: {len(empleados)} empleados", foreground="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar lista: {e}")
    
    def filtrar_empleados(self, event=None):
        """Filtrar empleados por estado"""
        self.cargar_lista_empleados()
    
    def ordenar_lista(self):
        """Ordenar lista de empleados"""
        self.cargar_lista_empleados()
    
    def seleccionar_empleado_lista(self, event=None):
        """Seleccionar empleado desde la lista"""
        selection = self.tree_empleados.selection()
        if not selection:
            return
        
        # Verificar si hay cambios sin guardar
        if self.datos_modificados:
            respuesta = messagebox.askyesnocancel(
                "Cambios sin guardar",
                "¿Desea guardar los cambios del empleado actual antes de continuar?\n\n"
                "• Sí: Guardar cambios y continuar\n"
                "• No: Descartar cambios y continuar\n" 
                "• Cancelar: Permanecer en empleado actual"
            )
            
            if respuesta is None:  # Cancelar
                return
            elif respuesta:  # Sí - Guardar
                if not self.guardar_cambios():
                    return  # Si falla el guardado, no continuar
        
        # Obtener código del empleado seleccionado
        item = self.tree_empleados.item(selection[0])
        codigo_empleado = item['values'][0]
        
        # Cargar empleado
        self.codigo_var.set(str(codigo_empleado))
        self.buscar_por_codigo()
    
    def primer_empleado(self):
        """Ir al primer empleado de la lista"""
        if self.tree_empleados.get_children():
            primer_item = self.tree_empleados.get_children()[0]
            self.tree_empleados.selection_set(primer_item)
            self.tree_empleados.focus(primer_item)
            self.seleccionar_empleado_lista()
    
    def ultimo_empleado(self):
        """Ir al último empleado de la lista"""
        if self.tree_empleados.get_children():
            ultimo_item = self.tree_empleados.get_children()[-1]
            self.tree_empleados.selection_set(ultimo_item)
            self.tree_empleados.focus(ultimo_item)
            self.seleccionar_empleado_lista()
    
    def empleado_anterior(self):
        """Ir al empleado anterior"""
        selection = self.tree_empleados.selection()
        if not selection:
            return
        
        current_item = selection[0]
        children = self.tree_empleados.get_children()
        
        try:
            current_index = children.index(current_item)
            if current_index > 0:
                prev_item = children[current_index - 1]
                self.tree_empleados.selection_set(prev_item)
                self.tree_empleados.focus(prev_item)
                self.seleccionar_empleado_lista()
        except ValueError:
            pass
    
    def empleado_siguiente(self):
        """Ir al empleado siguiente"""
        selection = self.tree_empleados.selection()
        if not selection:
            return
        
        current_item = selection[0]
        children = self.tree_empleados.get_children()
        
        try:
            current_index = children.index(current_item)
            if current_index < len(children) - 1:
                next_item = children[current_index + 1]
                self.tree_empleados.selection_set(next_item)
                self.tree_empleados.focus(next_item)
                self.seleccionar_empleado_lista()
        except ValueError:
            pass
    
    def abrir_vista_completa(self):
        """Abrir ventana con vista completa de datos"""
        VistaCompletaWindow(self.root, self.conn)
    
    def crear_pestaña_datos_generales(self):
        """Crear pestaña de datos generales"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Datos Generales")
        
        # Crear canvas y scrollbar para scroll
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Variables para campos
        self.datos_generales = {}
        
        # Información básica
        info_frame = ttk.LabelFrame(scrollable_frame, text="Información Personal", padding=10)
        info_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Primera fila
        ttk.Label(info_frame, text="Código:").grid(row=0, column=0, sticky='w', padx=5)
        self.datos_generales['EMPLEADO'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['EMPLEADO'], width=15).grid(row=0, column=1, padx=5, sticky='w')
        
        ttk.Label(info_frame, text="Cédula:").grid(row=0, column=2, sticky='w', padx=5)
        self.datos_generales['CEDULA'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['CEDULA'], width=15).grid(row=0, column=3, padx=5, sticky='w')
        
        ttk.Label(info_frame, text="Cód.Suc:").grid(row=0, column=4, sticky='w', padx=5)
        self.datos_generales['CODSUC'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['CODSUC'], width=10).grid(row=0, column=5, padx=5, sticky='w')
        
        ttk.Label(info_frame, text="Cód.Emp:").grid(row=0, column=6, sticky='w', padx=5)
        self.datos_generales['CODEMP'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['CODEMP'], width=10).grid(row=0, column=7, padx=5, sticky='w')
        
        # Segunda fila
        ttk.Label(info_frame, text="Nombres:").grid(row=1, column=0, sticky='w', padx=5)
        self.datos_generales['NOMBRES'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['NOMBRES'], width=30).grid(row=1, column=1, columnspan=2, padx=5, sticky='ew')
        
        # Tercera fila
        ttk.Label(info_frame, text="Apellidos:").grid(row=2, column=0, sticky='w', padx=5)
        self.datos_generales['APELLIDOS'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['APELLIDOS'], width=30).grid(row=2, column=1, columnspan=2, padx=5, sticky='ew')
        
        # Cuarta fila
        ttk.Label(info_frame, text="Sexo:").grid(row=3, column=0, sticky='w', padx=5)
        self.datos_generales['SEXO'] = tk.StringVar()
        sexo_combo = ttk.Combobox(info_frame, textvariable=self.datos_generales['SEXO'], 
                                 values=['1', '2'], width=12)
        sexo_combo.grid(row=3, column=1, padx=5, sticky='w')
        # Diccionarios para mapeo
        self.sexo_map = {'1': 'Masculino', '2': 'Femenino'}
        self.estado_civil_map = {'1': 'Casado', '2': 'Soltero', '3': 'Divorciado', '4': 'Viudo'}
        
        ttk.Label(info_frame, text="Estado Civil:").grid(row=3, column=2, sticky='w', padx=5)
        self.datos_generales['ESTADO_CI'] = tk.StringVar()
        estado_combo = ttk.Combobox(info_frame, textvariable=self.datos_generales['ESTADO_CI'], 
                                   values=['1', '2', '3', '4'], width=12)
        estado_combo.grid(row=3, column=3, padx=5, sticky='w')
        
        # Quinta fila
        ttk.Label(info_frame, text="Lugar Nac:").grid(row=4, column=0, sticky='w', padx=5)
        self.datos_generales['LUGAR_NAC'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['LUGAR_NAC'], width=20).grid(row=4, column=1, padx=5, sticky='w')
        
        ttk.Label(info_frame, text="Fecha Nac:").grid(row=4, column=2, sticky='w', padx=5)
        self.datos_generales['FECHA_NAC'] = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.datos_generales['FECHA_NAC'], width=15).grid(row=4, column=3, padx=5, sticky='w')
        
        # Dirección
        dir_frame = ttk.LabelFrame(scrollable_frame, text="Ubicación", padding=10)
        dir_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        ttk.Label(dir_frame, text="Dirección:").grid(row=0, column=0, sticky='w', padx=5)
        self.datos_generales['DIRECCION'] = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.datos_generales['DIRECCION'], width=50).grid(row=0, column=1, columnspan=3, padx=5, sticky='ew')
        
        ttk.Label(dir_frame, text="Provincia:").grid(row=1, column=0, sticky='w', padx=5)
        self.datos_generales['PROVINCIA'] = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.datos_generales['PROVINCIA'], width=15).grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(dir_frame, text="Cantón:").grid(row=1, column=2, sticky='w', padx=5)
        self.datos_generales['CANTON'] = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.datos_generales['CANTON'], width=15).grid(row=1, column=3, padx=5, sticky='w')
        
        ttk.Label(dir_frame, text="Parroquia:").grid(row=2, column=0, sticky='w', padx=5)
        self.datos_generales['PARROQUIA'] = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.datos_generales['PARROQUIA'], width=15).grid(row=2, column=1, padx=5, sticky='w')
        
        ttk.Label(dir_frame, text="Nacionalidad:").grid(row=2, column=2, sticky='w', padx=5)
        self.datos_generales['NACIONAL'] = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.datos_generales['NACIONAL'], width=15).grid(row=2, column=3, padx=5, sticky='w')
        
        # Información laboral
        lab_frame = ttk.LabelFrame(scrollable_frame, text="Información Laboral", padding=10)
        lab_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        ttk.Label(lab_frame, text="Fecha Ingreso:").grid(row=0, column=0, sticky='w', padx=5)
        self.datos_generales['FECHA_ING'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['FECHA_ING'], width=15).grid(row=0, column=1, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Departamento:").grid(row=0, column=2, sticky='w', padx=5)
        self.datos_generales['DEPTO'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['DEPTO'], width=15).grid(row=0, column=3, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Cargo:").grid(row=1, column=0, sticky='w', padx=5)
        self.datos_generales['CARGO'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['CARGO'], width=20).grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Sección:").grid(row=1, column=2, sticky='w', padx=5)
        self.datos_generales['SECCION'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['SECCION'], width=15).grid(row=1, column=3, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Estado:").grid(row=2, column=0, sticky='w', padx=5)
        self.datos_generales['ESTADO'] = tk.StringVar()
        estado_lab_combo = ttk.Combobox(lab_frame, textvariable=self.datos_generales['ESTADO'], 
                                       values=['ACTIVO', 'INACTIVO'], width=12)
        estado_lab_combo.grid(row=2, column=1, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Teléfono:").grid(row=2, column=2, sticky='w', padx=5)
        self.datos_generales['TELEFONO'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['TELEFONO'], width=15).grid(row=2, column=3, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Email:").grid(row=3, column=0, sticky='w', padx=5)
        self.datos_generales['emp_mail'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['emp_mail'], width=30).grid(row=3, column=1, columnspan=2, padx=5, sticky='ew')
        
        ttk.Label(lab_frame, text="Segundo Teléfono:").grid(row=4, column=0, sticky='w', padx=5)
        self.datos_generales['RPCAM'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['RPCAM'], width=15).grid(row=4, column=1, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Tipo Trabajo:").grid(row=5, column=0, sticky='w', padx=5)
        self.datos_generales['TIPO_TRA'] = tk.StringVar()
        tipo_tra_combo = ttk.Combobox(lab_frame, textvariable=self.datos_generales['TIPO_TRA'], 
                                     values=['1', '2', '3'], width=10)
        tipo_tra_combo.grid(row=5, column=1, padx=5, sticky='w')
        
        ttk.Label(lab_frame, text="Actividad:").grid(row=5, column=2, sticky='w', padx=5)
        self.datos_generales['ACTIVIDAD'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['ACTIVIDAD'], width=25).grid(row=5, column=3, padx=5, sticky='ew')
        
        ttk.Label(lab_frame, text="Cónyuge:").grid(row=6, column=0, sticky='w', padx=5)
        self.datos_generales['CONYUGUE'] = tk.StringVar()
        ttk.Entry(lab_frame, textvariable=self.datos_generales['CONYUGUE'], width=30).grid(row=6, column=1, columnspan=2, padx=5, sticky='ew')
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def toggle_checkbox(self, field):
        """Alternar estado de checkbox y actualizar variable"""
        current_state = self.checkbox_states.get(field, False)
        new_state = not current_state
        self.checkbox_states[field] = new_state
        self.otros_datos[field].set('S' if new_state else 'N')
    
    def crear_pestaña_ingresos_descuentos(self):
        """Crear pestaña de ingresos y descuentos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Ingresos Dctos.")
        
        self.ingresos = {}
        
        # Sueldo y Beneficios de Ley
        sueldo_frame = ttk.LabelFrame(frame, text="Sueldo y Beneficios de Ley", padding=10)
        sueldo_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(sueldo_frame, text="Sueldo:").grid(row=0, column=0, sticky='w', padx=5)
        self.ingresos['SUELDO'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['SUELDO'], width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(sueldo_frame, text="Bonificación:").grid(row=0, column=2, sticky='w', padx=5)
        self.ingresos['BONIFI'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['BONIFI'], width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(sueldo_frame, text="Compensación:").grid(row=0, column=4, sticky='w', padx=5)
        self.ingresos['COMPEN'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['COMPEN'], width=15).grid(row=0, column=5, padx=5)
        
        ttk.Label(sueldo_frame, text="Transporte:").grid(row=1, column=0, sticky='w', padx=5)
        self.ingresos['TRANSP'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['TRANSP'], width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(sueldo_frame, text="Lunch:").grid(row=1, column=2, sticky='w', padx=5)
        self.ingresos['LUNCH'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['LUNCH'], width=15).grid(row=1, column=3, padx=5)
        
        ttk.Label(sueldo_frame, text="Horas 25%:").grid(row=2, column=0, sticky='w', padx=5)
        self.ingresos['HOR25'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['HOR25'], width=15).grid(row=2, column=1, padx=5)
        
        ttk.Label(sueldo_frame, text="Horas 50%:").grid(row=2, column=2, sticky='w', padx=5)
        self.ingresos['HOR50'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['HOR50'], width=15).grid(row=2, column=3, padx=5)
        
        ttk.Label(sueldo_frame, text="Horas 100%:").grid(row=2, column=4, sticky='w', padx=5)
        self.ingresos['HOR100'] = tk.StringVar()
        ttk.Entry(sueldo_frame, textvariable=self.ingresos['HOR100'], width=15).grid(row=2, column=5, padx=5)
        
        # Decimos
        decimos_frame = ttk.LabelFrame(frame, text="Acumulados de Beneficios Sociales Históricos", padding=10)
        decimos_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(decimos_frame, text="Décimo 3er:").grid(row=0, column=0, sticky='w', padx=5)
        self.ingresos['DECIMO3'] = tk.StringVar()
        ttk.Entry(decimos_frame, textvariable=self.ingresos['DECIMO3'], width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(decimos_frame, text="Décimo 4to:").grid(row=0, column=2, sticky='w', padx=5)
        self.ingresos['DECIMO4'] = tk.StringVar()
        ttk.Entry(decimos_frame, textvariable=self.ingresos['DECIMO4'], width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(decimos_frame, text="Vacaciones:").grid(row=0, column=4, sticky='w', padx=5)
        self.ingresos['VACACION'] = tk.StringVar()
        ttk.Entry(decimos_frame, textvariable=self.ingresos['VACACION'], width=15).grid(row=0, column=5, padx=5)
        
        ttk.Label(decimos_frame, text="Fondo Reserva:").grid(row=1, column=0, sticky='w', padx=5)
        self.ingresos['FONRESER'] = tk.StringVar()
        ttk.Entry(decimos_frame, textvariable=self.ingresos['FONRESER'], width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(decimos_frame, text="V.Anticipo $:").grid(row=1, column=2, sticky='w', padx=5)
        self.ingresos['ANTICIPO'] = tk.StringVar()
        ttk.Entry(decimos_frame, textvariable=self.ingresos['ANTICIPO'], width=15).grid(row=1, column=3, padx=5)
        
        ttk.Label(decimos_frame, text="Concepto:").grid(row=2, column=0, sticky='w', padx=5)
        self.ingresos['CONCEPTO'] = tk.StringVar()
        ttk.Entry(decimos_frame, textvariable=self.ingresos['CONCEPTO'], width=30).grid(row=2, column=1, columnspan=2, padx=5, sticky='ew')
    
    def crear_pestaña_observaciones(self):
        """Crear pestaña de observaciones"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Observaciones")
        
        # Fecha
        fecha_frame = ttk.Frame(frame)
        fecha_frame.pack(fill=tk.X, padx=10, pady=5)
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        ttk.Label(fecha_frame, text=fecha_actual).pack(side=tk.RIGHT)
        ttk.Button(fecha_frame, text="Mostrar").pack(side=tk.RIGHT, padx=(0, 10))
        
        # Text widget para observaciones
        self.observaciones_text = tk.Text(frame, height=20, width=80)
        self.observaciones_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar para texto
        scrollbar_obs = ttk.Scrollbar(frame, orient="vertical", command=self.observaciones_text.yview)
        scrollbar_obs.pack(side="right", fill="y")
        self.observaciones_text.configure(yscrollcommand=scrollbar_obs.set)
    
    def crear_pestaña_otros_datos(self):
        """Crear pestaña de otros datos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Otros Datos")
        
        self.otros_datos = {}
        
        # Datos Generales
        datos_gen_frame = ttk.LabelFrame(frame, text="Datos Generales", padding=10)
        datos_gen_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        # Checkboxes
        self.otros_datos['INCL_ROL'] = tk.StringVar()
        incl_rol_check = ttk.Checkbutton(datos_gen_frame, text="Incluir en el Rol")
        incl_rol_check.grid(row=0, column=0, sticky='w', padx=5)
        incl_rol_check.configure(command=lambda: self.toggle_checkbox('INCL_ROL'))
        
        self.otros_datos['INCL_BAN'] = tk.StringVar()
        incl_ban_check = ttk.Checkbutton(datos_gen_frame, text="Acreditar")
        incl_ban_check.grid(row=0, column=1, sticky='w', padx=5)
        incl_ban_check.configure(command=lambda: self.toggle_checkbox('INCL_BAN'))
        
        # Variables para controlar estado de checkboxes
        self.checkbox_states = {'INCL_ROL': False, 'INCL_BAN': False}
        
        ttk.Label(datos_gen_frame, text="Cargas:").grid(row=1, column=0, sticky='w', padx=5)
        self.otros_datos['CARGAS'] = tk.StringVar()
        ttk.Entry(datos_gen_frame, textvariable=self.otros_datos['CARGAS'], width=10).grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_gen_frame, text="Última liquidación:").grid(row=2, column=0, sticky='w', padx=5)
        self.otros_datos['ULTLIQ'] = tk.StringVar()
        ttk.Entry(datos_gen_frame, textvariable=self.otros_datos['ULTLIQ'], width=15).grid(row=2, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_gen_frame, text="Días Trabaj.:").grid(row=3, column=0, sticky='w', padx=5)
        self.otros_datos['DIAS_TRA'] = tk.StringVar()
        ttk.Entry(datos_gen_frame, textvariable=self.otros_datos['DIAS_TRA'], width=10).grid(row=3, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_gen_frame, text="Grupo Sanguíneo:").grid(row=4, column=0, sticky='w', padx=5)
        self.otros_datos['TIPO_SAN'] = tk.StringVar()
        sangre_combo = ttk.Combobox(datos_gen_frame, textvariable=self.otros_datos['TIPO_SAN'], 
                                   values=['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'], width=10)
        sangre_combo.grid(row=4, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_gen_frame, text="Forma Pago:").grid(row=5, column=0, sticky='w', padx=5)
        self.otros_datos['TIPO_PGO'] = tk.StringVar()
        pago_combo = ttk.Combobox(datos_gen_frame, textvariable=self.otros_datos['TIPO_PGO'], 
                                 values=['1', '2', '3', '4'], width=15)
        pago_combo.grid(row=5, column=1, padx=5, sticky='w')
        # 1=Efectivo, 2=Cheque, 3=Transferencia, 4=Otro
        
        # Cuentas Contables
        cuentas_frame = ttk.LabelFrame(frame, text="Cuentas Contables", padding=10)
        cuentas_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(cuentas_frame, text="Código cta:").grid(row=0, column=0, sticky='w', padx=5)
        self.otros_datos['CODCTA'] = tk.StringVar()
        ttk.Entry(cuentas_frame, textvariable=self.otros_datos['CODCTA'], width=15).grid(row=0, column=1, padx=5, sticky='w')
        
        ttk.Label(cuentas_frame, text="Cta departamento:").grid(row=1, column=0, sticky='w', padx=5)
        self.otros_datos['CTADPT'] = tk.StringVar()
        ttk.Entry(cuentas_frame, textvariable=self.otros_datos['CTADPT'], width=15).grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(cuentas_frame, text="Cta auxiliar:").grid(row=2, column=0, sticky='w', padx=5)
        self.otros_datos['CTAAUX'] = tk.StringVar()
        ttk.Entry(cuentas_frame, textvariable=self.otros_datos['CTAAUX'], width=15).grid(row=2, column=1, padx=5, sticky='w')
        
        # Información Bancaria
        banco_frame = ttk.LabelFrame(frame, text="Información Bancaria", padding=10)
        banco_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(banco_frame, text="Banco Afiliado:").grid(row=0, column=0, sticky='w', padx=5)
        self.otros_datos['RUTA4'] = tk.StringVar()
        banco_combo = ttk.Combobox(banco_frame, textvariable=self.otros_datos['RUTA4'], 
                                  values=['PRODUBANCO', 'PICHINCHA', 'GUAYAQUIL', 'PACIFICO'], width=20)
        banco_combo.grid(row=0, column=1, padx=5, sticky='w')
        
        ttk.Label(banco_frame, text="Cuenta Corriente:").grid(row=1, column=0, sticky='w', padx=5)
        self.otros_datos['CTA_CTE'] = tk.StringVar()
        ttk.Entry(banco_frame, textvariable=self.otros_datos['CTA_CTE'], width=20).grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(banco_frame, text="Cuenta Ahorros:").grid(row=2, column=0, sticky='w', padx=5)
        self.otros_datos['CTA_AHO'] = tk.StringVar()
        ttk.Entry(banco_frame, textvariable=self.otros_datos['CTA_AHO'], width=20).grid(row=2, column=1, padx=5, sticky='w')
    
    def crear_pestaña_certificados(self):
        """Crear pestaña de certificados"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Certificados")
        
        self.certificados = {}
        
        # Cuadros para certificados (simulando las imágenes)
        cert_frame = ttk.Frame(frame)
        cert_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for i, nombre in enumerate(['Ced Identidad', 'Cert Votación', 'Record Policial', 'Libreta Militar']):
            cert_box = ttk.Frame(cert_frame, relief='solid', borderwidth=1)
            cert_box.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            ttk.Label(cert_box, text=nombre, anchor='center').pack(pady=10)
            # Simulando imagen/cuadro vacío
            canvas_cert = tk.Canvas(cert_box, width=80, height=60, bg='white')
            canvas_cert.pack(pady=5)
        
        # Familiares
        fam_frame = ttk.LabelFrame(frame, text="Familiares", padding=10)
        fam_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(fam_frame, text="Nombres:").grid(row=0, column=0, sticky='w', padx=5)
        self.certificados['NOM_FAM'] = tk.StringVar()
        ttk.Entry(fam_frame, textvariable=self.certificados['NOM_FAM'], width=40).grid(row=0, column=1, padx=5, sticky='ew')
        
        ttk.Label(fam_frame, text="Dirección:").grid(row=1, column=0, sticky='w', padx=5)
        self.certificados['DIR_FAM'] = tk.StringVar()
        ttk.Entry(fam_frame, textvariable=self.certificados['DIR_FAM'], width=40).grid(row=1, column=1, padx=5, sticky='ew')
        
        ttk.Label(fam_frame, text="Teléfonos:").grid(row=2, column=0, sticky='w', padx=5)
        self.certificados['TEL_FAM'] = tk.StringVar()
        ttk.Entry(fam_frame, textvariable=self.certificados['TEL_FAM'], width=20).grid(row=2, column=1, padx=5, sticky='w')
        
        # No Familiares
        nofam_frame = ttk.LabelFrame(frame, text="No Familiares", padding=10)
        nofam_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(nofam_frame, text="Nombres:").grid(row=0, column=0, sticky='w', padx=5)
        self.certificados['NOM_NO_FAM'] = tk.StringVar()
        ttk.Entry(nofam_frame, textvariable=self.certificados['NOM_NO_FAM'], width=40).grid(row=0, column=1, padx=5, sticky='ew')
        
        ttk.Label(nofam_frame, text="Dirección:").grid(row=1, column=0, sticky='w', padx=5)
        self.certificados['DIR_NO_FAM'] = tk.StringVar()
        ttk.Entry(nofam_frame, textvariable=self.certificados['DIR_NO_FAM'], width=40).grid(row=1, column=1, padx=5, sticky='ew')
        
        ttk.Label(nofam_frame, text="Teléfonos:").grid(row=2, column=0, sticky='w', padx=5)
        self.certificados['TEL_NO_FAM'] = tk.StringVar()
        ttk.Entry(nofam_frame, textvariable=self.certificados['TEL_NO_FAM'], width=20).grid(row=2, column=1, padx=5, sticky='w')
    
    def crear_pestaña_referencias(self):
        """Crear pestaña de referencias"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Referencias")
        
        # Crear canvas y scrollbar
        canvas = tk.Canvas(frame)
        scrollbar_ref = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame_ref = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar_ref.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame_ref, anchor="nw")
        
        self.referencias = {}
        
        # Datos Referenciales
        datos_ref_frame = ttk.LabelFrame(scrollable_frame_ref, text="Datos Referenciales", padding=10)
        datos_ref_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        ttk.Label(datos_ref_frame, text="Cédula Militar:").grid(row=0, column=0, sticky='w', padx=5)
        self.referencias['CED_MIL'] = tk.StringVar()
        ttk.Entry(datos_ref_frame, textvariable=self.referencias['CED_MIL'], width=20).grid(row=0, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_ref_frame, text="Edad:").grid(row=0, column=2, sticky='w', padx=5)
        self.referencias['EDAD'] = tk.StringVar()
        ttk.Entry(datos_ref_frame, textvariable=self.referencias['EDAD'], width=10).grid(row=0, column=3, padx=5, sticky='w')
        
        ttk.Label(datos_ref_frame, text="Tipo de Sangre:").grid(row=1, column=0, sticky='w', padx=5)
        self.referencias['TIP_SAN'] = tk.StringVar()
        ttk.Entry(datos_ref_frame, textvariable=self.referencias['TIP_SAN'], width=10).grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_ref_frame, text="Número Certificado de Votación:").grid(row=2, column=0, sticky='w', padx=5)
        self.referencias['IDVOTA'] = tk.StringVar()
        ttk.Entry(datos_ref_frame, textvariable=self.referencias['IDVOTA'], width=20).grid(row=2, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_ref_frame, text="Licencia de Conducir:").grid(row=3, column=0, sticky='w', padx=5)
        self.referencias['LICCOND'] = tk.StringVar()
        ttk.Entry(datos_ref_frame, textvariable=self.referencias['LICCOND'], width=15).grid(row=3, column=1, padx=5, sticky='w')
        
        ttk.Label(datos_ref_frame, text="Código del IESS:").grid(row=4, column=0, sticky='w', padx=5)
        self.referencias['CODIESS'] = tk.StringVar()
        ttk.Entry(datos_ref_frame, textvariable=self.referencias['CODIESS'], width=20).grid(row=4, column=1, padx=5, sticky='w')
        
        # Estudios
        estudios_frame = ttk.LabelFrame(scrollable_frame_ref, text="Estudios", padding=10)
        estudios_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Checkboxes para niveles de educación
        self.referencias['PRIMARIA'] = tk.BooleanVar()
        ttk.Checkbutton(estudios_frame, text="Primaria", 
                       variable=self.referencias['PRIMARIA']).grid(row=0, column=0, sticky='w', padx=5)
        
        self.referencias['SECUNDARIA'] = tk.BooleanVar()
        ttk.Checkbutton(estudios_frame, text="Secundaria", 
                       variable=self.referencias['SECUNDARIA']).grid(row=0, column=1, sticky='w', padx=5)
        
        self.referencias['EST_SUP'] = tk.BooleanVar()
        ttk.Checkbutton(estudios_frame, text="Universidad", 
                       variable=self.referencias['EST_SUP']).grid(row=0, column=2, sticky='w', padx=5)
        
        ttk.Label(estudios_frame, text="Título:").grid(row=1, column=0, sticky='w', padx=5)
        self.referencias['TITULO'] = tk.StringVar()
        ttk.Entry(estudios_frame, textvariable=self.referencias['TITULO'], width=30).grid(row=1, column=1, columnspan=2, padx=5, sticky='ew')
        
        ttk.Label(estudios_frame, text="Años de Estudio:").grid(row=2, column=0, sticky='w', padx=5)
        self.referencias['ANIO_EST'] = tk.StringVar()
        ttk.Entry(estudios_frame, textvariable=self.referencias['ANIO_EST'], width=10).grid(row=2, column=1, padx=5, sticky='w')
        
        # Servicios
        servicios_frame = ttk.LabelFrame(scrollable_frame_ref, text="Servicios", padding=10)
        servicios_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        ttk.Label(servicios_frame, text="Tipo:").grid(row=0, column=0, sticky='w', padx=5)
        self.referencias['RPCAM5'] = tk.StringVar()
        ttk.Entry(servicios_frame, textvariable=self.referencias['RPCAM5'], width=30).grid(row=0, column=1, padx=5, sticky='w')
        
        ttk.Label(servicios_frame, text="Contrato de Inspectoría:").grid(row=1, column=0, sticky='w', padx=5)
        self.referencias['CONTINS'] = tk.StringVar()
        ttk.Entry(servicios_frame, textvariable=self.referencias['CONTINS'], width=30).grid(row=1, column=1, padx=5, sticky='w')
        
        ttk.Label(servicios_frame, text="GIPASE:").grid(row=2, column=0, sticky='w', padx=5)
        self.referencias['RPCAM3'] = tk.StringVar()
        ttk.Entry(servicios_frame, textvariable=self.referencias['RPCAM3'], width=40).grid(row=2, column=1, padx=5, sticky='ew')
        
        ttk.Label(servicios_frame, text="AFIS:").grid(row=3, column=0, sticky='w', padx=5)
        self.referencias['RPCAM4'] = tk.StringVar()
        ttk.Entry(servicios_frame, textvariable=self.referencias['RPCAM4'], width=40).grid(row=3, column=1, padx=5, sticky='ew')
        
        ttk.Label(servicios_frame, text="CERTIFICADOS:").grid(row=4, column=0, sticky='w', padx=5)
        self.referencias['certificados'] = tk.StringVar()
        ttk.Entry(servicios_frame, textvariable=self.referencias['certificados'], width=40).grid(row=4, column=1, padx=5, sticky='ew')
        
        ttk.Label(servicios_frame, text="Reentrenamiento:").grid(row=5, column=0, sticky='w', padx=5)
        self.referencias['reentrenamiento'] = tk.StringVar()
        ttk.Entry(servicios_frame, textvariable=self.referencias['reentrenamiento'], width=40).grid(row=5, column=1, padx=5, sticky='ew')
        
        ttk.Label(servicios_frame, text="Vacuna:").grid(row=6, column=0, sticky='w', padx=5)
        self.referencias['vacuna'] = tk.StringVar()
        ttk.Entry(servicios_frame, textvariable=self.referencias['vacuna'], width=40).grid(row=6, column=1, padx=5, sticky='ew')
        
        # Información adicional
        adicional_frame = ttk.LabelFrame(scrollable_frame_ref, text="Información Adicional", padding=10)
        adicional_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        ttk.Label(adicional_frame, text="Cert. Violencia Intrafamiliar:").grid(row=0, column=0, sticky='w', padx=5)
        self.referencias['CERTVINF'] = tk.StringVar()
        ttk.Entry(adicional_frame, textvariable=self.referencias['CERTVINF'], width=50).grid(row=0, column=1, padx=5, sticky='ew')
        
        ttk.Label(adicional_frame, text="Maniobras:").grid(row=1, column=0, sticky='w', padx=5)
        self.referencias['MANIOBRAS'] = tk.StringVar()
        ttk.Entry(adicional_frame, textvariable=self.referencias['MANIOBRAS'], width=50).grid(row=1, column=1, padx=5, sticky='ew')
        
        ttk.Label(adicional_frame, text="No. Afiliación IESS:").grid(row=2, column=0, sticky='w', padx=5)
        self.referencias['NUM_AFIL'] = tk.StringVar()
        ttk.Entry(adicional_frame, textvariable=self.referencias['NUM_AFIL'], width=20).grid(row=2, column=1, padx=5, sticky='w')
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_ref.pack(side="right", fill="y")
    
    def crear_panel_botones(self, parent):
        """Crear panel inferior con botones y estado"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botones principales
        ttk.Button(button_frame, text="Nuevo", command=self.nuevo_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Modificar", command=self.modificar_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Buscar", command=self.buscar_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Imprimir", command=self.imprimir_empleado).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Crear Empleado como Proveedor", command=self.crear_empleado_proveedor).pack(side=tk.LEFT, padx=5)
        
        # Botones de acción
        action_frame = ttk.Frame(button_frame)
        action_frame.pack(side=tk.RIGHT)
        ttk.Button(action_frame, text="Aceptar", command=self.guardar_cambios).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancelar", command=self.cancelar_cambios).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Salir", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_label = ttk.Label(button_frame, text="Listo", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
    
    def buscar_por_cedula(self, event=None):
        """Buscar empleado por cédula"""
        cedula = self.cedula_var.get().strip()
        if not cedula:
            messagebox.showwarning("Advertencia", "Ingrese una cédula para buscar")
            return
        
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM RPEMPLEA WHERE CEDULA = ?"
            cursor.execute(query, (cedula,))
            empleado = cursor.fetchone()
            
            if empleado:
                self.cargar_datos_empleado(empleado, cursor.description)
                self.status_label.config(text=f"Empleado encontrado: {cedula}", foreground="green")
            else:
                messagebox.showinfo("No encontrado", f"No se encontró empleado con cédula: {cedula}")
                self.status_label.config(text="Empleado no encontrado", foreground="orange")
            
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar empleado: {e}")
    
    def buscar_por_codigo(self, event=None):
        """Buscar empleado por código"""
        codigo = self.codigo_var.get().strip()
        if not codigo:
            messagebox.showwarning("Advertencia", "Ingrese un código para buscar")
            return
        
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM RPEMPLEA WHERE EMPLEADO = ?"
            cursor.execute(query, (codigo,))
            empleado = cursor.fetchone()
            
            if empleado:
                self.cargar_datos_empleado(empleado, cursor.description)
                self.status_label.config(text=f"Empleado encontrado: {codigo}", foreground="green")
            else:
                messagebox.showinfo("No encontrado", f"No se encontró empleado con código: {codigo}")
                self.status_label.config(text="Empleado no encontrado", foreground="orange")
            
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar empleado: {e}")
    
    def cargar_datos_empleado(self, empleado, descripcion):
        """Cargar datos del empleado en la interfaz"""
        # Crear diccionario con nombres de columnas
        columnas = [col[0] for col in descripcion]
        datos = dict(zip(columnas, empleado))
        
        # Cargar datos generales
        for campo, var in self.datos_generales.items():
            if campo in datos and datos[campo] is not None:
                if isinstance(datos[campo], datetime):
                    var.set(datos[campo].strftime("%d/%m/%Y"))
                else:
                    var.set(str(datos[campo]))
        
        # Cargar ingresos
        for campo, var in self.ingresos.items():
            if campo in datos and datos[campo] is not None:
                var.set(str(datos[campo]))
        
        # Cargar otros datos
        for campo, var in self.otros_datos.items():
            if campo in datos and datos[campo] is not None:
                if campo in ['INCL_ROL', 'INCL_BAN']:
                    # Manejar checkboxes especiales S/N
                    valor = str(datos[campo])
                    var.set(valor)
                    self.checkbox_states[campo] = (valor == 'S')
                else:
                    var.set(str(datos[campo]))
        
        # Cargar certificados
        for campo, var in self.certificados.items():
            if campo in datos and datos[campo] is not None:
                var.set(str(datos[campo]))
        
        # Cargar referencias
        for campo, var in self.referencias.items():
            if campo in datos and datos[campo] is not None:
                if campo in ['PRIMARIA', 'SECUNDARIA', 'EST_SUP'] and isinstance(var, tk.BooleanVar):
                    var.set(bool(datos[campo]))
                else:
                    var.set(str(datos[campo]))
        
        # Cargar observaciones
        if 'OBSERV' in datos and datos['OBSERV'] is not None:
            self.observaciones_text.delete(1.0, tk.END)
            self.observaciones_text.insert(1.0, str(datos['OBSERV']))
        
        self.empleado_actual = datos
        self.datos_originales = datos.copy()  # Guardar copia de datos originales
        self.datos_modificados = False
        self.configurar_eventos_cambio()  # Configurar eventos para detectar cambios
    
    def nuevo_empleado(self):
        """Limpiar formulario para nuevo empleado"""
        # Limpiar todas las variables
        for var in self.datos_generales.values():
            var.set("")
        
        for var in self.ingresos.values():
            var.set("")
        
        for campo, var in self.otros_datos.items():
            if campo in ['INCL_ROL', 'INCL_BAN']:
                var.set('N')
                self.checkbox_states[campo] = False
            else:
                var.set("")
        
        for var in self.certificados.values():
            var.set("")
        
        for campo, var in self.referencias.items():
            if campo in ['PRIMARIA', 'SECUNDARIA', 'EST_SUP'] and isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set("")
        
        self.observaciones_text.delete(1.0, tk.END)
        self.empleado_actual = None
        self.datos_originales = None
        self.datos_modificados = False
        self.status_label.config(text="Nuevo empleado", foreground="blue")
    
    def configurar_eventos_cambio(self):
        """Configurar eventos para detectar cambios en los campos"""
        # Configurar eventos para datos generales
        for var in self.datos_generales.values():
            var.trace('w', self.marcar_modificado)
        
        # Configurar eventos para ingresos
        for var in self.ingresos.values():
            var.trace('w', self.marcar_modificado)
        
        # Configurar eventos para otros datos
        for var in self.otros_datos.values():
            if hasattr(var, 'trace'):
                var.trace('w', self.marcar_modificado)
        
        # Configurar eventos para certificados
        for var in self.certificados.values():
            var.trace('w', self.marcar_modificado)
        
        # Configurar eventos para referencias
        for var in self.referencias.values():
            if hasattr(var, 'trace'):
                var.trace('w', self.marcar_modificado)
        
        # Configurar evento para observaciones
        self.observaciones_text.bind('<KeyPress>', self.marcar_modificado)
        self.observaciones_text.bind('<Button-1>', self.marcar_modificado)
    
    def marcar_modificado(self, *args):
        """Marcar que los datos han sido modificados"""
        if not self.datos_modificados:
            self.datos_modificados = True
            self.status_label.config(text="Datos modificados - Sin guardar", foreground="orange")
    
    def confirmar_guardado(self, tipo_operacion):
        """Mostrar confirmación antes de guardar"""
        if tipo_operacion == "actualizar":
            nombre_completo = f"{self.datos_generales['NOMBRES'].get()} {self.datos_generales['APELLIDOS'].get()}"
            mensaje = (
                f"¿Está seguro de ACTUALIZAR los datos del empleado?\n\n"
                f"👤 Empleado: {nombre_completo}\n"
                f"🆔 Código: {self.datos_generales['EMPLEADO'].get()}\n"
                f"📄 Cédula: {self.datos_generales['CEDULA'].get()}\n\n"
                f"⚠️  ATENCIÓN: Esta acción modificará permanentemente los datos en la base de datos.\n\n"
                f"¿Desea continuar?"
            )
        else:  # crear
            nombre_completo = f"{self.datos_generales['NOMBRES'].get()} {self.datos_generales['APELLIDOS'].get()}"
            mensaje = (
                f"¿Está seguro de CREAR un nuevo empleado?\n\n"
                f"👤 Empleado: {nombre_completo}\n"
                f"🆔 Código: {self.datos_generales['EMPLEADO'].get()}\n"
                f"📄 Cédula: {self.datos_generales['CEDULA'].get()}\n\n"
                f"⚠️  ATENCIÓN: Esta acción agregará un nuevo registro a la base de datos.\n\n"
                f"¿Desea continuar?"
            )
        
        return messagebox.askyesno("Confirmar Operación", mensaje, icon='warning')
    
    def guardar_cambios(self):
        """Guardar cambios en la base de datos con confirmación"""
        if not self.conn:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return False
        
        # Validaciones básicas
        if not self.datos_generales['EMPLEADO'].get():
            messagebox.showerror("Error", "El código de empleado es obligatorio")
            return False
        
        if not self.datos_generales['CEDULA'].get():
            messagebox.showerror("Error", "La cédula es obligatoria")
            return False
        
        if not self.datos_generales['NOMBRES'].get():
            messagebox.showerror("Error", "Los nombres son obligatorios")
            return False
        
        if not self.datos_generales['APELLIDOS'].get():
            messagebox.showerror("Error", "Los apellidos son obligatorios")
            return False
        
        # Determinar tipo de operación
        tipo_operacion = "actualizar" if self.empleado_actual else "crear"
        
        # Mostrar confirmación
        if not self.confirmar_guardado(tipo_operacion):
            return False
        
        try:
            # Recopilar todos los datos
            datos = {}
            
            # Datos generales
            for campo, var in self.datos_generales.items():
                datos[campo] = var.get() if var.get() else None
            
            # Ingresos
            for campo, var in self.ingresos.items():
                valor = var.get()
                if valor:
                    try:
                        datos[campo] = float(valor) if valor.replace('.', '').isdigit() else valor
                    except:
                        datos[campo] = valor
                else:
                    datos[campo] = None
            
            # Otros datos
            for campo, var in self.otros_datos.items():
                if campo in ['INCL_ROL', 'INCL_BAN']:
                    datos[campo] = var.get() if var.get() in ['S', 'N'] else 'N'
                else:
                    datos[campo] = var.get() if var.get() else None
            
            # Certificados
            for campo, var in self.certificados.items():
                datos[campo] = var.get() if var.get() else None
            
            # Referencias
            for campo, var in self.referencias.items():
                if campo in ['PRIMARIA', 'SECUNDARIA', 'EST_SUP'] and isinstance(var, tk.BooleanVar):
                    datos[campo] = 1 if var.get() else 0
                else:
                    datos[campo] = var.get() if var.get() else None
            
            # Observaciones
            datos['OBSERV'] = self.observaciones_text.get(1.0, tk.END).strip()
            
            cursor = self.conn.cursor()
            
            if self.empleado_actual:  # Actualizar
                # Verificar si el empleado aún existe
                cursor.execute("SELECT COUNT(*) FROM RPEMPLEA WHERE EMPLEADO = ?", (datos['EMPLEADO'],))
                if cursor.fetchone()[0] == 0:
                    messagebox.showerror("Error", "El empleado ya no existe en la base de datos")
                    cursor.close()
                    return False
                
                # Construir query de actualización
                campos = [f"{campo} = ?" for campo in datos.keys() if campo != 'EMPLEADO']
                valores = [datos[campo] for campo in datos.keys() if campo != 'EMPLEADO']
                valores.append(datos['EMPLEADO'])
                
                query = f"UPDATE RPEMPLEA SET {', '.join(campos)} WHERE EMPLEADO = ?"
                cursor.execute(query, valores)
                
                mensaje = f"✅ Empleado {datos['EMPLEADO']} actualizado correctamente"
                
            else:  # Insertar nuevo
                # Verificar si ya existe un empleado con el mismo código
                cursor.execute("SELECT COUNT(*) FROM RPEMPLEA WHERE EMPLEADO = ?", (datos['EMPLEADO'],))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", f"Ya existe un empleado con código {datos['EMPLEADO']}")
                    cursor.close()
                    return False
                
                # Verificar si ya existe un empleado con la misma cédula
                cursor.execute("SELECT COUNT(*) FROM RPEMPLEA WHERE CEDULA = ?", (datos['CEDULA'],))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", f"Ya existe un empleado con cédula {datos['CEDULA']}")
                    cursor.close()
                    return False
                
                campos = list(datos.keys())
                placeholders = ', '.join(['?'] * len(campos))
                valores = list(datos.values())
                
                query = f"INSERT INTO RPEMPLEA ({', '.join(campos)}) VALUES ({placeholders})"
                cursor.execute(query, valores)
                
                mensaje = f"✅ Empleado {datos['EMPLEADO']} creado correctamente"
            
            self.conn.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", mensaje)
            self.status_label.config(text=mensaje, foreground="green")
            
            # Actualizar estado
            self.empleado_actual = datos if not self.empleado_actual else datos
            self.datos_originales = datos.copy()
            self.datos_modificados = False
            
            # Recargar lista de empleados
            self.cargar_lista_empleados()
            
            return True
            
        except Exception as e:
            error_msg = f"Error al guardar: {str(e)}"
            messagebox.showerror("Error", error_msg)
            if self.conn:
                self.conn.rollback()
            return False
    
    def edicion_masiva(self):
        """Abrir ventana para edición masiva"""
        EdicionMasivaWindow(self.root, self.conn)
    
    def modificar_empleado(self):
        """Habilitar edición del empleado actual"""
        if not self.empleado_actual:
            messagebox.showwarning("Advertencia", "No hay empleado seleccionado")
            return
        self.status_label.config(text="Modo edición", foreground="blue")
    
    def eliminar_empleado(self):
        """Eliminar empleado actual con confirmación"""
        if not self.empleado_actual:
            messagebox.showwarning("Advertencia", "No hay empleado seleccionado")
            return
        
        nombre_completo = f"{self.empleado_actual['NOMBRES']} {self.empleado_actual['APELLIDOS']}"
        
        # Confirmación de eliminación
        mensaje = (
            f"¿Está ABSOLUTAMENTE SEGURO de eliminar al empleado?\n\n"
            f"👤 Empleado: {nombre_completo}\n"
            f"🆔 Código: {self.empleado_actual['EMPLEADO']}\n"
            f"📄 Cédula: {self.empleado_actual['CEDULA']}\n\n"
            f"🚨 ADVERTENCIA CRÍTICA:\n"
            f"• Esta acción es IRREVERSIBLE\n"
            f"• Se perderán TODOS los datos del empleado\n"
            f"• El historial laboral se eliminará permanentemente\n\n"
            f"¿Desea continuar con la eliminación?"
        )
        
        respuesta = messagebox.askyesno("⚠️ CONFIRMAR ELIMINACIÓN", mensaje, icon='warning')
        
        if not respuesta:
            return
        
        # Segunda confirmación
        segunda_confirmacion = messagebox.askyesno(
            "⚠️ CONFIRMACIÓN FINAL", 
            f"ÚLTIMA OPORTUNIDAD:\n\n"
            f"Va a eliminar permanentemente a:\n"
            f"{nombre_completo} (Código: {self.empleado_actual['EMPLEADO']})\n\n"
            f"¿Está 100% seguro?",
            icon='error'
        )
        
        if not segunda_confirmacion:
            return
        
        try:
            cursor = self.conn.cursor()
            query = "DELETE FROM RPEMPLEA WHERE EMPLEADO = ?"
            cursor.execute(query, (self.empleado_actual['EMPLEADO'],))
            
            if cursor.rowcount == 0:
                messagebox.showerror("Error", "No se pudo eliminar el empleado. Posiblemente ya fue eliminado.")
                cursor.close()
                return
            
            self.conn.commit()
            cursor.close()
            
            messagebox.showinfo("Éxito", f"✅ Empleado {nombre_completo} eliminado correctamente")
            
            # Limpiar formulario y recargar lista
            self.nuevo_empleado()
            self.cargar_lista_empleados()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar empleado: {e}")
            if self.conn:
                self.conn.rollback()
    
    def buscar_empleado(self):
        """Abrir ventana de búsqueda avanzada"""
        # Implementar búsqueda avanzada
        pass
    
    def imprimir_empleado(self):
        """Imprimir ficha del empleado"""
        if not self.empleado_actual:
            messagebox.showwarning("Advertencia", "No hay empleado seleccionado")
            return
        messagebox.showinfo("Información", "Función de impresión no implementada")
    
    def crear_empleado_proveedor(self):
        """Crear empleado como proveedor"""
        if not self.empleado_actual:
            messagebox.showwarning("Advertencia", "No hay empleado seleccionado")
            return
        messagebox.showinfo("Información", "Función no implementada")
    
    def cancelar_cambios(self):
        """Cancelar cambios y recargar datos originales"""
        if self.datos_modificados:
            respuesta = messagebox.askyesno(
                "Cancelar Cambios",
                "¿Está seguro de cancelar los cambios?\n\n"
                "⚠️ Se perderán todas las modificaciones no guardadas."
            )
            if not respuesta:
                return
        
        if self.empleado_actual and self.datos_originales:
            # Recargar datos originales
            self.cargar_datos_desde_dict(self.datos_originales)
            self.datos_modificados = False
            self.status_label.config(text="Cambios cancelados - Datos originales restaurados", foreground="blue")
        else:
            self.nuevo_empleado()
    
    def cargar_datos_desde_dict(self, datos):
        """Cargar datos desde un diccionario a la interfaz"""
        # Cargar datos generales
        for campo, var in self.datos_generales.items():
            if campo in datos and datos[campo] is not None:
                if isinstance(datos[campo], datetime):
                    var.set(datos[campo].strftime("%d/%m/%Y"))
                else:
                    var.set(str(datos[campo]))
            else:
                var.set("")
        
        # Cargar ingresos
        for campo, var in self.ingresos.items():
            if campo in datos and datos[campo] is not None:
                var.set(str(datos[campo]))
            else:
                var.set("")
        
        # Cargar otros datos
        for campo, var in self.otros_datos.items():
            if campo in datos and datos[campo] is not None:
                if campo in ['INCL_ROL', 'INCL_BAN']:
                    valor = str(datos[campo])
                    var.set(valor)
                    self.checkbox_states[campo] = (valor == 'S')
                else:
                    var.set(str(datos[campo]))
            else:
                if campo in ['INCL_ROL', 'INCL_BAN']:
                    var.set('N')
                    self.checkbox_states[campo] = False
                else:
                    var.set("")
        
        # Cargar certificados
        for campo, var in self.certificados.items():
            if campo in datos and datos[campo] is not None:
                var.set(str(datos[campo]))
            else:
                var.set("")
        
        # Cargar referencias
        for campo, var in self.referencias.items():
            if campo in datos and datos[campo] is not None:
                if campo in ['PRIMARIA', 'SECUNDARIA', 'EST_SUP'] and isinstance(var, tk.BooleanVar):
                    var.set(bool(datos[campo]))
                else:
                    var.set(str(datos[campo]))
            else:
                if campo in ['PRIMARIA', 'SECUNDARIA', 'EST_SUP'] and isinstance(var, tk.BooleanVar):
                    var.set(False)
                else:
                    var.set("")
        
        # Cargar observaciones
        self.observaciones_text.delete(1.0, tk.END)
        if 'OBSERV' in datos and datos['OBSERV'] is not None:
            self.observaciones_text.insert(1.0, str(datos['OBSERV']))


class EdicionMasivaWindow:
    def __init__(self, parent, conn):
        self.conn = conn
        self.window = tk.Toplevel(parent)
        self.window.title("Edición Masiva de Empleados")
        self.window.geometry("600x400")
        self.window.grab_set()
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crear interfaz para edición masiva"""
        # Marco principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Selección de campo a modificar
        ttk.Label(main_frame, text="Campo a modificar:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.campo_var = tk.StringVar()
        campos_combo = ttk.Combobox(main_frame, textvariable=self.campo_var, width=20)
        campos_combo['values'] = ('TIPO_SAN', 'ESTADO', 'DEPTO', 'SECCION', 'CARGO', 'SUELDO', 'PROVINCIA', 'CANTON')
        campos_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Nuevo valor
        ttk.Label(main_frame, text="Nuevo valor:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        self.nuevo_valor_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.nuevo_valor_var, width=25).grid(row=1, column=1, padx=5, pady=5)
        
        # Filtros
        filtros_frame = ttk.LabelFrame(main_frame, text="Filtros (opcional)", padding=10)
        filtros_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=10)
        
        ttk.Label(filtros_frame, text="Código empleado específico:").grid(row=0, column=0, sticky='w', padx=5)
        self.codigo_filtro_var = tk.StringVar()
        ttk.Entry(filtros_frame, textvariable=self.codigo_filtro_var, width=15).grid(row=0, column=1, padx=5)
        
        ttk.Label(filtros_frame, text="Departamento:").grid(row=1, column=0, sticky='w', padx=5)
        self.depto_filtro_var = tk.StringVar()
        ttk.Entry(filtros_frame, textvariable=self.depto_filtro_var, width=15).grid(row=1, column=1, padx=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Vista Previa", command=self.vista_previa).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ejecutar", command=self.ejecutar_masiva).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Lista de resultados
        self.tree = ttk.Treeview(main_frame, columns=('codigo', 'nombre', 'valor_actual'), show='headings', height=10)
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('valor_actual', text='Valor Actual')
        self.tree.grid(row=4, column=0, columnspan=3, sticky='ew', pady=10)
    
    def vista_previa(self):
        """Mostrar vista previa de registros que serán afectados"""
        campo = self.campo_var.get()
        if not campo:
            messagebox.showwarning("Advertencia", "Seleccione un campo")
            return
        
        try:
            # Limpiar tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Construir query
            query = f"SELECT EMPLEADO, NOMBRES + ' ' + APELLIDOS as NOMBRE, {campo} FROM RPEMPLEA WHERE 1=1"
            params = []
            
            if self.codigo_filtro_var.get():
                query += " AND EMPLEADO = ?"
                params.append(self.codigo_filtro_var.get())
            
            if self.depto_filtro_var.get():
                query += " AND DEPTO = ?"
                params.append(self.depto_filtro_var.get())
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            for row in resultados:
                self.tree.insert('', 'end', values=row)
            
            cursor.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en vista previa: {e}")
    
    def ejecutar_masiva(self):
        """Ejecutar la actualización masiva"""
        campo = self.campo_var.get()
        nuevo_valor = self.nuevo_valor_var.get()
        
        if not campo or not nuevo_valor:
            messagebox.showwarning("Advertencia", "Complete todos los campos")
            return
        
        respuesta = messagebox.askyesno("Confirmar", 
                                       f"¿Está seguro de actualizar el campo {campo} a '{nuevo_valor}' para los registros seleccionados?")
        
        if respuesta:
            try:
                # Construir query de actualización
                query = f"UPDATE RPEMPLEA SET {campo} = ? WHERE 1=1"
                params = [nuevo_valor]
                
                if self.codigo_filtro_var.get():
                    query += " AND EMPLEADO = ?"
                    params.append(self.codigo_filtro_var.get())
                
                if self.depto_filtro_var.get():
                    query += " AND DEPTO = ?"
                    params.append(self.depto_filtro_var.get())
                
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                registros_afectados = cursor.rowcount
                self.conn.commit()
                cursor.close()
                
                messagebox.showinfo("Éxito", f"Se actualizaron {registros_afectados} registros")
                self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al ejecutar actualización: {e}")
                if self.conn:
                    self.conn.rollback()


class VistaCompletaWindow:
    """Ventana para mostrar vista completa de todos los empleados"""
    def __init__(self, parent, conn):
        self.conn = conn
        self.window = tk.Toplevel(parent)
        self.window.title("Vista Completa - Todos los Empleados")
        self.window.geometry("1000x600")
        self.window.grab_set()
        
        self.crear_interfaz()
        self.cargar_todos_empleados()
    
    def crear_interfaz(self):
        """Crear interfaz de vista completa"""
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior con controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Búsqueda rápida:").pack(side=tk.LEFT, padx=(0, 5))
        self.busqueda_var = tk.StringVar()
        busqueda_entry = ttk.Entry(control_frame, textvariable=self.busqueda_var, width=30)
        busqueda_entry.pack(side=tk.LEFT, padx=(0, 10))
        busqueda_entry.bind('<KeyRelease>', self.filtrar_busqueda)
        
        ttk.Button(control_frame, text="Exportar a Excel", command=self.exportar_excel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="Refrescar", command=self.cargar_todos_empleados).pack(side=tk.RIGHT, padx=5)
        
        # Treeview con todos los empleados
        columns = ('codigo', 'cedula', 'apellidos', 'nombres', 'cargo', 'depto', 'estado', 'sueldo')
        self.tree_completo = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        self.tree_completo.heading('codigo', text='Código')
        self.tree_completo.heading('cedula', text='Cédula')
        self.tree_completo.heading('apellidos', text='Apellidos')
        self.tree_completo.heading('nombres', text='Nombres')
        self.tree_completo.heading('cargo', text='Cargo')
        self.tree_completo.heading('depto', text='Depto')
        self.tree_completo.heading('estado', text='Estado')
        self.tree_completo.heading('sueldo', text='Sueldo')
        
        # Anchos de columnas
        self.tree_completo.column('codigo', width=80, anchor='center')
        self.tree_completo.column('cedula', width=100, anchor='center')
        self.tree_completo.column('apellidos', width=150)
        self.tree_completo.column('nombres', width=150)
        self.tree_completo.column('cargo', width=100)
        self.tree_completo.column('depto', width=80, anchor='center')
        self.tree_completo.column('estado', width=80, anchor='center')
        self.tree_completo.column('sueldo', width=100, anchor='e')
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree_completo.yview)
        scrollbar_h = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree_completo.xview)
        self.tree_completo.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Empaquetar
        self.tree_completo.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        
        # Frame inferior con estadísticas
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Cargando estadísticas...")
        self.stats_label.pack(side=tk.LEFT)
        
        ttk.Button(stats_frame, text="Cerrar", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def cargar_todos_empleados(self):
        """Cargar todos los empleados"""
        if not self.conn:
            return
        
        try:
            # Limpiar tree
            for item in self.tree_completo.get_children():
                self.tree_completo.delete(item)
            
            query = """
            SELECT EMPLEADO, CEDULA, APELLIDOS, NOMBRES, CARGO, DEPTO, ESTADO, SUELDO
            FROM RPEMPLEA 
            ORDER BY APELLIDOS, NOMBRES
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query)
            empleados = cursor.fetchall()
            
            total_empleados = 0
            activos = 0
            total_sueldos = 0
            
            for empleado in empleados:
                codigo, cedula, apellidos, nombres, cargo, depto, estado, sueldo = empleado
                
                # Formatear sueldo
                sueldo_fmt = f"${sueldo:,.2f}" if sueldo else "$0.00"
                
                self.tree_completo.insert('', 'end', values=(
                    codigo, cedula, apellidos, nombres, cargo or "", depto or "", estado or "", sueldo_fmt
                ))
                
                total_empleados += 1
                if estado == 'ACT':
                    activos += 1
                if sueldo:
                    total_sueldos += float(sueldo)
            
            cursor.close()
            
            # Actualizar estadísticas
            inactivos = total_empleados - activos
            promedio_sueldo = total_sueldos / activos if activos > 0 else 0
            
            stats_text = (
                f"Total: {total_empleados} empleados | "
                f"Activos: {activos} | "
                f"Inactivos: {inactivos} | "
                f"Nómina Total: ${total_sueldos:,.2f} | "
                f"Promedio: ${promedio_sueldo:,.2f}"
            )
            self.stats_label.config(text=stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar empleados: {e}")
    
    def filtrar_busqueda(self, event=None):
        """Filtrar empleados por búsqueda"""
        termino = self.busqueda_var.get().lower()
        
        # Mostrar/ocultar items según búsqueda
        for item in self.tree_completo.get_children():
            valores = self.tree_completo.item(item)['values']
            mostrar = any(termino in str(valor).lower() for valor in valores)
            
            if mostrar:
                self.tree_completo.reattach(item, '', 'end')
            else:
                self.tree_completo.detach(item)
    
    def exportar_excel(self):
        """Exportar datos a Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Recopilar datos
            datos = []
            for item in self.tree_completo.get_children():
                valores = self.tree_completo.item(item)['values']
                datos.append(valores)
            
            if not datos:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            # Crear DataFrame
            columnas = ['Código', 'Cédula', 'Apellidos', 'Nombres', 'Cargo', 'Depto', 'Estado', 'Sueldo']
            df = pd.DataFrame(datos, columns=columnas)
            
            # Guardar archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"Empleados_Vista_Completa_{timestamp}.xlsx"
            
            df.to_excel(archivo, index=False, sheet_name='Empleados')
            
            messagebox.showinfo("Éxito", f"Archivo exportado: {archivo}")
            
        except ImportError:
            messagebox.showerror("Error", "Se requiere pandas para exportar a Excel")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")


def main():
    root = tk.Tk()
    app = SistemaGestionEmpleados(root)
    root.mainloop()

if __name__ == "__main__":
    main()

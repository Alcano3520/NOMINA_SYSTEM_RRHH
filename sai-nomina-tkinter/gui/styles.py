"""Configuración de estilos para la aplicación"""

import tkinter as tk
from tkinter import ttk
from config import Config

def setup_styles(root):
    """Configurar estilos TTK personalizados"""
    style = ttk.Style(root)

    # Configurar tema base
    style.theme_use('clam')

    # Colores base
    style.configure('.',
        background=Config.COLORS['background'],
        foreground=Config.COLORS['text'],
        fieldbackground=Config.COLORS['surface'],
        font=Config.FONTS['default']
    )

    # Frame principal con gradiente
    style.configure('Main.TFrame',
        background=Config.COLORS['background'],
        relief='flat',
        borderwidth=0
    )

    # Frame de superficie (cards)
    style.configure('Card.TFrame',
        background=Config.COLORS['surface'],
        relief='flat',
        borderwidth=1
    )

    # Frame de gradiente primary
    style.configure('Primary.TFrame',
        background=Config.COLORS['primary'],
        relief='flat',
        borderwidth=0
    )

    # Frame de gradiente secondary
    style.configure('Secondary.TFrame',
        background=Config.COLORS['secondary'],
        relief='flat',
        borderwidth=0
    )

    # Botones primarios
    style.configure('Primary.TButton',
        background=Config.COLORS['primary'],
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        relief='flat',
        padding=(15, 10),
        font=Config.FONTS['default']
    )
    style.map('Primary.TButton',
        background=[
            ('active', Config.COLORS['primary_dark']),
            ('pressed', Config.COLORS['secondary'])
        ],
        relief=[('pressed', 'flat')]
    )

    # Botones secundarios
    style.configure('Secondary.TButton',
        background=Config.COLORS['secondary'],
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        relief='flat',
        padding=(15, 10),
        font=Config.FONTS['default']
    )
    style.map('Secondary.TButton',
        background=[
            ('active', Config.COLORS['secondary_dark']),
            ('pressed', Config.COLORS['primary'])
        ]
    )

    # Botón de éxito
    style.configure('Success.TButton',
        background=Config.COLORS['success'],
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        relief='flat',
        padding=(15, 10),
        font=Config.FONTS['default']
    )
    style.map('Success.TButton',
        background=[('active', '#38a169')]
    )

    # Botón de advertencia
    style.configure('Warning.TButton',
        background=Config.COLORS['warning'],
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        relief='flat',
        padding=(15, 10),
        font=Config.FONTS['default']
    )
    style.map('Warning.TButton',
        background=[('active', '#d69e2e')]
    )

    # Botón de peligro
    style.configure('Danger.TButton',
        background=Config.COLORS['danger'],
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        relief='flat',
        padding=(15, 10),
        font=Config.FONTS['default']
    )
    style.map('Danger.TButton',
        background=[('active', '#e53e3e')]
    )

    # Botón de información
    style.configure('Info.TButton',
        background=Config.COLORS['info'],
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        relief='flat',
        padding=(15, 10),
        font=Config.FONTS['default']
    )
    style.map('Info.TButton',
        background=[('active', '#3182ce')]
    )

    # Labels de encabezado
    style.configure('Heading.TLabel',
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['secondary'],
        font=Config.FONTS['heading']
    )

    # Labels de subtítulo
    style.configure('Subheading.TLabel',
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['text'],
        font=Config.FONTS['subheading']
    )

    # Labels pequeños
    style.configure('Small.TLabel',
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['text_light'],
        font=Config.FONTS['small']
    )

    # Labels para sidebar
    style.configure('Sidebar.TLabel',
        background=Config.COLORS['secondary'],
        foreground='white',
        font=Config.FONTS['default']
    )

    # Entries personalizados
    style.configure('Custom.TEntry',
        fieldbackground=Config.COLORS['surface'],
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['text'],
        borderwidth=1,
        relief='solid',
        insertcolor=Config.COLORS['text'],
        padding=(10, 8),
        font=Config.FONTS['default']
    )
    style.map('Custom.TEntry',
        bordercolor=[
            ('focus', Config.COLORS['primary']),
            ('!focus', Config.COLORS['border'])
        ]
    )

    # Combobox personalizado
    style.configure('Custom.TCombobox',
        fieldbackground=Config.COLORS['surface'],
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['text'],
        borderwidth=1,
        relief='solid',
        padding=(10, 8),
        font=Config.FONTS['default']
    )
    style.map('Custom.TCombobox',
        bordercolor=[
            ('focus', Config.COLORS['primary']),
            ('!focus', Config.COLORS['border'])
        ]
    )

    # Treeview personalizado
    style.configure('Custom.Treeview',
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['text'],
        rowheight=Config.UI_CONFIG['table_row_height'],
        fieldbackground=Config.COLORS['surface'],
        borderwidth=0,
        relief='flat',
        font=Config.FONTS['default']
    )

    # Encabezado del Treeview
    style.configure('Custom.Treeview.Heading',
        background=Config.COLORS['secondary'],
        foreground='white',
        relief='flat',
        borderwidth=0,
        padding=(10, 8),
        font=Config.FONTS['subheading']
    )
    style.map('Custom.Treeview.Heading',
        background=[('active', Config.COLORS['secondary_dark'])]
    )

    # Selección en Treeview
    style.map('Custom.Treeview',
        background=[
            ('selected', Config.COLORS['primary']),
            ('!selected', Config.COLORS['surface'])
        ],
        foreground=[
            ('selected', 'white'),
            ('!selected', Config.COLORS['text'])
        ]
    )

    # Scrollbar personalizada
    style.configure('Custom.Vertical.TScrollbar',
        background=Config.COLORS['border'],
        bordercolor=Config.COLORS['border'],
        arrowcolor=Config.COLORS['text_light'],
        darkcolor=Config.COLORS['border'],
        lightcolor=Config.COLORS['surface'],
        troughcolor=Config.COLORS['background'],
        borderwidth=0,
        relief='flat'
    )

    # Progressbar
    style.configure('Custom.TProgressbar',
        background=Config.COLORS['primary'],
        troughcolor=Config.COLORS['border'],
        borderwidth=0,
        lightcolor=Config.COLORS['primary'],
        darkcolor=Config.COLORS['primary']
    )

    # Notebook (pestañas)
    style.configure('Custom.TNotebook',
        background=Config.COLORS['background'],
        borderwidth=0,
        tabmargins=[0, 0, 0, 0]
    )

    style.configure('Custom.TNotebook.Tab',
        background=Config.COLORS['border'],
        foreground=Config.COLORS['text'],
        padding=(20, 10),
        borderwidth=0,
        font=Config.FONTS['default']
    )

    style.map('Custom.TNotebook.Tab',
        background=[
            ('selected', Config.COLORS['surface']),
            ('active', Config.COLORS['hover']),
            ('!selected', Config.COLORS['border'])
        ],
        foreground=[
            ('selected', Config.COLORS['secondary']),
            ('!selected', Config.COLORS['text'])
        ]
    )

    # Separadores
    style.configure('Custom.TSeparator',
        background=Config.COLORS['border']
    )

    # Checkbutton personalizado
    style.configure('Custom.TCheckbutton',
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['text'],
        focuscolor='none',
        font=Config.FONTS['default']
    )

    # Radiobutton personalizado
    style.configure('Custom.TRadiobutton',
        background=Config.COLORS['surface'],
        foreground=Config.COLORS['text'],
        focuscolor='none',
        font=Config.FONTS['default']
    )

def create_gradient_frame(parent, color1, color2, width=None, height=None):
    """Crear un frame con efecto gradiente simulado"""
    # Por limitaciones de tkinter, simulamos el gradiente con frames superpuestos
    main_frame = tk.Frame(parent, bg=color1, width=width, height=height)

    if width and height:
        main_frame.pack_propagate(False)

    return main_frame

def create_card_frame(parent, **kwargs):
    """Crear un frame con estilo de tarjeta (card)"""
    # Frame principal con borde
    card_frame = tk.Frame(
        parent,
        bg=Config.COLORS['surface'],
        relief='flat',
        bd=0,
        **kwargs
    )

    # Simular sombra con frames adicionales
    shadow_frame = tk.Frame(
        parent,
        bg=Config.COLORS['card_shadow'],
        height=2
    )

    return card_frame

def apply_hover_effect(widget, enter_color=None, leave_color=None):
    """Aplicar efecto hover a un widget"""
    if not enter_color:
        enter_color = Config.COLORS['hover']
    if not leave_color:
        leave_color = widget.cget('bg')

    def on_enter(event):
        widget.configure(bg=enter_color)

    def on_leave(event):
        widget.configure(bg=leave_color)

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def create_icon_button(parent, text, command, icon="", **kwargs):
    """Crear un botón con icono"""
    display_text = f"{icon} {text}" if icon else text

    btn = tk.Button(
        parent,
        text=display_text,
        command=command,
        bg=Config.COLORS['primary'],
        fg='white',
        font=Config.FONTS['default'],
        relief='flat',
        bd=0,
        padx=15,
        pady=10,
        cursor='hand2',
        **kwargs
    )

    # Aplicar hover
    apply_hover_effect(btn, Config.COLORS['primary_dark'], Config.COLORS['primary'])

    return btn

def create_modern_label(parent, text, style='default', **kwargs):
    """Crear un label con estilo moderno"""
    styles = {
        'heading': {
            'font': Config.FONTS['heading'],
            'fg': Config.COLORS['secondary'],
            'bg': Config.COLORS['surface']
        },
        'subheading': {
            'font': Config.FONTS['subheading'],
            'fg': Config.COLORS['text'],
            'bg': Config.COLORS['surface']
        },
        'small': {
            'font': Config.FONTS['small'],
            'fg': Config.COLORS['text_light'],
            'bg': Config.COLORS['surface']
        },
        'default': {
            'font': Config.FONTS['default'],
            'fg': Config.COLORS['text'],
            'bg': Config.COLORS['surface']
        }
    }

    style_config = styles.get(style, styles['default'])
    style_config.update(kwargs)

    return tk.Label(parent, text=text, **style_config)

def create_modern_entry(parent, placeholder="", **kwargs):
    """Crear un entry con estilo moderno"""
    entry = tk.Entry(
        parent,
        bg=Config.COLORS['surface'],
        fg=Config.COLORS['text'],
        font=Config.FONTS['default'],
        relief='solid',
        bd=1,
        insertbackground=Config.COLORS['text'],
        **kwargs
    )

    # Placeholder functionality
    if placeholder:
        entry.insert(0, placeholder)
        entry.configure(fg=Config.COLORS['text_light'])

        def on_focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.configure(fg=Config.COLORS['text'])

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(fg=Config.COLORS['text_light'])

        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    return entry
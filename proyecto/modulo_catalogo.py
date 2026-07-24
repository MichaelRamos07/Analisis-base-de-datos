import tkinter as tk
from tkinter import ttk
import persistencia

class VistaCatalogo(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.construir_componentes()
        self.actualizar_vista()

    def construir_componentes(self):
        # 1. PANEL SUPERIOR: INDICADORES CLAVE (KPIs)
        frame_kpis = ttk.LabelFrame(self, text=" Resumen de Estado ")
        frame_kpis.pack(fill='x', padx=10, pady=5)

        self.lbl_disp = ttk.Label(
            frame_kpis, 
            text="Disponibles: 0", 
            font=('Arial', 10, 'bold'), 
            foreground='green'
        )
        self.lbl_disp.pack(side='left', expand=True, pady=8)

        self.lbl_vend = ttk.Label(
            frame_kpis, 
            text="Vendidas: 0", 
            font=('Arial', 10, 'bold'), 
            foreground='blue'
        )
        self.lbl_vend.pack(side='left', expand=True, pady=8)

        self.lbl_alq = ttk.Label(
            frame_kpis, 
            text="Alquiladas: 0", 
            font=('Arial', 10, 'bold'), 
            foreground='orange'
        )
        self.lbl_alq.pack(side='left', expand=True, pady=8)

        # 2. PANEL INTERMEDIO: FILTROS Y BÚSQUEDA
        frame_filtros = ttk.LabelFrame(self, text=" Filtros de Búsqueda ")
        frame_filtros.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_filtros, text="Código/ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.ent_filtro_id = ttk.Entry(frame_filtros, width=14)
        self.ent_filtro_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_filtros, text="Tipo:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        # Filtro actualizado con la lista completa del dataset
        opciones_filtro_tipo = [
            "Todos", "apartment", "assisted living", "Community Pool", "condo", 
            "cottage/cabin", "duplex", "flat", "house", "in-law", 
            "land", "loft", "manufactured", "townhouse"
        ]
        self.combo_filtro_tipo = ttk.Combobox(
            frame_filtros, 
            values=opciones_filtro_tipo, 
            state="readonly", 
            width=16
        )
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_tipo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_filtros, text="Región:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.ent_filtro_region = ttk.Entry(frame_filtros, width=14)
        self.ent_filtro_region.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(frame_filtros, text="Precio Máx:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.ent_filtro_precio = ttk.Entry(frame_filtros, width=14)
        self.ent_filtro_precio.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_filtros, text="Disponibilidad:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.combo_filtro_disp = ttk.Combobox(
            frame_filtros, 
            values=["Todos", "disponible", "vendido", "alquilado"], 
            state="readonly", 
            width=16
        )
        self.combo_filtro_disp.set("Todos")
        self.combo_filtro_disp.grid(row=1, column=3, padx=5, pady=5)

        btn_filtrar = ttk.Button(frame_filtros, text="🔍 Buscar / Filtrar", command=self.actualizar_vista)
        btn_filtrar.grid(row=1, column=4, padx=5, pady=5, sticky='ew')

        btn_limpiar = ttk.Button(frame_filtros, text="🧹 Limpiar Filtros", command=self.limpiar_filtros)
        btn_limpiar.grid(row=1, column=5, padx=5, pady=5, sticky='ew')

        # 3. PANEL INFERIOR: TABLA DEL CATÁLOGO
        frame_tabla = ttk.LabelFrame(self, text=" Catálogo de Inmuebles ")
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=5)

        columnas = ("id", "type", "price", "region", "state", "disponibilidad")
        self.tree_propiedades = ttk.Treeview(frame_tabla, columns=columnas, show='headings')

        self.tree_propiedades.heading("id", text="ID / Código")
        self.tree_propiedades.heading("type", text="Tipo")
        self.tree_propiedades.heading("price", text="Precio ($)")
        self.tree_propiedades.heading("region", text="Región")
        self.tree_propiedades.heading("state", text="Estado Ubicación")
        self.tree_propiedades.heading("disponibilidad", text="Disponibilidad")

        self.tree_propiedades.column("id", width=120, anchor='center')
        self.tree_propiedades.column("type", width=120, anchor='center')
        self.tree_propiedades.column("price", width=110, anchor='e')
        self.tree_propiedades.column("region", width=150, anchor='w')
        self.tree_propiedades.column("state", width=80, anchor='center')
        self.tree_propiedades.column("disponibilidad", width=110, anchor='center')

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_propiedades.yview)
        self.tree_propiedades.configure(yscrollcommand=scrollbar.set)

        self.tree_propiedades.pack(side='left', fill='both', expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side='right', fill='y', padx=(0, 5), pady=5)

    def actualizar_vista(self):
        resumen = persistencia.obtener_resumen_propiedades()
        self.lbl_disp.config(text=f"Disponibles: {resumen['disponibles']}")
        self.lbl_vend.config(text=f"Vendidas: {resumen['vendidas']}")
        self.lbl_alq.config(text=f"Alquiladas: {resumen['alquiladas']}")

        for item in self.tree_propiedades.get_children():
            self.tree_propiedades.delete(item)

        filtro_id = self.ent_filtro_id.get().strip().lower()
        filtro_tipo = self.combo_filtro_tipo.get().lower()
        filtro_region = self.ent_filtro_region.get().strip().lower()
        filtro_precio = self.ent_filtro_precio.get().strip()
        filtro_disp = self.combo_filtro_disp.get().lower()

        propiedades = persistencia.obtener_todas_propiedades()

        for p in propiedades:
            if filtro_id and filtro_id not in str(p.get('id', '')).lower():
                continue

            if filtro_tipo != "todos" and filtro_tipo not in str(p.get('type', '')).lower():
                continue

            if filtro_region and filtro_region not in str(p.get('region', '')).lower():
                continue

            if filtro_disp != "todos" and filtro_disp != str(p.get('disponibilidad', '')).lower():
                continue

            if filtro_precio:
                try:
                    if float(p.get('price', 0)) > float(filtro_precio):
                        continue
                except ValueError:
                    pass

            try:
                precio_fmt = f"${float(p.get('price', 0)):,.2f}"
            except ValueError:
                precio_fmt = "$0.00"

            self.tree_propiedades.insert("", "end", values=(
                p.get('id', ''),
                p.get('type', ''),
                precio_fmt,
                p.get('region', ''),
                p.get('state', ''),
                p.get('disponibilidad', '').capitalize()
            ))

    def limpiar_filtros(self):
        self.ent_filtro_id.delete(0, 'end')
        self.combo_filtro_tipo.set("Todos")
        self.ent_filtro_region.delete(0, 'end')
        self.ent_filtro_precio.delete(0, 'end')
        self.combo_filtro_disp.set("Todos")
        self.actualizar_vista()
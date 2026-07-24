import tkinter as tk
from tkinter import ttk, messagebox
import persistencia


class VistaGestionAgente(ttk.Frame):
    def __init__(self, parent, al_actualizar=None):
        super().__init__(parent)
        self.al_actualizar = al_actualizar
        self.construir_componentes()
        self.actualizar_tabla()

    def construir_componentes(self):
        # Panel de Encabezado
        frame_top = ttk.LabelFrame(self, text=" Panel de Control SCM - Agente Inmobiliario ")
        frame_top.pack(fill='x', padx=10, pady=5)

        ttk.Label(
            frame_top, 
            text="Gestión de etapas comerciales y registro acumulativo de visitas.", 
            font=('Arial', 9, 'italic')
        ).pack(padx=10, pady=5)

        # Tabla de Gestión
        frame_tabla = ttk.LabelFrame(self, text=" Mis Inmuebles en Gestión ")
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=5)

        columnas = ("id_propiedad", "etapa_gestion", "visitas", "tipo", "precio")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show='headings')

        self.tree.heading("id_propiedad", text="ID Propiedad")
        self.tree.heading("etapa_gestion", text="Etapa SCM Actual")
        self.tree.heading("visitas", text="Visitas Registradas")
        self.tree.heading("tipo", text="Tipo Inmueble")
        self.tree.heading("precio", text="Precio ($)")

        self.tree.column("id_propiedad", width=120, anchor='center')
        self.tree.column("etapa_gestion", width=160, anchor='center')
        self.tree.column("visitas", width=120, anchor='center')
        self.tree.column("tipo", width=120, anchor='center')
        self.tree.column("precio", width=120, anchor='e')

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side='right', fill='y', padx=(0, 5), pady=5)

        # Panel de Acciones
        frame_acciones = ttk.Frame(self)
        frame_acciones.pack(fill='x', padx=10, pady=10)

        btn_actualizar_etapa = ttk.Button(
            frame_acciones, 
            text="✏️ Cambiar Etapa / Registrar Visita", 
            command=self.abrir_modal_cambio_etapa
        )
        btn_actualizar_etapa.pack(side='left', padx=5)

        btn_recargar = ttk.Button(
            frame_acciones, 
            text="🔄 Recargar Lista", 
            command=self.actualizar_tabla
        )
        btn_recargar.pack(side='right', padx=5)

    def actualizar_tabla(self):
        """Carga los datos leídos directamente de estado_comercial.csv y propiedades.csv."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Asegura la existencia de registros iniciales para todas las propiedades
        persistencia.sincronizar_propiedades_existentes_scm()

        # Diccionario auxiliar de propiedades para cruzar datos
        propiedades = {}
        for p in persistencia.obtener_todas_propiedades():
            p_id = str(p.get('id', p.get('id_propiedad', ''))).strip()
            if p_id:
                propiedades[p_id] = p

        gestion_list = persistencia.obtener_todos_gestion_agentes()

        for g in gestion_list:
            p_id = str(g.get('id_propiedad', '')).strip()
            info_p = propiedades.get(p_id, {})

            # Obtención e interpretación de precio
            raw_price = info_p.get('price', g.get('price', 0.0))
            try:
                precio_val = float(raw_price) if raw_price else 0.0
                precio_fmt = f"${precio_val:,.2f}"
            except (ValueError, TypeError):
                precio_fmt = "$0.00"

            # Parseo entero estricto para las visitas
            raw_visitas = g.get('visitas', 0)
            try:
                visitas_val = int(float(raw_visitas))
            except (ValueError, TypeError):
                visitas_val = 0

            # Formato de visualización de la etapa
            etapa_raw = str(g.get('etapa_gestion', 'disponible')).strip().lower()
            etapa_fmt = etapa_raw.replace('_', ' ').capitalize()

            self.tree.insert("", "end", values=(
                p_id,
                etapa_fmt,
                str(visitas_val),
                info_p.get('type', g.get('type', 'N/A')),
                precio_fmt
            ))

    def abrir_modal_cambio_etapa(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor, selecciona una propiedad de la lista.")
            return

        item_vals = self.tree.item(selected[0], 'values')
        id_propiedad = item_vals[0]

        # Ventana Modal Emergente
        modal = tk.Toplevel(self)
        modal.title(f"Actualizar Etapa SCM - Propiedad #{id_propiedad}")
        modal.geometry("380x250")
        modal.resizable(False, False)
        modal.grab_set()

        ttk.Label(modal, text=f"Modificando Propiedad ID: {id_propiedad}", font=('Arial', 10, 'bold')).pack(pady=10)

        # Selección de Etapa adaptada a los estados de estado_comercial.csv
        ttk.Label(modal, text="Nueva Etapa Comercial:").pack(anchor='w', padx=20)
        combo_etapas = ttk.Combobox(
            modal, 
            values=["disponible", "negociacion", "vendido", "alquilado", "cerrado"], 
            state="readonly",
            width=30
        )
        
        # Selección por defecto
        etapa_actual = item_vals[1].lower().replace(' ', '_')
        if etapa_actual in combo_etapas['values']:
            combo_etapas.set(etapa_actual)
        else:
            combo_etapas.set("disponible")
            
        combo_etapas.pack(padx=20, pady=5)

        # Incrementar Visitas
        ttk.Label(modal, text="Añadir Visitas Realizadas:").pack(anchor='w', padx=20)
        spin_visitas = ttk.Spinbox(modal, from_=0, to=50, width=5)
        spin_visitas.set(0)
        spin_visitas.pack(anchor='w', padx=20, pady=5)

        def guardar_cambio():
            nueva_etapa = combo_etapas.get()
            try:
                add_visitas = int(spin_visitas.get())
            except ValueError:
                add_visitas = 0

            persistencia.actualizar_etapa_agente(id_propiedad, nueva_etapa, incremento_visitas=add_visitas)
            messagebox.showinfo("Éxito", f"Propiedad #{id_propiedad} actualizada a etapa '{nueva_etapa}'.")
            
            modal.destroy()
            self.actualizar_tabla()
            
            if self.al_actualizar:
                self.al_actualizar()

        ttk.Button(modal, text="💾 Guardar Cambios", command=guardar_cambio).pack(pady=15)
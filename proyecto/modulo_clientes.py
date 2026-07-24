import tkinter as tk
from tkinter import ttk, messagebox
import persistencia

class VistaClientes(ttk.Frame):
    def __init__(self, parent, al_actualizar_cliente=None):
        super().__init__(parent)
        self.al_actualizar_cliente = al_actualizar_cliente
        self.construir_componentes()
        self.actualizar_vista()

    def construir_componentes(self):
        # 1. PANEL SUPERIOR: FORMULARIO
        frame_form = ttk.LabelFrame(self, text=" Registrar Nuevo Cliente ")
        frame_form.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_form, text="ID / Cédula:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.ent_id = ttk.Entry(frame_form, width=15)
        self.ent_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Nombre Completo:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.ent_nombre = ttk.Entry(frame_form, width=25)
        self.ent_nombre.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_form, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.ent_email = ttk.Entry(frame_form, width=20)
        self.ent_email.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Teléfono:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.ent_telefono = ttk.Entry(frame_form, width=15)
        self.ent_telefono.grid(row=1, column=3, padx=5, pady=5)

        btn_guardar = ttk.Button(frame_form, text="💾 Registrar Cliente", command=self.guardar_cliente)
        btn_guardar.grid(row=1, column=4, padx=10, pady=5)

        # 2. PANEL INTERMEDIO: BÚSQUEDA Y ELIMINACIÓN
        frame_filtro = ttk.LabelFrame(self, text=" Acciones / Buscar Cliente ")
        frame_filtro.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame_filtro, text="Buscar (ID o Nombre):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.ent_buscar = ttk.Entry(frame_filtro, width=30)
        self.ent_buscar.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(frame_filtro, text="🔍 Buscar", command=self.actualizar_vista)
        btn_buscar.grid(row=0, column=2, padx=5, pady=5)

        btn_limpiar = ttk.Button(frame_filtro, text="🧹 Limpiar", command=self.limpiar_busqueda)
        btn_limpiar.grid(row=0, column=3, padx=5, pady=5)

        btn_eliminar = ttk.Button(frame_filtro, text="🗑️ Eliminar Cliente Seleccionado", command=self.eliminar_cliente)
        btn_eliminar.grid(row=0, column=4, padx=15, pady=5)

        # 3. PANEL INFERIOR: TABLAS DE CLIENTES E HISTORIAL
        frame_tablas = ttk.Frame(self)
        frame_tablas.pack(fill='both', expand=True, padx=10, pady=5)

        frame_lista = ttk.LabelFrame(frame_tablas, text=" Directorio de Clientes ")
        frame_lista.pack(side='left', fill='both', expand=True, padx=(0, 5))

        columnas_cli = ("id", "nombre", "email", "telefono", "monto_total")
        self.tree_clientes = ttk.Treeview(frame_lista, columns=columnas_cli, show='headings')

        self.tree_clientes.heading("id", text="ID Cliente")
        self.tree_clientes.heading("nombre", text="Nombre")
        self.tree_clientes.heading("email", text="Email")
        self.tree_clientes.heading("telefono", text="Teléfono")
        self.tree_clientes.heading("monto_total", text="Monto Acumulado ($)")

        self.tree_clientes.column("id", width=90, anchor='center')
        self.tree_clientes.column("nombre", width=140, anchor='w')
        self.tree_clientes.column("email", width=150, anchor='w')
        self.tree_clientes.column("telefono", width=100, anchor='center')
        self.tree_clientes.column("monto_total", width=120, anchor='e')

        scroll_cli = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scroll_cli.set)

        self.tree_clientes.pack(side='left', fill='both', expand=True, padx=(5, 0), pady=5)
        scroll_cli.pack(side='right', fill='y', padx=(0, 5), pady=5)

        self.tree_clientes.bind("<<TreeviewSelect>>", self.cargar_historial_cliente)

        frame_historial = ttk.LabelFrame(frame_tablas, text=" Historial de Transacciones ")
        frame_historial.pack(side='right', fill='both', expand=True, padx=(5, 0))

        columnas_hist = ("id_propiedad", "tipo_op", "monto", "fecha")
        self.tree_historial = ttk.Treeview(frame_historial, columns=columnas_hist, show='headings')

        self.tree_historial.heading("id_propiedad", text="ID Propiedad")
        self.tree_historial.heading("tipo_op", text="Operación")
        self.tree_historial.heading("monto", text="Monto ($)")
        self.tree_historial.heading("fecha", text="Fecha")

        self.tree_historial.column("id_propiedad", width=100, anchor='center')
        self.tree_historial.column("tipo_op", width=90, anchor='center')
        self.tree_historial.column("monto", width=100, anchor='e')
        self.tree_historial.column("fecha", width=120, anchor='center')

        scroll_hist = ttk.Scrollbar(frame_historial, orient="vertical", command=self.tree_historial.yview)
        self.tree_historial.configure(yscrollcommand=scroll_hist.set)

        self.tree_historial.pack(side='left', fill='both', expand=True, padx=(5, 0), pady=5)
        scroll_hist.pack(side='right', fill='y', padx=(0, 5), pady=5)

    def guardar_cliente(self):
        id_cli = self.ent_id.get().strip()
        nombre = self.ent_nombre.get().strip()
        email = self.ent_email.get().strip()
        telefono = self.ent_telefono.get().strip()

        if not id_cli or not nombre:
            messagebox.showwarning("Campos Requeridos", "Los campos ID y Nombre son obligatorios.")
            return

        if persistencia.obtener_cliente_por_id(id_cli):
            messagebox.showerror("Error", f"El cliente con ID '{id_cli}' ya se encuentra registrado.")
            return

        cliente = {
            'id': id_cli,
            'nombre': nombre,
            'email': email,
            'telefono': telefono,
            'monto_total': '0.0'
        }

        try:
            persistencia.guardar_cliente_csv(cliente)
            messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado correctamente.")
            
            self.ent_id.delete(0, 'end')
            self.ent_nombre.delete(0, 'end')
            self.ent_email.delete(0, 'end')
            self.ent_telefono.delete(0, 'end')

            self.actualizar_vista()

            if self.al_actualizar_cliente:
                self.al_actualizar_cliente()

        except Exception as e:
            messagebox.showerror("Error de Persistencia", f"No se pudo guardar el cliente: {str(e)}")

    def eliminar_cliente(self):
        seleccion = self.tree_clientes.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, seleccione un cliente de la lista para eliminar.")
            return

        item_vals = self.tree_clientes.item(seleccion[0], 'values')
        id_cli = item_vals[0]
        nombre_cli = item_vals[1]

        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de que desea eliminar al cliente '{nombre_cli}' (ID: {id_cli})?"
        )
        
        if confirmacion:
            if persistencia.eliminar_cliente_csv(id_cli):
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.actualizar_vista()
                # Limpiar tabla de historial
                for item in self.tree_historial.get_children():
                    self.tree_historial.delete(item)
                if self.al_actualizar_cliente:
                    self.al_actualizar_cliente()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente especificado.")

    def actualizar_vista(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)

        criterio = self.ent_buscar.get().strip().lower()
        clientes = persistencia.obtener_todos_clientes()

        for c in clientes:
            id_cli = str(c.get('id', '')).lower()
            nombre_cli = str(c.get('nombre', '')).lower()

            if criterio and (criterio not in id_cli and criterio not in nombre_cli):
                continue

            try:
                monto_fmt = f"${float(c.get('monto_total', 0)):,.2f}"
            except ValueError:
                monto_fmt = "$0.00"

            self.tree_clientes.insert("", "end", values=(
                c.get('id', ''),
                c.get('nombre', ''),
                c.get('email', ''),
                c.get('telefono', ''),
                monto_fmt
            ))

    def cargar_historial_cliente(self, event):
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)

        seleccion = self.tree_clientes.selection()
        if not seleccion:
            return

        item_vals = self.tree_clientes.item(seleccion[0], 'values')
        id_cli = item_vals[0]

        transacciones = persistencia.obtener_transacciones_por_cliente(id_cli)
        for t in transacciones:
            try:
                monto_fmt = f"${float(t.get('monto', 0)):,.2f}"
            except ValueError:
                monto_fmt = "$0.00"

            tipo_op_correcta = t.get('tipo_operacion', '').capitalize()

            self.tree_historial.insert("", "end", values=(
                t.get('id_propiedad', ''),
                tipo_op_correcta,
                monto_fmt,
                t.get('fecha', '')
            ))

    def limpiar_busqueda(self):
        self.ent_buscar.delete(0, 'end')
        self.actualizar_vista()
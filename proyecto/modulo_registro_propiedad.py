import tkinter as tk
from tkinter import ttk, messagebox
import persistencia

class VistaRegistroPropiedad(ttk.Frame):
    def __init__(self, parent, al_guardar_propiedad=None):
        super().__init__(parent)
        self.al_guardar_propiedad = al_guardar_propiedad
        
        self.campos = [
            'id', 'url', 'region', 'region_url', 'price', 'type', 'sqfeet', 'beds',
            'baths', 'cats_allowed', 'dogs_allowed', 'smoking_allowed',
            'wheelchair_access', 'electric_vehicle_charge', 'comes_furnished',
            'laundry_options', 'parking_options', 'image_url', 'description',
            'lat', 'long', 'state'
        ]
        
        self.campos_yes_no = [
            'cats_allowed', 'dogs_allowed', 'smoking_allowed',
            'wheelchair_access', 'electric_vehicle_charge', 'comes_furnished'
        ]
        
        self.entries_prop = {}
        self.combo_comercio = None
        self.construir_componentes()

    def generar_siguiente_id(self):
        propiedades = persistencia.obtener_todas_propiedades()
        max_id = 0
        for p in propiedades:
            try:
                p_id = int(p.get('id', 0))
                if p_id > max_id:
                    max_id = p_id
            except ValueError:
                continue
        return str(max_id + 1)

    def construir_componentes(self):
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        frame_form = ttk.LabelFrame(scrollable_frame, text=" Registrar Nueva Propiedad ")
        frame_form.pack(fill='both', expand=True, padx=10, pady=10)

        row_counter = 0

        for field in self.campos:
            lbl_texto = field.replace('_', ' ').capitalize() + ":"
            lbl = ttk.Label(frame_form, text=lbl_texto, font=('Arial', 9, 'bold'))
            lbl.grid(row=row_counter, column=0, padx=12, pady=6, sticky='w')

            if field == 'id':
                ent = ttk.Entry(frame_form, width=55, state='readonly')
                ent.grid(row=row_counter, column=1, padx=12, pady=6, sticky='w')
            elif field == 'type':
                # Lista completa de los 13 tipos extraídos del CSV
                opciones_type = [
                    "apartment", "assisted living", "Community Pool", "condo", 
                    "cottage/cabin", "duplex", "flat", "house", "in-law", 
                    "land", "loft", "manufactured", "townhouse"
                ]
                ent = ttk.Combobox(frame_form, values=opciones_type, state="readonly", width=53)
                ent.grid(row=row_counter, column=1, padx=12, pady=6, sticky='w')
            elif field in self.campos_yes_no:
                ent = ttk.Combobox(frame_form, values=["yes", "no"], state="readonly", width=53)
                ent.grid(row=row_counter, column=1, padx=12, pady=6, sticky='w')
            elif field == 'description':
                ent = tk.Text(frame_form, height=4, width=50, font=('Arial', 9))
                ent.grid(row=row_counter, column=1, padx=12, pady=6, sticky='w')
            else:
                ent = ttk.Entry(frame_form, width=55)
                ent.grid(row=row_counter, column=1, padx=12, pady=6, sticky='w')

            self.entries_prop[field] = ent
            row_counter += 1

            if field == 'type':
                lbl_comercio = ttk.Label(frame_form, text="Comercio (Operación):", font=('Arial', 9, 'bold'))
                lbl_comercio.grid(row=row_counter, column=0, padx=12, pady=6, sticky='w')

                self.combo_comercio = ttk.Combobox(
                    frame_form, 
                    values=["venta", "alquiler"], 
                    state="readonly", 
                    width=53
                )
                self.combo_comercio.grid(row=row_counter, column=1, padx=12, pady=6, sticky='w')
                row_counter += 1

        btn_guardar = ttk.Button(
            frame_form, 
            text="💾 Guardar Propiedad", 
            command=self.guardar_propiedad
        )
        btn_guardar.grid(row=row_counter, column=0, columnspan=2, pady=20)

        self.actualizar_id_autogenerado()

    def actualizar_id_autogenerado(self):
        nuevo_id = self.generar_siguiente_id()
        self.entries_prop['id'].config(state='normal')
        self.entries_prop['id'].delete(0, 'end')
        self.entries_prop['id'].insert(0, nuevo_id)
        self.entries_prop['id'].config(state='readonly')

    def guardar_propiedad(self):
        datos_propiedad = {}
        for field, widget in self.entries_prop.items():
            if field == 'description':
                val = widget.get("1.0", "end-1c").strip()
            else:
                val = widget.get().strip()

            if field in self.campos_yes_no:
                if val.lower() == 'yes':
                    val = '1'
                elif val.lower() == 'no':
                    val = '0'

            datos_propiedad[field] = val

        for field, valor in datos_propiedad.items():
            if not valor:
                lbl_nombre = field.replace('_', ' ').capitalize()
                messagebox.showwarning("Campo Obligatorio", f"El campo '{lbl_nombre}' es obligatorio.")
                return

        tipo_comercio = self.combo_comercio.get().strip()
        if not tipo_comercio:
            messagebox.showwarning("Campo Obligatorio", "El campo 'Comercio (Operación)' es obligatorio.")
            return

        try:
            persistencia.guardar_propiedad_csv(datos_propiedad)
            
            datos_estado = {
                'id_propiedad': datos_propiedad['id'],
                'transaction_type': tipo_comercio,
                'status': 'disponible'
            }
            persistencia.guardar_estado_comercial_csv(datos_estado)

            messagebox.showinfo("Éxito", f"Propiedad con ID '{datos_propiedad['id']}' registrada correctamente.")
            
            self.limpiar_formulario()
            self.actualizar_id_autogenerado()

            if self.al_guardar_propiedad:
                self.al_guardar_propiedad()

        except Exception as e:
            messagebox.showerror("Error de Persistencia", f"No se pudo guardar la propiedad: {str(e)}")

    def limpiar_formulario(self):
        for field, widget in self.entries_prop.items():
            if field == 'id':
                continue
            elif field in ['type'] + self.campos_yes_no:
                widget.set('')
            elif field == 'description':
                widget.delete("1.0", "end")
            else:
                widget.delete(0, 'end')
        
        if self.combo_comercio:
            self.combo_comercio.set('')
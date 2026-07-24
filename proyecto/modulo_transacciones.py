import tkinter as tk
from tkinter import ttk, messagebox
import persistencia

class VistaTransacciones(ttk.Frame):
    def __init__(self, parent, al_completar_transaccion=None):
        super().__init__(parent)
        # Callback para notificar a otros módulos que refresquen sus vistas tras un cierre
        self.al_completar_transaccion = al_completar_transaccion
        self.cliente_verificado = False
        self.construir_componentes()

    def construir_componentes(self):
        # ------------------------------------------------------------------
        # PANEL PRINCIPAL: FORMULARIO DE REGISTRO
        # ------------------------------------------------------------------
        frame_form = ttk.LabelFrame(self, text=" Registro y Cierre de Transacción ")
        frame_form.pack(fill='x', padx=20, pady=20)

        # 1. Búsqueda y Verificación de Cliente
        ttk.Label(frame_form, text="ID Cliente:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.entry_id_cli = ttk.Entry(frame_form, width=25)
        self.entry_id_cli.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.entry_id_cli.bind("<Key>", self._restablecer_verificacion)

        btn_verificar = ttk.Button(frame_form, text="🔍 Verificar Cliente", command=self.verificar_cliente)
        btn_verificar.grid(row=0, column=2, padx=10, pady=10)

        self.lbl_info_cliente = ttk.Label(
            frame_form, 
            text="Estado: No verificado", 
            font=('Arial', 9, 'italic'), 
            foreground='gray'
        )
        self.lbl_info_cliente.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='w')

        # Separador visual
        ttk.Separator(frame_form, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)

        # 2. Selección de Inmueble y Tipo de Operación
        ttk.Label(frame_form, text="Tipo de Operación:").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.combo_tipo_op = ttk.Combobox(frame_form, values=["venta", "alquiler"], state="readonly", width=23)
        self.combo_tipo_op.grid(row=3, column=1, padx=10, pady=10, sticky='w')
        self.combo_tipo_op.set("venta")

        ttk.Label(frame_form, text="ID Propiedad / Código:").grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.entry_id_prop = ttk.Entry(frame_form, width=25)
        self.entry_id_prop.grid(row=4, column=1, padx=10, pady=10, sticky='w')

        # 3. Botón de Procesamiento
        btn_procesar = ttk.Button(frame_form, text="⚡ Validar y Procesar Cierre", command=self.procesar_cierre)
        btn_procesar.grid(row=5, column=0, columnspan=3, pady=20)

    def _restablecer_verificacion(self, event=None):
        """Reinicia el estado de verificación si el usuario altera el ID del cliente."""
        self.cliente_verificado = False
        self.lbl_info_cliente.config(text="Estado: No verificado (cambios detectados)", foreground='gray')

    def verificar_cliente(self):
        """Busca al cliente en la base de datos CRM, verifica si su propiedad de interés está en negociación y la autocompleta."""
        id_cli = self.entry_id_cli.get().strip()
        if not id_cli:
            messagebox.showwarning("Atención", "Ingrese un ID de cliente para consultar.")
            return

        cliente = persistencia.obtener_cliente_por_id(id_cli)
        if cliente:
            self.cliente_verificado = True
            nombre = cliente.get('nombre', 'N/A')
            email = cliente.get('email', 'N/A')
            tel = cliente.get('telefono', 'N/A')
            id_prop_interes = str(cliente.get('id_propiedad_interes', '')).strip()

            msg = f"✅ Cliente Confirmado: {nombre} | Email: {email} | Tel: {tel}"

            # Verificación de la propiedad de interés en SCM / Gestión de Agentes
            if id_prop_interes:
                registros_scm = persistencia.obtener_todos_gestion_agentes()
                etapa_propiedad = None

                for reg in registros_scm:
                    if str(reg.get('id_propiedad', '')).strip() == id_prop_interes:
                        etapa_propiedad = str(reg.get('etapa_gestion', '')).strip().lower()
                        break

                # Comprobar si la propiedad está en estado de negociación
                if etapa_propiedad in ['negociacion', 'negociación']:
                    self.entry_id_prop.delete(0, 'end')
                    self.entry_id_prop.insert(0, id_prop_interes)
                    msg += f" | 🏠 Propiedad en negociación asignada: {id_prop_interes}"
                else:
                    msg += f" | ℹ️ Propiedad de interés ({id_prop_interes}) no está en Negociación ({etapa_propiedad})."

            self.lbl_info_cliente.config(text=msg, foreground='green')
        else:
            self.cliente_verificado = False
            self.lbl_info_cliente.config(
                text=f"❌ El cliente con ID '{id_cli}' no existe en el CRM.",
                foreground='red'
            )

    def procesar_cierre(self):
        """Ejecuta las validaciones de negocio y registra la transacción."""
        id_cli = self.entry_id_cli.get().strip()
        id_prop = self.entry_id_prop.get().strip()
        tipo_op = self.combo_tipo_op.get()

        if not id_cli or not id_prop:
            messagebox.showwarning("Campos Incompletos", "Debe ingresar el ID del cliente y de la propiedad.")
            return

        # Si el usuario no presionó el botón de verificar previamente, lo validamos internamente
        if not self.cliente_verificado:
            if not persistencia.obtener_cliente_por_id(id_cli):
                messagebox.showerror("Error de Validación", f"El cliente '{id_cli}' no está registrado en el sistema.")
                return

        # Validar compatibilidad y disponibilidad de la propiedad
        valido, mensaje = persistencia.validar_propiedad_para_operacion(id_prop, tipo_op)
        if not valido:
            messagebox.showerror("Incompatibilidad de Transacción", mensaje)
            return

        # Obtener monto de la propiedad e ingresar registro
        precio = persistencia.obtener_precio_propiedad(id_prop)
        persistencia.registrar_transaccion_csv(id_cli, id_prop, tipo_op, precio)
        persistencia.actualizar_monto_cliente_crm(id_cli, precio)

        # Actualizar etapa SCM del agente a 'cerrado'
        persistencia.actualizar_etapa_agente(id_prop, "cerrado")

        messagebox.showinfo("Transacción Exitosa", f"¡Operación procesada correctamente!\nMonto total: ${precio:,.2f}")

        # Limpiar formulario tras éxito
        self.entry_id_cli.delete(0, 'end')
        self.entry_id_prop.delete(0, 'end')
        self.lbl_info_cliente.config(text="Estado: No verificado", foreground='gray')
        self.cliente_verificado = False

        # Notificar al contenedor principal para refrescar el catálogo, CRM y Agente
        if self.al_completar_transaccion:
            self.al_completar_transaccion()
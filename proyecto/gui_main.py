import tkinter as tk
from tkinter import ttk, messagebox
import persistencia

# Importación de los módulos independientes
from modulo_catalogo import VistaCatalogo
from modulo_transacciones import VistaTransacciones
from modulo_registro_propiedad import VistaRegistroPropiedad
from modulo_clientes import VistaClientes
from modulo_gestion_agente import VistaGestionAgente

# 1. IMPORTAR LA VISTA DE KPIS DESDE gui_kpi.py
from gui_kpi import VistaKPIs


class AplicacionInmobiliaria(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema Integrado de Gestión Inmobiliaria y CRM")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Inicializar y verificar archivos CSV al arrancar
        try:
            persistencia.inicializar_archivos_csv()
        except Exception as e:
            messagebox.showwarning(
                "Advertencia de Inicialización", 
                f"Ocurrió un detalle al verificar la persistencia CSV: {str(e)}"
            )

        self.construir_interfaz()

    def construir_interfaz(self):
        # ------------------------------------------------------------------
        # ENCABEZADO PRINCIPAL
        # ------------------------------------------------------------------
        frame_header = ttk.Frame(self)
        frame_header.pack(fill='x', padx=15, pady=10)

        lbl_titulo = ttk.Label(
            frame_header, 
            text="🏠 Sistema de Gestión Inmobiliaria", 
            font=('Arial', 16, 'bold')
        )
        lbl_titulo.pack(side='left')

        btn_refrescar_todo = ttk.Button(
            frame_header, 
            text="🔄 Actualizar Todo", 
            command=self.recargar_todas_las_vistas
        )
        btn_refrescar_todo.pack(side='right')

        # ------------------------------------------------------------------
        # CONTENEDOR DE PESTAÑAS (ttk.Notebook)
        # ------------------------------------------------------------------
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # 1. Pestaña Catálogo
        self.vista_catalogo = VistaCatalogo(self.notebook)
        self.notebook.add(self.vista_catalogo, text=" 🔍 Catálogo de Propiedades ")

        # 2. Pestaña Registro de Propiedades
        self.vista_registro_prop = VistaRegistroPropiedad(
            self.notebook, 
            al_guardar_propiedad=self.recargar_todas_las_vistas
        )
        self.notebook.add(self.vista_registro_prop, text=" ➕ Registrar Propiedad ")

        # 3. Pestaña Transacciones
        self.vista_transacciones = VistaTransacciones(
            self.notebook, 
            al_completar_transaccion=self.recargar_todas_las_vistas
        )
        self.notebook.add(self.vista_transacciones, text=" ⚡ Transacciones ")

        # 4. Pestaña Clientes / CRM
        self.vista_clientes = VistaClientes(
            self.notebook, 
            al_actualizar_cliente=self.recargar_todas_las_vistas
        )
        self.notebook.add(self.vista_clientes, text=" 👥 Clientes (CRM) ")

        # 5. Pestaña SCM / Gestión de Agente
        self.vista_agente = VistaGestionAgente(
            self.notebook,
            al_actualizar=self.recargar_todas_las_vistas
        )
        self.notebook.add(self.vista_agente, text=" 👔 Gestión Agente SCM ")

        # ------------------------------------------------------------------
        # 6. PESTAÑA DASHBOARD KPIS (NUEVA INTEGRACIÓN)
        # ------------------------------------------------------------------
        self.vista_kpis = VistaKPIs(self.notebook)
        self.notebook.add(self.vista_kpis, text=" 📊 Dashboard KPIs ")

    def recargar_todas_las_vistas(self):
        """Notifica a todos los módulos que refresquen sus datos desde los archivos CSV."""
        self.vista_catalogo.actualizar_vista()
        self.vista_clientes.actualizar_vista()
        
        # Se refresca la tabla del agente cuando ocurra un cambio global
        if hasattr(self, 'vista_agente'):
            self.vista_agente.actualizar_tabla()

        # Refrescar los gráficos del Dashboard de KPIs
        if hasattr(self, 'vista_kpis'):
            self.vista_kpis.actualizar_vista()


if __name__ == "__main__":
    app = AplicacionInmobiliaria()
    app.mainloop()
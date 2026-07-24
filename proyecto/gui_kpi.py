import os
import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

HOY = pd.Timestamp("2026-07-23")

class VistaKPIs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.canvas = None
        self.canvas_widget = None

        # Configurar estructura del Frame
        self.crear_encabezado()
        self.actualizar_vista()

    def crear_encabezado(self):
        """Crea la barra superior de control del módulo."""
        frame_top = ttk.Frame(self)
        frame_top.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)

        lbl_titulo = ttk.Label(
            frame_top, 
            text="📊 Dashboard de KPIs Inmobiliarios", 
            font=("Arial", 14, "bold")
        )
        lbl_titulo.pack(side=tk.LEFT)

        btn_refrescar = ttk.Button(
            frame_top, 
            text="🔄 Actualizar KPIs", 
            command=self.actualizar_vista
        )
        btn_refrescar.pack(side=tk.RIGHT)

    def generar_figura_kpis(self):
        """Procesa la información de los CSV y retorna la figura de Matplotlib."""
        rutas_csv = [
            "datos/transacciones_comerciales.csv",
            "datos/crm_clientes.csv",
            "datos/estado_comercial.csv",
            "datos/propiedades.csv"
        ]
        
        # Validar existencia de archivos
        if not all(os.path.exists(r) for r in rutas_csv):
            fig = plt.Figure(figsize=(10, 6), dpi=90, facecolor="#f8f9fa")
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "No se encontraron los datos CSV en datos/.\nInicialice la aplicación para generarlos.", 
                    ha="center", va="center", fontsize=12, color="#64748b")
            ax.axis("off")
            return fig

        try:
            # 1. Cargar DataFrames
            tx = pd.read_csv("datos/transacciones_comerciales.csv")
            clientes = pd.read_csv("datos/crm_clientes.csv")
            estado = pd.read_csv("datos/estado_comercial.csv")
            prop = pd.read_csv("datos/propiedades.csv", usecols=["id", "region"])

            fig = plt.Figure(figsize=(11, 7), dpi=90, facecolor="#f8f9fa")
            gs = fig.add_gridspec(3, 2, hspace=0.45, wspace=0.28, top=0.92, bottom=0.08, left=0.08, right=0.95)

            # Verificar si hay transacciones registradas
            if tx.empty:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, "Sin datos de transacciones comerciales registradas.", 
                        ha="center", va="center", fontsize=12, color="#64748b")
                ax.axis("off")
                return fig

            tx["fecha"] = pd.to_datetime(tx["fecha"])
            tx["id_propiedad"] = tx["id_propiedad"].astype(str)
            estado["id_propiedad"] = estado["id_propiedad"].astype(str)
            prop["id"] = prop["id"].astype(str)

            tx = tx.merge(prop, left_on="id_propiedad", right_on="id", how="left")

            # ------------------------------------------------------------------
            # KPI 1: Evolución de ventas
            # ------------------------------------------------------------------
            ax1 = fig.add_subplot(gs[0, :])
            diario = tx.set_index("fecha")["monto"].resample("D").sum().fillna(0)
            semanal = tx.set_index("fecha")["monto"].resample("W").sum().fillna(0)
            
            ax1.plot(diario.index, diario.values, color="#93c5fd", linewidth=0.8, alpha=0.6, label="Diario")
            ax1.plot(semanal.index, semanal.values, color="#1e40af", linewidth=2.0, label="Semanal")
            ax1.set_title("KPI 1 · Evolución de ventas (diaria y semanal)", fontsize=10, fontweight="bold", color="#1e293b")
            ax1.set_ylabel("Monto ($)", fontsize=8, color="#334155")
            ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
            ax1.legend(loc="upper left", fontsize=8)
            ax1.grid(alpha=0.3, color="#94a3b8", linestyle="--")

            # ------------------------------------------------------------------
            # KPI 2: Promedio recaudado por región
            # ------------------------------------------------------------------
            ax2 = fig.add_subplot(gs[1, 0])
            prom_region = tx.groupby("region")["monto"].mean().sort_values(ascending=False)
            if not prom_region.empty:
                top = prom_region.head(8)
                if len(prom_region) > 8:
                    top = pd.concat([top, pd.Series({"Otras": prom_region.iloc[8:].mean()})])

                colores_pie = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#38bdf8", "#06b6d4", "#14b8a6", "#10b981", "#64748b"][:len(top)]
                ax2.pie(
                    top.values, labels=top.index, autopct="%1.1f%%", colors=colores_pie,
                    textprops={"fontsize": 7.5, "color": "#1e293b"}, pctdistance=0.7,
                    wedgeprops=dict(width=0.55, edgecolor='white', linewidth=1.5)
                )
            ax2.set_title("KPI 2 · Promedio recaudado por región", fontsize=10, fontweight="bold", color="#1e293b")

            # ------------------------------------------------------------------
            # KPI 3: Etapa de gestión de la propiedad
            # ------------------------------------------------------------------
            ax3 = fig.add_subplot(gs[1, 1])
            etiquetas_estado = {
                "disponible": "Disponible", 
                "negociacion": "Negociación", 
                "en_negociacion": "Negociación", 
                "vendido": "Vendida", 
                "vendida": "Vendida",
                "alquilado": "Alquilada",
                "alquilada": "Alquilada"
            }
            
            estado_mapeado = estado["status"].astype(str).str.lower().map(etiquetas_estado).fillna("Otros")
            conteo_estado = estado_mapeado.value_counts()
            colores_estado = {"Disponible": "#10b981", "Negociación": "#f59e0b", "Vendida": "#1e40af", "Alquilada": "#8b5cf6", "Otros": "#64748b"}
            
            bars3 = ax3.bar(conteo_estado.index, conteo_estado.values, color=[colores_estado.get(k, "#64748b") for k in conteo_estado.index], width=0.48)
            ax3.set_title("KPI 3 · Etapa de gestión de la propiedad", fontsize=10, fontweight="bold", color="#1e293b")
            ax3.tick_params(axis="x", labelsize=8)
            ax3.grid(axis="y", alpha=0.3, color="#94a3b8", linestyle="--")
            
            for b in bars3:
                h = b.get_height()
                ax3.text(b.get_x() + b.get_width() / 2, h + (h * 0.02 if h > 0 else 0.1), f"{h:,.0f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

            # ------------------------------------------------------------------
            # KPI 4: Segmentación RFM
            # ------------------------------------------------------------------
            ax4 = fig.add_subplot(gs[2, 0])
            rfm = tx.groupby("id_cliente").agg(
                recencia=("fecha", lambda s: (HOY - s.max()).days),
                frecuencia=("id_transaccion", "count"),
                monetario=("monto", "sum"),
            ).reset_index()

            if len(rfm) >= 4:
                rfm["r_score"] = pd.qcut(rfm["recencia"], 4, labels=[4, 3, 2, 1], duplicates='drop').astype(int)
                rfm["f_score"] = pd.qcut(rfm["frecuencia"].rank(method="first"), 4, labels=[1, 2, 3, 4], duplicates='drop').astype(int)
                rfm["m_score"] = pd.qcut(rfm["monetario"], 4, labels=[1, 2, 3, 4], duplicates='drop').astype(int)
                rfm["rfm_total"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]
            else:
                rfm["rfm_total"] = 6 # Asignación por defecto en datasets pequeños

            def segmentar(s):
                if s >= 10: return "Champions"
                elif s >= 8: return "Leales"
                elif s >= 6: return "Potenciales"
                elif s >= 4: return "En riesgo"
                else: return "Perdidos"

            rfm["segmento"] = rfm["rfm_total"].apply(segmentar)
            orden_seg = ["Champions", "Leales", "Potenciales", "En riesgo", "Perdidos"]
            conteo_seg = rfm["segmento"].value_counts().reindex(orden_seg).fillna(0)
            colores_seg = ["#15803d", "#22c55e", "#f59e0b", "#f97316", "#ef4444"]

            bars4 = ax4.bar(conteo_seg.index, conteo_seg.values, color=colores_seg, width=0.48)
            ax4.set_title("KPI 4 · Segmentación RFM de clientes", fontsize=10, fontweight="bold", color="#1e293b")
            ax4.tick_params(axis="x", rotation=15, labelsize=8)
            ax4.grid(axis="y", alpha=0.3, color="#94a3b8", linestyle="--")

            for b in bars4:
                h = b.get_height()
                ax4.text(b.get_x() + b.get_width() / 2, h + (h * 0.02 if h > 0 else 0.1), f"{int(h)}", ha="center", va="bottom", fontsize=8, fontweight="bold")

            # ------------------------------------------------------------------
            # KPI 5: Embudo comercial CRM
            # ------------------------------------------------------------------
            ax5 = fig.add_subplot(gs[2, 1])
            orden_etapa = ["Prospecto", "Negociación", "Cliente Cerrado"]
            conteo_etapa = clientes["etapa"].value_counts().reindex(orden_etapa).fillna(0) if "etapa" in clientes.columns else pd.Series(0, index=orden_etapa)
            colores_etapa = ["#64748b", "#f59e0b", "#1e40af"]

            bars5 = ax5.barh(conteo_etapa.index[::-1], conteo_etapa.values[::-1], color=colores_etapa[::-1], height=0.45)
            ax5.set_title("KPI 5 · Embudo comercial CRM", fontsize=10, fontweight="bold", color="#1e293b")
            ax5.tick_params(axis="y", labelsize=8)
            ax5.grid(axis="x", alpha=0.3, color="#94a3b8", linestyle="--")

            for b in bars5:
                w = b.get_width()
                ax5.text(w + (w * 0.015 if w > 0 else 0.1), b.get_y() + b.get_height() / 2, f"{int(w):,}", va="center", fontsize=8, fontweight="bold")

            # Estilo general de ejes
            for ax in [ax1, ax3, ax4, ax5]:
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)

            return fig

        except Exception as e:
            fig = plt.Figure(figsize=(10, 6), dpi=90, facecolor="#f8f9fa")
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error cargando gráficos del Dashboard:\n{str(e)}", 
                    ha="center", va="center", fontsize=11, color="#ef4444")
            ax.axis("off")
            return fig

    def actualizar_vista(self):
        """Refresca la figura eliminando el canvas previo y montando la nueva gráfica."""
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        fig = self.generar_figura_kpis()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.canvas.draw()
import csv
import os
from datetime import datetime

RUTA_DATOS = "datos"

def asegurar_directorio():
    if not os.path.exists(RUTA_DATOS):
        os.makedirs(RUTA_DATOS)

# Rutas unificadas dentro del directorio 'datos'
ARCHIVO_PROPIEDADES = os.path.join(RUTA_DATOS, "propiedades.csv")
ARCHIVO_ESTADO = os.path.join(RUTA_DATOS, "estado_comercial.csv")
ARCHIVO_CLIENTES = os.path.join(RUTA_DATOS, "crm_clientes.csv")
ARCHIVO_TRANSACCIONES = os.path.join(RUTA_DATOS, "transacciones_comerciales.csv")

FIELDNAMES_ESTADO = ['id_propiedad', 'transaction_type', 'status', 'visitas']
FIELDNAMES_CLIENTES = ['id_cliente', 'nombre', 'email', 'telefono', 'id_propiedad_interes', 'etapa', 'fecha_ultima_interaccion', 'monto_total']

# ----------------------------------------------------------------------
# CACHÉ EN MEMORIA PARA LECTURAS ULTRARRÁPIDAS
# ----------------------------------------------------------------------
_CACHE_PROPIEDADES = None
_CACHE_ESTADO = None
_CACHE_CLIENTES = None

def _cargar_cache_propiedades(recargar=False):
    global _CACHE_PROPIEDADES
    if _CACHE_PROPIEDADES is not None and not recargar:
        return _CACHE_PROPIEDADES
    
    _CACHE_PROPIEDADES = {}
    if os.path.exists(ARCHIVO_PROPIEDADES):
        with open(ARCHIVO_PROPIEDADES, mode='r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                p_id = str(row.get('id') or '').strip()
                if p_id:
                    _CACHE_PROPIEDADES[p_id] = row
    return _CACHE_PROPIEDADES

def _cargar_cache_estado(recargar=False):
    global _CACHE_ESTADO
    if _CACHE_ESTADO is not None and not recargar:
        return _CACHE_ESTADO
    
    _CACHE_ESTADO = {}
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, mode='r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                p_id = str(row.get('id_propiedad') or '').strip()
                if p_id:
                    _CACHE_ESTADO[p_id] = row
    return _CACHE_ESTADO

def _cargar_cache_clientes(recargar=False):
    global _CACHE_CLIENTES
    if _CACHE_CLIENTES is not None and not recargar:
        return _CACHE_CLIENTES
    
    _CACHE_CLIENTES = {}
    if os.path.exists(ARCHIVO_CLIENTES):
        with open(ARCHIVO_CLIENTES, mode='r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                c_id = str(row.get('id_cliente') or '').strip()
                if c_id:
                    row['id'] = c_id
                    _CACHE_CLIENTES[c_id] = row
    return _CACHE_CLIENTES


def inicializar_archivos_csv():
    """Garantiza la existencia del directorio y de las estructuras iniciales."""
    asegurar_directorio()

    if not os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES_ESTADO)

    if not os.path.exists(ARCHIVO_CLIENTES):
        with open(ARCHIVO_CLIENTES, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(FIELDNAMES_CLIENTES)
    
    # Precargar cachés desde el disco al iniciar
    _cargar_cache_propiedades(recargar=True)
    _cargar_cache_estado(recargar=True)
    _cargar_cache_clientes(recargar=True)


# ----------------------------------------------------------------------
# 1. GESTIÓN DE PROPIEDADES (INMUEBLES)
# ----------------------------------------------------------------------
def guardar_propiedad_csv(datos_propiedad):
    """Guarda o actualiza una propiedad sobreescribiendo si el ID ya existe."""
    asegurar_directorio()
    
    encabezados = [
        'id', 'url', 'region', 'region_url', 'price', 'type', 'sqfeet', 'beds',
        'baths', 'cats_allowed', 'dogs_allowed', 'smoking_allowed',
        'wheelchair_access', 'electric_vehicle_charge', 'comes_furnished',
        'laundry_options', 'parking_options', 'image_url', 'description',
        'lat', 'long', 'state'
    ]
    
    id_prop = str(datos_propiedad.get('id') or '').strip()
    tipo_op = str(datos_propiedad.get('type') or 'venta').strip().lower()
    
    props_cache = _cargar_cache_propiedades()
    if id_prop in props_cache:
        fila = {k: datos_propiedad.get(k, props_cache[id_prop].get(k, '')) for k in encabezados}
    else:
        fila = {k: datos_propiedad.get(k, '') for k in encabezados}
    
    props_cache[id_prop] = fila

    with open(ARCHIVO_PROPIEDADES, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        writer.writeheader()
        writer.writerows(list(props_cache.values()))

    # Sincronizar memoria y estado inicial
    _cargar_cache_propiedades(recargar=True)
    _crear_o_actualizar_estado_inicial(id_prop, tipo_op)


def _crear_o_actualizar_estado_inicial(id_propiedad, tipo_operacion):
    id_prop = str(id_propiedad or '').strip()
    if not id_prop:
        return

    estado_cache = _cargar_cache_estado()

    if id_prop not in estado_cache:
        estado_cache[id_prop] = {
            'id_propiedad': id_prop,
            'transaction_type': str(tipo_operacion or 'venta').strip().lower(),
            'status': 'disponible',
            'visitas': '0'
        }
        with open(ARCHIVO_ESTADO, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES_ESTADO)
            writer.writeheader()
            writer.writerows(list(estado_cache.values()))

        _cargar_cache_estado(recargar=True)


def obtener_todas_propiedades():
    props_map = _cargar_cache_propiedades(recargar=True)
    estados_map = _cargar_cache_estado(recargar=True)

    resultado = []
    for p_id, prop in props_map.items():
        prop_copy = dict(prop)
        estado_info = estados_map.get(p_id, {})
        val_status = estado_info.get('status') if estado_info else None
        prop_copy['disponibilidad'] = str(val_status or 'disponible').strip().lower()
        resultado.append(prop_copy)
    return resultado


def obtener_resumen_propiedades():
    estados_map = _cargar_cache_estado(recargar=True)
    disponibles = vendidas = alquiladas = 0

    for row in estados_map.values():
        val_status = row.get('status')
        status = str(val_status or '').strip().lower()
        if status in ['disponible', 'captacion', 'evaluacion', 'negociacion']:
            disponibles += 1
        elif status in ['vendido', 'vendida']:
            vendidas += 1
        elif status in ['alquilado', 'alquilada']:
            alquiladas += 1

    return {"disponibles": disponibles, "vendidas": vendidas, "alquiladas": alquiladas}


def obtener_precio_propiedad(id_propiedad):
    props = _cargar_cache_propiedades()
    p_info = props.get(str(id_propiedad or '').strip())
    if p_info:
        try:
            return float(p_info.get('price', 0.0))
        except (ValueError, TypeError):
            return 0.0
    return 0.0


# ----------------------------------------------------------------------
# 2. CLIENTES Y CRM
# ----------------------------------------------------------------------
def guardar_cliente_csv(datos_cliente):
    asegurar_directorio()
    
    clientes_cache = _cargar_cache_clientes(recargar=True)

    id_cli = str(datos_cliente.get('id') or datos_cliente.get('id_cliente') or '').strip()
    if not id_cli:
        return

    row_prev = clientes_cache.get(id_cli, {})
    
    nuevo_registro = {
        'id_cliente': id_cli,
        'nombre': datos_cliente.get('nombre', row_prev.get('nombre', '')),
        'email': datos_cliente.get('email', row_prev.get('email', '')),
        'telefono': datos_cliente.get('telefono', row_prev.get('telefono', '')),
        'id_propiedad_interes': str(datos_cliente.get('id_propiedad_interes', row_prev.get('id_propiedad_interes', ''))).strip(),
        'etapa': datos_cliente.get('etapa', row_prev.get('etapa', 'Prospecto')),
        'fecha_ultima_interaccion': datetime.now().strftime('%Y-%m-%d'),
        'monto_total': str(datos_cliente.get('monto_total', row_prev.get('monto_total', '0.0')))
    }
    nuevo_registro['id'] = id_cli
    clientes_cache[id_cli] = nuevo_registro

    with open(ARCHIVO_CLIENTES, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES_CLIENTES)
        writer.writeheader()
        for cli in clientes_cache.values():
            fila_filtrada = {k: cli.get(k, '') for k in FIELDNAMES_CLIENTES}
            writer.writerow(fila_filtrada)

    _cargar_cache_clientes(recargar=True)


def obtener_todos_clientes():
    clientes_map = _cargar_cache_clientes(recargar=True)
    return list(clientes_map.values())


def obtener_cliente_por_id(id_cliente):
    clientes_map = _cargar_cache_clientes()
    return clientes_map.get(str(id_cliente or '').strip())


def actualizar_monto_cliente_crm(id_cliente, monto_adicional):
    clientes_map = _cargar_cache_clientes(recargar=True)
    id_cli = str(id_cliente or '').strip()
    
    if id_cli in clientes_map:
        cliente = clientes_map[id_cli]
        monto_actual = float(cliente.get('monto_total', 0.0) or 0.0)
        cliente['monto_total'] = str(monto_actual + float(monto_adicional))
        cliente['fecha_ultima_interaccion'] = datetime.now().strftime('%Y-%m-%d')
        cliente['etapa'] = 'Cliente Cerrado'

        with open(ARCHIVO_CLIENTES, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES_CLIENTES)
            writer.writeheader()
            for cli in clientes_map.values():
                fila_filtrada = {k: cli.get(k, '') for k in FIELDNAMES_CLIENTES}
                writer.writerow(fila_filtrada)

        _cargar_cache_clientes(recargar=True)


def eliminar_cliente_csv(id_cliente):
    clientes_map = _cargar_cache_clientes(recargar=True)
    id_cli = str(id_cliente or '').strip()

    if id_cli in clientes_map:
        del clientes_map[id_cli]
        with open(ARCHIVO_CLIENTES, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES_CLIENTES)
            writer.writeheader()
            for cli in clientes_map.values():
                fila_filtrada = {k: cli.get(k, '') for k in FIELDNAMES_CLIENTES}
                writer.writerow(fila_filtrada)

        _cargar_cache_clientes(recargar=True)
        return True
    return False


# ----------------------------------------------------------------------
# 3. TRANSACCIONES Y VALIDACIONES
# ----------------------------------------------------------------------
def validar_propiedad_para_operacion(id_propiedad, tipo_operacion, id_cliente=None):
    """
    Valida la viabilidad de la operación.
    - Si está en 'negociacion', SOLO la puede operar el cliente asignado en CRM.
    """
    estados_map = _cargar_cache_estado(recargar=True)
    id_prop_str = str(id_propiedad or '').strip()
    id_cli_str = str(id_cliente or '').strip() if id_cliente else None

    row = estados_map.get(id_prop_str)
    if not row:
        return False, f"La propiedad '{id_prop_str}' no fue encontrada en el sistema."

    tx_type = str(row.get('transaction_type') or '').strip().lower()
    status = str(row.get('status') or '').strip().lower()

    if status in ['vendido', 'vendida', 'alquilado', 'alquilada', 'cerrado']:
        return False, f"La propiedad '{id_prop_str}' NO está disponible (Estado actual: {status.upper()})."

    if tx_type != str(tipo_operacion or '').strip().lower():
        return False, f"Incompatibilidad: La propiedad es de tipo '{tx_type.upper()}' y se intenta operar como '{tipo_operacion.upper()}'."

    if status == 'negociacion':
        cliente_titular = _obtener_cliente_asociado_negociacion(id_prop_str)
        if cliente_titular and cliente_titular != id_cli_str:
            return False, f"Operación denegada: La propiedad #{id_prop_str} se encuentra reservada en negociación por otro cliente."

    return True, "Propiedad válida."


def _obtener_cliente_asociado_negociacion(id_propiedad):
    """Busca en caché qué cliente tiene en interés esta propiedad."""
    clientes_map = _cargar_cache_clientes()
    id_prop_str = str(id_propiedad or '').strip()
    for c_id, cliente in clientes_map.items():
        if str(cliente.get('id_propiedad_interes') or '').strip() == id_prop_str:
            return c_id
    return None


def registrar_transaccion_csv(id_cliente, id_propiedad, tipo_operacion, monto):
    asegurar_directorio()
    encabezados = ['id_transaccion', 'id_cliente', 'id_propiedad', 'tipo_operacion', 'monto', 'fecha']
    
    id_transaccion = f"TX-{int(datetime.now().timestamp())}"
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    file_exists = os.path.exists(ARCHIVO_TRANSACCIONES)

    with open(ARCHIVO_TRANSACCIONES, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'id_transaccion': id_transaccion,
            'id_cliente': str(id_cliente),
            'id_propiedad': str(id_propiedad),
            'tipo_operacion': str(tipo_operacion or '').strip().lower(),
            'monto': str(monto),
            'fecha': fecha_actual
        })

    nuevo_estado = "vendido" if str(tipo_operacion or '').lower() == "venta" else "alquilado"
    actualizar_estado_comercial_csv(id_propiedad, nuevo_estado)


def actualizar_estado_comercial_csv(id_propiedad, nuevo_estado):
    actualizar_etapa_agente(id_propiedad, nuevo_estado)


def guardar_estado_comercial_csv(datos_estado):
    id_prop = str(datos_estado.get('id_propiedad') or '').strip()
    etapa = str(datos_estado.get('status') or 'disponible').strip().lower()
    
    try:
        visitas_int = int(float(datos_estado.get('visitas', 0)))
    except (ValueError, TypeError):
        visitas_int = 0

    actualizar_etapa_agente(id_prop, etapa, incremento_visitas=visitas_int)


def obtener_transacciones_por_cliente(id_cliente):
    if not os.path.exists(ARCHIVO_TRANSACCIONES):
        return []

    transacciones = []
    id_cli_target = str(id_cliente or '').strip()
    with open(ARCHIVO_TRANSACCIONES, mode='r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if str(row.get('id_cliente') or '').strip() == id_cli_target:
                transacciones.append(row)
    return transacciones


# ----------------------------------------------------------------------
# 4. GESTIÓN SCM UNIFICADA (estado_comercial.csv)
# ----------------------------------------------------------------------
def inicializar_gestion_agentes(id_propiedad, **kwargs):
    asegurar_directorio()
    id_propiedad = str(id_propiedad or '').strip()
    if not id_propiedad:
        return
    _crear_o_actualizar_estado_inicial(id_propiedad, kwargs.get('transaction_type', 'venta'))


def obtener_todos_gestion_agentes():
    propiedades_map = _cargar_cache_propiedades(recargar=True)
    estados_map = _cargar_cache_estado(recargar=True)

    resultado_final = []
    for p_id, estado_row in estados_map.items():
        p_info = propiedades_map.get(p_id, {'type': 'N/A', 'price': '0.0'})
        
        try:
            visitas_val = int(float(estado_row.get('visitas', 0)))
        except (ValueError, TypeError):
            visitas_val = 0

        resultado_final.append({
            'id_propiedad': p_id,
            'etapa_gestion': str(estado_row.get('status') or 'disponible').strip().lower(),
            'visitas': str(visitas_val),
            'type': p_info.get('type', 'N/A'),
            'price': p_info.get('price', '0.0')
        })

    return resultado_final


def actualizar_etapa_agente(id_propiedad, nueva_etapa, incremento_visitas=0, **kwargs):
    asegurar_directorio()
    id_target = str(id_propiedad or '').strip()
    etapa_limpia = str(nueva_etapa or '').strip().lower()
    
    estados_map = _cargar_cache_estado()
    
    if id_target in estados_map:
        row = estados_map[id_target]
        row['status'] = etapa_limpia
        try:
            visitas_actuales = int(float(row.get('visitas', 0)))
        except (ValueError, TypeError):
            visitas_actuales = 0
        row['visitas'] = str(visitas_actuales + int(incremento_visitas))
    else:
        estados_map[id_target] = {
            'id_propiedad': id_target,
            'transaction_type': 'venta',
            'status': etapa_limpia,
            'visitas': str(int(incremento_visitas))
        }

    with open(ARCHIVO_ESTADO, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES_ESTADO)
        writer.writeheader()
        writer.writerows(list(estados_map.values()))

    # Se invalida el caché para reflejar los cambios en el resumen del Dashboard
    _cargar_cache_estado(recargar=True)


def sincronizar_propiedades_existentes_scm():
    props_map = _cargar_cache_propiedades()
    for p_id, p in props_map.items():
        p_tipo = str(p.get('type') or 'venta').strip()
        _crear_o_actualizar_estado_inicial(p_id, p_tipo)


def registrar_cierre_transaccion(id_propiedad):
    id_prop = str(id_propiedad or '').strip()
    
    estados_map = _cargar_cache_estado()
    estado_info = estados_map.get(id_prop, {})
    tipo_operacion = str(estado_info.get('transaction_type') or '').strip().lower()

    if not tipo_operacion:
        props_map = _cargar_cache_propiedades()
        tipo_operacion = str(props_map.get(id_prop, {}).get('type') or 'venta').strip().lower()

    if tipo_operacion in ['venta', 'sale', 'vender']:
        nuevo_estado = 'vendido'
    else:
        nuevo_estado = 'alquilado'

    actualizar_etapa_agente(id_prop, nuevo_estado)

# Alias de compatibilidad
obtener_propiedades_por_cliente = obtener_transacciones_por_cliente
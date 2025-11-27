# Líneas 1-3
import streamlit as st
import sqlite3
import datetime

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_NAME = 'usuarios.db' # Usamos tu nombre de archivo original

def crear_tabla():
    """Crea la tabla de tickets si no existe con todos los campos necesarios."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Cambiamos 'fecha' y 'estado' por 'fecha_creacion' y 'estatus' para mayor claridad.
    # Y agregamos el campo 'detalles_adicionales'
    c.execute("""CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                asunto TEXT,
                tipo TEXT,
                descripcion TEXT,
                detalles_adicionales TEXT, 
                fecha_creacion TEXT,
                estatus TEXT
              )""")
    conn.commit()
    conn.close()

def guardar_ticket(nombre, asunto, tipo, descripcion, detalles_adicionales=None):
    """Inserta un nuevo ticket en la base de datos."""
    
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estatus_inicial = "Abierto" # Asignamos el estatus por defecto
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""INSERT INTO tickets 
              (nombre, asunto, tipo, descripcion, detalles_adicionales, fecha_creacion, estatus) 
              VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (nombre, asunto, tipo, descripcion, detalles_adicionales, fecha_actual, estatus_inicial))
    
    conn.commit()
    ticket_id = c.lastrowid # Obtenemos el ID generado para usarlo como folio
    conn.close()
    
    return ticket_id

# Inicializamos la DB al arrancar la app
crear_tabla() 

# --- INTERFAZ GRÁFICA WEB ---
st.set_page_config(page_title="Mesa de Ayuda", page_icon="🔧")

st.title("🔧 Centro de Soporte y Garantías")
st.markdown("---")

# Menú lateral
menu = st.sidebar.radio("Selecciona tu perfil:", ["Soy Cliente", "Soy Empleado"])

# --- VISTA CLIENTE ---
if menu == "Soy Cliente":
    if menu == "Soy Cliente":
       st.subheader("📝 Reportar un problema")
       st.info("Llena este formulario y nuestro equipo te atenderá. Los campos variarán según tu solicitud.")
    
    # 1. Inicialización de variables adicionales para evitar errores
    # Si la variable 'detalles_adicionales' no se usa, la inicializamos vacía
    detalles_adicionales = None
    
    with st.form("form_ticket"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Tu Nombre o Empresa", key="nombre_cliente")
        tipo = col2.selectbox("Tipo de Solicitud", ["Falla de Equipo", "Garantía", "Software/Licencias", "Otro"], key="tipo_solicitud")
        
        # 2. LÓGICA CONDICIONAL DE CAMPOS ADICIONALES
        if tipo == "Falla de Equipo":
            detalles_adicionales = st.text_input("Número de Serie o Tag de Inventario del Equipo", key="serie_equipo")
        elif tipo == "Software/Licencias":
            detalles_adicionales = st.text_input("Número de Licencia o Clave de Producto", key="licencia_software")
        
        # El resto del formulario
        asunto = st.text_input("Asunto (Ej: La impresora X no enciende)", key="asunto_ticket")
        descripcion = st.text_area("Describe el problema detalladamente (Ubicación, qué pasó, mensajes de error)", key="descripcion_ticket")
        
        enviado = st.form_submit_button("Enviar Ticket")
        
if enviado:
            # Tu lógica de validación aquí...
            
            # Si el tipo requiere un campo adicional, y no fue llenado
            if (tipo == "Falla de Equipo" or tipo == "Software/Licencias") and not detalles_adicionales:
                st.error("⚠️ Por favor ingresa el número de serie/licencia requerido para este tipo de solicitud.")
            
            # Si la validación pasa:
            elif nombre and asunto and descripcion:
                # Llama a la función de guardado y captura el FOLIO
                folio = guardar_ticket(nombre, asunto, tipo, descripcion, detalles_adicionales) 
                
                st.success(f"✅ ¡Ticket enviado! Tu folio de seguimiento es el **{folio}**.")
                st.balloons()
            else:
                st.error("⚠️ Por favor llena los campos Nombre, Asunto y Descripción.")
# --- VISTA EMPLEADO ---
elif menu == "Soy Empleado":
    st.subheader("🔒 Panel Administrativo")
    
    clave = st.text_input("Ingresa la contraseña de acceso:", type="password")
    
    if clave == "admin123":
        st.success("Acceso Correcto")
        
        conn = sqlite3.connect("usuarios.db")
        tickets = conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
        conn.close()
        
        st.metric(label="Tickets Totales", value=len(tickets))
        
        st.write("### Últimos Tickets Recibidos")
        
        if len(tickets) == 0:
            st.warning("No hay tickets registrados aún.")
        
        for t in tickets:
            with st.expander(f"🎫 #{t[0]} - {t[2]} ({t[1]})"):
                st.write(f"**Fecha:** {t[5]}")
                st.write(f"**Tipo:** {t[3]}")
                st.write(f"**Descripción:** {t[4]}")
                st.write(f"**Estado:** {t[6]}")
                st.button("Marcar como Resuelto", key=f"btn_{t[0]}")
                
    elif clave:
        st.warning("Contraseña incorrecta")
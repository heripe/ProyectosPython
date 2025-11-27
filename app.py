import streamlit as st
import sqlite3
import datetime

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    # Tabla de tickets con columna de FECHA
    c.execute('''CREATE TABLE IF NOT EXISTS tickets 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nombre TEXT, 
                  asunto TEXT, 
                  tipo TEXT, 
                  descripcion TEXT, 
                  fecha TEXT,
                  estado TEXT)''')
    conn.commit()
    conn.close()

def guardar_ticket(nombre, asunto, tipo, desc):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    # Obtenemos fecha y hora actual automáticamente
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    c.execute("INSERT INTO tickets (nombre, asunto, tipo, descripcion, fecha, estado) VALUES (?, ?, ?, ?, ?, 'ABIERTO')", 
              (nombre, asunto, tipo, desc, fecha_hoy))
    conn.commit()
    conn.close()

# Inicializamos la DB al arrancar la app
init_db()

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
            # 3. VALIDACIÓN (Añadimos la validación del nuevo campo si es necesario)
            if nombre and asunto and descripcion:
                # Verificamos si se requiere el campo adicional y si fue llenado
                if (tipo == "Falla de Equipo" or tipo == "Software/Licencias") and not detalles_adicionales:
                    st.error("⚠️ Por favor ingresa el número de serie/licencia requerido para este tipo de solicitud.")
                else:
                    # Llama a tu función de guardado (tendrás que modificarla para que acepte el nuevo campo)
                    guardar_ticket(nombre, asunto, tipo, descripcion, detalles_adicionales) 
                    st.success("✅ ¡Ticket enviado! Tu folio ha sido registrado.")
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
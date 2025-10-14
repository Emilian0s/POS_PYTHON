import sqlite3
import os

# ✅ Ruta absoluta a la base
carpeta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta_db = os.path.join(carpeta_raiz, "pos_carniceria.db")

# ✅ Función de conexión
def obtener_conexion():
    return sqlite3.connect(ruta_db)

# ✅ Crear tabla ventas (solo si no existe)
def crear_tabla_ventas():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            factura INTEGER,
            nombre_articulo TEXT,
            valor_articulo INTEGER,
            cantidad INTEGER,
            subtotal INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'ventas' verificada/creada correctamente.")

# ✅ Crear tabla inventario (solo si no existe)
def crear_tabla_inventario():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            codigo_barra TEXT UNIQUE,              
            nombre TEXT NOT NULL,                      
            proveedor TEXT NOT NULL,
            precio REAL NOT NULL,
            costo REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla 'inventario' verificada/creada correctamente.")

# ✅ Crear todas las tablas
def crear_tablas():
    crear_tabla_ventas()
    crear_tabla_inventario()

# ✅ Insertar producto en inventario
def guardar_producto(codigo_barra, nombre, proveedor, precio, costo, stock):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventario (codigo_barra, nombre, proveedor, precio, costo, stock)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (codigo_barra, nombre, proveedor, precio, costo, stock))
    conn.commit()
    conn.close()

# ✅ Insertar artículo vendido
def guardar_venta(factura, nombre, valor, cantidad, subtotal):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ventas (factura, nombre_articulo, valor_articulo, cantidad, subtotal)
        VALUES (?, ?, ?, ?, ?)
    ''', (factura, nombre, valor, cantidad, subtotal))
    conn.commit()
    conn.close()

# ✅ Ejecutar si se corre directo
if __name__ == "__main__":
    crear_tablas()

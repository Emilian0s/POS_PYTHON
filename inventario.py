import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from DB.database import obtener_conexion
from tkinter import simpledialog
from faker import Faker
import random

faker = Faker("es_ES")


class Inventario(tk.Frame):
    db_name = "pos_carniceria.db"
    
    def __init__(self, padre):
        super().__init__(padre)
        self.place(x=0, y=0, width=1100, height=650)
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.crear_tablas()  # <-- Agregar esta línea
        self.widgets()

    def crear_tablas(self):
        # Crear tabla inventario si no existe
        self.cursor.execute('''
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
        # Crear tabla ventas si no existe
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                factura INTEGER,
                nombre_articulo TEXT,
                valor_articulo INTEGER,
                cantidad INTEGER,
                subtotal INTEGER
            )
        ''')
        self.conn.commit()

    def widgets(self):
    
        frame1 = tk.Frame(self, bg="#dddddd", highlightbackground="gray", highlightthickness=1)
        frame1.place(x=0, y=0, width=1100, height=100)
    
        titulo = tk.Label(self, text="INVENTARIOS", bg="#dddddd", font="sans 30 bold")
        titulo.place(x=5, y=0, width=1090, height=90)
    
        frame2 = tk.Frame(self, bg="#c6d9e3", highlightbackground="gray", highlightthickness=1)
        frame2.place(x=0, y=100, width=1100, height=550)
    
        labelframe = LabelFrame(frame2, text="Productos: ", font="sans 22 bold", bg="#c6d9e3")
        labelframe.place(x=20, y=30, width=400, height=500)
    
        # --- NUEVO Código de Barra ---
        lblcodigo = Label(labelframe, text="Código Barra:", font="sans 14 bold", bg="#c6d9e3")
        lblcodigo.place(x=10, y=20)
        self.codigo_barra = ttk.Entry(labelframe, font="sans 14 bold")
        self.codigo_barra.place(x=140, y=20, width=240, height=40)
    
        # Nombre
        lblnombre = Label(labelframe, text="Nombre: ", font="sans 14 bold", bg="#c6d9e3")
        lblnombre.place(x=10, y=80)
        self.nombre = ttk.Entry(labelframe, font="sans 14 bold")
        self.nombre.place(x=140, y=80, width=240, height=40)

        # Proveedor
        lblproveedor = Label(labelframe, text="Proveedor: ", font="sans 14 bold", bg="#c6d9e3")
        lblproveedor.place(x=10, y=140)
        self.proveedor = ttk.Entry(labelframe, font="sans 14 bold")
        self.proveedor.place(x=140, y=140, width=240, height=40)
    
        # Precio
        lblprecio = Label(labelframe, text="Precio: ", font="sans 14 bold", bg="#c6d9e3")
        lblprecio.place(x=10, y=200)
        self.precio = ttk.Entry(labelframe, font="sans 14 bold")
        self.precio.place(x=140, y=200, width=240, height=40)
    
        # Costo
        lblcosto = Label(labelframe, text="Costo: ", font="sans 14 bold", bg="#c6d9e3")
        lblcosto.place(x=10, y=260)
        self.costo = ttk.Entry(labelframe, font="sans 14 bold")
        self.costo.place(x=140, y=260, width=240, height=40)
    
        # Stock
        lblstock = Label(labelframe, text="Stock: ", font="sans 14 bold", bg="#c6d9e3")
        lblstock.place(x=10, y=320)
        self.stock = ttk.Entry(labelframe, font="sans 14 bold")
        self.stock.place(x=140, y=320, width=240, height=40)
    
        # Botones
        boton_agregar = tk.Button(labelframe, text="Ingresar", font="sans 14 bold", bg="#dddddd", command=self.registrar)
        boton_agregar.place(x=80, y=380, width=240, height=40)
    
        boton_editar = tk.Button(labelframe, text="Editar", font="sans 14 bold", bg="#dddddd", command=self.editar_producto)
        boton_editar.place(x=80, y=425, width=240, height=40)
    
        # --- Tabla ---
        treFrame = Frame(frame2, bg="white")
        treFrame.place(x=450, y=50, width=620, height=400)
    
        scrol_y = Scrollbar(treFrame)
        scrol_y.place(x=600, y=0, width=20, height=380)
    
        scrol_x = Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.place(x=0, y=380, width=600, height=20)
    
        self.tre = ttk.Treeview(
            treFrame,
            yscrollcommand=scrol_y.set,
            xscrollcommand=scrol_x.set,
            height=40,
            columns=("ID", "CODIGO", "PRODUCTO","PROVEEDOR", "PRECIO", "COSTO", "STOCK"),
            show="headings",
            selectmode="extended"   # ← AQUÍ
        )
    
        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)
    
        self.tre.heading("ID", text="Id")
        self.tre.heading("CODIGO", text="Código")
        self.tre.heading("PRODUCTO", text="Producto")
        self.tre.heading("PROVEEDOR", text="Proveedor")
        self.tre.heading("PRECIO", text="Precio")
        self.tre.heading("COSTO", text="Costo")
        self.tre.heading("STOCK", text="Stock")
    
        self.tre.column("ID", width=50, anchor="center")
        self.tre.column("CODIGO", width=100, anchor="center")
        self.tre.column("PRODUCTO", width=100, anchor="center")
        self.tre.column("PROVEEDOR", width=100, anchor="center")
        self.tre.column("PRECIO", width=80, anchor="center")
        self.tre.column("COSTO", width=80, anchor="center")
        self.tre.column("STOCK", width=60, anchor="center")
    
        self.tre.place(x=0, y=0, width=600, height=380)
    
        self.mostrar()
    
        # Contenedor para botones de inventario
        frame_botones = Frame(frame2, bg="#c6d9e3")
        frame_botones.place(x=440, y=480, width=700, height=50)
    
        btn_actualizar = Button(frame_botones, text="Actualizar", font="sans 14 bold", command=self.actualizar_inventario)
        btn_actualizar.pack(side=LEFT, padx=6, pady=5, ipadx=10, ipady=5)
    
        btn_prueba = Button(frame_botones, text="Prueba", font="sans 14 bold", command=self.generar_datos_prueba)
        btn_prueba.pack(side=LEFT, padx=6, pady=5, ipadx=10, ipady=5)
        
        btn_eliminar_seleccion = Button(frame_botones, text="Eliminar seleccion", font="sans 14 bold", command=self.eliminar_registros)
        btn_eliminar_seleccion.pack(side=LEFT, padx=6, pady=5, ipadx=5, ipady=5)
    
        btn_eliminar = Button(frame_botones, text="Eliminar todos", font="sans 14 bold", command=self.eliminar_todos_los_datos)
        btn_eliminar.pack(side=LEFT, padx=6, pady=5, ipadx=10, ipady=10)

    def eje_consulta(self, consulta, parametros=()):
        conn = obtener_conexion()  # siempre la DB correcta
        cursor = conn.cursor()
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()  # ahora sí se llama la función
        conn.commit()
        conn.close()
        return filas
    
    def validacion(self, nombre, prov, precio, costo, stock):
        if not (nombre and prov and precio and costo and stock):
            return False
        try:
            float(precio)
            float(costo)
            int(stock)
        except ValueError:
            return False
        return True

    def mostrar(self):
        consulta = "SELECT id, codigo_barra, nombre, proveedor, precio, costo, stock FROM inventario ORDER BY id DESC"
        result = self.eje_consulta(consulta)
        for elem in result:
            try:
                precio_ars = "{:.2f} ARS".format(float(elem[4])) if elem[4] else ""
                costo_ars = "{:.2f} ARS".format(float(elem[5])) if elem[5] else "" 
            except ValueError:
                precio_ars = elem[4]
                costo_ars = elem[5]

            # Corregir el orden de valores según Treeview:
            # Treeview: ID, CODIGO, PRODUCTO, PROVEEDOR, PRECIO, COSTO, STOCK
            self.tre.insert(
                "", 0, text=elem[0],
                values=(
                    elem[0],        # ID
                    elem[1],        # Código de barra
                    elem[2],        # Producto (nombre)
                    elem[3],        # Proveedor
                    precio_ars,     # Precio
                    costo_ars,      # Costo
                    elem[6]         # Stock
                )
            )

    def actualizar_inventario(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        
        self.mostrar()

        messagebox.showinfo("Actualizacion", "El inventario ha sido actualizado correctamente.")

    def registrar(self):
        # Limpiar Treeview
        for i in self.tre.get_children():
            self.tre.delete(i)

        codigo_barra = self.codigo_barra.get()
        nombre = self.nombre.get()
        prov = self.proveedor.get()
        precio = self.precio.get()
        costo = self.costo.get()
        stock = self.stock.get()

        # Validación
        if self.validacion(nombre, prov, precio, costo, stock):
            try:
                consulta = """INSERT INTO inventario 
                              (codigo_barra, nombre, proveedor, precio, costo, stock) 
                              VALUES (?, ?, ?, ?, ?, ?)"""
                parametros = (codigo_barra, nombre, prov, precio, costo, stock)
                self.eje_consulta(consulta, parametros)

                # Limpiar entradas
                self.codigo_barra.delete(0, END)
                self.nombre.delete(0, END)
                self.proveedor.delete(0, END)
                self.precio.delete(0, END)
                self.costo.delete(0, END)
                self.stock.delete(0, END)

                # Mostrar actualizado
                self.mostrar()
            except Exception as e:
                messagebox.showwarning(title="Error", message=f"Error al registrar el producto: {e}")
        else:
            messagebox.showwarning(title="Error", message=f"Rellene los campos correctamente")
            self.mostrar()

    def generar_datos_prueba(self):
        try:
            # Preguntar cuántos productos generar
            cantidad = simpledialog.askinteger(
                "Cantidad",
                "¿Cuántos registros de prueba desea generar?",
                minvalue=1,
                maxvalue=10000000
            )

            if cantidad is None:  # si el usuario cancela
                return

            for _ in range(cantidad):
                # Generar datos falsos
                codigo_barra = faker.unique.ean13()  # genera un código de barras válido (13 dígitos)
                nombre = faker.word().capitalize()
                proveedor = faker.company()
                precio = round(random.uniform(100, 2000), 2)
                costo = round(precio * random.uniform(0.5, 0.9), 2)
                stock = random.randint(1, 100)

                consulta = """
                    INSERT INTO inventario 
                    (codigo_barra, nombre, proveedor, precio, costo, stock) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                parametros = (codigo_barra, nombre, proveedor, precio, costo, stock)
                self.eje_consulta(consulta, parametros)

            self.actualizar_inventario()
            messagebox.showinfo("Prueba", f"Se generaron {cantidad} productos de prueba con éxito ✅")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron generar datos de prueba: {e}")

    def eliminar_todos_los_datos(self):
        try:
            confirmacion = messagebox.askyesno(
                "Confirmar",
                "¿Seguro que querés eliminar TODOS los productos del inventario?"
            )
    
            if confirmacion:
                self.eje_consulta("DELETE FROM inventario")
                # resetear sqlite_sequence para que el próximo id empiece desde 1
                conn = sqlite3.connect(self.db_name)
                cur = conn.cursor()
                try:
                    cur.execute("DELETE FROM sqlite_sequence WHERE name = ?", ("inventario",))
                    conn.commit()
                finally:
                    conn.close()

                self.actualizar_inventario()
                messagebox.showinfo("Eliminar", "Se eliminaron todos los productos ✅")
    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron eliminar datos: {e}")

    def eliminar_registros(self):
        seleccion = self.tre.selection()

        if not seleccion:
            messagebox.showwarning("Eliminar", "No hay registros seleccionados.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar {len(seleccion)} registro(s) seleccionado(s)?"
        )
        if not confirmar:
            return

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for item in seleccion:
            valores = self.tre.item(item, "values")
            id_registro = valores[0]  # La primera columna es ID
            cursor.execute("DELETE FROM inventario WHERE id = ?", (id_registro,))

        conn.commit()
        conn.close()

        # Quitar del Treeview
        for item in seleccion:
            self.tre.delete(item)

        # Preguntar si reenumerar IDs para eliminar huecos (ATENCIÓN: esto cambia ids y rompe FK si existen)
        reenumerar = messagebox.askyesno(
            "Reenumerar IDs",
            "¿Desea reenumerar los IDs para eliminar los huecos dejados por los registros borrados?\n"
            "Esto reasignará nuevos IDs consecutivos (1,2,3...) y puede romper referencias si otras tablas usan estos IDs."
        )
        if reenumerar:
            try:
                self.resequence_inventario()
                self.actualizar_inventario()
                messagebox.showinfo("Reenumerar", "IDs reenumerados correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reenumerar: {e}")

        messagebox.showinfo("Éxito", "Registro(s) eliminado(s).")

    def resequence_inventario(self):
        """
        Reconstruye la tabla inventario para reasignar ids consecutivos.
        ADVERTENCIA: si otras tablas referencian inventario.id, esas referencias quedarán inválidas.
        """
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        try:
            cur.execute("PRAGMA foreign_keys = OFF;")
            conn.commit()

            # Crear tabla temporal con misma estructura
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventario_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo_barra TEXT UNIQUE,
                    nombre TEXT NOT NULL,
                    proveedor TEXT NOT NULL,
                    precio REAL NOT NULL,
                    costo REAL NOT NULL,
                    stock INTEGER NOT NULL
                );
            """)
            # Copiar datos sin el id para que se reasignen secuencialmente
            cur.execute("""
                INSERT INTO inventario_new (codigo_barra, nombre, proveedor, precio, costo, stock)
                SELECT codigo_barra, nombre, proveedor, precio, costo, stock
                FROM inventario
                ORDER BY id;
            """)
            # Borrar tabla antigua y renombrar la nueva
            cur.execute("DROP TABLE inventario;")
            cur.execute("ALTER TABLE inventario_new RENAME TO inventario;")

            # Reiniciar sqlite_sequence por si acaso
            cur.execute("DELETE FROM sqlite_sequence WHERE name = ?", ("inventario",))
            conn.commit()
        finally:
            cur.execute("PRAGMA foreign_keys = ON;")
            conn.commit()
            conn.close()

    def editar_producto(self):
        seleccion = self.tre.selection()
        if not seleccion:
            messagebox.showwarning("Editar producto", "Seleccione un producto para editar.")
            return
        
        item_id = self.tre.item(seleccion)["text"]  # <-- usamos el ID real aquí
        item_values = self.tre.item(seleccion)["values"]

        
        ventana_editar = Toplevel(self)
        ventana_editar.title("Editar producto")
        ventana_editar.geometry("400x450")
        ventana_editar.config(bg="#c6d9e3")

        # --- Código de barra ---
        lblcodigo = Label(ventana_editar, text="Código de Barra:", font="sans 14 bold", bg="#c6d9e3")
        lblcodigo.grid(row=1, column=0, padx=10, pady=10)
        entry_codigo = Entry(ventana_editar, font="sans 14 bold")
        entry_codigo.grid(row=1, column=1, padx=10, pady=10)
        entry_codigo.insert(0, item_values[1])  # ← Código de barra en la primera columna del Treeview

        # --- Nombre ---
        lblnombre = Label(ventana_editar, text="Nombre:", font="sans 14 bold", bg="#c6d9e3")
        lblnombre.grid(row=2, column=0, padx=10, pady=10)
        entry_nombre = Entry(ventana_editar, font="sans 14 bold")
        entry_nombre.grid(row=2, column=1, padx=10, pady=10)
        entry_nombre.insert(0, item_values[2])

        # --- Proveedor ---
        lblproveedor = Label(ventana_editar, text="Proveedor:", font="sans 14 bold", bg="#c6d9e3")
        lblproveedor.grid(row=3, column=0, padx=10, pady=10)
        entry_proveedor = Entry(ventana_editar, font="sans 14 bold")
        entry_proveedor.grid(row=3, column=1, padx=10, pady=10)
        entry_proveedor.insert(0, item_values[3])

        # --- Precio ---
        lblprecio = Label(ventana_editar, text="Precio:", font="sans 14 bold", bg="#c6d9e3")
        lblprecio.grid(row=4, column=0, padx=10, pady=10)
        entry_precio = Entry(ventana_editar, font="sans 14 bold")
        entry_precio.grid(row=4, column=1, padx=10, pady=10)
        entry_precio.insert(0, item_values[4].split()[0].replace(",", ""))

        # --- Costo ---
        lblcosto = Label(ventana_editar, text="Costo:", font="sans 14 bold", bg="#c6d9e3")
        lblcosto.grid(row=5, column=0, padx=10, pady=10)
        entry_costo = Entry(ventana_editar, font="sans 14 bold")
        entry_costo.grid(row=5, column=1, padx=10, pady=10)
        entry_costo.insert(0, item_values[5].split()[0].replace(",", ""))

        # --- Stock ---
        lblstock = Label(ventana_editar, text="Stock:", font="sans 14 bold", bg="#c6d9e3")
        lblstock.grid(row=6, column=0, padx=10, pady=10)
        entry_stock = Entry(ventana_editar, font="sans 14 bold")
        entry_stock.grid(row=6, column=1, padx=10, pady=10)
        entry_stock.insert(0, item_values[6])

        def guardar_cambios():
            codigo_barra = entry_codigo.get()   # <- asegúrate de tener el campo en tu formulario
            nombre = entry_nombre.get()
            proveedor = entry_proveedor.get()
            precio = entry_precio.get()
            costo = entry_costo.get()
            stock = entry_stock.get()
        
            if not (codigo_barra and nombre and proveedor and precio and costo and stock):
                messagebox.showwarning("Guardar cambios", "Rellene todos los campos.")
                return
        
            try:
                precio = float(precio.replace(",", ""))
                costo = float(costo.replace(",", "")) 
            except ValueError:
                messagebox.showwarning("Guardar cambios", "Ingrese valores numéricos válidos para precio y costo")
                return
        
            consulta = """
                UPDATE inventario 
                SET codigo_barra=?, nombre=?, proveedor=?, precio=?, costo=?, stock=? 
                WHERE id=?
            """
            parametros = (codigo_barra, nombre, proveedor, precio, costo, stock, item_id)
            self.eje_consulta(consulta, parametros)
            self.actualizar_inventario()
            ventana_editar.destroy()
        
        btn_guardar = Button(
            ventana_editar,
            text="Guardar cambios",
            font="sans 14 bold",
            command=guardar_cambios
        )
        btn_guardar.place(x=80, y=380, width=240, height=40)
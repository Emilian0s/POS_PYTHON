from tkinter import *
import sqlite3 
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from reportlab.lib.styles import getSampleStyleSheet
import os
import datetime

class Ventas(tk.Frame):
    db_name = "pos_carniceria.db"

    def __init__(self, parent):
        super().__init__(parent)
        self.numero_factura_actual = self.obtener_numero_factura_actual()
        self.widgets()
        self.mostrar_numero_factura()

    def widgets(self):

        frame1 = tk.Frame(self, bg="#d2dad9", highlightbackground="gray", highlightthickness=1)
        frame1.pack()
        frame1.place(x=0, y=0, width=1100, height=70)
    
        titulo = tk.Label(self, text="VENTAS", bg="#dddddd", font="sans 30 bold", anchor="center")
        titulo.pack()
        titulo.place(x=5, y=0, width=1090, height=65)

        frame2 = tk.Frame(self, bg="#b5c7d1")
        frame2.pack()
        frame2.place(x=0, y=100, width=1100, height=550)

        lblframe =  LabelFrame(frame2, text="Informacion de venta", bg="#c6d9e3", font="sans 16 bold")
        lblframe.place(x=10, y=0, width=1060, height=500)

        label_numero_factura = tk.Label(lblframe, text="Numero\n de factura", bg="#c6d9e3", font="sans 12 bold")
        label_numero_factura.place(x=5, y=5)
        self.numero_factura = tk.StringVar()

        self.entry_numero_factura= ttk.Entry(lblframe, textvariable=self.numero_factura, state="readonly", font="sans 16 bold")
        self.entry_numero_factura.place(x=100,y=20, width= 60)

        # === Campo de código de Barra ===
        tk.Label(lblframe, text="Código de barra:", bg="#c6d9e3", font="sans 12 bold").place(x=270, y=-5)
        self.entry_codigo_barra = ttk.Entry(lblframe, font="sans 12 bold")
        self.entry_codigo_barra.place(x=265, y=20, width=180)
        self.entry_codigo_barra.bind("<Return>", self.buscar_por_codigo)  # enter para buscar
        
        # === Campo de búsqueda con autocompletado ===
        tk.Label(lblframe, text="Producto:", bg="#c6d9e3", font="sans 12 bold").place(x=470, y=-5)
        
        self.entry_busqueda = tk.Entry(lblframe, font="sans 12 bold", width=19)
        self.entry_busqueda.place(x=465, y=20)
        self.entry_busqueda.bind("<KeyRelease>", self.autocompletar)

        # Campo de búsqueda
        self.entry_busqueda = tk.Entry(lblframe, font="sans 12 bold", width=19)
        self.entry_busqueda.grid(row=0, column=0, padx=465, pady=20, sticky="w")
        self.entry_busqueda.bind("<KeyRelease>", self.autocompletar)

        # Listbox de sugerencias (oculta al inicio)
        self.listbox_sugerencias = tk.Listbox(lblframe,  width=40, height=5)
        self.listbox_sugerencias.grid(row=1, column=0, padx=465, pady=0, sticky="w")
        self.listbox_sugerencias.place_forget() # <-- oculta al inicio


        # === Precio y cantidad ===
        label_valor = tk.Label(lblframe, text="Precio: ", bg="#c6d9e3", font="sans 12 bold")
        label_valor.place(x=670, y=-5)
        self.entry_valor = ttk.Entry(lblframe, font="sans 12 bold", state="readonly")
        self.entry_valor.place (x=665, y=20, width=180)
        
        label_cantidad = tk.Label(lblframe, text="Cantidad: ", bg="#c6d9e3", font="sans 12 bold")
        label_cantidad.place(x=870, y=-5)
        self.entry_cantidad = ttk.Entry(lblframe, font="sans 12 bold")
        self.entry_cantidad.place(x=865, y=20)
        
        treeFrame= tk.Frame(frame2, bg="#c6d9e3")
        treeFrame.place(x=150, y=175, width=800, height=200)

        scroll_y = ttk.Scrollbar(treeFrame, orient=VERTICAL)
        scroll_y.pack(side=RIGHT, fill=Y)

        scroll_x = ttk.Scrollbar(treeFrame, orient=HORIZONTAL)
        scroll_x.pack(side=BOTTOM, fill=X)

        self.tree = ttk.Treeview(treeFrame, columns=("Productos", "Precio", "Cantidad", "Subtotal"), show="headings", height=10, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.heading("#1", text="Productos")
        self.tree.heading("#2", text="Precio")
        self.tree.heading("#3", text="Cantidad")
        self.tree.heading("#4", text="Subtotal")

        self.tree.column("Productos", anchor="center")
        self.tree.column("Precio", anchor="center")
        self.tree.column("Cantidad", anchor="center")
        self.tree.column("Subtotal", anchor="center")

        self.tree.pack(expand=True, fill=BOTH )

        lblframe1 = LabelFrame(frame2, text="Opciones", bg="#c6d9e3", font="sans 12 bold")
        lblframe1.place(x=10, y=445, width=1080, height=100)

        boton_agregar = tk.Button(lblframe1, text="Agregar Articulo", bg="#dddddd", font="sans 12 bold", command= self.registrar)
        boton_agregar.place(x=50, y=10, width=240, height=50)

        boton_pagar = tk.Button(lblframe1, text="Pagar", bg="#dddddd", font="sans 12 bold", command= self.abrir_ventana_pagar)
        boton_pagar.place(x=400, y=10, width=240, height=50)

        boton_ver_facturas = tk.Button(lblframe1, text="Ver Facturas", bg="#dddddd", font="sans 12 bold", command= self.abrir_ventana_factura)
        boton_ver_facturas.place(x=750, y=10, width=240, height=50)    
        
        self.label_suma_total = tk.Label(frame2, text="Total a pagar:  $0 ARS", bg="#c6d9e3", font="sans 25 bold")
        self.label_suma_total.place(x=360, y=405)
    
    def buscar_por_codigo(self, event=None):
        codigo = self.entry_codigo_barra.get().strip()
        if not codigo:
            return

        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute("SELECT codigo_barra, nombre, precio, stock FROM inventario WHERE codigo_barra = ?", (codigo,))
        producto = cursor.fetchone()
        conexion.close()

        if producto:
            self.rellenar_campos(producto)
        else:
            messagebox.showwarning("No encontrado", f"No existe un producto con código {codigo}")

    def autocompletar(self, event):
        texto = self.entry_busqueda.get().lower()
        self.listbox_sugerencias.delete(0, tk.END)
    
        if texto == "":
            self.listbox_sugerencias.grid_remove()
            return
    
        # Ejemplo con productos fijos (luego lo adaptamos a tu BD)
        productos = [
            "Carne vacuna",
            "Carne de cerdo",
            "Pollo entero",
            "Pechuga de pollo",
            "Chorizo",
            "Morcilla",
            "Queso cremoso",
            "Queso rallado",
        ]
    
        sugerencias = [p for p in productos if texto in p.lower()]
    
        if sugerencias:
            for s in sugerencias:
                self.listbox_sugerencias.insert(tk.END, s)
            self.listbox_sugerencias.grid()
        else:
            self.listbox_sugerencias.grid_remove()
    
    def seleccionar_flecha_abajo(self, event):
        if self.listbox_sugerencias.size() == 0:
            return
        current = self.listbox_sugerencias.curselection()
        if not current:
            next_index = 0
        else:
            next_index = (current[0] + 1) % self.listbox_sugerencias.size()
        self.listbox_sugerencias.selection_clear(0, tk.END)
        self.listbox_sugerencias.selection_set(next_index)
        self.listbox_sugerencias.activate(next_index)

    def seleccionar_flecha_arriba(self, event):
        if self.listbox_sugerencias.size() == 0:
            return
        current = self.listbox_sugerencias.curselection()
        if not current:
            next_index = self.listbox_sugerencias.size() - 1
        else:
            next_index = (current[0] - 1) % self.listbox_sugerencias.size()
        self.listbox_sugerencias.selection_clear(0, tk.END)
        self.listbox_sugerencias.selection_set(next_index)
        self.listbox_sugerencias.activate(next_index)

    def seleccionar_sugerencia(self, event=None):
        seleccion = self.listbox_sugerencias.curselection()
        if not seleccion:
            return

        valor = self.listbox_sugerencias.get(seleccion[0])
        codigo = valor.split(" | ")[0]  # sacar código de barras

        conexion = sqlite3.connect(self.db_name)
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT codigo_barra, nombre, precio, stock FROM inventario WHERE codigo_barra = ?",
            (codigo,)
        )
        producto = cursor.fetchone()
        conexion.close()

        if producto:
            self.rellenar_campos(producto)

        self.listbox_sugerencias.place_forget()

    def rellenar_campos(self, producto):
        codigo, nombre, precio, stock = producto
    
        # Rellenar el entry de búsqueda con el nombre
        self.entry_busqueda.delete(0, tk.END)
        self.entry_busqueda.insert(0, nombre)
    
        # Guardar el código de barras en su campo
        self.entry_codigo_barra.delete(0, tk.END)
        self.entry_codigo_barra.insert(0, codigo)
    
        # Rellenar el precio
        self.entry_valor.config(state="normal")
        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, precio)
        self.entry_valor.config(state="readonly")
    
        # Opcional → podrías mostrar un campo de stock
        if hasattr(self, "entry_stock"):
            self.entry_stock.config(state="normal")
            self.entry_stock.delete(0, tk.END)
            self.entry_stock.insert(0, stock)
            self.entry_stock.config(state="readonly")

        # Para debug
        print(f"DEBUG: Stock disponible de {nombre}: {stock}")
    
    def actualizar_precio(self, event=None):
        nombre_producto = self.entry_nombre.get()
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT precio FROM inventario WHERE nombre = ?", (nombre_producto,))
            precio = c.fetchone()

            self.entry_valor.config(state="normal")
            self.entry_valor.delete(0, tk.END)

            if precio:
                self.entry_valor.insert(0, precio[0])
            else:
                self.entry_valor.insert(0, "Precio no disponible")

            self.entry_valor.config(state="readonly")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener el precio: {e}")
        finally:
            if conn:
                conn.close()
            
    def actualizar_total(self):
        total= 0.0
        for child in self.tree.get_children():
            subtotal = float(self.tree.item(child, "values") [3])
            total += subtotal
        self.label_suma_total.config(text=f"Total a pagar: ${total:.2f} ARS" )

    def registrar(self):
        producto = self.entry_nombre.get()
        precio = self.entry_valor.get()
        cantidad = self.entry_cantidad.get()

        if producto and precio and cantidad:
            try:
                cantidad = int(cantidad)
                if not self.verificar_stock(producto, cantidad):
                    messagebox.showerror("Error, Stock insuficiente")
                precio = float(precio)
                subtotal = cantidad * precio

                self.tree.insert("", "end", values = (producto, f"{precio:.2f}", cantidad, f"{subtotal:.2f}") )
                self.entry_nombre.set("")
                self.entry_valor.config(state="normal")
                self.entry_valor.delete(0, tk.END)
                self.entry_valor.config(state="readonly")
                self.entry_valor.delete(0, tk.END)

                self.actualizar_total()
            except ValueError:
                messagebox.showerror("Error,", " Cantidad o precio no validos")
        else:
            messagebox.showerror("Error", " Debe completar todos los campos")

    def verificar_stock(self, nombre_producto, cantidad):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT stock FROM inventario WHERE nombre = ?", (nombre_producto,))
            stock = c.fetchone()
            if stock and stock[0] >= cantidad:
                return True
            else:
                return False

        except sqlite3.Error as e:
            messagebox.showerror(f"Error al verificar al stock: {e}")
            return False
        finally:
            conn.close()
        
    def obtener_total(self):
        total = 0.0
        for child in self.tree.get_children():
            subtotal = float(self.tree.item(child, "values")[3])
            total += subtotal 
        return total
    
    def abrir_ventana_pagar(self):
        if not self.tree.get_children():
            messagebox.showerror("Error", "No hay artículos para pagar")
            return 
    
        ventana_pago = Toplevel(self)
        ventana_pago.title("Realizar pago")
        ventana_pago.geometry("400x400")
        ventana_pago.config(bg="#c6d9e3")
        ventana_pago.resizable(False, False)
    
        label_total = tk.Label(
            ventana_pago, bg="#c6d9e3",
            text=f"Total a pagar: ${self.obtener_total():.2f} ARS",
            font="sans 18 bold"
        )
        label_total.place(x=70, y=20)
    
        label_cantidad_pagada = tk.Label(
            ventana_pago, bg="#c6d9e3",
            text="Cantidad pagada: ", font="sans 14 bold"
        )
        label_cantidad_pagada.place(x=100, y=90)
    
        entry_cantidad_pagada = ttk.Entry(ventana_pago, font="sans 14 bold")
        entry_cantidad_pagada.place(x=100, y=130)
    
        label_cambio = tk.Label(ventana_pago, bg="#c6d9e3", text="", font="sans 14 bold")
        label_cambio.place(x=100, y=190)
    
        def calcular_cambio():
            try:
                cantidad_pagada = float(entry_cantidad_pagada.get())
                total = self.obtener_total()
                cambio = cantidad_pagada - total
                if cambio < 0:
                    messagebox.showerror("Error", "La cantidad pagada es insuficiente")
                    return 
                label_cambio.config(text=f"Vuelto: ${cambio:.2f} ARS") 
            except ValueError:
                messagebox.showerror("Error", "Cantidad pagada no válida")
    
        # Botones fuera de calcular_cambio para que aparezcan siempre
        boton_calcular = tk.Button(
            ventana_pago, text="Calcular pago", bg="white",
            font="sans 12 bold", command=calcular_cambio
        )
        boton_calcular.place(x=100, y=240, width=240, height=40)
    
        boton_pagar = tk.Button(
            ventana_pago, text="Pagar", bg="green",
            font="sans 12 bold",
            command=lambda: self.pagar(ventana_pago, entry_cantidad_pagada, label_cambio)
        )
        boton_pagar.place(x=100, y=300, width=240, height=40)    
    
    def pagar(self, ventana_pago, entry_cantidad_pagada, label_cambio):
        try:
            cantidad_pagada = float(entry_cantidad_pagada.get())
            total = self.obtener_total()
            cambio = cantidad_pagada - total
            if cambio < 0:
                messagebox.showerror("Error", "La cantidad pagada es insuficiente")
                return
            label_cambio.config(text=f"Cambio: ${cambio:.2f}")
    
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            try:
                productos = []
                for child in self.tree.get_children():
                    item = self.tree.item(child, "values")
                    producto = item[0]
                    precio = item[1]
                    cantidad_vendida = int(item[2])
                    subtotal = float(item[3])
                    productos.append([producto, precio, cantidad_vendida, subtotal])
                    
                    c.execute(
                        "INSERT INTO ventas (factura, nombre_articulo, valor_articulo, cantidad, subtotal) VALUES (?,?,?,?,?)",
                        (self.numero_factura_actual, producto, float(precio), cantidad_vendida, subtotal)
                    )

                    
                    c.execute(
                        "UPDATE inventario SET stock = stock - ? WHERE nombre = ?",
                        (cantidad_vendida, producto)
                    )
                
                conn.commit()
                messagebox.showinfo("Éxito", "Venta registrada exitosamente")
    
                self.numero_factura_actual += 1
                self.mostrar_numero_factura()
    
                for child in self.tree.get_children():
                    self.tree.delete(child)
                self.label_suma_total.config(text="Total a pagar: $ARS" )
    
                ventana_pago.destroy()
    
                fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.generar_factura_pdf(productos, total, self.numero_factura_actual - 1, fecha)
    
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Error", f"Error al registrar la venta: {e}")
            finally:
                conn.close()
        except ValueError:
            messagebox.showerror("Error", "Cantidad pagada no válida")
       
    def generar_factura_pdf(self, productos, total, factura_numero, fecha):
        archivo_pdf= f"facturas/factura_{factura_numero}.pdf"
        c = canvas.Canvas(archivo_pdf, pagesize=letter)
        width, height = letter

        styles = getSampleStyleSheet()
        estilo_titulo = styles["Title"]
        estilo_normal = styles["Normal"]

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height-50, f"Factura numero:{factura_numero}")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height-70, f"Fecha:{fecha}")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height-250, f"Total pagar : ${total:.2f}ARS")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height-400, f"Gracias por su compra, vuelva pronto🤗")
        
        c.save()

        messagebox.showinfo("Factura generada" f"La factura #{factura_numero} se creó exitosamente")
        
        os.startfile(os.path.abspath(archivo_pdf))


        data = [["Producto", "Precio", "Cantidad", "Subtotal"]] + productos
        table = Table(data)
        table.wrapOn(c, width, height)
        table.drawOn(c, 100, height - 200)


    def obtener_numero_factura_actual(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("SELECT MAX(factura) FROM ventas")
            max_factura = c.fetchone()[0]
            if max_factura:
                return max_factura + 1
            else: 
                return 1
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Eror al obtener el número de factura: {e}")
            return 1
        finally:
            conn.close()

    def mostrar_numero_factura(self):
        self.numero_factura.set(self.numero_factura_actual)

    def abrir_ventana_factura(self):
        ventana_facturas = Toplevel(self)
        ventana_facturas.title("Factura")
        ventana_facturas.geometry("800x500")
        ventana_facturas.config(bg="#c6d9e3")
        ventana_facturas.resizable(False, False)
        
        facturas = Label(ventana_facturas, bg="#c6d9e3", text="facturas registradas", font="sans 36 bold")
        facturas.place(x=150, y=15)

        treFrame = tk.Frame(ventana_facturas, bg="#c6d9e3")
        treFrame.place(x=10, y=100, width=780, height=380)

        treeFrame = tk.Frame(ventana_facturas, bg="#c6d9e3")
        treeFrame.place(x=20, y=120, width=760, height=200)

        scroll_y = ttk.Scrollbar(treeFrame, orient=VERTICAL)
        scroll_y.pack(side=RIGHT, fill=Y)

        scroll_x = ttk.Scrollbar(treeFrame, orient=HORIZONTAL)
        scroll_x.pack(side=BOTTOM, fill=X)

        tree_facturas = ttk.Treeview(treeFrame, columns=("ID", "Factura", "Producto", "Precio",  "Cantidad", "Subtotal"), show="headings", height=10, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=tree_facturas.yview)
        scroll_x.config(command=tree_facturas.xview)

        tree_facturas.heading("#1", text="ID")
        tree_facturas.heading("#2", text="Factura")
        tree_facturas.heading("#3", text="Producto")
        tree_facturas.heading("#4", text="Precio")
        tree_facturas.heading("#5", text="Cantidad")
        tree_facturas.heading("#6", text="Subtotal")
        
        tree_facturas.column("ID", width=70, anchor="center")
        tree_facturas.column("Factura", width=100, anchor="center")
        tree_facturas.column("Producto", width=200, anchor="center")
        tree_facturas.column("Precio", width=130, anchor="center")
        tree_facturas.column("Cantidad", width=130, anchor="center")
        tree_facturas.column("Subtotal", width=130 , anchor="center")
        
        tree_facturas.pack(expand=True, fill=BOTH)
        
        self.cargar_facturas(tree_facturas)

    def cargar_facturas(self,tree):
        try:
            conn =sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT * FROM ventas")
            facturas = c.fetchall()
            for factura in facturas:
                tree.insert("", "end", values=factura)
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror(f"Error al cargar las facturas: {e}")

'''def generar_ticket(productos, total, pago, cambio, descuento=0, forma_pago="Efectivo"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = "ticket.txt"

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("🧾 TICKET DE VENTA\n")
        f.write(f"Fecha: {fecha}\n")
        f.write("-" * 30 + "\n")

        for nombre, cantidad, unidad, _, subtotal in productos:
            f.write(f"{nombre} x{cantidad}{unidad} - ${subtotal:.2f}\n")

        f.write("-" * 30 + "\n")
        f.write(f"TOTAL: ${total + descuento:.2f}\n")
        if descuento > 0:
            f.write(f"DESCUENTO: -${descuento:.2f}\n")
        f.write(f"FINAL: ${total:.2f}\n")
        f.write(f"Pago: ${pago:.2f}\n")
        f.write(f"Vuelto: ${cambio:.2f}\n")
        f.write(f"Pago: ${pago:.2f} ({forma_pago})\n")
        f.write("=" * 30 + "\n")
        f.write("¡Gracias por su compra!\n")

    try:
        os.startfile(nombre_archivo, "print")
    except:
        messagebox.showinfo("Impresión", "Ticket generado, pero no se pudo imprimir automáticamente.")
'''
'''def mostrar_sugerencias(self, resultados):
        # Limpiar listbox primero
        self.listbox_sugerencias.delete(0, tk.END)

        # resultados es una lista de tuplas -> solo mostramos el nombre (índice 1)
        for producto in resultados:
            self.listbox_sugerencias.insert(tk.END, producto[1])

        # Guardamos los resultados para cuando el usuario seleccione
        self.resultados_actuales = resultados

        # Mostrar si hay resultados
        if resultados:
            self.listbox_sugerencias.place(
                x=self.entry_busqueda.winfo_x(),
                y=self.entry_busqueda.winfo_y() + self.entry_busqueda.winfo_height(),
                width=self.entry_busqueda.winfo_width()
            )
        else:
            self.listbox_sugerencias.place_forget()

    def cargar_productos(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT nombre FROM inventario")
            productos = c.fetchall()

            # Si tenés un combobox de productos
            self.entry_nombre["values"] = [producto[0] for producto in productos]

            if not productos:
                print("⚠ No se encontraron productos en la base de datos.")
        except sqlite3.Error as e:
            print("❌ Error al cargar productos desde la base de datos:", e)
        finally:
            if conn:
                conn.close()
'''
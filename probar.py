import tkinter as tk

class BuscadorProductos:
    def __init__(self, root):
        self.root = root

        # Campo de búsqueda
        self.entry_busqueda = tk.Entry(root, width=40)
        self.entry_busqueda.pack(pady=5)
        self.entry_busqueda.bind("<KeyRelease>", self.autocompletar)

        # Listbox de sugerencias (oculta al inicio)
        self.listbox_sugerencias = tk.Listbox(root, width=40, height=5)
        self.listbox_sugerencias.pack(pady=5)
        self.listbox_sugerencias.pack_forget()

        # Productos de prueba
        self.productos = [
            "Carne vacuna",
            "Carne de cerdo",
            "Pollo entero",
            "Pechuga de pollo",
            "Chorizo",
            "Morcilla",
            "Queso cremoso",
            "Queso rallado",
        ]

    def autocompletar(self, event):
        texto = self.entry_busqueda.get().lower()
        self.listbox_sugerencias.delete(0, tk.END)

        if texto == "":
            self.listbox_sugerencias.pack_forget()
            return

        sugerencias = [p for p in self.productos if texto in p.lower()]

        if sugerencias:
            for s in sugerencias:
                self.listbox_sugerencias.insert(tk.END, s)
            self.listbox_sugerencias.pack(pady=5)  # <- aquí se asegura de mostrarse
        else:
            self.listbox_sugerencias.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba de autocompletar")
    app = BuscadorProductos(root)
    root.mainloop()

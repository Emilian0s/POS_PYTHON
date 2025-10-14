# Sistema POS🛒 para Carnicería 🥩

Este proyecto es un sistema de punto de venta (POS) desarrollado en Python y Tkinter, diseñado especialmente para carnicerías. Permite realizar ventas por unidad o peso, imprimir tickets y administrar el stock.

## Cómo empezar🔎:

1. Cloná el proyecto.

2. Instalá los requisitos del proyecto (si tenés un archivo `requirements.txt`):

```bash
pip install -r requirements.txt
```

3. Ejecutá el sistema:
```
python index.py
```

## Changelog: 
- [ ] Uso multiusuario:
Se tiene pensado poder ampliar su capacidad para poder usarlo en más de un solo dispositivo, pudiendo contar con un registro de usuario.

- [ ] Mejor Interfaz: 
La interfaz se hará mucho más intuitiva y fácil de usar, contará con logotipos más amigables y tendrá un diseño responsive, también se podrá hacer uso de temas personalizados. Se añadirán atajos por teclado, control y asistencia por voz.

## Historias de usuario: 
- Como cajero, quiero registrar los productos con nombre, precio, id, nro de codigo de barra 
- Como cajero, quiero imprimir una boleta o facturas de manera automática una vez realizada la venta
- Como administrador, quiero ver qué hay en stock
- Como administrador, quiero bloquear/suspender cajas registradoras

## Ultima modificacion:

- arreglé un problema con el entorno virtual- aparentemente mi version de python no traía una dependecia instlada

- agregué el campo código de barra en base de datos y tabla inventarios 

- trato de solucionar un problema con el buscador de ventas.py

- arreglar entry_nombre
# ST Ventas

Panel multipagina en Streamlit para explorar ventas inmobiliarias y caracteristicas de clientes.

## Ejecutar

```bash
uv sync
uv run streamlit run src/st_ventas/app.py
```

La aplicacion carga por defecto `data/ventas_prediccion.csv`. Se puede sustituir desde el menu lateral por otro CSV con el mismo esquema. Las operaciones duplicadas se eliminan por `idoperacion` y los clientes se cuentan por `RutCliente`.

Los montos se presentan en la escala de `PRECIO_VENTA`; el archivo de origen no especifica una moneda.

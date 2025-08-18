# Odoo 18 stack (creación manual de base de datos)

1. Descomprime el paquete.
2. Ejecuta `docker-compose up --build`.
3. Abre http://localhost:8069/ ; aparecerá el gestor de bases.
4. Crea la base **con el correo y contraseña que quieras**.
5. Activa el modo desarrollador y carga el módulo `invoice_custom`.

El contenedor Postgres se crea automáticamente y persiste datos en los volúmenes declarados.

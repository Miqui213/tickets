# Microservicio de Tickets

Microservicio REST desarrollado con FastAPI encargado de la gestión de vuelos y destinos dentro de la plataforma de viajes.

Este servicio actúa como la fuente principal de información de vuelos y es consumido por otros microservicios como reservas y wishlist.

## Tecnologías

* Python
* FastAPI
* PostgreSQL
* Psycopg2

## Descripción

El microservicio de tickets permite gestionar información relacionada con vuelos y destinos, incluyendo operaciones de creación, consulta, actualización y eliminación.

Además, proporciona funcionalidades avanzadas como filtrado dinámico, paginación y control de disponibilidad de asientos.

## Modelo de datos

### Entidad Vuelo

* numero_vuelo
* id_destino
* aerolinea
* precio_base
* fecha_salida
* capacidad_total
* asientos_disponibles
* modelo_avion

### Entidad Destino

* nombre_destino
* pais
* codigo_iata

## Endpoints

### Vuelos

* GET /vuelos → Listar vuelos con filtros y paginación
* GET /vuelos/{id} → Obtener vuelo por ID
* GET /vuelos/all → Obtener todos los vuelos sin paginación
* POST /vuelos → Crear vuelo
* PUT /vuelos/{id} → Actualizar vuelo
* DELETE /vuelos/{id} → Eliminar vuelo

### Reserva de asientos

* PATCH /vuelos/{id}/reservar

Permite descontar un asiento disponible. Este endpoint es utilizado por el microservicio de reservas.

### Destinos

* GET /destinos → Listar destinos
* GET /destinos/{id} → Obtener destino por ID
* GET /destinos/all → Obtener todos los destinos
* POST /destinos → Crear destino
* PUT /destinos/{id} → Actualizar destino
* DELETE /destinos/{id} → Eliminar destino

### Health Check

* GET /health

Verifica la disponibilidad del servicio y la conexión a la base de datos.

## Variables de entorno

```env id="tickets_env_clean"
DB_HOST=localhost
POSTGRES_DB=tickets_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=*****
POSTGRES_PORT=5432
```
## Ejecución del proyecto

### 1. Instalar dependencias

```bash id="tickets_install_clean"
pip install fastapi uvicorn psycopg2-binary
```

### 2. Ejecutar el servidor

```bash id="tickets_run_clean"
uvicorn main:app --reload
```
## Funcionalidades avanzadas

### Filtros en búsqueda de vuelos

El endpoint GET /vuelos permite aplicar filtros opcionales:

* destino
* aerolinea
* fecha
* precio mínimo
* precio máximo
* disponibilidad de asientos

### Paginación

Los resultados pueden ser paginados mediante parámetros:

* page
* size

## Integración con otros microservicios

Este microservicio es consumido por:

* Microservicio de reservas → validación de vuelos y actualización de asientos
* Microservicio de wishlist → obtención de información de vuelos

## Flujo de funcionamiento

1. El cliente consulta vuelos disponibles.
2. El servicio aplica filtros y retorna resultados paginados.
3. El microservicio de reservas consulta este servicio para validar disponibilidad.
4. Se descuenta un asiento cuando se confirma una reserva.

## Manejo de errores

El servicio maneja diferentes escenarios:

* Vuelo no encontrado (404)
* Sin asientos disponibles (400)
* Error en base de datos (500)

## Características

* Consultas SQL dinámicas
* Paginación configurable
* Validación de disponibilidad en tiempo real
* Manejo estructurado de respuestas
* Verificación de conexión a base de datos

## Limitaciones

* Dependencia directa de PostgreSQL
* No se implementa caché
* No incluye autenticación

## Justificación de diseño

Este microservicio centraliza la lógica relacionada con vuelos, evitando duplicación de datos y garantizando consistencia en el sistema.

El control de disponibilidad de asientos se mantiene en este servicio, asegurando que otros microservicios no manipulen directamente esta lógica.

## Rol dentro del sistema

Este microservicio es el responsable de gestionar la información de vuelos y destinos, actuando como la fuente única de verdad dentro de la arquitectura de microservicios.

## Notas

* Diseñado para integrarse en una arquitectura distribuida
* Preparado para escalar horizontalmente
* Puede extenderse para incluir caché o mecanismos de optimización

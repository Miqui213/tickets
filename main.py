from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="API de Tickets - CRUD Completo")

# Esquema para creación y actualización
class VueloSchema(BaseModel):
    numero_vuelo: str
    id_destino: int
    aerolinea: str
    precio_base: float
    fecha_salida: str
    capacidad_total: int
    asientos_disponibles: int
    modelo_avion: str

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        cursor_factory=RealDictCursor
    )

@app.post("/vuelos", status_code=201)
def crear_vuelo(vuelo: VueloSchema):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO vuelos (numero_vuelo, id_destino, aerolinea, precio_base, 
               fecha_salida, capacidad_total, asientos_disponibles, modelo_avion) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_vuelo""",
            (vuelo.numero_vuelo, vuelo.id_destino, vuelo.aerolinea, vuelo.precio_base,
             vuelo.fecha_salida, vuelo.capacidad_total, vuelo.asientos_disponibles, vuelo.modelo_avion)
        )
        nuevo_id = cur.fetchone()['id_vuelo']
        conn.commit()
        return {"id": nuevo_id, "mensaje": "Vuelo creado exitosamente"}
    finally:
        cur.close()
        conn.close()

@app.get("/vuelos")
def listar_vuelos(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    destino: Optional[str] = None,
    aerolinea: Optional[str] = None,
    fecha: Optional[str] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
    solo_disponibles: bool = True
):
    offset = (page - 1) * size
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        where_clauses = []
        params = []
        if solo_disponibles: where_clauses.append("v.asientos_disponibles > 0")
        if destino:
            where_clauses.append("d.nombre_destino ILIKE %s")
            params.append(f"%{destino}%")
        if aerolinea:
            where_clauses.append("v.aerolinea ILIKE %s")
            params.append(f"%{aerolinea}%")
        if fecha:
            where_clauses.append("v.fecha_salida::date = %s")
            params.append(fecha)
        if precio_min is not None:
            where_clauses.append("v.precio_base >= %s")
            params.append(precio_min)
        if precio_max is not None:
            where_clauses.append("v.precio_base <= %s")
            params.append(precio_max)

        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"SELECT v.*, d.nombre_destino FROM vuelos v JOIN destinos d ON v.id_destino = d.id_destino {where_str} ORDER BY v.precio_base ASC LIMIT %s OFFSET %s"
        cur.execute(query, params + [size, offset])
        vuelos = cur.fetchall()

        cur.execute(f"SELECT COUNT(*) FROM vuelos v JOIN destinos d ON v.id_destino = d.id_destino {where_str}", params)
        total = cur.fetchone()['count']

        return {"items": vuelos, "total": total, "page": page, "size": size}
    finally:
        cur.close()
        conn.close()

@app.get("/vuelos/{id_vuelo}")
def obtener_vuelo_por_id(id_vuelo: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT v.*, d.nombre_destino, d.pais 
            FROM vuelos v
            JOIN destinos d ON v.id_destino = d.id_destino
            WHERE v.id_vuelo = %s
        """, (id_vuelo,))
        vuelo = cur.fetchone()
        if not vuelo:
            raise HTTPException(status_code=404, detail="Vuelo no encontrado")
        return vuelo
    finally:
        cur.close()
        conn.close()

@app.put("/vuelos/{id_vuelo}")
def actualizar_vuelo(id_vuelo: int, vuelo: VueloSchema):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """UPDATE vuelos SET numero_vuelo=%s, id_destino=%s, aerolinea=%s, 
               precio_base=%s, fecha_salida=%s, capacidad_total=%s, 
               asientos_disponibles=%s, modelo_avion=%s WHERE id_vuelo=%s""",
            (vuelo.numero_vuelo, vuelo.id_destino, vuelo.aerolinea, vuelo.precio_base,
             vuelo.fecha_salida, vuelo.capacidad_total, vuelo.asientos_disponibles, 
             vuelo.modelo_avion, id_vuelo)
        )
        conn.commit()
        return {"mensaje": "Vuelo actualizado correctamente"}
    finally:
        cur.close()
        conn.close()

@app.delete("/vuelos/{id_vuelo}")
def eliminar_vuelo(id_vuelo: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM vuelos WHERE id_vuelo = %s", (id_vuelo,))
        conn.commit()
        return {"mensaje": "Vuelo eliminado"}
    finally:
        cur.close()
        conn.close()
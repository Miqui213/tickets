from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = FastAPI(title="Microservicio de Tickets (CRUD)")

DB_CONFIG = {
    "host": "db-tickets",
    "database": "travel_tickets",
    "user": "u_tickets",
    "password": "password123"
}

class Vuelo(BaseModel):
    numero_vuelo: str
    id_destino: int
    aerolinea: str
    precio_base: float
    fecha_salida: datetime
    capacidad_total: int
    asientos_disponibles: int
    modelo_avion: str

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.post("/vuelos", status_code=status.HTTP_201_CREATED)
def create_vuelo(vuelo: Vuelo):
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
        new_id = cur.fetchone()[0]
        conn.commit()
        return {"id_vuelo": new_id, "message": "Vuelo creado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/vuelos")
def get_vuelos(limit: int = 100):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM vuelos LIMIT %s", (limit,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

@app.put("/vuelos/{vuelo_id}")
def update_vuelo(vuelo_id: int, vuelo: Vuelo):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """UPDATE vuelos SET numero_vuelo=%s, precio_base=%s, asientos_disponibles=%s 
               WHERE id_vuelo=%s""",
            (vuelo.numero_vuelo, vuelo.precio_base, vuelo.asientos_disponibles, vuelo_id)
        )
        conn.commit()
        return {"message": "Vuelo actualizado correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/vuelos/{vuelo_id}")
def delete_vuelo(vuelo_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM vuelos WHERE id_vuelo = %s", (vuelo_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Vuelo eliminado"}
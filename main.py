from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="API de Tickets - Filtros de Precio y Disponibilidad")

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db-tickets"),
        database=os.getenv("POSTGRES_DB", "travel_tickets"),
        user=os.getenv("POSTGRES_USER", "u_tickets"),
        password=os.getenv("POSTGRES_PASSWORD", "password123"),
        cursor_factory=RealDictCursor
    )

@app.get("/vuelos")
def listar_vuelos(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    destino: Optional[str] = Query(None, description="Nombre del destino"),
    aerolinea: Optional[str] = Query(None, description="Nombre de la aerolínea"),
    fecha: Optional[str] = Query(None, description="Fecha de salida (YYYY-MM-DD)"),
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    solo_disponibles: bool = Query(True, description="Mostrar solo vuelos con asientos libres")
):
    offset = (page - 1) * size
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        where_clauses = []
        params = []

        if solo_disponibles:
            where_clauses.append("v.asientos_disponibles > 0")

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

        query = f"""
            SELECT v.*, d.nombre_destino, d.pais 
            FROM vuelos v
            JOIN destinos d ON v.id_destino = d.id_destino
            {where_str}
            ORDER BY v.precio_base ASC
            LIMIT %s OFFSET %s
        """
        cur.execute(query, params + [size, offset])
        vuelos = cur.fetchall()

        count_query = f"""
            SELECT COUNT(*) 
            FROM vuelos v
            JOIN destinos d ON v.id_destino = d.id_destino
            {where_str}
        """
        cur.execute(count_query, params)
        total_records = cur.fetchone()['count']

        return {
            "items": vuelos,
            "total": total_records,
            "page": page,
            "size": size,
            "pages": (total_records + size - 1) // size if total_records > 0 else 0
        }
    finally:
        cur.close()
        conn.close()
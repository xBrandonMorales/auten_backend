import fastapi
import sqlite3
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

# Crea la base de datos
conn = sqlite3.connect("sql/contactos.db")

app = fastapi.FastAPI()

origins = [
    "https://contactos-frontend-ajio.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Contacto(BaseModel):
    email : str
    nombre : str
    telefono : str

from fastapi import HTTPException

@app.post("/contactos")
async def crear_contacto(contacto: Contacto):
    """Crea un nuevo contacto."""
    try:
        # Verifica si el email ya existe en la base de datos
        c = conn.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (contacto.email,))
        existing_contact = c.fetchone()

        if existing_contact:
            raise HTTPException(status_code=400, detail={"mensaje": "El email ya existe"})

        # Inserta el nuevo contacto en la base de datos
        c.execute('INSERT INTO contactos (email, nombre, telefono) VALUES (?, ?, ?)',
                  (contacto.email, contacto.nombre, contacto.telefono))
        conn.commit()

        return {"mensaje": "Contacto insertado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar los datos"})


@app.get("/contactos")
async def obtener_contactos():
    """Obtiene todos los contactos."""
    try:
        # Consulta todos los contactos de la base de datos y los envía en un JSON
        c = conn.cursor()
        c.execute('SELECT * FROM contactos')
        response = []
        for row in c.fetchall():
            contacto = {
                "email": row[0],
                "nombre": row[1],
                "telefono": row[2]
            }
            response.append(contacto)

        if response:
            return response
        else:
            raise HTTPException(status_code=202, detail="No hay registros")

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar los datos"})


@app.get("/contactos/{email}")
async def obtener_contacto(email: str):
    """Obtiene un contacto por su email."""
    try:
        # Consulta el contacto por su email
        c = conn.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        row = c.fetchone()

        if row:
            contacto = {
                "email": row[0],
                "nombre": row[1],
                "telefono": row[2]
            }
            return contacto
        else:
            raise HTTPException(status_code=404, detail={"mensaje": "El email no existe"})

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar los datos"})

@app.put("/contactos/{email}")
async def actualizar_contacto(email: str, contacto: Contacto):
    """Actualiza un contacto."""
    try:
        if contacto.nombre is None or contacto.telefono is None:
            raise HTTPException(status_code=422, detail="Nombre y teléfono son campos obligatorios")

        # Verifica si el contacto con el email proporcionado existe
        c = conn.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        existing_contact = c.fetchone()

        if not existing_contact:
            raise HTTPException(status_code=404, detail={"mensaje": "El ID contacto no existe"})

        # Actualiza el contacto en la base de datos
        c.execute('UPDATE contactos SET nombre = ?, telefono = ? WHERE email = ?',
                  (contacto.nombre, contacto.telefono, email))
        conn.commit()

        return {"mensaje": "Contacto actualizado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar o actualizar los datos"})


@app.delete("/contactos/{email}")
async def eliminar_contacto(email: str):
    """Elimina un contacto."""
    try:
        # Verifica si el contacto con el email proporcionado existe
        c = conn.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        existing_contact = c.fetchone()

        if not existing_contact:
            raise HTTPException(status_code=404, detail={"mensaje": "El email del contacto no existe"})

        # Elimina el contacto de la base de datos
        c.execute('DELETE FROM contactos WHERE email = ?', (email,))
        conn.commit()

        return {"mensaje": "Contacto borrado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar o eliminar los datos"})

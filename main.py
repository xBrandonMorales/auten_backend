import fastapi
import sqlite3
import hashlib
from fastapi import Depends, HTTPException, Request, Cookie
from fastapi.security import HTTPBearer
from starlette.responses import JSONResponse  # Importa la clase JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

securityBearer = HTTPBearer()

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

def md5_hash(text):
    """Función para calcular el hash MD5 de una cadena"""
    return hashlib.md5(text.encode()).hexdigest()

# Almacenamiento de sesiones en memoria (no recomendado para producción)
sessions = {}

class Session:
    def __init__(self):
        self.token = None

@app.middleware("http")
async def add_session(request: Request, call_next):
    request.state.session = Session()
    response = await call_next(request)
    return response

class Contacto(BaseModel):
    email: str
    nombre: str
    telefono: str

def get_connection():
    """Función para obtener una nueva conexión a la base de datos"""
    return sqlite3.connect("sql/contactos.db")

@app.get("/")
def auth(credentials: HTTPBearer = Depends(securityBearer), session: Session = Depends()):
    """Autenticación con token fijo"""
    token = credentials.credentials
    connx = get_connection()
    c = connx.cursor()
    c.execute('SELECT token FROM usuarios WHERE token = ?', (token,))
    existe = c.fetchone()

    if existe is None:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    else:
        # Almacenar el token en la sesión
        session.token = token
        # Almacenar la sesión en el diccionario (no recomendado para producción)
        sessions[token] = session
        return {"mensaje": "Hola Mundo"}

@app.post("/token", response_class=JSONResponse)  # Usa JSONResponse como clase de respuesta
def get_token(username: str = fastapi.Form(...), password: str = fastapi.Form(...), session: Session = Depends()):
    """Obtener token si las credenciales son correctas"""
    connx = get_connection()
    c = connx.cursor()

    hashed_password = md5_hash(password)

    c.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, hashed_password))
    user_exists = c.fetchone()

    if user_exists:
        token = user_exists[2]  # Suponiendo que el token está en la tercera columna de la tabla usuarios
        # Almacenar el token en la sesión
        session.token = token
        # Almacenar la sesión en el diccionario (no recomendado para producción)
        sessions[token] = session

        # Devolver el token (y opcionalmente almacenarlo en el cliente)
        response = JSONResponse(content={"token": token})
        # Puedes almacenar el token en una cookie o en el cuerpo de la respuesta, según tus necesidades.
        # Aquí, se almacena en una cookie con httponly=True para mayor seguridad.
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    else:
        raise HTTPException(status_code=401, detail="Not Authenticated")

@app.post("/contactos", dependencies=[Depends(auth)])
async def crear_contacto(contacto: Contacto):
    """Crea un nuevo contacto."""
    try:
        # Verifica si el email ya existe en la base de datos
        connx = get_connection()
        c = connx.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (contacto.email,))
        existing_contact = c.fetchone()

        if existing_contact:
            raise HTTPException(status_code=400, detail={"mensaje": "El email ya existe"})

        # Inserta el nuevo contacto en la base de datos
        c.execute('INSERT INTO contactos (email, nombre, telefono) VALUES (?, ?, ?)',
                  (contacto.email, contacto.nombre, contacto.telefono))
        connx.commit()

        return {"mensaje": "Contacto insertado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar los datos"})

@app.get("/contactos", dependencies=[Depends(auth)])
async def obtener_contactos():
    """Obtiene todos los contactos."""
    try:
        # Consulta todos los contactos de la base de datos y los envía en un JSON
        connx = get_connection()
        c = connx.cursor()
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

@app.get("/contactos/{email}", dependencies=[Depends(auth)])
async def obtener_contacto(email: str):
    """Obtiene un contacto por su email."""
    try:
        # Consulta el contacto por su email
        connx = get_connection()
        c = connx.cursor()
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

@app.put("/contactos/{email}", dependencies=[Depends(auth)])
async def actualizar_contacto(email: str, contacto: Contacto):
    """Actualiza un contacto."""
    try:
        if contacto.nombre is None or contacto.telefono is None:
            raise HTTPException(status_code=422, detail="Nombre y teléfono son campos obligatorios")

        # Verifica si el contacto con el email proporcionado existe
        connx = get_connection()
        c = connx.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        existing_contact = c.fetchone()

        if not existing_contact:
            raise HTTPException(status_code=404, detail={"mensaje": "El ID contacto no existe"})

        # Actualiza el contacto en la base de datos
        c.execute('UPDATE contactos SET nombre = ?, telefono = ? WHERE email = ?',
                  (contacto.nombre, contacto.telefono, email))
        connx.commit()

        return {"mensaje": "Contacto actualizado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar o actualizar los datos"})

@app.delete("/contactos/{email}", dependencies=[Depends(auth)])
async def eliminar_contacto(email: str):
    """Elimina un contacto."""
    try:
        # Verifica si el contacto con el email proporcionado existe
        connx = get_connection()
        c = connx.cursor()
        c.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        existing_contact = c.fetchone()

        if not existing_contact:
            raise HTTPException(status_code=404, detail={"mensaje": "El email del contacto no existe"})

        # Elimina el contacto de la base de datos
        c.execute('DELETE FROM contactos WHERE email = ?', (email,))
        connx.commit()

        return {"mensaje": "Contacto borrado correctamente"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"mensaje": "Error al consultar o eliminar los datos"})

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="autenticar-usuario")

# Modelos
class Usuario(BaseModel):
    nombre_usuario: str
    contrasena: str

class Servicio(BaseModel):
    nombre: str
    descripcion: str
    endpoints: List[str]

class Orquestacion(BaseModel):
    servicio_destino: str
    parametros_adicionales: dict

class ReglasOrquestacion(BaseModel):
    reglas: dict

class Autorizacion(BaseModel):
    recursos: List[str]
    rol_usuario: str

# Simulación de base de usuarios
usuarios_db = {
    "admin": {"contrasena": "1234", "rol": "Administrador"},
    "orquestador": {"contrasena": "abcd", "rol": "Orquestador"},
}

# Endpoints
@app.post("/autenticar-usuario")
def autenticar(usuario: Usuario):
    user = usuarios_db.get(usuario.nombre_usuario)
    if user and user["contrasena"] == usuario.contrasena:
        return {"access_token": usuario.nombre_usuario + "_token", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

@app.post("/autorizar-acceso")
def autorizar(data: Autorizacion, token: str = Depends(oauth2_scheme)):
    if "admin" in token and data.rol_usuario == "Administrador":
        return {"autorizado": True}
    elif "orquestador" in token and data.rol_usuario == "Orquestador":
        return {"autorizado": True}
    else:
        raise HTTPException(status_code=403, detail="Acceso denegado")

@app.post("/registrar-servicio")
def registrar_servicio(servicio: Servicio, token: str = Depends(oauth2_scheme)):
    if "admin" not in token:
        raise HTTPException(status_code=403, detail="Solo administradores pueden registrar servicios")
    return {"mensaje": "Servicio registrado correctamente", "servicio": servicio}

@app.get("/informacion-servicio/{id}")
def obtener_info(id: str, token: str = Depends(oauth2_scheme)):
    return {"id": id, "nombre": "ServicioX", "descripcion": "Ejemplo"}

@app.post("/orquestar")
def orquestar(data: Orquestacion, token: str = Depends(oauth2_scheme)):
    if "orquestador" not in token and "admin" not in token:
        raise HTTPException(status_code=403, detail="No autorizado")
    return {"mensaje": f"Servicio {data.servicio_destino} orquestado con éxito", "parametros": data.parametros_adicionales}

@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(data: ReglasOrquestacion, token: str = Depends(oauth2_scheme)):
    if "orquestador" not in token:
        raise HTTPException(status_code=403, detail="Solo orquestadores pueden actualizar reglas")
    return {"mensaje": "Reglas actualizadas", "reglas": data.reglas}

# 👇 Este bloque permite que Railway inicie correctamente el servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Usa el puerto que proporciona Railway
    uvicorn.run("main:app", host="0.0.0.0", port=port)


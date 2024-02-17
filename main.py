from fastapi import FastAPI
from routers import users_db, logueo_jwt
from fastapi.staticfiles import StaticFiles


#Crea la instancia de FastAPI
app = FastAPI()


#Incluye los routers a la hora de ejecutar en toda una API
app.include_router(users_db.router)
#app.include_router(logueo_jwt.router)

#Muestra una foto
#http://127.0.0.1:8000/static/images/python.jpg
app.mount("/static", StaticFiles(directory="static"),name="static")


#Cuando hace el get en la api retorna "Hola Mundo"
@app.get("/")
async def hola_mundo():
    return "Hola Mundo"

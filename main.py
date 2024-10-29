from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configurar la URL de la base de datos externamente
DATABASE_URL = "postgresql://cine_db_zun9_user:CIGmMh0ycctPEbPGLr5FqtQE5JoTRcGN@dpg-csgkhh68ii6s73aigpog-a.oregon-postgres.render.com/cine_db_zun9"

# Configurar la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Crear el modelo de la tabla peliculas
class Pelicula(Base):
    __tablename__ = "peliculas"
    pelicula_id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False)
    genero = Column(String(50), nullable=False)
    duracion = Column(Integer, nullable=False)
    clasificacion = Column(String(10), nullable=False)
    director = Column(String(100), nullable=False)
    ano_estreno = Column(Integer, nullable=False)

# Crear la base de datos y las tablas
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI()

# Definir el esquema para validar las entradas de la API
class PeliculaCreate(BaseModel):
    titulo: str
    genero: str
    duracion: int
    clasificacion: str
    director: str
    ano_estreno: int

class PeliculaResponse(PeliculaCreate):
    pelicula_id: int

    class Config:
        orm_mode = True

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Películas"}

# Ruta para obtener todas las películas
@app.get("/peliculas", response_model=list[PeliculaResponse])
def get_peliculas(db: Session = Depends(get_db)):
    peliculas = db.query(Pelicula).all()
    return peliculas

# Ruta para obtener una película por ID
@app.get("/peliculas/{pelicula_id}", response_model=PeliculaResponse)
def get_pelicula(pelicula_id: int, db: Session = Depends(get_db)):
    pelicula = db.query(Pelicula).filter(Pelicula.pelicula_id == pelicula_id).first()
    if pelicula is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return pelicula

# Ruta para crear una nueva película
@app.post("/peliculas", response_model=PeliculaResponse)
def create_pelicula(pelicula: PeliculaCreate, db: Session = Depends(get_db)):
    nueva_pelicula = Pelicula(**pelicula.dict())
    db.add(nueva_pelicula)
    db.commit()
    db.refresh(nueva_pelicula)
    return nueva_pelicula

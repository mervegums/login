import sys
sys.path.append("..")
from datetime import date
from typing import Optional
from fastapi import  Depends, HTTPException , APIRouter
import models
from database import engine , SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/musteriler",
    tags=["musteriler"],
    responses={404:{"description": "Bulunamadı"}}
)

models.Base.metadata.create_all(bind=engine)



def get_db():
    try:
        db= SessionLocal()
        yield db

    finally:
        db.close()



class Musteri(BaseModel):
    kategori:   str
    firmaAdi : str
    email : str
    yetkili: str
    ulke : str
    sehir : str
    adres : str
    web : str
    durum : str
    musteri_temsilci: str
    kartvizit: str
    Bayi : str
    ilkSatisYili : date
    sonSatisYili: date




@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Musteri).all()



@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Musteri)\
        .filter(models.Musteri.owner_id == user.get("id"))\
        .all()



@router.get("/{musteri_id}")
async def read_musteri(musteri_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    musteri_model= db.query(models.Musteri)\
        .filter(models.Musteri.id == musteri_id)\
        .filter(models.Musteri.owner_id == user.get("id"))\
        .first()
    if musteri_model is not None:
        return musteri_model
    raise http_exception()    

@router.post("/")
async def create_musteri(musteri: Musteri,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
   
    if user is None:
        raise get_user_exception()
    musteri_model = models.Musteri()
    musteri_model.kategori =musteri.kategori
    musteri_model.firmaAdi =musteri.firmaAdi
    musteri_model.email =musteri.email
    musteri_model.yetkili =musteri.yetkili
    musteri_model.ulke =musteri.ulke
    musteri_model.sehir =musteri.sehir
    musteri_model.adres =musteri.adres
    musteri_model.web =musteri.web
    musteri_model.durum =musteri.durum
    musteri_model.musteri_temsilci =musteri.musteri_temsilci
    musteri_model.kartvizit =musteri.kartvizit
    musteri_model.Bayi =musteri.Bayi
    musteri_model.ilkSatisYili =musteri.ilkSatisYili
    musteri_model.sonSatisYili=musteri.sonSatisYili
    musteri_model.owner_id= user.get("id")


    db.add(musteri_model)
    db.commit()

    return successful_response(200)

     
@router.put("/{musteri_id}")
async def update_musteri(musteri_id: int, 
                         musteri: Musteri,
                         user: dict= Depends(get_current_user),
                         db: Session = Depends(get_db)):
    
        if user is None:
            raise get_user_exception()
        musteri_model = db.query(models.Musteri)\
            .filter(models.Musteri.id == musteri_id)\
            .filter(models.Musteri.owner_id == user.get("id"))\
            .first()


        if musteri_model is None:
            raise http_exception()
        musteri_model.kategori =musteri.kategori
        musteri_model.firmaAdi =musteri.firmaAdi
        musteri_model.email =musteri.email
        musteri_model.yetkili =musteri.yetkili
        musteri_model.ulke =musteri.ulke
        musteri_model.sehir =musteri.sehir
        musteri_model.adres =musteri.adres
        musteri_model.web =musteri.web
        musteri_model.durum =musteri.durum
        musteri_model.musteri_temsilci =musteri.musteri_temsilci  
        musteri_model.kartvizit =musteri.kartvizit
        musteri_model.Bayi =musteri.Bayi
        musteri_model.ilkSatisYili =musteri.ilkSatisYili
        musteri_model.sonSatisYili=musteri.sonSatisYili
       
        
        db.add(musteri_model)
        db.commit()


        return successful_response(200)


@router.delete("/{musteri_id}")
async def delete_musteri(musteri_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    musteri_model = db.query(models.Musteriler)\
        .filter(models.Musteri.id == musteri_id)\
        .filter(models.Musteri.owner_id == user.get("id"))\
        .first()

    if musteri_model is None:
        raise http_exception()

    db.query(models.Musteri)\
        .filter(models.Musteri.id == musteri_id)\
        .delete()

    db.commit()

    return successful_response(200)


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }

def http_exception():
    return HTTPException(status_code=404, detail="Müşteri bilgisine ulaşılamadı")    
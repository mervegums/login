from datetime import date
from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Query
import models
from database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, Field
from auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/musteriler",
    tags=["musteriler"],
    responses={404:{"description": "Bulunamadı"}}
)

models.Base.metadata.create_all(bind=engine)



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
async def read_all_customers_paginated(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for company name, email, or contact"),
    category: Optional[str] = Query(None, description="Filter by category"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get customers with pagination and filtering"""
    if user is None:
        raise get_user_exception()
    
    query = db.query(models.Musteri).filter(
        models.Musteri.owner_id == user.get("id")
    )
    
    # Add search filter
    if search:
        search_filter = or_(
            models.Musteri.firmaAdi.ilike(f"%{search}%"),
            models.Musteri.email.ilike(f"%{search}%"),
            models.Musteri.yetkili.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Add category filter
    if category:
        query = query.filter(models.Musteri.kategori == category)
    
    # Get total count for pagination info
    total = query.count()
    
    # Apply pagination
    customers = query.offset(skip).limit(limit).all()
    
    return {
        "customers": customers,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }


@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """Deprecated: Use / endpoint with pagination instead"""
    if user is None:
        raise get_user_exception()
    return db.query(models.Musteri)\
        .filter(models.Musteri.owner_id == user.get("id"))\
        .limit(100)\
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

    musteri_model = db.query(models.Musteri)\
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
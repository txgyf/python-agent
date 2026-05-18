from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Model
from app.schemas import ModelCreate, ModelUpdate, ModelResponse, PaginatedResponse

router = APIRouter(prefix="/api/models", tags=["Models"])


@router.get("", response_model=PaginatedResponse[ModelResponse])
def list_models(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Model)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.post("", response_model=ModelResponse, status_code=201)
def create_model(model: ModelCreate, db: Session = Depends(get_db)):
    db_model = Model(**model.model_dump())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(model_id: int, model: ModelUpdate, db: Session = Depends(get_db)):
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    for key, value in model.model_dump(exclude_unset=True).items():
        setattr(db_model, key, value)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    db_model = db.query(Model).filter(Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    from app.models import Experiment
    if db.query(Experiment).filter(Experiment.model_id == model_id).first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete model with associated experiments"
        )
    db.delete(db_model)
    db.commit()
    return {"message": "deleted"}

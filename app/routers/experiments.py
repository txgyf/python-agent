from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Experiment
from app.schemas import (
    ExperimentCreate, ExperimentUpdate, ExperimentResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/experiments", tags=["Experiments"])


@router.get("", response_model=PaginatedResponse[ExperimentResponse])
def list_experiments(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    model_id: int = None,
    gpu_id: int = None,
    db: Session = Depends(get_db),
):
    query = db.query(Experiment)
    if status:
        query = query.filter(Experiment.status == status)
    if model_id:
        query = query.filter(Experiment.model_id == model_id)
    if gpu_id:
        query = query.filter(Experiment.gpu_id == gpu_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.post("", response_model=ExperimentResponse, status_code=201)
def create_experiment(
    experiment: ExperimentCreate, db: Session = Depends(get_db)
):
    from app.models import GPU, Model
    if not db.query(GPU).filter(GPU.id == experiment.gpu_id).first():
        raise HTTPException(status_code=400, detail="GPU not found")
    if not db.query(Model).filter(Model.id == experiment.model_id).first():
        raise HTTPException(status_code=400, detail="Model not found")
    db_exp = Experiment(**experiment.model_dump())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(
    experiment_id: int, experiment: ExperimentUpdate, db: Session = Depends(get_db)
):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    for key, value in experiment.model_dump(exclude_unset=True).items():
        setattr(exp, key, value)
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/{experiment_id}")
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    db.delete(exp)
    db.commit()
    return {"message": "deleted"}

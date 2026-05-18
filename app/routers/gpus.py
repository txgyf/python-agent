from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GPU
from app.schemas import GPUCreate, GPUUpdate, GPUResponse, PaginatedResponse

router = APIRouter(prefix="/api/gpus", tags=["GPUs"])


@router.get("", response_model=PaginatedResponse[GPUResponse])
def list_gpus(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(GPU)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}


@router.post("", response_model=GPUResponse, status_code=201)
def create_gpu(gpu: GPUCreate, db: Session = Depends(get_db)):
    db_gpu = GPU(**gpu.model_dump())
    db.add(db_gpu)
    db.commit()
    db.refresh(db_gpu)
    return db_gpu


@router.get("/{gpu_id}", response_model=GPUResponse)
def get_gpu(gpu_id: int, db: Session = Depends(get_db)):
    gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    return gpu


@router.put("/{gpu_id}", response_model=GPUResponse)
def update_gpu(gpu_id: int, gpu: GPUUpdate, db: Session = Depends(get_db)):
    db_gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    for key, value in gpu.model_dump(exclude_unset=True).items():
        setattr(db_gpu, key, value)
    db.commit()
    db.refresh(db_gpu)
    return db_gpu


@router.delete("/{gpu_id}")
def delete_gpu(gpu_id: int, db: Session = Depends(get_db)):
    db_gpu = db.query(GPU).filter(GPU.id == gpu_id).first()
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    from app.models import Experiment
    if db.query(Experiment).filter(Experiment.gpu_id == gpu_id).first():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete GPU with associated experiments"
        )
    db.delete(db_gpu)
    db.commit()
    return {"message": "deleted"}

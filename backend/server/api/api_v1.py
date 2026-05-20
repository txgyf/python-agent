from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from server.db.session import get_db
from server.crud import crud
from server.schemas.schemas import (
    ComputeSpec, ComputeSpecCreate, ComputeSpecUpdate,
    ModelMetadata, ModelMetadataCreate, ModelMetadataUpdate,
    Experiment, ExperimentSimple, ExperimentCreate, ExperimentUpdate,
)

router = APIRouter(prefix="/api/v1")


@router.get("")
def root():
    return {"message": "InfereVal API v1"}


# --- ComputeSpec ---

@router.get("/compute-specs", response_model=list[ComputeSpec])
def list_compute_specs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_compute_specs(db, skip=skip, limit=limit)


@router.post("/compute-specs", response_model=ComputeSpec, status_code=201)
def create_compute_spec(data: ComputeSpecCreate, db: Session = Depends(get_db)):
    return crud.create_compute_spec(db, data)


@router.post("/compute-specs/batch", response_model=list[ComputeSpec], status_code=201)
def create_compute_specs_batch(items: list[ComputeSpecCreate], db: Session = Depends(get_db)):
    return crud.create_compute_specs_batch(db, items)


@router.put("/compute-specs/{spec_id}", response_model=ComputeSpec)
def update_compute_spec(spec_id: int, data: ComputeSpecUpdate, db: Session = Depends(get_db)):
    result = crud.update_compute_spec(db, spec_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="ComputeSpec not found")
    return result


@router.delete("/compute-specs/{spec_id}", response_model=ComputeSpec)
def delete_compute_spec(spec_id: int, db: Session = Depends(get_db)):
    result = crud.delete_compute_spec(db, spec_id)
    if result is None:
        raise HTTPException(status_code=404, detail="ComputeSpec not found")
    if isinstance(result, int):
        raise HTTPException(
            status_code=409,
            detail=f"该芯片有 {result} 条关联实验，请先删除相关实验数据"
        )
    return result


# --- ModelMetadata ---

@router.get("/models", response_model=list[ModelMetadata])
def list_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_models(db, skip=skip, limit=limit)


@router.post("/models", response_model=ModelMetadata, status_code=201)
def create_model(data: ModelMetadataCreate, db: Session = Depends(get_db)):
    return crud.create_model(db, data)


@router.post("/models/batch", response_model=list[ModelMetadata], status_code=201)
def create_models_batch(items: list[ModelMetadataCreate], db: Session = Depends(get_db)):
    return crud.create_models_batch(db, items)


@router.put("/models/{model_id}", response_model=ModelMetadata)
def update_model(model_id: int, data: ModelMetadataUpdate, db: Session = Depends(get_db)):
    result = crud.update_model(db, model_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="ModelMetadata not found")
    return result


@router.delete("/models/{model_id}", response_model=ModelMetadata)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    result = crud.delete_model(db, model_id)
    if result is None:
        raise HTTPException(status_code=404, detail="ModelMetadata not found")
    if isinstance(result, int):
        raise HTTPException(
            status_code=409,
            detail=f"该模型有 {result} 条关联实验，请先删除相关实验数据"
        )
    return result


# --- Experiment ---

@router.get("/experiments", response_model=list[Experiment])
def list_experiments(
    model_id: int | None = None,
    compute_spec_id: int | None = None,
    experiment_name_q: str | None = None,
    skip: int = 0,
    limit: int = 10000,
    db: Session = Depends(get_db),
):
    items = crud.get_experiments(
        db, model_id=model_id, compute_spec_id=compute_spec_id,
        experiment_name_q=experiment_name_q, skip=skip, limit=limit,
    )
    total = crud.get_experiments_count(
        db, model_id=model_id, compute_spec_id=compute_spec_id,
        experiment_name_q=experiment_name_q,
    )
    return Response(
        content=_serialize_list(items),
        media_type="application/json",
        headers={"X-Total-Count": str(total)},
    )


def _serialize_list(items):
    import json
    from pydantic import TypeAdapter
    adapter = TypeAdapter(list[Experiment])
    return adapter.dump_json(items).decode()


@router.post("/experiments", response_model=ExperimentSimple, status_code=201)
def create_experiment(data: ExperimentCreate, db: Session = Depends(get_db)):
    return crud.create_experiment(db, data)


@router.post("/experiments/batch", response_model=list[ExperimentSimple], status_code=201)
def create_experiments_batch(items: list[ExperimentCreate], db: Session = Depends(get_db)):
    return crud.create_experiments_batch(db, items)


@router.put("/experiments/{exp_id}", response_model=ExperimentSimple)
def update_experiment(exp_id: int, data: ExperimentUpdate, db: Session = Depends(get_db)):
    result = crud.update_experiment(db, exp_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result


@router.delete("/experiments/{exp_id}", response_model=ExperimentSimple)
def delete_experiment(exp_id: int, db: Session = Depends(get_db)):
    result = crud.delete_experiment(db, exp_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result

import re

from sqlalchemy.orm import Session

from server.models.compute_spec import ComputeSpec
from server.models.model_metadata import ModelMetadata
from server.models.experiment_result import ExperimentResult
from server.models.experiment import Experiment
from server.schemas.schemas import (
    ComputeSpecCreate, ComputeSpecUpdate,
    ModelMetadataCreate, ModelMetadataUpdate,
    ExperimentResultCreate, ExperimentResultUpdate,
    ExperimentCreate, ExperimentUpdate,
)
from server.services.experiment_naming import generate_experiment_name, normalize_name


# --- ComputeSpec ---

def get_compute_specs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ComputeSpec).offset(skip).limit(limit).all()


def create_compute_spec(db: Session, data: ComputeSpecCreate):
    obj = ComputeSpec(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_compute_specs_batch(db: Session, items: list[ComputeSpecCreate]):
    objs = [ComputeSpec(**item.model_dump()) for item in items]
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def update_compute_spec(db: Session, spec_id: int, data: ComputeSpecUpdate):
    obj = db.query(ComputeSpec).filter(ComputeSpec.id == spec_id).first()
    if not obj:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_compute_spec(db: Session, spec_id: int):
    obj = db.query(ComputeSpec).filter(ComputeSpec.id == spec_id).first()
    if not obj:
        return None
    count = db.query(Experiment).filter(Experiment.compute_spec_id == spec_id).count()
    if count > 0:
        return count
    db.delete(obj)
    db.commit()
    return obj


# --- ModelMetadata ---

def get_models(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ModelMetadata).offset(skip).limit(limit).all()


def create_model(db: Session, data: ModelMetadataCreate):
    obj = ModelMetadata(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_models_batch(db: Session, items: list[ModelMetadataCreate]):
    objs = [ModelMetadata(**item.model_dump()) for item in items]
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def update_model(db: Session, model_id: int, data: ModelMetadataUpdate):
    obj = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    if not obj:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_model(db: Session, model_id: int):
    obj = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    if not obj:
        return None
    count = db.query(Experiment).filter(Experiment.model_id == model_id).count()
    if count > 0:
        return count
    db.delete(obj)
    db.commit()
    return obj


# --- Experiment ---

def get_experiments(
    db: Session,
    model_id: int | None = None,
    compute_spec_id: int | None = None,
    experiment_name_q: str | None = None,
    skip: int = 0,
    limit: int = 10000,
):
    query = db.query(Experiment)
    if model_id is not None:
        query = query.filter(Experiment.model_id == model_id)
    if compute_spec_id is not None:
        query = query.filter(Experiment.compute_spec_id == compute_spec_id)
    if experiment_name_q:
        cleaned = re.sub(r"\s+", "", experiment_name_q).lower()
        query = query.filter(
            Experiment.experiment_name != None  # noqa: E711
        )
        rows = query.all()
        matched = [
            r for r in rows
            if cleaned in re.sub(r"\s+", "", r.experiment_name or "").lower()
        ]
        return matched
    return query.offset(skip).limit(limit).all()


def get_experiments_count(
    db: Session,
    model_id: int | None = None,
    compute_spec_id: int | None = None,
    experiment_name_q: str | None = None,
):
    query = db.query(Experiment)
    if model_id is not None:
        query = query.filter(Experiment.model_id == model_id)
    if compute_spec_id is not None:
        query = query.filter(Experiment.compute_spec_id == compute_spec_id)
    if experiment_name_q:
        cleaned = re.sub(r"\s+", "", experiment_name_q).lower()
        query = query.filter(
            Experiment.experiment_name != None  # noqa: E711
        )
        rows = query.all()
        return len([
            r for r in rows
            if cleaned in re.sub(r"\s+", "", r.experiment_name or "").lower()
        ])
    return query.count()


def create_experiment(db: Session, data: ExperimentCreate):
    result = ExperimentResult(**data.result.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)

    name = normalize_name(data.experiment_name)
    if name is None:
        name = generate_experiment_name(db, data.compute_spec_id, data.model_id, result.id)

    exp_data = data.model_dump(exclude={"result", "experiment_name"})
    exp = Experiment(experiment_name=name, result_id=result.id, **exp_data)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


def create_experiments_batch(db: Session, items: list[ExperimentCreate]):
    return [create_experiment(db, item) for item in items]


def update_experiment(db: Session, exp_id: int, data: ExperimentUpdate):
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if not exp:
        return None
    if data.result is not None:
        result = db.query(ExperimentResult).filter(
            ExperimentResult.id == exp.result_id
        ).first()
        if result:
            for key, value in data.result.model_dump(exclude_unset=True).items():
                setattr(result, key, value)
    update_data = data.model_dump(exclude_unset=True, exclude={"result"})
    for key, value in update_data.items():
        setattr(exp, key, value)
    db.commit()
    db.refresh(exp)
    return exp


def delete_experiment(db: Session, exp_id: int):
    exp = db.query(Experiment).filter(Experiment.id == exp_id).first()
    if not exp:
        return None
    result_id = exp.result_id
    db.delete(exp)
    result = db.query(ExperimentResult).filter(ExperimentResult.id == result_id).first()
    if result:
        db.delete(result)
    db.commit()
    return exp

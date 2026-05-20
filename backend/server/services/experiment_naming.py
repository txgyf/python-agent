from datetime import datetime

from sqlalchemy.orm import Session


def generate_experiment_name(
    db: Session,
    compute_spec_id: int,
    model_id: int,
    result_id: int,
) -> str:
    from server.models.compute_spec import ComputeSpec
    from server.models.model_metadata import ModelMetadata

    spec = db.query(ComputeSpec).filter(ComputeSpec.id == compute_spec_id).first()
    model = db.query(ModelMetadata).filter(ModelMetadata.id == model_id).first()
    chip_name = spec.chip_name.replace(" ", "") if spec else "unknown"
    model_name = model.model_name.replace(" ", "") if model else "unknown"
    date_str = datetime.now().strftime("%y%m%d")
    suffix = str(result_id % 10000).zfill(4)
    return f"{model_name}_{chip_name}_{date_str}_{suffix}"


def normalize_name(name: str | None) -> str | None:
    if name is None:
        return None
    return name.replace(" ", "")

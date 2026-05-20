"""Seed the database with sample data."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from server.db.base import Base
from server.db.session import engine, SessionLocal
from server.crud.crud import (
    create_compute_spec,
    create_model,
    create_experiment,
)
from server.schemas.schemas import (
    ComputeSpecCreate, ModelMetadataCreate,
    ExperimentCreate, ExperimentResultCreate,
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        spec1 = create_compute_spec(db, ComputeSpecCreate(
            chip_name="NVIDIA H800", fp32_tflops=67.0, tf32_tflops=989.0,
            fp16_tflops=1979.0, fp8_tflops=3958.0, fp4_tflops=0.0,
            interconnect_bandwidth=900.0, memory_gb=80.0,
            memory_bandwidth_tbs=3.35, updated_by="admin"
        ))
        spec2 = create_compute_spec(db, ComputeSpecCreate(
            chip_name="NVIDIA H20", fp32_tflops=44.0, tf32_tflops=148.0,
            fp16_tflops=296.0, fp8_tflops=593.0, fp4_tflops=0.0,
            interconnect_bandwidth=900.0, memory_gb=96.0,
            memory_bandwidth_tbs=4.0, updated_by="admin"
        ))

        model1 = create_model(db, ModelMetadataCreate(
            model_name="Llama-3-70B", architecture="Dense",
            parameters_count="70B", active_parameters_count="70B",
            updated_by="admin"
        ))
        model2 = create_model(db, ModelMetadataCreate(
            model_name="DeepSeek-V3", architecture="MoE",
            parameters_count="671B", active_parameters_count="37B",
            updated_by="admin"
        ))

        result_data = ExperimentResultCreate(
            actual_request_rate=10.0, max_request_concurrency=32,
            successful_requests=100, duration_s=60.0,
            total_input_tokens=51200, total_generated_tokens=51200,
            request_throughput_reqs=12.5, input_token_throughput_toks=6400.0,
            output_token_throughput_toks=1600.0, total_token_throughput_toks=8000.0,
            actual_concurrency=30.0, e2e_mean_ms=100.0, e2e_median_ms=95.0,
            ttft_mean_ms=48.5, ttft_median_ms=45.0,
            itl_mean_ms=5.0, itl_median_ms=4.5,
        )
        create_experiment(db, ExperimentCreate(
            compute_spec_id=spec1.id, model_id=model1.id,
            engine="vLLM", engine_version="v0.6.3",
            deployment_precision="BF16", isl=512, osl=512,
            request_rate=10.0, total_requests=100, concurrency=32,
            resource_count=8, updated_by="admin", result=result_data
        ))

        print("Seed data created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

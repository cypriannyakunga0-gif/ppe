"""Download the PPE YOLO weights from Hugging Face."""

from pathlib import Path

from huggingface_hub import hf_hub_download

import config


def download_ppe_model() -> Path:
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if config.PPE_MODEL_PATH.exists():
        print(f"Model already present: {config.PPE_MODEL_PATH}")
        return config.PPE_MODEL_PATH

    print(f"Downloading {config.HF_MODEL_ID}/{config.HF_MODEL_FILE} ...")
    cached = hf_hub_download(
        repo_id=config.HF_MODEL_ID,
        filename=config.HF_MODEL_FILE,
        local_dir=str(config.MODELS_DIR),
    )
    path = Path(cached)
    print(f"Saved to {path}")
    return path


if __name__ == "__main__":
    download_ppe_model()

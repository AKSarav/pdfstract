from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="opendatalab/PDF-Extract-Kit-1.0",
    local_dir="hf-cache/PDF-Extract-Kit-1.0",
    local_dir_use_symlinks=False,
)

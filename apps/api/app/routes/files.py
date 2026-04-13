from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["files"])


@router.get("")
def list_files() -> dict:
    return {"items": []}


@router.post("/upload")
def upload_file() -> dict:
    return {"status": "not_implemented"}


@router.post("/index")
def index_files() -> dict:
    return {"status": "not_implemented"}

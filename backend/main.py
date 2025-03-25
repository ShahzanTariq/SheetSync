from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from createCard import *
from masterUtil import *
from transformer import precheck_hash_dupe
from io import BytesIO


@asynccontextmanager
async def lifespan(app: FastAPI):
    precheck_hash_dupe()
    print("done checking hashes")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}


@app.post("/addMaster")
async def upload_csv(file: UploadFile = File(...), card: str = Form (...)):
    print(type(file))
    contents = await file.read()
    file = BytesIO(contents)
    if card == "TD":
        TD_account(file)
        return JSONResponse(content={"message": f"File {file.filename} uploaded successfully for {card} card."})
    else:
        return JSONResponse(
            status_code=400,
            content={"message": f"Card '{card}' is not implemented yet."}
        )

@app.get("/getMaster")
async def get_master():
    util = masterUtil()
    return util.get_rows()



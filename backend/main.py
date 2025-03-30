from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from pydantic import BaseModel
from typing import List

from createCard import *
from masterUtil import *
from sheetUtil import *
from transformer import precheck_hash_dupe
from io import BytesIO

google_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    precheck_hash_dupe()
    print("done checking hashes")

    print("Authenticating Google Sheets...")
    global google_service
    google_service = authenticate_google_sheets()
    if google_service:
        print("Google Sheets authenticated.")
    else:
        print("ERROR: Failed to authenticate Google Sheets!")
        google_service = None
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
    contents = await file.read()
    file_bytes = BytesIO(contents)
    if card == "TD":
        TD_account(file_bytes)
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


class ItemDetail(BaseModel):
    hash: str
    transactionDate: str 
    amount: float 
    description: str
    category: str


@app.post("/updateCompletion/{sheetName}")
async def update_completion(sheetName: str, request: ItemDetail):
    tf = append_row_to_sheet(google_service, sheetName, request.transactionDate, request.amount, request.description, request.category )
    if tf:
        util = masterUtil()
        util.update_completion(request.hash)
    else:
        print("google sheet thing didndt work")


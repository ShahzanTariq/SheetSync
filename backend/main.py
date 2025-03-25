from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from createCard import TD_account
from masterUtil import *

app = FastAPI()

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


# @app.post("/add_to_master_csv")
# async def upload_csv(file: UploadFile = File(...):
#     TD_account(file)

@app.get("/getMaster")
async def get_master():
    util = masterUtil()
    return util.get_rows()



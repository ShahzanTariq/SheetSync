import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from io import BytesIO
from pydantic import BaseModel
from typing import List, Optional

from transformer import Transformer, precheck_hash_dupe
from masterUtil import masterUtil
from sheetUtil import authenticate_google_sheets, append_row_to_sheet

google_service = None
card_config = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global card_config, google_service
    try:
        with open('config.json', 'r') as f:
            card_config = json.load(f)
        print("Card configuration loaded successfully.")
    except FileNotFoundError:
        print("ERROR: config.json not found!")
        card_config = {}
    except json.JSONDecodeError:
        print("ERROR: config.json is not valid JSON!")
        card_config = {}

    precheck_hash_dupe()
    print("done checking hashes")
    print("Authenticating Google Sheets...")
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

@app.get("/getCardOptions")
async def get_card_options():
    global card_config
    if not card_config:
         return []
    options = [
        {"value": key, "label": details.get("display_name", key)}
        for key, details in card_config.items()
    ]
    return options

@app.post("/addMaster")
async def upload_csv(file: UploadFile = File(...), card: str = Form(...)):
    global card_config
    if card not in card_config:
        raise HTTPException(
            status_code=400,
            detail=f"Configuration for card type '{card}' not found."
        )

    config_for_card = card_config[card]
    contents = await file.read()
    file_bytes = BytesIO(contents)

    processing_messages = []

    try:
        transformer = Transformer(
            card_name=config_for_card.get('display_name', card),
            date_col=config_for_card['date_col'],
            amount_col=config_for_card['amount_col'],
            description_col=config_for_card['description_col'],
            category_col=config_for_card.get('category_col'),
            header=config_for_card.get('header', False),
            skip_rows=config_for_card.get('skip_rows', 0)
        )
        success, processing_messages, duplicate_rows = transformer.reformat_csv(file_bytes)

        main_message = f"File '{file.filename}' processed for {config_for_card.get('display_name', card)}."
        if not success:
             main_message = f"Processing failed for file '{file.filename}'. See details."

        if success and processing_messages and ("No new transactions found" in processing_messages[-1] or "Appended 0 new rows" in processing_messages[-1]):
             main_message = f"File '{file.filename}' processed. No new transactions were added."

        print("FROM UPLOADCSV, this the type: ", type(duplicate_rows))
        return JSONResponse(
            content={
                "message": main_message,
                "details": processing_messages,
                "duplicate_rows": duplicate_rows
            }
        )

    except Exception as e:
        print(f"ERROR processing file {file.filename} for card {card}: {e}")
        import traceback
        traceback.print_exc()
        error_detail = f"An unexpected error occurred: {str(e)}"
        processing_messages.append(error_detail)
        raise HTTPException(
            status_code=500,
            detail={"message": f"Failed to process file '{file.filename}'.", "details": processing_messages}
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
    category: Optional[str] = None

@app.post("/updateCompletion/{sheetName}")
async def update_completion(sheetName: str, request: ItemDetail):
    global google_service
    if not google_service:
        raise HTTPException(status_code=503, detail="Google Sheets service unavailable.")

    data = append_row_to_sheet(
        google_service,
        sheetName,
        request.transactionDate,
        request.amount,
        request.description,
        request.category
    )
    if data:
        util = masterUtil()
        util.update_completion(request.hash)
        print(f"Updated completion for hash: {request.hash}")
        return {"message": "Completion updated successfully."}
    else:
        print(f"Google Sheet update failed for hash: {request.hash}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update Google Sheet. Completion status not updated."
        )
    
@app.post("/updateIgnore/{hash}")
async def update_ignore(hash: str):
    util = masterUtil()
    success = util.update_ignore(hash)
    if success:
        print(f"Successfully ignored {hash}")
        return {"message": "Ignored successfully."}
    else:
        print(f"Failed to ignore {hash}")
        raise HTTPException(
            status_code=500,
            detail="Failed to ignore row. Status not updated."
        )

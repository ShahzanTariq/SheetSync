# main.py
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from io import BytesIO
from pydantic import BaseModel
from typing import List, Optional # Added Optional

# Keep existing imports that are used
from transformer import Transformer, precheck_hash_dupe # Make sure Transformer is imported
from masterUtil import masterUtil
from sheetUtil import authenticate_google_sheets, append_row_to_sheet
# Remove: from createCard import * (if it existed)

google_service = None
card_config = {} # Global variable to hold the config

@asynccontextmanager
async def lifespan(app: FastAPI):
    global card_config, google_service
    # --- Load Card Config ---
    try:
        with open('config.json', 'r') as f:
            card_config = json.load(f)
        print("Card configuration loaded successfully.")
    except FileNotFoundError:
        print("ERROR: config.json not found!")
        card_config = {} # Run without config or raise an error
    except json.JSONDecodeError:
        print("ERROR: config.json is not valid JSON!")
        card_config = {} # Run without config or raise an error

    # --- Existing Lifespan Code ---
    precheck_hash_dupe()
    print("done checking hashes")
    print("Authenticating Google Sheets...")
    google_service = authenticate_google_sheets()
    if google_service:
        print("Google Sheets authenticated.")
    else:
        print("ERROR: Failed to authenticate Google Sheets!")
        google_service = None
    # --- End of Existing Lifespan Code ---
    yield
    # Cleanup can go here if needed

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Root Endpoint (Keep as is) ---
@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}

# --- NEW Endpoint to Get Card Options ---
@app.get("/getCardOptions")
async def get_card_options():
    global card_config
    if not card_config:
         return [] # Return empty list if config failed to load
    # Format for Mantine Select component ({ value: key, label: display_name })
    options = [
        {"value": key, "label": details.get("display_name", key)}
        for key, details in card_config.items()
    ]
    return options

# --- Modified /addMaster Endpoint ---
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

    processing_messages = [] # Initialize list for messages

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
        # Capture success status and messages
        success, processing_messages = transformer.reformat_csv(file_bytes)

        # Determine the main message based on success and content of messages
        main_message = f"File '{file.filename}' processed for {config_for_card.get('display_name', card)}."
        if not success:
             # If reformat_csv returned False, it implies a critical error like writing failed
             main_message = f"Processing failed for file '{file.filename}'. See details."
             # Return an error status code if appropriate
             # return JSONResponse(status_code=500, content={"message": main_message, "details": processing_messages})
             # Or stick with 200 but indicate failure in message, letting frontend decide appearance

        # If success is True, but last message indicates no new rows, adjust main message
        if success and processing_messages and ("No new transactions found" in processing_messages[-1] or "Appended 0 new rows" in processing_messages[-1]):
             main_message = f"File '{file.filename}' processed. No new transactions were added."


        return JSONResponse(
            content={
                "message": main_message,
                "details": processing_messages # Include the list of messages
            }
        )

    except Exception as e:
        print(f"ERROR processing file {file.filename} for card {card}: {e}")
        import traceback
        traceback.print_exc()
        # Include the exception message in the details if possible
        error_detail = f"An unexpected error occurred: {str(e)}"
        processing_messages.append(error_detail)
        raise HTTPException(
            status_code=500,
            # Use the detail field for the main error, include collected messages if any
            detail={"message": f"Failed to process file '{file.filename}'.", "details": processing_messages}
        )

# --- /getMaster Endpoint (Keep as is) ---
# Assumes masterUtil reads master.csv correctly in its current state
@app.get("/getMaster")
async def get_master():
    util = masterUtil()
    return util.get_rows() # Returns rows based on master.csv's structure

# --- Pydantic Model ItemDetail (Keep as is) ---
# This model should reflect the structure of data RETURNED BY /getMaster
# and SENT TO /updateCompletion. It should match the keys masterUtil provides.
# If masterUtil.get_rows returns dicts like {'index': N, 0: date, 1: amount, ... 'Hash': hash},
# this model and the frontend table need to match THAT structure.
# Let's keep the existing model, assuming get_rows returns these specific keys.
class ItemDetail(BaseModel):
    hash: str
    transactionDate: str
    amount: float
    description: str
    category: Optional[str] = None # Make category optional if it might be missing

# --- /updateCompletion Endpoint (Keep as is) ---
# Assumes the ItemDetail model matches the data structure and that
# sheetUtil.append_row_to_sheet expects these specific arguments.
@app.post("/updateCompletion/{sheetName}")
async def update_completion(sheetName: str, request: ItemDetail):
    global google_service # Ensure service is available
    if not google_service:
        raise HTTPException(status_code=503, detail="Google Sheets service unavailable.")

    # Pass data based on the ItemDetail model fields
    tf = append_row_to_sheet(
        google_service,
        sheetName,
        request.transactionDate, # Matches ItemDetail
        request.amount,          # Matches ItemDetail
        request.description,     # Matches ItemDetail
        request.category         # Matches ItemDetail (will be None if missing)
    )
    if tf:
        util = masterUtil()
        # Assumes masterUtil.update_completion uses the 'Hash' string and 'Completion' column name internally
        util.update_completion(request.hash) # Pass hash from ItemDetail
        print(f"Updated completion for hash: {request.hash}")
        return {"message": "Completion updated successfully."}
    else:
        print(f"Google Sheet update failed for hash: {request.hash}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update Google Sheet. Completion status not updated."
        )
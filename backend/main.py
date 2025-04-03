# main.py
import json
import os # Import os for environment variables
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional, Set # Import Set
from io import BytesIO
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables (especially Sheet IDs)
load_dotenv()

# Import updated utilities
from transformer import Transformer # Removed precheck_hash_dupe import
from masterUtil import masterUtil, ItemDetail # Import ItemDetail if defined there
from sheetUtil import authenticate_google_sheets, write_row_to_sheet, MASTER_SHEET_ID # Import MASTER_SHEET_ID

CONFIG_FILE_PATH = 'card_config.json'
# MASTER_SHEET_ID is now imported from sheetUtil or loaded directly via os.getenv here

# --- Lifespan Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    # 1. Load Card Config
    print(f"Loading card configuration from {CONFIG_FILE_PATH}...")
    try:
        with open(CONFIG_FILE_PATH, 'r') as f: app.state.card_configs = json.load(f)
        print(f"Loaded configurations for: {list(app.state.card_configs.keys())}")
    except Exception as e: print(f"ERROR loading card config: {e}"); app.state.card_configs = None

    # 2. Authenticate Google Sheets & Init Master Util
    print("Authenticating Google Sheets...")
    google_service = authenticate_google_sheets()
    app.state.google_service = google_service
    if google_service:
        print("Google Sheets authenticated.")
        try:
            app.state.master_util = masterUtil(google_service)
            print("masterUtil initialized.")
        except Exception as e: print(f"ERROR initializing masterUtil: {e}"); app.state.master_util = None
    else:
        print("ERROR: Failed to authenticate Google Sheets!"); app.state.master_util = None

    # --- No more hash precheck from CSV ---

    yield # App runs
    print("Application shutdown...")

# --- FastAPI App & Middleware ---
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, # ... (keep CORS config) ...
    allow_origins=['*'], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Helper Dependencies ---
def get_google_service(request: Request): # ... (keep as before) ...
    service = getattr(request.app.state, 'google_service', None)
    if not service: raise HTTPException(status_code=503, detail="Google Sheets service unavailable.")
    return service

def get_master_util(request: Request) -> masterUtil: # ... (keep as before) ...
    util = getattr(request.app.state, 'master_util', None)
    if not util: raise HTTPException(status_code=503, detail="Master utility unavailable.")
    return util

def get_card_configs(request: Request): # ... (keep as before) ...
    configs = getattr(request.app.state, 'card_configs', None)
    if not configs: raise HTTPException(status_code=503, detail="Card configurations unavailable.")
    return configs

# --- Endpoints ---
@app.get("/")
def read_root(): return {"message": "FastAPI (Sheets Only) is working!"}

@app.get("/getCardTypes")
async def get_card_types(request: Request): # ... (keep as before) ...
    card_configs = get_card_configs(request)
    options = [{"value": key, "label": config.get("displayName", key)}
               for key, config in card_configs.items()]
    return options

@app.post("/addMaster")
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    card: str = Form(...)
):
    card_configs = get_card_configs(request)
    specific_config = card_configs.get(card)
    if not specific_config:
        raise HTTPException(status_code=400, detail=f"Config for card '{card}' not found.")

    master_util_instance = get_master_util(request) # Get util instance

    # Ensure MASTER_SHEET_ID is valid
    if not MASTER_SHEET_ID:
        raise HTTPException(status_code=500, detail="Master Sheet ID is not configured.")

    contents = await file.read()
    file_bytes = BytesIO(contents)

    try:
        # 1. Transform CSV in memory
        transformer = Transformer(specific_config)
        processed_rows: List[Dict[str, Any]] = transformer.process_csv(file_bytes)
        if not processed_rows:
             return JSONResponse(content={"message": f"No processable rows found in {file.filename}."})

        # 2. Get existing hashes from Master Google Sheet
        #    Specify the correct range for the 'Hash' column in your Master Sheet
        master_hash_column_range = 'Sheet1!F:F' # <<< ADJUST based on your Master Sheet layout
        existing_hashes: Set[str] = master_util_instance.get_existing_hashes(MASTER_SHEET_ID, master_hash_column_range)
        print(f"Found {len(existing_hashes)} existing hashes in Master Sheet.")

        # 3. Filter out duplicates
        new_unique_rows = []
        for row in processed_rows:
            if row['Hash'] and str(row['Hash']) not in existing_hashes:
                new_unique_rows.append(row)
                existing_hashes.add(str(row['Hash'])) # Add to set to prevent duplicates *within the same upload*

        # 4. Append unique rows to Master Google Sheet
        append_success = False
        if new_unique_rows:
            print(f"Attempting to append {len(new_unique_rows)} new unique rows to Master Sheet.")
            # Specify the correct Master worksheet name if not 'Sheet1'
            master_worksheet_name = 'Sheet1' # <<< ADJUST based on your Master Sheet layout
            append_success = master_util_instance.append_rows_to_master(
                MASTER_SHEET_ID,
                new_unique_rows,
                master_worksheet_name
            )
            if not append_success:
                 # Log error but maybe don't fail the whole request? Depends on requirements.
                 print("ERROR: Failed to append new rows to Master Google Sheet.")
                 # Optionally raise HTTPException here if append must succeed
                 # raise HTTPException(status_code=500, detail="Failed to save new rows to Master Sheet.")
        else:
            print("No new (non-duplicate) rows found to add to Master Sheet.")
            append_success = True # No action needed is considered success for this step

        # --- Remove appending to master.csv ---

        return JSONResponse(content={
            "message": f"File {file.filename} processed. Found {len(processed_rows)} total rows, added {len(new_unique_rows)} new unique rows to Master Sheet.",
            "total_processed": len(processed_rows),
            "new_rows_added": len(new_unique_rows),
            "append_status": "Success" if append_success else "Failed"
        })

    except ValueError as ve: raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e: print(f"Error in /addMaster: {e}"); raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/getMaster")
async def get_master(request: Request):
    # ... (Keep implementation using masterUtil.get_master_sheet_data and MASTER_SHEET_ID) ...
    util = get_master_util(request)
    if not MASTER_SHEET_ID:
         raise HTTPException(status_code=500, detail="Master Sheet ID is not configured.")
    try:
        # Specify the correct Master worksheet name if not 'Sheet1'
        master_worksheet = 'Sheet1' # <<< ADJUST based on your Master Sheet layout
        data = util.get_master_sheet_data(MASTER_SHEET_ID, master_worksheet)
        # Removed check for dict error, assuming get_master_sheet_data returns list or raises
        return data
    except Exception as e: print(f"Error in /getMaster: {e}"); raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {e}")


@app.post("/updateCompletion/{sheetNameKey}")
async def update_completion(sheetNameKey: str, request_body: ItemDetail, req: Request):
    # ... (Keep implementation using write_row_to_sheet for target sheet) ...
    # ... (and masterUtil.update_completion_status_in_master for Master Sheet) ...
    g_service = get_google_service(req)
    master_util_instance = get_master_util(req)
    if not MASTER_SHEET_ID:
        raise HTTPException(status_code=500, detail="Master Sheet ID is not configured.")

    # 1. Write to target sheet
    write_success = write_row_to_sheet(
        service=g_service, sheet_name_key=sheetNameKey, #... pass data from request_body ...
        transactionDate=request_body.transactionDate, amount=request_body.amount,
        description=request_body.description, category=request_body.category
    )
    if not write_success:
        raise HTTPException(status_code=500, detail=f"Failed to write data to sheet '{sheetNameKey}'.")

    # 2. Update Master Sheet completion
    # Specify the correct Master worksheet name if not 'Sheet1'
    master_worksheet = 'Sheet1' # <<< ADJUST based on your Master Sheet layout
    completion_success = master_util_instance.update_completion_status_in_master(
        MASTER_SHEET_ID, request_body.hash, master_worksheet
    )
    if not completion_success:
        print(f"Warning: Failed to update completion in master for hash {request_body.hash}.")
        # Return success anyway? Or raise? Depends on requirements.

    return {"message": f"Data written to sheet '{sheetNameKey}', completion status update attempted."}
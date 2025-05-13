GoogleSheetInput
A lightweight web tool for parsing bank CSVs and sending data directly to Google Sheets.

Overview:
GoogleSheetInput is a Python and JavaScript-based web application designed to streamline personal finance tracking by automatically sending transaction data from CSV files to pre-configured Google Sheets. Originally built for a family use case, it eliminates the need to manually copy-paste bank transactions into spreadsheets.

Key Features:

CSV Upload & Parsing: Supports CSV files from TD Bank by default, with an extendable config system to support other banks (e.g., Rogers).

Google Sheets Integration: Uses the Google Sheets API with OAuth authentication, enabling secure, account-specific access.

Button-based Sheet Mapping: Each button represents a pre-linked Google Sheet. Once a transaction group is submitted, it’s removed from the UI.

Bank-specific Configs: Users can define how CSV columns map to dates, amounts, descriptions, and categories using JSON config files.

FastAPI Backend: Handles CSV parsing, sheet integration, and communication between the frontend and backend.

Tech Stack:

Frontend: HTML, JavaScript

Backend: Python (FastAPI), Google Sheets API

Other: OAuth 2.0 authentication, JSON-based dynamic config system

Problem Solved:
Manual entry of banking transactions into Google Sheets was time-consuming and error-prone. GoogleSheetInput allows for fast, one-click syncing of parsed bank CSV data into relevant Google Sheets, significantly speeding up personal bookkeeping.

Challenges Addressed:

Created a flexible configuration system for parsing various bank CSV formats.

Integrated OAuth-based Google API access, allowing seamless data entry into spreadsheets owned by the authenticated user.


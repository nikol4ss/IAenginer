# IA Enginer

Create and authenticate integrations using the OpenAI library and the Google Sheets API, performing data cleansing and querying through prompts that interpret strings, extract information, and integrate the data into a new table, in an automated process executed via GitHub Actions.

## Tech Stack

**Client:** Git Actions

**Server:** Python, Pandas, OpenAI, SYS, Logging, google.auth
## Google Sheets Integration

This script authenticates and connects to a Google Sheets document, retrieves all records from the first worksheet (`sheet1`), and logs the operations.  It is intended for automated data retrieval processes.

## API Reference

```http
GET /api/google-sheet/records


| Parameter | Type     | Description                       
:-------------------------------------------- 
`api_key`   `string`    Required. Authentication key loaded from .env
:-------------------------------------------- 
`sheet_id`  `string`    Required. Spreadsheet ID loaded from .env

sheet = google_client_authentication(google_credentials, spreadsheet_id)
data = sheet.worksheet("Dataset")
values = data.get_all_values()

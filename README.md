# IA Enginer

Create and authenticate integrations using the OpenAI library and the Google Sheets API, performing data cleansing and querying through prompts that interpret strings, extract information, and integrate the data into a new table, in an automated process executed via GitHub Actions.

## Tech Stack

**Client:** Git Actions

**Server:** Python, Pandas, OpenAI, SYS, Logging, google.auth
## Google Sheets Integration
Connects to a Google Sheets document, retrieves records from the spreadsheet_id, and logs the operations for the automated data retrieval process.

### API Reference

```http
GET /api/google-sheet/records
````

| Parameter  | Type   | Description                                             |
|------------|--------|---------------------------------------------------------|
| `api_key`  | string | Required. Authentication key loaded from .env          |
| `sheet_id` | string | Required. Spreadsheet ID loaded from .env              |

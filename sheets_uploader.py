import gspread
import pandas as pd
import config
import os
import random

# Global variable to track active model
ACTIVE_MODEL_NAME = None

def set_active_model(model_name):
    """Set the active model name for table naming"""
    global ACTIVE_MODEL_NAME
    ACTIVE_MODEL_NAME = model_name

def upload_to_google_sheets(df, sheet_name):
    """
    Uploads data and converts it to a native 2024 Google Sheets Table.
    Includes dropdown chips (uncolored) and professional formatting.
    """
    try:
        # 1. Setup Table and Column Names
        model = ACTIVE_MODEL_NAME if ACTIVE_MODEL_NAME else 'claude'
        model = model.replace('-', '_').replace('.', '_')
        random_num = random.randint(100, 999)
        table_name = f"metta_table_1_{model}_{random_num}"
        
        mapping = {
            'Page/Section': 'REFERENCE',
            'Question': 'QUERY',
            'Status': 'STATUS',
            'Expected Answer': 'Expected Response',
            'RAG Response': 'Generated Response'
        }
        
        existing_cols = [c for c in mapping.keys() if c in df.columns]
        upload_df = df[existing_cols].rename(columns=mapping)

        # 2. Authenticate
        creds_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "gspread")
        service_account = os.path.join(creds_dir, "service_account.json")
        if not os.path.exists(service_account):
            return False

        gc = gspread.service_account(filename=service_account)
        sh = gc.open_by_key(config.GOOGLE_SHEET_ID)
        
        try:
            worksheet = sh.worksheet(sheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title=sheet_name, rows=100, cols=10)
        
        # 3. Write Data
        values = [upload_df.columns.values.tolist()] + upload_df.values.tolist()
        worksheet.update('A1', values)
        
        num_rows = len(upload_df) + 1
        num_cols = len(upload_df.columns)
        status_col_idx = upload_df.columns.get_loc("STATUS")

        # 4. API Requests
        requests = []

        # A. Create Native Table with Explicit Column Indices
        column_props = []
        for i, col_name in enumerate(upload_df.columns):
            column_props.append({
                "columnIndex": i,
                "columnName": col_name
            })

        requests.append({
            "addTable": {
                "table": {
                    "name": table_name,
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": 0, "endRowIndex": num_rows,
                        "startColumnIndex": 0, "endColumnIndex": num_cols
                    },
                    "columnProperties": column_props
                }
            }
        })

        # B. Convert STATUS column to Dropdown "Chips"
        requests.append({
            "setDataValidation": {
                "range": {
                    "sheetId": worksheet.id,
                    "startRowIndex": 1, "endRowIndex": num_rows,
                    "startColumnIndex": status_col_idx, "endColumnIndex": status_col_idx + 1
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [
                            {"userEnteredValue": "Fully Correct"},
                            {"userEnteredValue": "Partially correct"},
                            {"userEnteredValue": "Wrongly answered"},
                            {"userEnteredValue": "not answered"}
                        ]
                    },
                    "showCustomUi": True, "strict": True
                }
            }
        })

        # C. Header Styling (Dark Green background + White bold text)
        requests.append({
            "repeatCell": {
                "range": {"sheetId": worksheet.id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": num_cols},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.12, "green": 0.33, "blue": 0.25},
                        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
                        "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        })

        # D. Column Widths and Text Wrapping
        # Dimensions: REF(180), QUERY(300), STATUS(150), Expected(450), Generated(450)
        col_widths = [180, 300, 150, 450, 450]
        for i, width in enumerate(col_widths):
            if i < num_cols:
                requests.append({
                    "updateDimensionProperties": {
                        "range": {"sheetId": worksheet.id, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
                        "properties": {"pixelSize": width},
                        "fields": "pixelSize"
                    }
                })

        # Enable text wrapping for better readability
        requests.append({
            "repeatCell": {
                "range": {"sheetId": worksheet.id, "startRowIndex": 1, "endRowIndex": num_rows, "startColumnIndex": 0, "endColumnIndex": num_cols},
                "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
                "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)"
            }
        })

        # 5. Execute API Call
        sh.batch_update({"requests": requests})
        print(f"✓ Native Table created with dropdown chips and dark green header.")
        return True

    except Exception as e:
        print(f"\n⚠️ Google Sheets upload failed: {e}")
        return False
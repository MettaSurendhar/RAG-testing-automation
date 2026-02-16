# RAG EVALUATOR - QUICK START (5 Minutes)

## STEP 1: INSTALL (1 min)

Windows:
Double-click setup.bat

Mac/Linux:
pip install -r requirements.txt

## STEP 2: CONFIGURE (2 min)

Edit config.py:

1. Add AT LEAST ONE API key:
   GOOGLE_API_KEY = "your_key" ← Get free: https://makersuite.google.com/app/apikey
2. Add RAG credentials:
   AUTH_EMAIL = "your_email@company.com"
   AUTH_PASSWORD = "your_password"

## STEP 3: ADD DOCUMENTS (30 sec)

Put your PDF/DOCX files in the data/ folder

## STEP 4: RUN (1 min)

python main.py

Follow prompts:
→ Enter data path: [Press Enter]
→ Mode: 2 (Direct)
→ Files: [Press Enter for all]
→ Questions: 5 [or press Enter for 10]

## STEP 5: CHECK RESULTS (30 sec)

✓ Excel: rag_test_results.xlsx
✓ Google Sheets: (if configured)

DONE! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING:

❌ "No API key"
→ Add at least one API key to config.py

❌ "Authentication failed"  
 → Check RAG email/password in config.py

❌ "No files found"
→ Put .pdf or .docx files in data/ folder

❌ "Quota exceeded"
→ Script auto-switches to backup model

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## OPTIONAL: Google Sheets Setup

1. Create service account: console.cloud.google.com
2. Download JSON key
3. Save to: C:\Users\<You>\AppData\Roaming\gspread\service_account.json
4. Share your Sheet with service account email
5. Add Sheet ID to config.py

Skip this if Excel-only is fine!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIPS:
• Start with 5 questions to test
• Use Direct mode for individual files
• Use Comparison mode for entity comparisons
• Gemini is free and works well
• Excel output always works, Sheets optional

Need help? Check README.md for detailed guide.

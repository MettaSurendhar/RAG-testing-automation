# RAG System Evaluation Tool

Automated testing tool for evaluating RAG (Retrieval-Augmented Generation) systems. Generates questions from documents, queries your RAG system, and evaluates responses.

## Features

- ✅ Automatic question generation from PDF/DOCX files
- ✅ Direct mode: Test files individually
- ✅ Comparison mode: Compare across multiple documents
- ✅ Multiple AI models: Gemini, Mistral, Groq, OpenRouter (auto-fallback)
- ✅ Google Sheets integration with formatted tables
- ✅ Excel export with results

---

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **API Keys** for at least one AI provider:
   - Gemini (free tier available)
   - Mistral
   - Groq
   - OpenRouter
3. **Google Service Account** (optional, for Sheets integration)
4. **RAG System Access** (credentials for your RAG API)

---

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys

Edit `config.py` and add your credentials:

```python
# AI Model API Keys
GOOGLE_API_KEY = "your_gemini_api_key"
MISTRAL_API_KEY = "your_mistral_api_key"
GROQ_API_KEY = "your_groq_api_key"
OPENROUTER_API_KEY = "your_openrouter_api_key"

# RAG System Credentials
AUTH_URL = "your_rag_auth_url"
AUTH_EMAIL = "your_email"
AUTH_PASSWORD = "your_password"
RAG_QUERY_URL = "your_rag_query_url"
RAG_TEAM_ID = "your_team_id"

# S3 Path (if applicable)
S3_BASE_PATH = "s3://your-bucket/path/"

# Google Sheets (optional)
GOOGLE_SHEET_ID = "your_sheet_id"
USER_NAME = "YOUR_NAME"  # For table naming
```

### Step 3: Setup Google Sheets (Optional)

**For Google Sheets integration:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a Service Account
3. Download the JSON key file
4. Save as: `C:\Users\<YourName>\AppData\Roaming\gspread\service_account.json`
5. Share your Google Sheet with the service account email

**Skip this step if you only want Excel output.**

---

## 📂 Folder Structure

```
rag_evaluator/
├── main.py                 # Main script
├── generator.py            # Question generation
├── auth.py                 # RAG authentication
├── file_reader.py          # PDF/DOCX reader
├── sheets_uploader.py      # Google Sheets integration
├── config.py               # Configuration (EDIT THIS!)
├── requirements.txt        # Dependencies
└── data/                   # Put your documents here
    ├── document1.pdf
    └── document2.docx
```

---

## 🎯 How to Use

### 1. Add Your Documents

Place PDF or DOCX files in the `data/` folder (or any folder you choose)

### 2. Run the Script

```bash
python main.py
```

### 3. Follow the Prompts

**Example session:**

```
Enter directory path (default: ./data): [Press Enter]

Found 3 document(s):
  1. annual_report_2024.pdf
  2. product_guide.pdf
  3. technical_docs.docx

============================================================
Select Testing Mode:
  1. Comparison (compare across multiple files/entities)
  2. Direct (test individual files separately)
============================================================
Enter choice (1 or 2): 2

Select files to test:
  - Enter file numbers separated by commas (e.g., 1,2,3)
  - Or press Enter to use ALL files
Your selection: 1,2

Selected 2 file(s) for testing.

Enter number of questions to generate per file (default: 10): 5
Will generate 5 question(s) per file.

Authenticating...
Successfully authenticated with RAG system.
```

### 4. Check Results

- **Excel file**: `rag_test_results.xlsx` (always created)
- **Google Sheets**: Check your shared sheet (if configured)

---

## 📊 Understanding Results

### Status Values:

| Status                | Meaning                  | Color           |
| --------------------- | ------------------------ | --------------- |
| **Fully Correct**     | RAG answered correctly   | 🟢 Light Green  |
| **Partially correct** | Partially correct answer | 🟡 Light Yellow |
| **Wrongly answered**  | Incorrect answer         | 🔴 Light Red    |
| **not answered**      | RAG couldn't answer      | 🟤 Brown        |

### Columns:

- **REFERENCE**: Page/section where info is found
- **QUERY**: Generated question
- **STATUS**: Evaluation result (with dropdown)
- **Expected Response**: Gold standard answer
- **Generated Response**: RAG system's actual response

---

## 🔧 Troubleshooting

### "No API Key" or "Quota Exceeded"

✅ Script auto-switches between models (Gemini → Mistral → Groq → OpenRouter)
✅ Make sure at least ONE API key is valid

### "Google Sheets credentials not found"

✅ Check: `C:\Users\<YourName>\AppData\Roaming\gspread\service_account.json`
✅ Or skip Sheets - Excel always works

### "RAG Query Failed"

✅ Check RAG credentials in `config.py`
✅ Verify RAG system is accessible

### "No files found"

✅ Make sure files are `.pdf` or `.docx`
✅ Check the data directory path

---

## 🎨 Customization

### Change Default Settings

Edit `config.py`:

- Number of questions: Default is 10 (you can change via prompt)
- User name: For table naming in Sheets
- Model priority: Edit in `generator.py`

### Add More File Types

Edit `file_reader.py` to support additional formats

---

## 🤝 Sharing with Team

**Option 1: ZIP File** (Simple)

1. Zip the entire folder
2. Share via email/Teams/Slack
3. Colleagues extract and follow setup

**Option 2: Git Repository** (Recommended)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

Share repo link with team

**Option 3: Internal Wiki**

- Upload to company wiki/confluence
- Add setup guide + video walkthrough

---

## 📞 Support

**Common Questions:**

- Q: Which AI model is best?
  - A: Gemini (best quality) → Mistral → Groq (fastest) → OpenRouter

- Q: Can I run without Google Sheets?
  - A: Yes! Excel output always works

- Q: How do I update API keys?
  - A: Edit `config.py` and save

---

## 📝 Notes for Colleagues

1. **API Keys**: Get your own free keys from:
   - Gemini: https://makersuite.google.com/app/apikey
   - Groq: https://console.groq.com/
   - Mistral: https://console.mistral.ai/

2. **RAG Credentials**: Use the same credentials you use for the RAG system

3. **First Run**: Start with 1-2 questions to test everything works

4. **File Format**: PDFs and DOCX only

---

Made with ❤️ for better RAG evaluation

import os

# ==========================================
# USER CONFIGURATION - EDIT THIS FILE
# ==========================================

# Your name (used for table naming in Google Sheets)
USER_NAME = "METTA"  # Change to your name

# ==========================================
# AI MODEL API KEYS
# ==========================================
# Get free API keys from:
# - Gemini: https://makersuite.google.com/app/apikey
# - Groq: https://console.groq.com/
# - Mistral: https://console.mistral.ai/
# - OpenRouter: https://openrouter.ai/

GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
MISTRAL_API_KEY = "YOUR_MISTRAL_API_KEY_HERE" 
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"

# ==========================================
# RAG SYSTEM CREDENTIALS
# ==========================================
# Use the same credentials you use to access the RAG system

AUTH_URL = "rag_system_authentication_url"
AUTH_EMAIL = "your_email@company.com"  # Your RAG system email
AUTH_PASSWORD = "your_password"  # Your RAG system password

# RAG System Query Endpoint
RAG_QUERY_URL = "rag_system_query_url"
RAG_TEAM_ID = "rag_team_id"

# ==========================================
# S3 CONFIGURATION (if applicable)
# ==========================================
# The base S3 path where your documents are stored
# Local file "report.pdf" will map to S3_BASE_PATH + "report.pdf"

S3_BASE_PATH = "s3://"

# ==========================================
# LOCAL SETTINGS
# ==========================================
# Default directory to scan for documents
DEFAULT_INPUT_DIR = "./data"

# ==========================================
# GOOGLE SHEETS INTEGRATION (Optional)
# ==========================================
# Leave blank if you don't want Google Sheets integration
# Get your Google Sheet ID from the URL:
# https://docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit

GOOGLE_SHEET_ID = "YOUR_GOOGLE_SHEET_ID_HERE"

# ==========================================
# NOTES
# ==========================================
# - At least ONE AI API key must be valid
# - Script auto-switches between models if one fails
# - Google Sheets is optional - Excel always works
# - RAG credentials must match your system access
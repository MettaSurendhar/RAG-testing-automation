import google.generativeai as genai
import requests
import config
import json
import time
import warnings

# Suppress the annoying deprecation warning from google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

# Configure Gemini
genai.configure(api_key=config.GOOGLE_API_KEY)

# Model configurations
MODEL_NAME = "gemini-2.0-flash-lite-001"
MISTRAL_MODEL = "mistral-large-latest"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast and good quality
OPENROUTER_MODEL = "google/gemini-2.0-flash-lite-001:free"

# Global variable to track which provider is working
ACTIVE_PROVIDER = None  # Will be set to "gemini", "mistral", "groq", or "openrouter"

def test_gemini_availability():
    """Test if Gemini is available and has quota."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # Try a minimal request to check quota
        response = model.generate_content("Say OK")
        return True
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print("  [Init] Gemini quota exhausted, switching to fallback...")
            return False
        print(f"  [Init] Gemini error: {e}")
        return False

def determine_active_provider():
    """Determine which provider to use for the entire session."""
    global ACTIVE_PROVIDER
    
    if ACTIVE_PROVIDER is not None:
        return ACTIVE_PROVIDER
    
    print("  [Init] Testing model availability...")
    
    # Import here to avoid circular import
    import sheets_uploader
    
    # 1. Test Gemini first (Best quality)
    if test_gemini_availability():
        print("  [Init] Using Gemini for this session.")
        ACTIVE_PROVIDER = "gemini"
        sheets_uploader.set_active_model("gemini-2.0-flash")
        return ACTIVE_PROVIDER
    
    # 2. Test Mistral (2nd best - solid reasoning)
    if config.MISTRAL_API_KEY:
        print("  [Init] Testing Mistral...")
        test_prompt = "Say OK"
        result = generate_with_mistral(test_prompt)
        if result:
            print("  [Init] Using Mistral for this session.")
            ACTIVE_PROVIDER = "mistral"
            sheets_uploader.set_active_model("mistral-large")
            return ACTIVE_PROVIDER
    
    # 3. Test Groq (3rd - very fast but less accurate)
    if config.GROQ_API_KEY:
        print("  [Init] Testing Groq...")
        test_prompt = "Say OK"
        result = generate_with_groq(test_prompt)
        if result:
            print("  [Init] Using Groq for this session.")
            ACTIVE_PROVIDER = "groq"
            sheets_uploader.set_active_model("llama-3.3-70b")
            return ACTIVE_PROVIDER
    
    # 4. Test OpenRouter (Last resort - free models)
    if config.OPENROUTER_API_KEY:
        print("  [Init] Testing OpenRouter...")
        test_prompt = "Say OK"
        result = generate_with_openrouter(test_prompt)
        if result:
            print("  [Init] Using OpenRouter for this session.")
            ACTIVE_PROVIDER = "openrouter"
            sheets_uploader.set_active_model("gemini-free")
            return ACTIVE_PROVIDER
    
    # Fallback to Gemini even if quota limited (will error later)
    print("  [Init] Warning: No working providers found. Defaulting to Gemini.")
    ACTIVE_PROVIDER = "gemini"
    sheets_uploader.set_active_model("gemini-2.0-flash")
    return ACTIVE_PROVIDER

def generate_with_openrouter(prompt, is_json=False):
    """
    Fallback function to generate content using OpenRouter API.
    """
    if not config.OPENROUTER_API_KEY:
        print("  [OpenRouter] No API Key found.")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://rag-evaluator.local", # OpenRouter requirement
        "X-Title": "RAG Evaluator Script"
    }
    
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.2
    }
    
    if is_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"  [OpenRouter Error] {e}")
        if hasattr(e, 'response') and e.response:
             print(f"  [OpenRouter Response] {e.response.text}")
        return None

def generate_with_mistral(prompt, is_json=False):
    """
    Fallback function to generate content using Mistral API.
    """
    if not config.MISTRAL_API_KEY:
        print("  [Mistral] No API Key found.")
        return None

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": MISTRAL_MODEL,
        "messages": messages,
        "temperature": 0.2
    }
    
    if is_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"  [Mistral Error] {e}")
        return None

def generate_with_groq(prompt, is_json=False):
    """
    Generate content using Groq API (very fast inference).
    """
    if not config.GROQ_API_KEY:
        print("  [Groq] No API Key found.")
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": prompt}]
    
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.2
    }
    
    if is_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"  [Groq Error] {e}")
        return None

def generate_test_cases(file_name, file_text, num_questions=10):
    """
    Sends file text to LLM and asks for JSON formatted Q&A pairs.
    """
    # Determine which provider to use
    provider = determine_active_provider()
    
    # Drastically reduce context to avoid hitting TPM (Tokens Per Minute) limits on Free Tier
    # 40,000 chars is roughly 10k tokens, which is safer.
    truncated_text = file_text[:40000]
    
    prompt = f"""
    You are an expert QA generator for RAG systems.
    
    I have a document named "{file_name}".
    Generate ONLY {num_questions} high-quality test questions to EFFECTIVELY STRESS-TEST a RAG system.
    
    CRITICAL REQUIREMENTS:
    
    1. **Include Document-Specific Keywords**: Since the RAG system contains MULTIPLE documents, questions MUST include:
       - Specific entities, names, or terms from THIS document (e.g., company names, product names, dates, metrics)
       - Context clues that help the RAG system identify the correct source document
       - Example: Instead of "What was the revenue?", ask "What was Zensar's revenue in Q1 FY24?"
    
    2. **Question Type Mix** (to thoroughly test the system):
       - **Straightforward Questions (30%)**: Direct facts clearly stated in the document
       - **Inference Questions (30%)**: Require reasoning or combining multiple pieces of information
       - **Edge Cases (20%)**: 
         * Questions about specific details that might be easy to miss
         * Questions requiring precise numeric values
         * Questions about comparisons or trends
       - **Challenging Questions (20%)**: 
         * Questions that are SLIGHTLY outside the document scope (but related)
         * Questions that require context the document might not fully provide
         * These should result in "Not Answered" or partial answers from the RAG
    
    3. **Diversity**: Ensure questions cover different sections/topics within the document
    
    For each question, provide:
    1. The Question itself (with appropriate keywords/context)
    2. The Expected Answer (Gold Standard) - if the info is NOT in the document, say "Not in document"
    3. The Page Number or Section Name (if available)
    4. The exact Quote from the text (if available)
    
    Output MUST be valid JSON. Format:
    [
        {{
            "question": "...",
            "expected_answer": "...",
            "metadata": {{
                "page": "...",
                "section": "...",
                "quote": "..."
            }}
        }}
    ]
    
    Document Text:
    {truncated_text} 
    """ 
    # Truncate to 300k chars just to be safe, though Flash supports 1M.

    # Use the active provider directly
    if provider == "gemini":
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:-3]
            elif text.startswith("```"): text = text[3:-3]
            return json.loads(text)
        except Exception as e:
            print(f"  [Gemini Error] {e}")
            return []
    
    elif provider == "mistral":
        mistral_text = generate_with_mistral(prompt, is_json=True)
        if mistral_text:
            try:
                return json.loads(mistral_text)
            except json.JSONDecodeError:
                print("  [Mistral] Failed to decode JSON.")
                return []
        return []
    
    elif provider == "groq":
        groq_text = generate_with_groq(prompt, is_json=True)
        if groq_text:
            try:
                return json.loads(groq_text)
            except json.JSONDecodeError:
                print("  [Groq] Failed to decode JSON.")
                return []
        return []
    
    elif provider == "openrouter":
        or_text = generate_with_openrouter(prompt, is_json=True)
        if or_text:
            try:
                return json.loads(or_text)
            except json.JSONDecodeError:
                print("  [OpenRouter] Failed to decode JSON.")
                return []
        return []
    
    print("  [Error] No provider available.")
    return []

def generate_comparison_test_cases(files_data, num_questions=10):
    """
    Generate comparison questions across multiple documents.
    files_data: list of dicts with keys 'filename', 'text', 's3_uri'
    """
    provider = determine_active_provider()
    
    # Build a combined context with file summaries
    file_summaries = []
    for file_info in files_data:
        truncated = file_info['text'][:15000]  # Shorter per-file to fit multiple
        file_summaries.append(f"--- Document: {file_info['filename']} ---\n{truncated}\n")
    
    combined_text = "\n".join(file_summaries)
    
    prompt = f"""
    You are an expert QA generator for RAG systems.
    
    You have {len(files_data)} documents. Generate {num_questions} COMPARISON questions to test a RAG system's ability to compare information across documents.
    
    Documents:
    {combined_text}
    
    CRITICAL REQUIREMENTS:
    
    1. **Comparison Questions Only**: Every question MUST compare or relate information from MULTIPLE documents/entities.
       - Example: "Compare [Entity A]'s revenue in Q1 vs [Entity B]'s revenue in Q1"
       - Example: "Which company had higher growth rate?"
       - Example: "What is the difference between [Entity A] and [Entity B] in terms of [metric]?"
    
    2. **Diverse Question Types**:
       - Direct comparisons (30%): "What was the difference between X and Y?"
       - Ranking questions (30%): "Which entity had the highest/lowest [metric]?"
       - Trend comparisons (20%): "Compare the trends of X vs Y"
       - Challenging cross-doc queries (20%): Require synthesizing info that might not be directly comparable
    
    3. **Clear Entity Names**: Include specific entity names (companies, products, time periods) from the documents
    
    For each question, provide:
    1. The Question (must reference multiple entities/documents)
    2. The Expected Answer - compare/synthesize from all relevant documents
    3. Metadata with doc references and page/section info where the comparison data is found
    
    Output MUST be valid JSON:
    [
        {{
            "question": "...",
            "expected_answer": "...",
            "metadata": {{
                "documents": ["file1.pdf", "file2.pdf"],
                "comparison_type": "numeric|qualitative|ranking",
                "page": "page numbers from source docs (if available)",
                "section": "section names from source docs (if available)",
                "quote": "..."
            }}
        }}
    ]
    """
    
    # Use active provider
    if provider == "gemini":
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:-3]
            elif text.startswith("```"): text = text[3:-3]
            return json.loads(text)
        except Exception as e:
            print(f"  [Gemini Error] {e}")
            return []
    
    elif provider == "mistral":
        mistral_text = generate_with_mistral(prompt, is_json=True)
        if mistral_text:
            try:
                return json.loads(mistral_text)
            except json.JSONDecodeError:
                print("  [Mistral] Failed to decode JSON.")
                return []
        return []
    
    elif provider == "groq":
        groq_text = generate_with_groq(prompt, is_json=True)
        if groq_text:
            try:
                return json.loads(groq_text)
            except json.JSONDecodeError:
                print("  [Groq] Failed to decode JSON.")
                return []
        return []
    
    elif provider == "openrouter":
        or_text = generate_with_openrouter(prompt, is_json=True)
        if or_text:
            try:
                return json.loads(or_text)
            except json.JSONDecodeError:
                print("  [OpenRouter] Failed to decode JSON.")
                return []
        return []
    
    print("  [Error] No provider available for comparison questions.")
    return []

def evaluate_rag_response(question, expected_answer, rag_response):
    """
    Evaluates the RAG response against the expected answer using an LLM.
    Returns a status string: "Fully Correct", "Partially Correct", "Wrongly Answered", or "Not Answered".
    """
    # Use the same provider as question generation
    provider = ACTIVE_PROVIDER or determine_active_provider()
    
    prompt = f"""
    You are an expert judge for a RAG system.
    
    Question: {question}
    
    Expected Answer (Gold Standard): {expected_answer}
    
    Actual RAG Response: {rag_response}
    
    Compare the Actual RAG Response with the Expected Answer.
    Determine the accuracy status based on these criteria:
    - "Fully Correct": The response contains the correct answer and is accurate. It may be phrased differently.
    - "Partially correct": The response contains some correct information but is incomplete or contains mix of correct and incorrect info.
    - "Wrongly answered": The response is incorrect or provides irrelevant information.
    - "not answered": The response states it doesn't know, or is empty/null.
    
    Output ONLY the status string from the list above. Do not output anything else.
    """

    # Helper function to parse evaluation result
    def parse_status(text):
        if not text: return None
        text = text.strip().lower()
        if "fully correct" in text: return "Fully Correct"
        if "partially correct" in text: return "Partially correct"
        if "wrong" in text: return "Wrongly answered"
        if "not answered" in text: return "not answered"
        return None

    # Use the active provider
    if provider == "gemini":
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            status = parse_status(response.text)
            if status: return status
        except Exception as e:
            print(f"  [Gemini Error] {e}")
            return "Error"
    
    elif provider == "mistral":
        mistral_text = generate_with_mistral(prompt)
        status = parse_status(mistral_text)
        if status: return status
        return "Error"

    elif provider == "groq":
        groq_text = generate_with_groq(prompt)
        status = parse_status(groq_text)
        if status: return status
        return "Error"

    elif provider == "openrouter":
        or_text = generate_with_openrouter(prompt)
        status = parse_status(or_text)
        if status: return status
        return "Error"
    
    return "Error (No Provider)"

if __name__ == "__main__":
    # Test stub
    pass
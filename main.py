import os
import pandas as pd
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor

# Import our modules
import config
import auth
import file_reader
import generator
import sheets_uploader

def query_rag_system(question, s3_uri, token):
    """
    Queries the RAG API.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Doc-Ai-Team-Id": config.RAG_TEAM_ID,
        "Content-Type": "application/json"
    }
    
    body = {
        "userQuery": question,
        "documentUris": [s3_uri]
    }
    
    try:
        response = requests.post(config.RAG_QUERY_URL, json=body, headers=headers)
        response.raise_for_status()
        return response.json() # Adjust based on actual response structure
    except Exception as e:
        print(f"RAG Query Failed: {e}")
        return {"error": str(e)}

def process_file(file_path, input_dir, token, num_questions=10):
    filename = os.path.basename(file_path)
    print(f"Processing: {filename}...")
    
    # 1. Read File
    text = file_reader.read_file(file_path)
    if not text:
        return []
    
    # 2. Generate Questions (The "Teacher")
    print(f"  - Generating questions for {filename}...")
    qa_pairs = generator.generate_test_cases(filename, text, num_questions=num_questions)
    print(f"  - Generated {len(qa_pairs)} questions.")
    
    # 3. Map to S3
    # Assumption: local file "X.pdf" -> BASE_S3 + "X.pdf"
    s3_uri = f"{config.S3_BASE_PATH}{filename}"
    
    results = []
    
    # 4. Test RAG System (The "Student")
    for i, item in enumerate(qa_pairs):
        question = item.get("question")
        expected = item.get("expected_answer")
        meta = item.get("metadata", {})
        
        print(f"  - Q{i+1}: {question[:50]}...")
        
        # Query RAG if we have a token
        # Query RAG if we have a token
        if token:
            rag_response_raw = query_rag_system(question, s3_uri, token)
            # Assuming rag_response_raw is a dict or string. 
            # We need to extract the actual answer text.
            # Adjust this parsing logic based on actual API response structure!
            # Extract only the 'summary' field from the RAG response
            if isinstance(rag_response_raw, dict):
                rag_actual = rag_response_raw.get('summary', str(rag_response_raw))
            else:
                rag_actual = str(rag_response_raw)
        else:
            rag_actual = "Skipped (No Token)"
        
        
        # Evaluate
        if token:
            print(f"  - Evaluating Q{i+1}...")
            status = generator.evaluate_rag_response(question, expected, rag_actual)
        else:
            status = "Not Answered"

        # Format Page/Section
        page = meta.get('page')
        section = meta.get('section')
        location = ""
        if page and str(page).lower() != 'na':
            location += f"Page {page}"
        if section and str(section).lower() != 'na':
            if location: location += " / "
            location += section
        
        results.append({
            "Filename": filename,
            "S3_URI": s3_uri,
            "Question": question,
            "Expected Answer": expected,
            "RAG Response": rag_actual,
            "Status": status,
            "Page/Section": location
        })
        
        # Polite delay to avoid hammering the dev API too hard?
        time.sleep(0.5)
        
    return results

def process_comparison_files(selected_files, input_dir, token, num_questions=10):
    """Process multiple files together for comparison questions."""
    print(f"\n=== Comparison Mode: Processing {len(selected_files)} files together ===\n")
    
    # Read all files
    files_data = []
    for file_path in selected_files:
        filename = os.path.basename(file_path)
        print(f"Reading: {filename}...")
        text = file_reader.read_file(file_path)
        if text:
            s3_uri = f"{config.S3_BASE_PATH}{filename}"
            files_data.append({
                'filename': filename,
                'text': text,
                's3_uri': s3_uri,
                'path': file_path
            })
    
    if len(files_data) < 2:
        print("Error: Comparison mode requires at least 2 files.")
        return []
    
    # Generate comparison questions
    print(f"\n  - Generating comparison questions across {len(files_data)} files...")
    qa_pairs = generator.generate_comparison_test_cases(files_data, num_questions=num_questions)
    print(f"  - Generated {len(qa_pairs)} comparison questions.\n")
    
    # Process each comparison question
    results = []
    for i, qa in enumerate(qa_pairs):
        question = qa['question']
        expected = qa['expected_answer']
        meta = qa.get('metadata', {})
        
        print(f"  - Q{i+1}: {question[:60]}...")
        
        # For comparison queries, use ALL document URIs
        all_uris = [f['s3_uri'] for f in files_data]
        
        # Query RAG with all documents
        if token:
            rag_response_raw = query_rag_system_multi(question, all_uris, token)
            
            if isinstance(rag_response_raw, dict):
                rag_actual = rag_response_raw.get('summary', str(rag_response_raw))
            else:
                rag_actual = str(rag_response_raw)
        else:
            rag_actual = "Skipped (No Token)"
        
        # Evaluate
        if token:
            print(f"  - Evaluating Q{i+1}...")
            status = generator.evaluate_rag_response(question, expected, rag_actual)
        else:
            status = "Not Answered"
        
        # Format metadata
        docs_list = meta.get('documents', [f['filename'] for f in files_data])
        comparison_type = meta.get('comparison_type', '')
        
        page = meta.get('page', '')
        section = meta.get('section', '')
        location = ""

        def normalize(val):
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val if v)
            return str(val).strip()

        page = normalize(page)
        section = normalize(section)

        if page and page.lower() not in ['', 'n/a', 'na', 'unknown']:
            location = f"Page {page}"

        if section and section.lower() not in ['', 'n/a', 'na', 'unknown']:
            if location:
                location += f", {section}"
            else:
                location = section

        results.append({
            'Filename': ', '.join(docs_list),
            'S3_URI': ', '.join(all_uris),
            'Question': question,
            'Expected Answer': expected,
            'RAG Response': rag_actual,
            'Status': status,
            'Page/Section': location,
            'Comparison Type': comparison_type
        })
        
    return results

def query_rag_system_multi(question, s3_uris, token):
    """Query RAG system with multiple document URIs for comparison."""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Doc-Ai-Team-Id": config.RAG_TEAM_ID,
        "Content-Type": "application/json"
    }
    
    body = {
        "userQuery": question,
        "documentUris": s3_uris  # Multiple URIs for comparison
    }
    
    try:
        response = requests.post(config.RAG_QUERY_URL, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"RAG Query Failed: {e}")
        return {"error": str(e)}

def main():
    input_dir = input(f"Enter directory path containing files (default: {config.DEFAULT_INPUT_DIR}): ").strip()
    if not input_dir:
        input_dir = config.DEFAULT_INPUT_DIR
        
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} not found. Creating it...")
        os.makedirs(input_dir)
        print(f"Please put your PDF/DOCX files in {input_dir} and run again.")
        return

    # List available files
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.pdf', '.docx'))]
    if not files:
        print(f"No PDF/DOCX files found in {input_dir}")
        return
    
    print(f"\nFound {len(files)} document(s):")
    for idx, f in enumerate(files, 1):
        print(f"  {idx}. {f}")
    
    # Mode selection
    print("\n" + "="*60)
    print("Select Testing Mode:")
    print("  1. Comparison (compare across multiple files/entities)")
    print("  2. Direct (test individual files separately)")
    print("="*60)
    
    mode = input("Enter choice (1 or 2): ").strip()
    
    # File selection
    print("\nSelect files to test:")
    print("  - Enter file numbers separated by commas (e.g., 1,2,3)")
    print("  - Or press Enter to use ALL files")
    
    selection = input("Your selection: ").strip()
    
    if not selection:
        selected_indices = list(range(len(files)))
    else:
        try:
            selected_indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_indices = [i for i in selected_indices if 0 <= i < len(files)]
        except:
            print("Invalid selection. Using all files.")
            selected_indices = list(range(len(files)))
    
    selected_files = [os.path.join(input_dir, files[i]) for i in selected_indices]
    
    if not selected_files:
        print("No files selected.")
        return
    
    print(f"\nSelected {len(selected_files)} file(s) for testing.\n")
    
    # Ask for number of questions
    num_questions_input = input("Enter number of questions to generate per file (default: 10): ").strip()
    if num_questions_input:
        try:
            num_questions = int(num_questions_input)
            if num_questions < 1:
                print("Invalid number. Using default: 10")
                num_questions = 10
        except ValueError:
            print("Invalid input. Using default: 10")
            num_questions = 10
    else:
        num_questions = 10
    
    print(f"Will generate {num_questions} question(s) per file.\n")

    # Authentication
    print("Authenticating...")
    token = auth.login_and_get_token()
    if not token:
        print("Warning: Could not obtain token. RAG queries will be skipped.")
        return
    
    all_results = []
    
    # Execute based on mode
    if mode == "1":
        # Comparison mode
        all_results = process_comparison_files(selected_files, input_dir, token, num_questions)
        
        if all_results:
            # Create a combined sheet name: file1 vs file2...
            base_names = [os.path.basename(f) for f in selected_files]
            sheet_title = " vs ".join(base_names)
            # Limit sheet title length (Google Sheets limit is 100)
            if len(sheet_title) > 90: sheet_title = sheet_title[:87] + "..."
            
            sheets_uploader.upload_to_google_sheets(pd.DataFrame(all_results), sheet_title)
    else:
        # Direct mode (existing behavior)
        print("\n=== Direct Mode: Processing files individually ===\n")
        for file_path in selected_files:
            file_results = process_file(file_path, input_dir, token, num_questions)
            if file_results:
                all_results.extend(file_results)
                # Sync each file to its own sheet
                sheets_uploader.upload_to_google_sheets(pd.DataFrame(file_results), os.path.basename(file_path))
    
    # Save results to local Excel (Combined)
    if all_results:
        df = pd.DataFrame(all_results)
        output_file = "rag_test_results.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\nDone! Results saved to {output_file}")
    else:
        print("\nNo results generated.")

if __name__ == "__main__":
    main()
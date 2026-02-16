import requests
import config

def login_and_get_token():
    """
    Logs in to the RAG system and returns the Bearer token.
    """
    payload = {
        "email": config.AUTH_EMAIL,
        "password": config.AUTH_PASSWORD
    }
    print(payload)
    
    try:
        response = requests.post(config.AUTH_URL, json=payload)
        response.raise_for_status()
        
        data = response.json()
        token = data.get("token")
        
        if not token:
            print(f"Error: Login successful but no token returned. Response: {data}")
            return None
            
        print("Successfully authenticated with RAG system.")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response Body: {e.response.text}")
        return None

if __name__ == "__main__":
    # Quick test
    t = login_and_get_token()
    print(f"Token received: {t[:20]}..." if t else "No token")

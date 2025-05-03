def get_translation(text, api_key):
    import requests

    url = "https://api.sarvam.com/translate"  # Replace with the actual Sarvam API endpoint
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "target_language": "en"  # Specify the target language as needed
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()  # Return the JSON response from the API
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

def manage_response(api_response):
    # Process the API response and return structured data
    if 'translated_text' in api_response:
        return api_response['translated_text']
    else:
        raise ValueError("Invalid response format from Sarvam API")
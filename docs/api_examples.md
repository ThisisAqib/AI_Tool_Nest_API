# AI Tool Nest API - Code Examples

This document provides practical examples for interacting with the AI Tool Nest API endpoints. Each example is standalone and can be run directly.

## Authentication

### Health Check
Check the API's health status.

**Rate Limit:** 5 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/health'
response = requests.get(url)
print(response.json())

# Example Response:
# {
#     'status': 'healthy'
# }
```

### User Registration
Register a new user account.

**Rate Limit:** 5 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/auth/register'
payload = {
    'username': 'your_username',
    'email': 'your_email@example.com',
    'password': 'your_secure_password'
}

response = requests.post(url, json=payload)
print(response.json())

# Example Response:
# {
#     'email': 'your_email@example.com',
#     'username': 'your_username',
#     'id': 5,
#     'is_active': True
# }
```

### User Login
Get an access token for authentication.

**Rate Limit:** 5 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/auth/login'
payload = {
    'username': 'your_username',
    'password': 'your_secure_password'
}

response = requests.post(url, json=payload)
print(response.json())

# Example Response:
# {
#     'access_token': 'your-jwt-token',
#     'token_type': 'bearer'
# }

# Store the access token for later use
access_token = response.json()['access_token']
```

## API Key Management

### Create API Key
Generate a new API key for accessing protected endpoints.

**Rate Limit:** 2 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/api-keys'
headers = {
    'Authorization': f'Bearer {access_token}'  # Use access_token from login
}
payload = {
    'name': 'my_api_key'
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

# Example Response:
# {
#     'id': 2,
#     'name': 'my_api_key',
#     'key_prefix': '_66EFEuo',
#     'status': 'active',
#     'created_at': '2025-04-24T10:25:57.538980',
#     'last_used_at': None,
#     'revoked_at': None,
#     'api_key': '_66EFEuoiT-hqBx43y0bGKTcDUnHQL107MSkZ9k91A4'
# }

# Store the API key for later use
api_key = response.json()['api_key']
```

### List API Keys
View all your active API keys.

**Rate Limit:** 10 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/api-keys'
headers = {
    'Authorization': f'Bearer {access_token}'  # Use access_token from login
}

response = requests.get(url, headers=headers)
api_keys = response.json()['api_keys']

# Print API keys in a readable format
print(f"Total API keys: {len(api_keys)}")
for key in api_keys:
    print(
        f"ID: {key['id']} || "
        f"Name: {key['name']} || "
        f"Key Prefix: {key['key_prefix']} || "
        f"Status: {key['status']} || "
        f"Created at: {key['created_at']} || "
        f"Last Used at: {key['last_used_at']}"
    )

# Example Response:
# Total API keys: 1
# ID: 16 || Name: my_api_key || Key Prefix: Jtd4NLva || Status: active || Created at: 2025-05-05T11:15:18.735071 || Last Used at: None
```

### Get API Key Usage
Check usage statistics for a specific API key.

**Rate Limit:** 10 requests per minute

```python
import requests

api_key_id = 123  # Replace with your API key ID
url = f'http://localhost:8002/ai-tool-nest-api/v1/endpoints/api-keys/{api_key_id}/usage'
headers = {
    'Authorization': f'Bearer {access_token}'  # Use access_token from login
}

response = requests.get(url, headers=headers)
print(response.json())

# Example Response:
# {
#     'total_requests': 0,
#     'successful_requests': 0,
#     'failed_requests': 0,
#     'average_response_time': 0.0,
#     'usage_by_endpoint': {},
#     'recent_usage': []
# }
```

### Delete API Key
Revoke an existing API key.

**Rate Limit:** 2 requests per minute

```python
import requests

api_key_id = 123  # Replace with the API key ID you want to delete
url = f'http://localhost:8002/ai-tool-nest-api/v1/endpoints/api-keys/{api_key_id}'
headers = {
    'Authorization': f'Bearer {access_token}'  # Use access_token from login
}

response = requests.delete(url, headers=headers)
print(response.json())

# Example Response:
# {
#     'id': 16,
#     'name': 'my_api_key',
#     'key_prefix': 'Jtd4NLva',
#     'status': 'revoked',
#     'created_at': '2025-05-05T11:15:18.735071',
#     'last_used_at': '2025-05-05T11:18:55.319380',
#     'revoked_at': '2025-05-05T11:20:34.740395'
# }
```

## AI Tools

### Text Summarization
Generate a concise summary of provided text.

**Rate Limit:** 5 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/ai-tools/summarize'
headers = {
    'X-API-Key': api_key  # Use api_key from the create API key response
}
payload = {
    'text': '''A Python developer is needed to join an AI project focusing on building an intelligent 
    chatbot and AI agent. The ideal candidate should have strong Python proficiency, experience 
    integrating AI/ML services and APIs, and good communication skills in English. Experience in 
    Python web frameworks, vector databases, SQL databases, asynchronous programming, and Docker 
    is also required.''',
    'include_keywords': True
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

# Example Response:
# {
#     'summary': 'A Python developer is sought to join an AI project focused on developing an intelligent chatbot and AI agent. The role requires strong Python skills, experience integrating AI/ML services and APIs, and good English communication abilities. Proficiency in Python web frameworks, vector databases, SQL databases, asynchronous programming, and Docker is also necessary.',
#     'keywords': None
# }
```

### Text Paraphrasing
Rewrite text in different styles.

**Rate Limit:** 5 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/ai-tools/paraphrase'
headers = {
    'X-API-Key': api_key  # Use api_key from the create API key response
}
payload = {
    'text': '''A Python developer is needed to join an AI project focusing on building an intelligent 
    chatbot and AI agent. The ideal candidate should have strong Python proficiency, experience 
    integrating AI/ML services and APIs, and good communication skills in English.''',
    'style': 'formal',
    'intensity': 'high',
    'length_option': 'longer'
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())

# Example Response:
# {
#     'paraphrased_text': 'We are currently seeking a Python developer to collaborate on an artificial intelligence initiative centered around the development of a sophisticated chatbot and AI agent. The successful candidate must demonstrate exceptional proficiency in Python programming, possess substantial experience in the integration of artificial intelligence and machine learning services and APIs, and exhibit excellent communication capabilities in the English language.'
# }
```

### Image to Text

#### Using Image URL
Convert an image to text using its URL.

**Rate Limit:** 5 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/ai-tools/image-to-text'
headers = {
    'X-API-Key': api_key  # Use api_key from the create API key response
}
payload = {
    'image_url': 'https://example.com/path/to/your/image.jpg',
    'mode': 'ocr',
    'detail_level': 'standard'
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

#### Using Image File
Convert an image to text by uploading a file.

**Rate Limit:** 5 requests per minute

```python
import requests

url = 'http://localhost:8002/ai-tool-nest-api/v1/endpoints/ai-tools/image-to-text'
headers = {
    'X-API-Key': api_key  # Use api_key from the create API key response
}
payload = {
    'mode': 'description',
    'detail_level': 'standard'
}

file_path = 'path/to/your/image.jpg'  # Replace with your image path
with open(file_path, 'rb') as file:
    files = {'image_file': (file_path, file, 'image/jpeg')}
    response = requests.post(url, files=files, headers=headers, data=payload)
    print(response.json())
```

## Error Handling Example

Here's how to handle errors when making API requests:

```python
import requests

try:
    # Make your API request here
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raises an error for bad status codes
    result = response.json()
    print("Success:", result)
    
except requests.exceptions.RequestException as e:
    if hasattr(e.response, 'json'):
        error_detail = e.response.json()
        print(f"API Error: {error_detail}")
    else:
        print(f"Request Error: {str(e)}")
        
except Exception as e:
    print(f"Unexpected Error: {str(e)}")
```

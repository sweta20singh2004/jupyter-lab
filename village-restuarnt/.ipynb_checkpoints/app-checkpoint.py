import requests

# API Key
api_key = "9aNmlnpUIRRax9ldXhk0LRT_L5ZODAlZJTHAOj3xBtcRM8OXwuMQNI7eAU6yRu52q6o97PTXwTFADUU39tWbISCAmoudmGuuK0fX11UfaLejCG_JPL7UvP5Z5bJWZ3Yx"

# API Endpoint
url = "https://api.yelp.com/v3/businvillage-the-soul-of-india-hicksvillencisco"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {api_key}"
}

# Make the GET request
response = requests.get(url, headers=headers)

# Check the response
if response.status_code == 200:
    print(response.json())  # Prints restaurant details
else:
    print(f"Error: {response.status_code}, {response.json()}")

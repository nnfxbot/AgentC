import requests
import os
import json

def search(query):
    api_url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "X-Subscription-Token": os.getenv("BRAVE_API_KEY")
    }
    params = {
        "q": query,
        "count":3
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data["web"])
        else:
            print("An error occurred. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

def handle_function_call(function_call):
    args = json.loads(function_call.arguments)
    if function_call.name == "search":
        return search(**args)
    else:
        return f'Error calling {function_call.name}'

functions = [
    {
      "name": "search",
      "description": "search the web for up to date info",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "query to search for"
          }
        },
        "required": ["query"]
      }
    }
  ]
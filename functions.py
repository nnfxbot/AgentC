import requests
import os
import json

def search_web(query):
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": os.getenv("BRAVE_API_KEY")}
    params = {"q": query}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            result = [
                {
                    "title": item["title"],
                    "url": item["url"],
                    "description": item["description"],
                    "age": item.get("age", ""),
                    "extra_snippets": item.get("extra_snippets", [])
                }
                for item in data["web"]["results"]
            ]
            return json.dumps(result)
        else:
            print("An error occurred. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

def handle_function_call(function_call):
    args = json.loads(function_call.arguments)
    if function_call.name == "search_web":
        return search_web(**args)
    else:
        return f'Error calling {function_call.name}'

functions = [
    {
      "name": "search_web",
      "description": "Search the web for up to date info. Only use this function when specifically asked to search_web. be as comprehensive as you can when responding using as much information from the search results as possible and always include a link to the source and the date of the source if available in the format [url][date].",
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

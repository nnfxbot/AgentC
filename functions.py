import requests
import os
import json
import openai

def get_completion(model = "gpt-3.5-turbo", temperature = 0, messages = [], enable_functions = False):
    try:
        if enable_functions:
            return openai.ChatCompletion.create(model=model, messages=messages,functions = functions, function_call = "auto", temperature = temperature)
        else:
            return openai.ChatCompletion.create(model=model, messages=messages, temperature = temperature)
    except:
        print(f'Error getting completion from OpenAI')

def search_web(query, freshness="pm", count = 3):
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": os.getenv("BRAVE_API_KEY")}
    params = {"q": query, "freshness": freshness,"text_decorations":"false" , "count":count}
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
    elif function_call.name == "python":
        with st.echo():
            args.code
    else:
        return f'Error calling {function_call.name}'

functions = [
    {
      "name": "search_web",
      "description": "Search the web for up to date info. be as comprehensive as you can when responding using as much information from the search results as possible and always include a link to the source and the date of the source if available in the format [url][date].",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "query to search for."
          },
          "freshness": {
            "type": "string",
            "description": "Filters search results by when they were discovered. Defaults to pm. The following time deltas are supported: pd Discovered in last 24 hours. pw Discovered in last 7 Days. pm Discovered in last 31 Days. py Discovered in last 365 Days. "
          }
        },
        "required": ["query"]
      }
    },
    {
      "name": "python",
      "description":  "Execute python code",
      "parameters": {
        "type": "object",
        "properties": {
          "code": {
            "type": "string",
            "description": "python code to execute. print output using streamlit functions such as st.write, st.markdown, st.plotly_chart, st.dataframe etc where applicable."
          }
        },
        "required": ["code"]
      }
    }
  ]

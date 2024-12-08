# kibernikto-playwright

Use to basic test your pages.  
Demonstrating kibernikto+playwright.

What it basically does:

- Goes to yr page and looks what can be clicked. 
- Generates click options objects for the page with some expectations from element clicks.
- Performs the actual clicks and checks what happens.
- Compares the expectations and reality.
- Prints and saves the results in the following form
```json
{
  "action_description": "The filter successfully applied, displaying only high ",
  "rating companies without changing the URL.",
  "expected_behaviour": "Filters companies by high rating",
  "actual_behaviour": "The list of companies was filtered to show only those with high ratings",
  "click_count": 1,
  "description": "High rating companies filter",
  "exact_element_text": "High rating",
  "new_url": "None",
  "status": "Success",
  "x": 100,
  "y": 800
}

```

## Set up the env:

```dotenv
OPENAI_API_KEY=sk-svcacct-blahblahblah
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-4o
```

## Update main.py:
Change the url to yr site url

```python
asyncio.run(test_website(web_link="http://127.0.0.1:3000/dashboard"))
```

Or run as a console chat
```python
asyncio.run(run_cmd_chat())
```

## Run code  
*(assuming you set the environment yrself)*

- Install the requirements   
  `pip install -r requirements.txt`
- Install needed playwright stuff
  `playwright install`
- Run `main.py` file using the environment provided.
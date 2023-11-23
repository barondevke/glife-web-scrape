import json
import requests
import os
from openai import OpenAI
from prompts import  assistant_instructions
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
ZAPIER_WEBHOOK = os.getenv('ZAPIER')

# Init OpenAI Client
client = OpenAI(api_key=OPEN_AI_KEY)


# Add lead to Airtable
def create_lead(name, phone, address):
  url = ZAPIER_WEBHOOK 
  leadData ={
    name:name,
    phone:phone,
    address:address
}

  response = requests.post(url,leadData)
  if response.status_code == 200:
    print("Lead created successfully.")
    return response.json()
  else:
    print(f"Failed to create lead: {response.text}")



# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    # If no assistant.json is present, create a new assistant using the below specifications

    # To change the knowledge document, modifiy the file name below to match your document
    # If you want to add multiple files, paste this function into ChatGPT and ask for it to add support for multiple files
    file = client.files.create(file=open("glifeDatapdf2.pdf", "rb"),
                               purpose='assistants')

    assistant = client.beta.assistants.create(
        # Getting assistant prompt from "prompts.py" file, edit on left panel if you want to change the prompt
        instructions=assistant_instructions,
        model="gpt-3.5-turbo-1106",
        tools=[
            {
                "type": "retrieval"  # This adds the knowledge base as a tool
            },

            {
                "type": "function",  # This adds the lead capture as a tool
                "function": {
                    "name": "create_lead",
                    "description":
                    "Capture lead details and send to Zapier.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the lead."
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number of the lead."
                            },
                            "address": {
                                "type": "string",
                                "description": "Address of the lead."
                            }
                        },
                        "required": ["name", "phone", "address"]
                    }
                }
            }
        ],
        file_ids=[file.id])

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id

import os
import logging
from pprint import pprint

# Google Cloud and security
from google.cloud import secretmanager
from google.api_core import exceptions

# LangChain core components
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model

# LangChain integrations
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

# --- STEP 1: Replace dotenv with Google Secret Manager ---

def get_secret(project_id, secret_id, version_id="latest"):
    """
    Retrieves a secret from Google Secret Manager with enhanced error handling.
    """
    print(f"Attempting to retrieve secret '{secret_id}' from project '{project_id}'...")
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8").strip()
        print(f"Successfully retrieved secret '{secret_id}'.")
        os.environ[secret_id] = secret_value  # Set the secret as an environment variable
    except exceptions.PermissionDenied:
        print(f"\n--- PERMISSION DENIED for '{secret_id}' ---")
        print("The user does not have 'Secret Manager Secret Accessor' role.")
        print("Run 'gcloud auth application-default login' and try again.")
        return None
    except Exception as e:
        print(f"\n--- UNEXPECTED ERROR for '{secret_id}': {e} ---")
        return None

# Call the function to get the key
key_to_retrieve = "OPENAI_API_KEY, LANGSMITH_API_KEY"
for key in key_to_retrieve.split(","):
    get_secret("edcat-site", key.strip())  # Retrieve each key and set as environment variable
if all(os.getenv(key.strip()) for key in key_to_retrieve.split(",")):
    print("\nAll secrets retrieved successfully and set as environment variables.")

os.environ["LANGSMITH_PROJECT"] = "rag-v6"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"

# Path to chroma DB:
CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "chroma_db"))

print(f"Using ChromaDB path: {CHROMA_PATH}")

# Embedding  Models:
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Vector store configuration:
vector_store = Chroma(
    collection_name="Jung_Individuacao",
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH,
)

# RAG Agent:

@tool
def search_handbook(query: str) -> str:
    """Search Chroma DB for information"""
    results = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in results
    )
    return serialized, results

model = init_chat_model("gpt-5-mini")

tools=[search_handbook]
prompt= ("Strictly search the chroma DB for information."
         " If the answer is not found in the chroma DB, respond with 'Information not found in Chroma DB.'"
)
agent = create_agent(
    model, tools, system_prompt=prompt)
    

query = (
    "O que há no arquivo de texto sobre a individuação?"
)

for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()
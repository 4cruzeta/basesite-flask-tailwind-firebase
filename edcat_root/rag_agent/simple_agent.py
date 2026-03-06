import os
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pprint import pprint
from dotenv import load_dotenv
from google.cloud import secretmanager

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
        return secret_value
    except exceptions.PermissionDenied:
        print(f"\n--- PERMISSION DENIED for '{secret_id}' ---")
        print("The user does not have 'Secret Manager Secret Accessor' role.")
        print("Run 'gcloud auth application-default login' and try again.")
        return None
    except Exception as e:
        print(f"\n--- UNEXPECTED ERROR for '{secret_id}': {e} ---")
        return None

# Call the function to get the key
retrieved_openai_key = get_secret("edcat-site", "OPENAI_API_KEY")

# CRUCIAL FIX: Set the retrieved key as an environment variable
# The OpenAI library looks for this exact environment variable name.
if retrieved_openai_key:
    os.environ["OPENAI_API_KEY"] = retrieved_openai_key
else:
    exit("Halting script: OpenAI API Key could not be retrieved.")
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
prompt= ("You are a helpful agent that can search the chroma DB for information."
)
agent = create_agent(
    model, tools, system_prompt=prompt)
    

query = (
    "Baseado no conteúdo do Chroma DB, qual é o assunto tratado?"
)

for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()
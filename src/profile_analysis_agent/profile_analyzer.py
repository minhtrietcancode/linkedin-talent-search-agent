import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)
from dotenv import load_dotenv

load_dotenv('config.env')

# Load OpenAI API key
os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a data parser. Given raw LinkedIn data, output a Python dict with keys:
- name (str)
- skills (List[str])
- experience (int)
- education (dict: degree one of [None, Diploma, Bachelor, Master, PhD], school str)
Only output a valid Python literal for the dict.
"""

HUMAN_PROMPT = """
Raw Data:
{raw_data}
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(HUMAN_PROMPT),
])

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

def analyze_profile_data(raw_data: dict) -> dict:
    """
    Use the LLM to transform raw scraped data into the structured format.
    """
    response = llm(prompt.format_prompt(raw_data=raw_data).to_messages())
    result = eval(response.content)
    return result

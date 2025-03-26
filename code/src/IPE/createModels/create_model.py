from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

class LLMModel:
  load_dotenv()
  
  #getting keys
 
  def __init__(self, llm):
    self.llm = llm

  def InitialiseLLM(self):
    groq_api_key = os.getenv("groq_api_key")
    match self.llm:
      case "lama3" :
         model = ChatGroq(temperature=0.7, model_name="llama3-70b-8192", groq_api_key = groq_api_key)
         return model
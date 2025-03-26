import os
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
from langchain_core.tools import Tool, StructuredTool
import logging

class InputAnalyzer:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("groq_api_key"),
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=1024
        )

    def analyze_input(self, user_input: str) -> dict:
        """
        Use LLM to analyze user input and determine appropriate action
        """
        prompt = f"""
        Analyze the following user input and determine the appropriate action.
        
        User Input: {user_input}

        there are 3 Rules for analysis:
        Rules for analysis:
        1. If the input contains an incident number (format: INCxxxxxxx), this is an incident request
        2. If the input is asking to search or find or recheck information/solutions/articles, this is a KB search request
           like example "can you help me with rechecking the keywords like job failed, job error, job issue and or schedule issue"
        3. If neither of above, this is general conversation that needs a friendly response
        
         Provide your analysis in the following JSON format:
        {{
            "action_type": "incident" | "kb_search" | "conversation",
            "incident_number": "INCxxxxxxx" (if found, else null),
            "search_keywords": "relevant search terms" (if kb_search, else null),
            "conversation_context": "context for conversation" (if conversation, else null),
            "confidence": 0.0 to 1.0
        }}

        Example responses:
        For incident: {{"action_type": "incident", "incident_number": "INC0000123", "search_keywords": null, "conversation_context": null, "confidence": 0.95}}
        For KB search: {{"action_type": "kb_search", "incident_number": null, "search_keywords": "password reset procedure", "conversation_context": null, "confidence": 0.88}}
        For conversation: {{"action_type": "conversation", "incident_number": null, "search_keywords": null, "conversation_context": "greeting and well-being inquiry", "confidence": 0.90}}
        
        Remember just give the json object dont give anything prefix test or suffix test just Json object 
        """

        # 1. If the input contains an incident number (format: INCxxxxxxx), this is an incident request then just return the incident number 
        # ---------------------------------------------------
        # example 1:
        # user prompt = can you information about INC0000123 
        # response: INC0000123
        # example 2:
        # user prompt = what is the status of incident inc0000123
        # response: inc0000123
        # ------------------------------------------------------------------------
        # 2. If the input is asking to search or find information/solutions/articles, this is a KB search request
        # -------------------------------------------------------------------------
        # example 1:
        # userprompt =search with more keywords like usb ports not working or pc harware issue  
        # response: 
        #  **Searchable keywords for KB article search:**

        #  keywords: "usb port","USB port not working", "PC hardware issue", "USB port malfunction", "PC USB problem"

        # example 2:
        # userprompt = I dont see releavant response for my incident, can you search with more keywords like file share not working, files issue  
        # response: 
        #  **Searchable keywords for KB article search:**

        #  keywords: "files share access", "team folder access", "file share issue", "team file share problem" 
        # --------------------------------------------------------------------------------------
        # 3. If neither of above, this is general conversation that needs a friendly response
        # example 1:
        # userprompt = hi
        # response: Hi, how can I help you today?
        # example 2:
        # userprompt = can you help on what ?
        # response: Sure, I can help on incident and its resolution?
        # """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # Convert the LLM's response to a Python dictionary
            python_safe_response = response.content.replace('null', 'None')
            analysis = eval(python_safe_response)
            logging.info(f"Input analysis: {analysis}")
            return analysis
        except Exception as e:
            logging.error(f"Error analyzing input: {str(e)}")
            return {
                "action_type": "conversation",
                "incident_number": None,
                "search_keywords": None,
                "conversation_context": "error handling",
                "confidence": 1.0
            }
        
__all__ = ['InputAnalyzer']
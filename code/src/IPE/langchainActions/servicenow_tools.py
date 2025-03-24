import os
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
from langchain_core.tools import Tool, StructuredTool
import logging
import requests

class ServiceNowAPI:
    def __init__(self):
        load_dotenv()
        self.snow_instance = os.getenv("snow_instance")
        self.incident_url = os.getenv("incident_url")
        self.rest_key = os.getenv("rest_key")
        self.headers = {
            "x-sn-apikey": self.rest_key,
            "Content-Type": "application/json"
        }

    def get_details(self, url: str, params: Dict = {}) -> Dict:
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                logging.debug(f"API Response: {data}")
                return data
            else:
                logging.error(f"Error: {response.status_code}, {response.text}")
                return {}
        except Exception as e:
            logging.error(f"API request failed: {str(e)}")
            return {}

    def process_data(self, data: Dict) -> str:
        if data.get('result') and len(data['result']) > 0:
            incident = data['result'][0]
            incident_str = (
                f"Short Description: {incident.get('short_description', 'N/A')}\n"
                f"Description: {incident.get('description', 'N/A')}\n"
                f"Configuration Item: {incident.get('cmdb_ci', 'N/A')}\n"
                f"Work Notes: {incident.get('work_notes', 'N/A')}"
            )
            return incident_str
        return None

class IncidentAnalyzer:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("groq_api_key"),
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=1024
        )

    def extract_keywords(self, analysis_string: str) -> str:
        try:
            keywords_split = analysis_string.split('**Searchable keywords for KB article search:**')
            if len(keywords_split) > 1:
                keywords_section = keywords_split[1].strip()
                keywords = keywords_section.replace('keywords:', '').strip()
                keywords = keywords.split('\n')[0].strip()
                keywords = keywords.strip('"')
                logging.debug(f"Extracted keywords: {keywords}")
                return keywords
        except Exception as e:
            logging.error(f"Error extracting keywords: {str(e)}")
            return ""

class ServiceNowTools:
    def __init__(self):
        self.snow_api = ServiceNowAPI()
        self.analyzer = IncidentAnalyzer()

    def query_incident(self, incident_number: str) -> str:
        """Query ServiceNow for incident details."""
        logging.info(f"Executing query_incident for {incident_number}")
        try:
            params = {
                'sysparm_query': "number=" + incident_number,
                'sysparm_limit': '1',
                'sysparm_fields': 'short_description,description,cmdb_ci,work_notes',
                'sysparm_suppress_cache_control': 'true'
            }
            jsonResponse = self.snow_api.get_details(self.snow_api.incident_url, params)
            details = self.snow_api.process_data(jsonResponse)
            if details:
                logging.info(f"Found incident details: {details}")
                return f"Incident details found: {details}"
            else:
                logging.warning(f"Incident not found: {incident_number}")
                return "Incident not found."
        except Exception as e:
            logging.error(f"Error in query_incident: {str(e)}")
            return f"Error querying incident: {str(e)}"

    def analyze_incident(self, incident_details: str) -> str:
        """Analyze incident details using Llama."""
        logging.info("Executing analyze_incident")
        try:
            prompt = f"""
            Analyze these incident details and extract key points for KB article search:
            {incident_details}
            
            Please provide a concise summary focusing on:
            1. Main issue
            2. Category/Impact
            3. Key technical terms
            And also provide me with the keywords just 2 words for the KB article search everytime make sure you pass lowercase 
            and give keywords coma seperated on same line like example below Always remeber to give in same format.
            example: keywords: "usb port", "hardware PC", "hardware issue", "usb hardware" "usb issue"
            sample output:
            1. **Main issue:** USB port not working on PC
            2. **Category/Impact:** Hardware issue, affecting PC functionality
            3. **Key technical terms:** USB port, PC, hardware issue
            
            **Searchable keywords for KB article search:**

            keywords: "usb port","USB port not working", "PC hardware issue", "USB port malfunction", "PC USB problem"

            These keywords can be used to search for relevant KB articles that may provide solutions or troubleshooting steps for the issue.
            """
            # response ="""**Incident Analysis:**
            #     1. **Main issue:** Unable to access team file share
            #     2. **Category/Impact:** File access issue, affecting team collaboration
            #     3. **Key technical terms:** File share, team folder, personal folder

            #     **Searchable keywords for KB article search:**

            #     keywords: "file share access", "team folder access", "file share issue", "team file share problem", "access denied file share"""""
            response = self.analyzer.llm.invoke([HumanMessage(content=prompt)])
            logging.info(f"Analysis result: {response.content}")
            return f"Analysis complete: {response.content}"
        except Exception as e:
            logging.error(f"Error in analyze_incident: {str(e)}")
            return f"Error analyzing incident: {str(e)}"

    def find_kb_articles(self, analysis: str) -> str:
        """Find relevant KB articles based on analysis."""
        logging.info("Executing find_kb_articles")
        try:
            keywords = self.analyzer.extract_keywords(analysis)
            if not keywords:
                return "No keywords found to search with."
                
            logging.info(f"Searching with keywords: {keywords}")
            
            search_terms = [term.strip().strip('"') for term in keywords.split(',')]
            search_query = "short_descriptionLIKE" + search_terms[0]
            for term in search_terms[1:]:
                search_query += "^ORshort_descriptionLIKE" + term

            url = f"https://dev306388.service-now.com/api/now/table/kb_template_known_error_article"
            params = {
                'sysparm_query': search_query,
                'sysparm_type': "kb_knowledge_base",
                'sysparm_limit': '5',
                'sysparm_suppress_cache_control': 'true'
            }

            articles = self.snow_api.get_details(url, params)
            
            if articles and articles.get('result'):
                kb_articles = []
                for article in articles['result']:
                    
                    article_info = ( f"       \n"
                        f"**<h4>KB Article</h4>**\n"
                        f"**Number:** <p>{article.get('number', 'N/A')}<p>\n"
                        f"**Title:** <p>{article.get('short_description', 'N/A')}</p>\n"
                        f"**Cause:** {article.get('kb_cause', 'N/A')}\n"
                        f"**WorkAround:** {article.get('kb_workaround', 'N/A')}"                                           
                    )
                    kb_articles.append(article_info)
                return "KB articles found: " + "\n".join(kb_articles)
            
            logging.warning("No KB articles found")
            return "No relevant KB articles found."
            
        except Exception as e:
            logging.error(f"Error in find_kb_articles: {str(e)}")
            return f"Error searching KB articles: {str(e)}"

class WorkflowManager:
    def __init__(self):
        self.snow_tools = ServiceNowTools()
        self.tools = [
            StructuredTool.from_function(
                func=self.snow_tools.query_incident,
                name="query_incident",
                description="Query ServiceNow for incident details"
            ),
            StructuredTool.from_function(
                func=self.snow_tools.analyze_incident,
                name="analyze_incident",
                description="Analyze incident details using Llama"
            ),
            StructuredTool.from_function(
                func=self.snow_tools.find_kb_articles,
                name="find_kb_articles",
                description="Find relevant KB articles based on analysis"
            )
        ]
        self.chain = None

    def create_workflow(self):
        workflow = StateGraph(MessagesState)
        
        def query_node(state):
            messages = state["messages"]
            incident_number = None
            for message in messages:
                if isinstance(message, HumanMessage) and "INC" in message.content:
                    for word in message.content.split():
                        if word.startswith("INC"):
                            incident_number = word
                            break
            
            if incident_number:
                try:
                    result = self.snow_tools.query_incident(incident_number)
                    return {
                        "messages": messages + [AIMessage(content=result)]
                    }
                except Exception as e:
                    logging.error(f"Error in query_node: {str(e)}")
                    return {
                        "messages": messages + [AIMessage(content=f"Error processing incident: {str(e)}")]
                    }
            return state

        def analyze_node(state):
            messages = state["messages"]
            last_message = messages[-1]
            if "Incident details found" in last_message.content:
                try:
                    result = self.snow_tools.analyze_incident(last_message.content)
                    return {
                        "messages": messages + [AIMessage(content=result)]
                    }
                except Exception as e:
                    logging.error(f"Error in analyze_node: {str(e)}")
                    return {
                        "messages": messages + [AIMessage(content=f"Error analyzing incident: {str(e)}")]
                    }
            return state

        def kb_node(state):
            messages = state["messages"]
            last_message = messages[-1]
            if "Analysis complete" in last_message.content:
                try:
                    result = self.snow_tools.find_kb_articles(last_message.content)
                    return {
                        "messages": messages + [AIMessage(content=result)]
                    }
                except Exception as e:
                    logging.error(f"Error in kb_node: {str(e)}")
                    return {
                        "messages": messages + [AIMessage(content=f"Error searching KB articles: {str(e)}")]
                    }
            return state

        # Add nodes and edges
        workflow.add_node("query", query_node)
        workflow.add_node("analyze", analyze_node)
        workflow.add_node("kb_search", kb_node)
        
        def get_next_step(state: Dict) -> str:
            messages = state["messages"]
            if not messages:
                return "end"
                
            last_message = messages[-1]
            content = last_message.content.lower()
            
            if "incident details found" in content:
                return "analyze"
            elif "analysis complete" in content:
                return "kb_search"
            elif any([
                "kb articles found" in content,
                "no relevant kb articles found" in content,
                "error" in content
            ]):
                return "end"
            else:
                return "query"

        workflow.add_edge(START, "query")
        for node in ["query", "analyze", "kb_search"]:
            workflow.add_conditional_edges(
                node,
                get_next_step,
                {
                    "query": "query",
                    "analyze": "analyze",
                    "kb_search": "kb_search",
                    "end": END
                }
            )
        self.chain = workflow.compile()
        return self.chain

    def invoke_chain(self,user_input):
        try:
            incident_number = "INC0000059"
            
            initial_state = {
                "messages": [
                    SystemMessage(content="Processing ServiceNow incident workflow."),
                    HumanMessage(content=f"Process incident {incident_number}")
                ]
            }
            
            logging.info("Starting workflow execution...")
            
            result = self.chain.invoke(
                initial_state,
                {"recursion_limit": 100}
            )
            
            print("\n=== Workflow Results ===")
            for message in result["messages"]:
                print(f"\n{message.type}: {message.content}")

            if isinstance(result, dict) and "messages" in result:
                formatted_response = []
                for message in result["messages"]:
                    if hasattr(message, 'content'):
                        formatted_response.append(message.content)
                return "\n".join(formatted_response)
        
            return str(result)
        except Exception as e:
            logging.error("Workflow execution error", exc_info=True)
            print(f"Error executing workflow: {str(e)}")

# if __name__ == "__main__":
#     try:
#         logging.basicConfig(level=logging.INFO)
        
#         workflow_manager = WorkflowManager()
#         chain = workflow_manager.create_workflow()
        
#         incident_number = "INC0000059"
        
#         initial_state = {
#             "messages": [
#                 SystemMessage(content="Processing ServiceNow incident workflow."),
#                 HumanMessage(content=f"Process incident {incident_number}")
#             ]
#         }
        
#         logging.info("Starting workflow execution...")
        
#         result = chain.invoke(
#             initial_state,
#             {"recursion_limit": 100}
#         )
        
#         print("\n=== Workflow Results ===")
#         for message in result["messages"]:
#             print(f"\n{message.type}: {message.content}")
            
#     except Exception as e:
#         logging.error("Workflow execution error", exc_info=True)
#         print(f"Error executing workflow: {str(e)}")

__all__ = ['WorkflowManager']
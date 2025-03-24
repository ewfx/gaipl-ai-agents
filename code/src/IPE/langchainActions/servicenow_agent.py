from langchain_core.messages import HumanMessage, AIMessage,SystemMessage
import os
from dotenv import load_dotenv
import logging
import urllib.parse
import requests
from Servicenow_tools import query_incident, analyze_incident

if __name__ == "__main__":
    try:
        # Create the workflow
        chain = create_workflow()
        
        # Initialize with an incident number
        incident_number = "INC0000059"  # Replace with actual incident number
        
        initial_state = {
            "messages": [
                SystemMessage(content="Processing ServiceNow incident workflow."),
                HumanMessage(content=f"Process incident {incident_number}")
            ]
        }
        
        logging.info("Starting workflow execution...")
        
        # Execute with higher recursion limit
        result = chain.invoke(
            initial_state,
            {"recursion_limit": 100}
        )
        
        print("\n=== Workflow Results ===")
        for message in result["messages"]:
            print(f"\n{message.type}: {message.content}")
            
    except Exception as e:
        logging.error("Workflow execution error", exc_info=True)
        print(f"Error executing workflow: {str(e)}")


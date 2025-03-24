import streamlit as st
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from langchainActions.servicenow_tools import WorkflowManager

logging.basicConfig(level=logging.INFO)

def initialize_workflow():
    """Initialize the workflow manager and create the workflow chain"""
    try:
        workflow_manager = WorkflowManager()
        workflow_manager.create_workflow()
        return workflow_manager
    except Exception as e:
        logging.error(f"Error initializing workflow: {str(e)}")
        return None

def initialize_session_state():
    """Initialize session state variables"""
    if 'workflow_manager' not in st.session_state:
        st.session_state.workflow_manager = initialize_workflow()
    
    if 'messages' not in st.session_state:
        welcomeNote = "Hi, I'm a chatbot I can help you with all your queries. How can I help you?"
        st.session_state.messages = [{"role": "assistant", "content": welcomeNote, "type": "text"}]

def display_sidebar():
    """Display and handle sidebar elements"""
    with st.sidebar:
        llmmodel = st.selectbox("Select LLM", ["lama3"], index=0)
        type = st.selectbox("Framework", ["Langchain", "lamaindex"], index=0)
    return llmmodel, type

def process_user_input(user_input):
    """Process user input and generate response"""
    try:
        if not st.session_state.workflow_manager:
            st.error("Workflow manager not initialized properly")
            return None

        response = st.session_state.workflow_manager.invoke_chain(user_input)
        
        # Handle the response
        if response:
            return response
        else:
            return "No response generated"
            
    except Exception as e:
        logging.error(f"Error in chain invocation: {str(e)}")
        st.error(f"Error processing request: {str(e)}")
        return None

def update_chat_history(role, content):
    """Update chat history with new messages"""
    if content:
        message = {"role": role, "content": content, "type": "text"}
        st.session_state.messages.append(message)
        
        # Display the message
        with st.chat_message(role):
            st.write(content)

def display_chat_history():
    """Display all messages in chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def main():
    """Main application function"""
    st.title("ServiceNow Assistant")
    
    # Initialize session state
    initialize_session_state()

    # Setup sidebar
    llmmodel, framework_type = display_sidebar()

    # Display existing chat history
    display_chat_history()

    # Get user input
    user_input = st.chat_input(placeholder="Enter your incident number or query here...", key="user_input")

    # Process user input if provided
    if user_input:
        # Update chat with user message
        update_chat_history("user", user_input)

        # Process input and get response
        with st.spinner('Processing your request...'):
            response = process_user_input(user_input)
            
            # Update chat with assistant response
            if response:
                update_chat_history("assistant", response)
            else:
                update_chat_history("assistant", "I apologize, but I couldn't process your request.")

if __name__ == "__main__":
    main()

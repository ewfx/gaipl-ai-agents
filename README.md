# 🚀 Integrated Platform Evironment By AI Agents teams


## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
This project automates ServiceNow incident resolution using an AI-driven approach. The system consists of two key backend components:

1. **Optimus Agent**: Pulls unassigned incidents from ServiceNow, determines the assignment group, and assigns the incident to the respective platform owner.
2. **Vertical Agent**: An AI-powered agent with a knowledge base that assists in resolving incidents efficiently.

## 🔧 Tech Stack
- **Backend**: Python, Django
- **Database**: MongoDB
- **Containerization**: Docker
- **API Testing**: Postman
- **Cloud & Deployment**: Azure
- **AI & NLP**: OpenAI (text-embedding-3-small)
- **ITSM Integration**: ServiceNow

## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](https://github.com/ewfx/gaipl-ai-agents/blob/main/demo.webm) (if applicable)  
🖼️ Screenshots:

https://github.com/ewfx/gaipl-ai-agents/tree/main/image%20assets

## 🚀 Features
✅ **Automated Incident Assignment** using ServiceNow API  
✅ **AI-powered Resolution Engine** with automation capabilities  
✅ **Chatbot Assistance** for logs, metrics, and recommendations  
✅ **Integration with Grafana** for real-time monitoring  
✅ **Seamless Deployment with Docker & Azure**  


## ⚙️ What It Does
The application integrates with ServiceNow tools to analyze issues, provide suggested workarounds from Knowledge Base (KB) articles, and execute user-defined instructions efficiently.

## 🛠️ How We Built It
Our application is built using LangChain and LangGraph, with Streamlit utilized for the frontend interface. The core functionality is developed in Python as the base programming language.

## 🛠 Implementation Details

### 🔹 Incident Assignment Flow
1. **Data Retrieval**:
   - The **Optimus Agent** fetches all unassigned incidents from ServiceNow.
   - It checks the **assignment group** and assigns the incident to the **platform owner**.

2. **AI-Driven Assistance**:
   - The **Vertical Agent** receives the incident and checks for possible automation.
   - If automation is available, the incident is auto-resolved.
   - If no automation exists, the agent searches the **knowledge base** (logs, dashboards, past incidents, and knowledge articles).

3. **Support Engineer Interaction**:
   - If further action is required, a support engineer can interact with the AI chatbot.
   - The chatbot provides recommendations, retrieves logs for specific time ranges, and allows document uploads for better context.
   - The support engineer can also fetch **logs, metrics, and tracing information** directly within the chat.

4. **Incident Resolution**:
   - The engineer finds the resolution and **closes the incident from the UI itself**.


## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaipl-ai-agents
   ```
2. Install dependencies  
   ```sh
   create the virtual environment using conda or python
   conda create --name my_env_name python=3.11
   conda activate my_env_name
   pip install -r requirements.txt
   ```
3. Run the project  
   ```sh
     launch.json already committed, just download python extension and run the application.
   ```

## 🏗️ Tech Stack
   - 🔹 Streamlit
   - 🔹 python
   - 🔹 LangChain
   - 🔹 LangGraph
   - 🔹 LLama3
     ![image](https://github.com/user-attachments/assets/e7845c95-e9b5-4469-9b51-3a1a9f5b12cf)

## 👥 Team
   -- **Phani Vijaya Aditya Mukkavilli** -
   --**Datta Sai Krishna Somesula**
   --**Subhajit Mondal**
   --**Prasanth Panda**
   --**GiriBabu Goli**

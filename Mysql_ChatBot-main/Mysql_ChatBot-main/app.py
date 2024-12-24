import streamlit as st
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import urllib.parse
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Set the API keys environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
langsmith_key = os.getenv("LANGCHAIN_SQL_APIKEY")  # Load LangSmith API key
st.set_page_config(page_title="LangChain: Chat with MYsql DB", page_icon="🍺")
st.title("🍺 LangChain: Chat with MYsql Database")

# MySQL connection details from user input
mysql_host = st.sidebar.text_input("MySQL Host", value="localhost")
mysql_port = st.sidebar.text_input("MySQL Port", value="3306")  # Default MySQL port
mysql_user = st.sidebar.text_input("MySQL User")
mysql_password = st.sidebar.text_input("MySQL Password", type="password")
mysql_db = st.sidebar.text_input("MySQL Database")

# Update API key 
groq_api_key = st.sidebar.text_input(label="Groq API Key", type="password", value=groq_api_key)
langsmith_key = st.sidebar.text_input(label="LangSmith API Key", type="password", value=langsmith_key)

if not groq_api_key:
    st.info("Please add the Groq API key")
if not langsmith_key:
    st.info("Please add the LangSmith API key")

# Encode special characters in the password
mysql_password = urllib.parse.quote_plus(mysql_password)

# LLM model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192", streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(mysql_host, mysql_port, mysql_user, mysql_password, mysql_db):
    if not (mysql_host and mysql_user and mysql_password and mysql_db):
        st.error("Please provide all MySQL connection details.")
        st.stop()
    
    try:
        # Create SQLAlchemy engine for MySQL
        connection_string = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            # Test the connection by executing a simple query
            result = conn.execute(text("SELECT 1"))
            if result.fetchone() is None:
                raise Exception("Failed to execute test query.")
        
        return engine
    except SQLAlchemyError as e:
        st.error(f"SQLAlchemy Error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()
engine = configure_db(mysql_host, mysql_port, mysql_user, mysql_password, mysql_db)

# Toolkit
db = SQLDatabase(engine)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Create the SQL agent with monitoring integration (update callback as needed)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

# Sidebar navigation
nav_option = st.sidebar.radio(
    "Navigation",
    ["Chat with Database", "View Table Data"]
)

if nav_option == "Chat with Database":
    
    if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    # Display message history
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Get user input
    user_query = st.chat_input(placeholder="Ask anything about the database")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.chat_message("assistant"):
            try:
                # Run the query through the SQL agent
                response = agent.run(user_query)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

elif nav_option == "View Table Data":
    st.subheader("View Table Data")

    try:
        # Fetch table names
        with engine.connect() as conn:
            tables = conn.execute(text("SHOW TABLES")).fetchall()
        
        table_names = [table[0] for table in tables]
        
        selected_table = st.selectbox("Select a table to view", table_names)
        
        if selected_table:
            st.write(f"Showing data for table: {selected_table}")
            
            # Fetch table data
            query = text(f"SELECT * FROM `{selected_table}`")
            with engine.connect() as conn:
                data = conn.execute(query).fetchall()
            
            # Display data in a DataFrame
            with engine.connect() as conn:
                columns_query = text(f"SHOW COLUMNS FROM `{selected_table}`")
                columns = [col[0] for col in conn.execute(columns_query).fetchall()]
            df = pd.DataFrame(data, columns=columns)
            st.dataframe(df)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

import streamlit as st
import openai
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()

# Set environment variables
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user's queries."),
        ("user", "Question: {question}")
    ]
)

def generate_response(question, engine, temperature, max_tokens):
    groq_api_key = os.environ["GROQ_API_KEY"]
    llm = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    answer = chain.invoke({'question': question})
    return answer

st.title("Enhanced Q&A Chatbot With OpenAI")
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq AI API Key:", type="password")  

engine = st.sidebar.selectbox("Select model", ["GPT-4 Turbo", "GPT-4", "LLaMA 2 7B", "LLaMA 2 13B", "Claude 3"])

# Adjust response parameters
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7)
max_tokens = st.sidebar.slider("Max Tokens", min_value=50, max_value=300, value=150)

# Main interface for user input
st.write("Go ahead and ask any question")  
user_input = st.text_input("You:")

if user_input and api_key:
    response = generate_response(user_input, engine, temperature, max_tokens)  
    st.write(response)

elif user_input:
    st.warning("Please enter the Groq API Key in the sidebar")  
else:
    st.write("Please provide user input")

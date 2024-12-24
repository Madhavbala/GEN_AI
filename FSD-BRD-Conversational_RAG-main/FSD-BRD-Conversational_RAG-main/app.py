import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()
os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Streamlit app setup
st.title("Conversational RAG with AI Test Case Generation")
st.write("Upload FSD/BRD PDFs, generate test cases, and interact with content using AI.")

# Input Groq API Key
api_key = st.text_input("Enter your Groq API key:", type="password")

# Check if Groq API Key is provided
if api_key:
    llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

    # Predefined Session IDs with passwords
    session_passwords = {
        "1001": "password1001",
        "1002": "password1002"
    }

    # Session ID and Password input boxes
    session_id = st.text_input("Enter your Session ID:")
    password = st.text_input("Enter your Password:", type="password")

    if session_id and password:
        if session_id in session_passwords and session_passwords[session_id] == password:
            st.session_state.session_name = session_id  # Store session ID in session state

            if 'store' not in st.session_state:
                st.session_state.store = {}

            uploaded_files = st.file_uploader("Choose a PDF file", type="pdf", accept_multiple_files=True)

            # Process uploaded PDFs
            def process_uploaded_pdfs(uploaded_files):
                documents = []
                for uploaded_file in uploaded_files:
                    temp_pdf = f"./temp_{uploaded_file.name}"
                    with open(temp_pdf, "wb") as file:
                        file.write(uploaded_file.getvalue())
                    
                    loader = PyPDFLoader(temp_pdf)
                    docs = loader.load()
                    documents.extend(docs)
                return documents

            if uploaded_files:
                with st.spinner("Processing PDFs..."):
                    documents = process_uploaded_pdfs(uploaded_files)

                # Split and embed documents
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
                splits = text_splitter.split_documents(documents)
                vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
                retriever = vectorstore.as_retriever()

                # Contextualize questions prompt
                contextualize_q_system_prompt = (
                    "Given a chat history and the latest user question "
                    "which might reference context in the chat history, "
                    "formulate a standalone question which can be understood "
                    "without the chat history. Do NOT answer the question, "
                    "just reformulate it if needed and otherwise return it as is."
                )
                contextualize_q_prompt = ChatPromptTemplate.from_messages([
                    ("system", contextualize_q_system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ])

                history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

                # Q&A Prompt
                system_prompt = (
                    "You are an assistant for question-answering tasks. "
                    "Use the following pieces of retrieved context to answer "
                    "the question. If you don't know the answer, say that you "
                    "don't know. Use three sentences maximum and keep the "
                    "answer concise.\n\n"
                    "{context}"
                )
                qa_prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ])

                question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
                rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

                def get_session_history(session: str) -> BaseChatMessageHistory:
                    if session not in st.session_state.store:
                        st.session_state.store[session] = ChatMessageHistory()
                    return st.session_state.store[session]

                conversational_rag_chain = RunnableWithMessageHistory(
                    rag_chain,
                    get_session_history,
                    input_messages_key="input",
                    history_messages_key="chat_history",
                    output_messages_key="answer"
                )

                # AI Test Case Generation
                def generate_test_cases_from_fsd(fsd_data, user_query):
                    # Tokenize and generate test cases based on user input query
                    tokenized_data = [doc.page_content[:16384] for doc in fsd_data]  # Limit content to 16k tokens
                    test_cases = []
                    
                    # Generate test cases dynamically based on the user query
                    for idx, content in enumerate(tokenized_data, start=1):
                        # Extract relevant steps based on query
                        # Simple example: Split document content into steps or sections based on line breaks or other patterns
                        # You can enhance this by using NLP models or more complex parsing
                        
                        # Simple step extraction - assuming steps are numbered or have some recognizable pattern
                        steps = []
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().lower().startswith('step'):  # Simple check for "Step" keyword
                                steps.append(line.strip())
                        
                        # If no steps are found, create a generic fallback
                        if not steps:
                            steps = ["Step 1: Verify the system is in the correct state.", 
                                     "Step 2: Perform the necessary action based on the test case.", 
                                     "Step 3: Check the expected outcome based on the requirement."]
                        
                        # Generate test case based on the query
                        test_case = {
                            "Number": idx,
                            "Content Snippet": content,  # Show a snippet of the document as part of the test case
                            "Generated Test Case": f"Test Case {idx} based on query '{user_query}'",  # Dynamic based on query
                            "Related Content": content,  # You could filter this if you use advanced NLP or search methods
                            "Query Based Action": user_query,  # The user query itself can be tied to the test case
                            "Test Steps": steps  # Add extracted steps
                        }
                        
                        # Append the dynamically generated test case
                        test_cases.append(test_case)
                    
                    return test_cases

                # User query input
                user_query = st.text_input("Enter your query for generating test cases:")

                if st.button("Generate Test Cases from FSD/BRD"):
                    if user_query:
                        with st.spinner("Generating Test Cases..."):
                            test_cases = generate_test_cases_from_fsd(splits, user_query)
                            # Save to Excel
                            df = pd.DataFrame(test_cases)
                            df.to_excel("Generated_Test_Cases_from_Query.xlsx", index=False)
                            st.success("Test cases generated and saved as 'Generated_Test_Cases_from_Query.xlsx'.")
                    else:
                        st.warning("Please enter a query to generate test cases.")

                # User question input
                user_input = st.text_input("Your question:")
                if user_input:
                    session_history = get_session_history(session_id)
                    response = conversational_rag_chain.invoke(
                        {"input": user_input},
                        config={"configurable": {"session_id": session_id}},
                    )
                    st.write("Assistant:", response['answer'])

        else:
            st.error("Invalid Session ID or Password.")
else:
    st.warning("Please enter the Groq API Key.")

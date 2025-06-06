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
import moviepy as mp
import speech_recognition as sr
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

os.environ['HF_TOKEN'] = os.getenv("HF_TOKEN")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Set up Streamlit UI
st.title("Conversational RAG With Video and PDF Uploads")
st.write("Upload PDFs, videos, and chat with their content")

# Input for Groq API Key
api_key = st.text_input("Enter your Groq API key:", type="password")

# Check if Groq API key is provided
if api_key:
    llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

    # Chat interface
    # Removed session_id input as per your request

    # State to manage chat history
    if 'store' not in st.session_state:
        st.session_state.store = {}

    uploaded_files = st.file_uploader("Choose PDF file(s)", type="pdf", accept_multiple_files=True)

    # Process uploaded PDFs
    if uploaded_files:
        documents = []
        for uploaded_file in uploaded_files:
            temppdf = f"./temp.pdf"
            with open(temppdf, "wb") as file:
                file.write(uploaded_file.getvalue())
                file_name = uploaded_file.name

            loader = PyPDFLoader(temppdf)
            docs = loader.load()
            documents.extend(docs)

        # Split and create embeddings for the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever()

        # Contextualize question prompt
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question, "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

        # Answer question
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        def get_session_history() -> BaseChatMessageHistory:
            # Removed session_id input and used default
            if 'default_session' not in st.session_state.store:
                st.session_state.store['default_session'] = ChatMessageHistory()
            return st.session_state.store['default_session']
        
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain, get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        user_input = st.text_input("Your question:")
        if user_input:
            session_history = get_session_history()
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": "default_session"}},
            )
            st.write("Assistant:", response['answer'])

    # Video Upload and Audio Extraction
    video_file = st.file_uploader("Upload a Video (MP4 format)", type=["mp4"])

    if video_file:
        temp_video_path = f"./temp_video.mp4"
        with open(temp_video_path, "wb") as video:
            video.write(video_file.getvalue())

        # Extract audio from video
        my_vid = mp.VideoFileClip(temp_video_path)

        if my_vid.audio:
            st.write("Audio track found. Extracting audio...")
            audio_path = "my_result.wav"
            my_vid.audio.write_audiofile(audio_path)
            st.write("Audio extracted successfully.")

            # Speech Recognition to Convert Audio to Text
            def audio_to_text(file):
                try:
                    with sr.AudioFile(file) as source:
                        recognizer = sr.Recognizer()
                        audio_data = recognizer.record(source)
                        return recognizer.recognize_google(audio_data)
                except Exception as e:
                    return f"Error: {e}"

            audio_text = audio_to_text(audio_path)
            st.write("Transcription of Audio:", audio_text)

            # Convert transcribed text to PDF
            def text_to_pdf(text, output_file):
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                for line in text.splitlines():
                    pdf.multi_cell(0, 10, line)

                pdf.output(output_file)

            output_pdf = "transcribed_text.pdf"
            text_to_pdf(audio_text, output_pdf)
            st.write(f"PDF created successfully and saved as {output_pdf}")
        else:
            st.write("No audio found in the video.")

else:
    st.warning("Please enter the Groq API Key.")

# Conversational RAG with AI Test Case Generation

This Streamlit-based application allows users to upload FSD/BRD PDF files, generate test cases dynamically based on user queries, and retrieve answers using an AI-powered retrieval-augmented generation (RAG) system.

## Features:
- Upload multiple PDF files (FSD/BRD documents).
- Extract and tokenize document content.
- Dynamically generate test cases based on user queries.
- Provide AI-driven responses to questions related to the content.
- Automatically extract steps for test cases or generate fallback steps if not found.
- Save generated test cases as an Excel file.
- Support for session-based user authentication.

## Requirements:
- Python 3.8 or higher
- Streamlit
- LangChain
- Groq API (for AI-powered querying)
- Hugging Face API (for embeddings)
- Pandas
- PyPDF2
- Chroma
- .env file for API keys

## Installation:

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/Conversational-RAG-Test-Case-Generation.git


2. Install the necessary Python dependencies:

3. pip install -r requirements.txt

4. Create a .env file in the root directory and add your Hugging Face and Groq API tokens:

   HF_TOKEN=<your_hugging_face_api_token>
   GROQ_API_KEY=<your_groq_api_key>

5. Run the application using Streamlit:

streamlit run app.py

Usage:
Upload PDF Files:

Click on the "Choose a PDF file" button to upload multiple FSD/BRD PDF documents.
Enter Query:

Enter a query to generate test cases based on the uploaded content. The system will tokenize the content and extract steps or generate default steps if not found.
Generate Test Cases:

Click on the "Generate Test Cases from FSD/BRD" button to generate and save the test cases based on the uploaded documents and your query.
The test cases will be saved as an Excel file, which you can download.
Ask Questions:

Enter any query related to the uploaded content, and the system will provide an AI-driven answer using the Conversational RAG model.
Example:
Query for Test Case: "Generate test case for user login functionality."
Generated Test Case:
Number: 1
Content Snippet: "User logs into the system with valid credentials..."
Test Steps:
Verify the system is in the correct state.
Perform the necessary action based on the test case.
Check the expected outcome based on the requirement.
Session Management:
The application supports session-based user authentication.
Enter a valid session ID and password to access the functionalities.
Contributing:
Feel free to fork the repository, make improvements, and submit pull requests. All contributions are welcome!

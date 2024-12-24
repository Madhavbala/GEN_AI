# Chat with MySQL Database

## Overview
This Streamlit application allows users to interact with a MySQL database through a conversational interface. It enables querying and viewing of database tables in a user-friendly manner.

## Features
- **Chat with Database**: Ask questions and get responses using an SQL agent.
- **View Table Data**: Select and display data from MySQL tables.
- **Environment Management**: API keys and database credentials are managed via a `.env` file.
- **Connection Validation**: Ensures the MySQL connection is properly established.

## Installation

1. Clone the repository:
    ```bash
    git clone path/Chat-MySQL.git
    cd Chat-MySQL
    ```

2. Set up your virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file with the following variables:
    ```plaintext
    GROQ_API_KEY=your_groq_api_key
    LANGCHAIN_SQL_APIKEY=your_langsmith_api_key
    ```

## Usage

1. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. Open the provided URL in your web browser to interact with the application.


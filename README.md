
# AI/ML Intern Assignment: TalentScout Hiring Assistant

The chatbot assists in the initial screening of candidates by gathering essential information and posing relevant technical questions based on the candidate's declared tech stack.

## Project Overview

The chatbot guides the conversation to:
1.  **Gather Initial Candidate Information**: Collects details like name, contact information, experience, and desired position.
2.  **Generate Technical Questions**: Based on the candidate’s specified tech stack, it generates relevant technical questions using the Gemini language model to assess their proficiency.
3.  **Ensure Coherent Interactions**: It maintains the flow of the conversation to provide a seamless user experience.

## Technical Details

*   **Programming Language**: Python
*   **Frontend Interface**: Streamlit
*   **Large Language Model**: Google Gemini (`gemini-pro`)
*   **Package Manager**: `uv`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment using `uv`:**
    ```bash
    uv venv
    ```

3.  **Activate the environment:**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install the required packages:**
    ```bash
    uv pip install -r requirements.txt
    ```

5.  **Set up your Google API Key:**
    The application requires a Google API key to use the Gemini model. It is recommended to set this up as a Streamlit secret.

    *   Create a file named `.streamlit/secrets.toml` in the project root.
    *   Add your API key to this file:
        ```toml
        GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
        ```
    *   Alternatively, you can set it as an environment variable named `GOOGLE_API_KEY`.

## Usage Guide

To run the application, execute the following command in your terminal:

```bash
streamlit run main.py
```

The application will open in your web browser. Interact with the chatbot by typing in the input field and pressing Enter. The conversation will end automatically after the technical questions are provided, or you can use keywords like `bye`, `exit`, or `quit`.

## Prompt Design

Prompts guide the chatbot's flow and question generation. For information gathering, pre-defined prompts ensure structured data collection. For technical questions, a detailed prompt instructs Gemini to act as a recruiter and generate 4 relevant, concept-based questions based on the candidate's tech stack.

## Challenges & Solutions

Challenges included managing conversation state in Streamlit, solved using `session_state`. Ensuring relevant LLM questions was addressed by crafting detailed prompts that define the model's persona and expected output.

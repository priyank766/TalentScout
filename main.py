import streamlit as st
import google.generativeai as genai
import os
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator

# --- Configuration ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.error("Google API Key not found. Please set it as an environment variable.")
    st.stop()


# --- Pydantic Model for Applicant Information ---
class ApplicantInfo(BaseModel):
    name: str | None = Field(None)
    email: EmailStr | None = Field(None)
    phone: str | None = Field(None)
    experience: float | None = Field(None)
    position: str | None = Field(None)
    location: str | None = Field(None)
    tech_stack: str | None = Field(None)

    @validator("name")
    def validate_name(cls, v):
        if v is not None and (
            not all(x.isalpha() or x.isspace() for x in v) or not v.strip()
        ):
            raise ValueError("Name must contain only alphabetic characters and spaces.")
        return v

    @validator("phone")
    def validate_phone(cls, v):
        if v is not None and (not v.isdigit() or len(v) != 10):
            raise ValueError("Phone number must be 10 digits (digits only).")
        return v

    @validator("experience")
    def validate_experience(cls, v):
        if v is not None and v < 0:
            raise ValueError("Experience cannot be negative.")
        return v

    @validator("position", "location", "tech_stack")
    def validate_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("This field cannot be empty.")
        return v


# --- Chatbot Logic ---
def get_next_prompt(applicant_info: ApplicantInfo) -> tuple[str, str | None]:
    """Returns the appropriate prompt and the field to fill next."""
    if applicant_info.name is None:
        return (
            "Hello! I'm an intelligent hiring assistant from TalentScout. I'm here to ask you a few questions to get started with your application. What is your full name?",
            "name",
        )
    if applicant_info.email is None:
        return f"Thanks, {applicant_info.name}. What's your email address?", "email"
    if applicant_info.phone is None:
        return "Got it. What is your phone number?", "phone"
    if applicant_info.experience is None:
        return (
            "Great. How many years of professional experience do you have?",
            "experience",
        )
    if applicant_info.position is None:
        return "Thanks. What is your desired position or role?", "position"
    if applicant_info.location is None:
        return "Okay. Where are you currently located?", "location"
    if applicant_info.tech_stack is None:
        return (
            "Understood. Please list your primary tech stack (e.g., Python, React, Node.js, PostgreSQL).",
            "tech_stack",
        )

    return (
        "Thank you. I will now generate a few technical questions based on your tech stack: {tech_stack}. Please wait a moment.",
        "generate_questions",
    )


def generate_technical_questions(tech_stack: str) -> str:
    """Generates technical questions using the Gemini API."""
    if not GOOGLE_API_KEY:
        return "Error: API Key is not configured."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        You are a senior technical recruiter for a fictional agency called "TalentScout".
        Your role is to conduct an initial screening of a candidate.
        Based on the tech stack provided by the candidate, generate exactly 4 relevant technical questions.
        The questions should be designed to assess their fundamental knowledge and practical experience.
        Do not ask trivia. Ask concept-based questions.
        Question should be clear relevant to the tech stack.
        Return the questions as a single string, with each question numbered.
        Display the questions in a  bulleted list format and new line as well.


        Candidate's Tech Stack: "{tech_stack}"
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while generating questions: {e}")
        return "I was unable to generate the technical questions at this moment. We can proceed without them. Thank you for your understanding."


# --- Streamlit UI ---
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")
st.title("🤖 TalentScout Hiring Assistant")

st.markdown(
    """
    <style>
    /* Import a clean modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Background */
    body, .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        min-height: 100vh;
    }

    /* Header */
    .custom-chat-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
        text-shadow: 0 3px 10px rgba(0,0,0,0.25);
        animation: fadeInDown 1s ease-in-out;
    }

    /* Chat container */
    .custom-chat-container {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.25);
        padding: 2rem 1.5rem;
        margin: 2rem auto;
        max-width: 650px;
        animation: fadeInUp 1s ease-in-out both;
    }

    /* Chat messages */
    .custom-chat-message {
        margin-bottom: 1rem;
        padding: 0.9rem 1.2rem;
        border-radius: 16px;
        font-size: 1.05rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        animation: fadeInUp 0.6s ease both;
        max-width: 80%;
        line-height: 1.5;
    }

    /* User bubble */
    .custom-chat-message.user {
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: #ffffff;
        text-align: right;
        margin-left: auto;
    }

    /* Assistant bubble */
    .custom-chat-message.assistant {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        color: #1e293b;
        text-align: left;
        margin-right: auto;
    }

    /* Animations */
    @keyframes fadeInUp {
        0% { transform: translateY(20px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    @keyframes fadeInDown {
        0% { transform: translateY(-20px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "messages" not in st.session_state:
    st.session_state.messages = []
if "applicant_info" not in st.session_state:
    st.session_state.applicant_info = ApplicantInfo()
if "current_field_to_fill" not in st.session_state:
    st.session_state.current_field_to_fill = None
if "conversation_finished" not in st.session_state:
    st.session_state.conversation_finished = False


if not st.session_state.messages:
    initial_prompt, field_to_fill = get_next_prompt(st.session_state.applicant_info)
    st.session_state.messages.append({"role": "assistant", "content": initial_prompt})
    st.session_state.current_field_to_fill = field_to_fill

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if not st.session_state.conversation_finished:
    if user_input := st.chat_input(
        "Your response...", key="user_input"
    ):  # Added key to prevent duplicate widget error
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        assistant_response_content = ""

        if user_input.lower() in ["bye", "exit", "quit"]:
            assistant_response_content = "Thank you for answering the questions. That's all I need for now. The TalentScout team will review your submission and get back to you soon. Have a great day!"
            st.session_state.conversation_finished = True
            st.session_state.current_field_to_fill = None
        else:
            if st.session_state.current_field_to_fill:
                try:
                    temp_data = st.session_state.applicant_info.model_dump()
                    if st.session_state.current_field_to_fill == "experience":
                        temp_data[st.session_state.current_field_to_fill] = float(
                            user_input
                        )
                    else:
                        temp_data[st.session_state.current_field_to_fill] = user_input

                    st.session_state.applicant_info = ApplicantInfo.model_validate(
                        temp_data
                    )

                    next_prompt, next_field_to_fill = get_next_prompt(
                        st.session_state.applicant_info
                    )
                    st.session_state.current_field_to_fill = next_field_to_fill
                    assistant_response_content = next_prompt

                    if next_field_to_fill == "generate_questions":
                        ack_message = assistant_response_content.format(
                            tech_stack=st.session_state.applicant_info.tech_stack
                        )
                        with st.chat_message("assistant"):
                            st.markdown(ack_message)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": ack_message}
                        )

                        with st.chat_message("assistant"):
                            with st.spinner("Generating technical questions..."):
                                tech_questions = generate_technical_questions(
                                    st.session_state.applicant_info.tech_stack
                                )
                            st.markdown(tech_questions)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": tech_questions}
                        )

                        assistant_response_content = "Thank you for answering the questions. That's all I need for now. The TalentScout team will review your submission and get back to you soon. Have a great day!"
                        st.session_state.conversation_finished = True
                        st.session_state.current_field_to_fill = None

                except ValidationError as e:
                    assistant_response_content = (
                        f"Validation Error: {e.errors()[0]['msg']}. Please try again."
                    )
                except ValueError as e:
                    assistant_response_content = f"Input Error: {e}. Please try again."
                except Exception as e:
                    assistant_response_content = (
                        f"An unexpected error occurred: {e}. Please try again."
                    )
            else:
                assistant_response_content = (
                    "I'm sorry, I didn't quite understand that. Let's start over."
                )
                st.session_state.conversation_finished = True

        if assistant_response_content:
            with st.chat_message("assistant"):
                st.markdown(assistant_response_content)
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_response_content}
            )

if st.session_state.conversation_finished:
    st.success("The initial screening is complete. Here is the information collected:")
    st.json(st.session_state.applicant_info.model_dump())

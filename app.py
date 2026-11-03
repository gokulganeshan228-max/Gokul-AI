import streamlit as st
import ollama
import json
import uuid
from pathlib import Path
from datetime import datetime
from chatbot.documents import extract_text

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="Gokul AI",
    page_icon="🤖",
    layout="wide"
)

MODEL = "llama3.2:3b"
HISTORY_FILE = Path("chat_history.json")

SYSTEM_PROMPT = """
You are a helpful AI assistant.
Give accurate, clear and friendly answers.
Explain technical topics with simple examples.
"""

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

.main-title {
    font-size: 36px;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin-top: 80px;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    font-size: 16px;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid #30363d;
    background-color: #21262d;
    color: white;
    width: 100%;
}

div.stButton > button:hover {
    background-color: #30363d;
    border-color: #58a6ff;
    color: white;
}

[data-testid="stChatInput"] {
    border-radius: 15px;
}

.history-title {
    color: #9ca3af;
    font-size: 13px;
    font-weight: bold;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- CHAT HISTORY FUNCTIONS ----------------

def load_history():

    if HISTORY_FILE.exists():

        try:
            with open(HISTORY_FILE, "r") as file:
                data = json.load(file)

            if isinstance(data, dict):
                return data

        except (json.JSONDecodeError, OSError):
            pass

    return {}


def save_history():

    with open(HISTORY_FILE, "w") as file:
        json.dump(
            st.session_state.chats,
            file,
            indent=4
        )


# ---------------- SESSION INITIALIZATION ----------------

if "chats" not in st.session_state:

    st.session_state.chats = load_history()


if "active_chat" not in st.session_state:

    st.session_state.active_chat = None


# ---------------- CHAT MANAGEMENT ----------------

def create_new_chat():

    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "updated_at": datetime.now().isoformat()
    }

    st.session_state.active_chat = chat_id

    save_history()


def delete_chat(chat_id):

    if chat_id in st.session_state.chats:

        del st.session_state.chats[chat_id]

        if st.session_state.active_chat == chat_id:
            st.session_state.active_chat = None

        save_history()


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("🤖 Gokul AI")

    st.caption("Your Personal AI Assistant")

    st.divider()

    if st.button("＋  New Chat", use_container_width=True):

        create_new_chat()
        st.rerun()

    st.markdown(
        '<p class="history-title">YOUR CONVERSATIONS</p>',
        unsafe_allow_html=True
    )

    # Sort conversations by latest activity

    sorted_chats = sorted(
        st.session_state.chats.items(),
        key=lambda item: item[1].get("updated_at", ""),
        reverse=True
    )

    for chat_id, chat in sorted_chats:

        col1, col2 = st.columns([0.80, 0.20])

        with col1:

            if st.button(
                "💬 " + chat["title"][:25],
                key="open_" + chat_id,
                use_container_width=True
            ):

                st.session_state.active_chat = chat_id
                st.rerun()

        with col2:

            if st.button(
                "🗑️",
                key="delete_" + chat_id
            ):

                delete_chat(chat_id)
                st.rerun()

    st.divider()

    st.caption("Model: Llama 3.2:3B")

    st.caption("Powered by Ollama")
    st.sidebar.subheader("📁 Upload Documents")

uploaded_file = st.sidebar.file_uploader(
    "Upload PDF, DOCX or TXT",
    type=["pdf", "docx", "txt"]
)

if uploaded_file is not None:

    file_path = f"temp_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        extracted_text = extract_text(file_path)

        st.session_state.document_text = extracted_text
        st.session_state.document_name = uploaded_file.name

        st.sidebar.success("Document uploaded successfully!")

    except Exception as e:
        st.sidebar.error(f"Error: {e}")


# ---------------- MAIN CHAT AREA ----------------

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if st.session_state.document_text:

    st.subheader(
        f"📄 Document: {st.session_state.document_name}"
    )

    question = st.text_input(
        "Ask something about your document"
    )

    if st.button("Ask AI") and question:

        with st.spinner("AI is reading your document..."):

            response = ollama.chat(
                model="llama3.2:3b",
                messages=[
                    {
                        "role": "system",
                        "content": "Answer questions using the provided document. If the answer is not present, say so."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Document:
                        {st.session_state.document_text}

                        Question:
                        {question}
                        """
                    }
                ],
                options={"num_predict": 300}
            )

            st.write(response["message"]["content"])
            
# Create a new chat automatically if none exists

if st.session_state.active_chat is None or st.session_state.active_chat not in st.session_state.chats:

    st.markdown(
        '<div class="main-title">Welcome to Gokul AI 👋</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Your personal AI assistant. Ask me anything!</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("💡 **Learn Something**\n\nExplain complex topics simply.")

    with col2:
        st.info("💻 **Coding Help**\n\nGet help with Python and programming.")

    with col3:
        st.info("🚀 **Explore AI**\n\nUnderstand LLMs and Generative AI.")

    messages = []

else:

    current_chat = st.session_state.chats[st.session_state.active_chat]
    messages = current_chat["messages"]

    st.subheader("💬 " + current_chat["title"])
    


# ---------------- DISPLAY CHAT MESSAGES ----------------

for message in messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ---------------- USER INPUT ----------------

user_input = st.chat_input("Message Gokul AI...")


if user_input:

    # Create a chat if one doesn't exist

    if (
        st.session_state.active_chat is None
        or st.session_state.active_chat not in st.session_state.chats
    ):

        create_new_chat()

    active_id = st.session_state.active_chat

    current_chat = st.session_state.chats[active_id]

    # Save user message

    current_chat["messages"].append({
        "role": "user",
        "content": user_input
    })

    # Generate chat title from first question

    if current_chat["title"] == "New Chat":

        current_chat["title"] = user_input[:30]

    current_chat["updated_at"] = datetime.now().isoformat()

    save_history()

    # Display user message

    with st.chat_message("user"):

        st.markdown(user_input)

    # Generate AI response

    with st.chat_message("assistant"):

        with st.spinner("Gokul AI is thinking..."):

            try:

                response = ollama.chat(

                    model=MODEL,

                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        *current_chat["messages"]
                    ],

                    options={
                        "temperature": 0.7,
                        "num_predict": 300
                    },

                    keep_alive="30m"
                )

                ai_response = response["message"]["content"]

                st.markdown(ai_response)

                # Save assistant response

                current_chat["messages"].append({
                    "role": "assistant",
                    "content": ai_response
                })

                current_chat["updated_at"] = datetime.now().isoformat()

                save_history()

            except Exception as e:

                st.error(f"Something went wrong: {e}")
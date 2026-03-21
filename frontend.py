import streamlit as st
import time
from query_data import llm_response
from create_database import create_databse
from chat_db import load_chat, save_message

st.set_page_config(page_title="RAG Document Chat", page_icon="📄", layout="centered")

# ── Session state ──
if "chats" not in st.session_state:
    st.session_state.chats = []
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ══════════════════════════════════════════
#  STEP 1 — Upload screen
# ══════════════════════════════════════════
st.title("📄 RAG Document Chat")
st.divider()

if not st.session_state.chats:
    st.subheader("Upload a document to get started")
    uploaded = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "docx", "md"],
        help="Supported formats: PDF, TXT, DOCX, Markdown",
    )

    if uploaded is not None:
        with st.spinner("Indexing document… please wait"):
            collection_name = create_databse(uploaded)
            time.sleep(1.5)
        st.session_state.chats.append(
            {"name": uploaded.name, "collection": collection_name}
        )
        st.session_state.active_chat = {
            "name": uploaded.name,
            "collection": collection_name,
        }
        st.session_state.chat_history = []
        st.rerun()

# ══════════════════════════════════════════
#  STEP 2 — Chat screen
# ══════════════════════════════════════════
else:
    with st.sidebar:
        if "show_uploader" not in st.session_state:
            st.session_state.show_uploader = False

        if st.button("🔄 New File", use_container_width=True):
            st.session_state.show_uploader = True

        if st.session_state.show_uploader:
            uploaded = st.file_uploader(
                "Choose a file",
                type=["pdf", "txt", "docx", "md"],
                help="Supported formats: PDF, TXT, DOCX, Markdown",
            )
            if uploaded is not None:
                with st.spinner("Indexing document… please wait"):
                    collection = create_databse(uploaded)
                    time.sleep(1.5)
                st.session_state.chats.append(
                    {"name": uploaded.name, "collection": collection}
                )
                st.session_state.active_chat = {
                    "name": uploaded.name,
                    "collection": collection,
                }
                st.session_state.chat_history = load_chat(collection_name=collection)
                st.session_state.show_uploader = False
                st.rerun()

        st.title("History")
        for item in st.session_state.chats:

            if st.button(
                item["name"],
                use_container_width=True,
                key=item["name"],
                type=(
                    "primary"
                    if st.session_state.active_chat["name"] == item["name"]
                    else "secondary"
                ),
            ):
                st.session_state.active_chat = {
                    "name": item["name"],
                    "collection": item["collection"],
                }
                st.session_state.chat_history = load_chat(
                    collection_name=item["collection"]
                )
                st.rerun()

    st.success(f"📎 **{st.session_state.active_chat["name"]}** is loaded and ready")

    st.divider()

    # ── Render chat history ──
    if not st.session_state.chat_history:
        st.info("💬 Ask a question about your document below.")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # ── Chat input ──
    user_input = st.chat_input(
        f"Ask something about {st.session_state.active_chat["name"]}…"
    )

    if user_input and user_input.strip():
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        # Append to history
        save_message(
            collection_name=st.session_state.active_chat["collection"],
            content=user_input.strip(),
            role="user",
        )
        # st.session_state.chat_history.append(
        #     {"role": "user", "content": user_input.strip()}
        # )

        # Show thinking animation while "calling" LLM
        with st.chat_message("assistant"):

            with st.spinner("Thinking…"):
                response = llm_response(
                    user_input,
                    collection_name=st.session_state.active_chat["collection"],
                )
                time.sleep(2)

            st.write(response)
            st.caption(f"📚 Source: {st.session_state.active_chat["name"]}")

        # Append assistant response
        save_message(
            collection_name=st.session_state.active_chat["collection"],
            content=response,
            role="assistant",
        )
        # st.session_state.chat_history.append({"role": "assistant", "content": response})

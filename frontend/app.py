import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(page_title="Mini AI Chat", layout="wide")

if "selected_thread_id" not in st.session_state:
    st.session_state.selected_thread_id = None


def fetch_threads():
    try:
        resp = requests.get(f"{BACKEND_URL}/threads")
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch threads: {e}")
        return []


def create_thread(title: str):
    try:
        resp = requests.post(f"{BACKEND_URL}/threads", json={"title": title})
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Failed to create thread: {e}")
        return None


def fetch_thread_detail(thread_id: int):
    try:
        resp = requests.get(f"{BACKEND_URL}/threads/{thread_id}")
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch thread: {e}")
        return None


def send_message(thread_id: int, message: str):
    try:
        resp = requests.post(f"{BACKEND_URL}/chat/{thread_id}", json={"message": message})
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        st.error(f"Failed to send message: {e}")
        return None


with st.sidebar:
    st.title("Chat Threads")

    with st.form("new_thread_form", clear_on_submit=True):
        new_title = st.text_input("New thread title")
        submitted = st.form_submit_button("Create New Thread")
        if submitted and new_title.strip():
            created = create_thread(new_title.strip())
            if created:
                st.session_state.selected_thread_id = created["id"]
                st.rerun()

    st.markdown("---")

    threads = fetch_threads()
    for thread in threads:
        label = f"{thread['title']} (#{thread['id']})"
        if st.button(label, key=f"thread_{thread['id']}", use_container_width=True):
            st.session_state.selected_thread_id = thread["id"]
            st.rerun()

st.title("Mini AI Chat")

if st.session_state.selected_thread_id is None:
    st.info("Create or select a thread from the sidebar to start chatting.")
else:
    thread_detail = fetch_thread_detail(st.session_state.selected_thread_id)

    if thread_detail:
        st.subheader(thread_detail["title"])

        for msg in thread_detail["messages"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Type your message...")
        if user_input:
            result = send_message(st.session_state.selected_thread_id, user_input)
            if result:
                st.rerun()

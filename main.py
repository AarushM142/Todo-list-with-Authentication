import streamlit as st
from supabase import create_client, Client

# ----------------------------------------------------
#   ALWAYS READ FROM st.secrets (Cloud-safe)
# ----------------------------------------------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

# Create Supabase client
supabase: Client = create_client(url, key)

# ----------------------------------------------------
#   AUTH FUNCTIONS
# ----------------------------------------------------
def sign_up(email, password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})

        # Supabase duplicate email detection
        if hasattr(user, "user") and user.user is not None:
            identities = user.user.identities

            if identities is not None and len(identities) == 0:
                st.error("This email is already registered. Please log in instead.")
                return None

            return user

        st.error("Registration failed. Please try again.")
        return None

    except Exception as e:
        st.error(f"Registration failed: {e}")
        return None


    except Exception as e:
        message = str(e).lower()

        # Explicit message check (Supabase error pattern)
        if "duplicate key value" in message or "already registered" in message:
            st.error("This email is already registered. Please log in instead.")
        else:
            st.error(f"Registration failed: {e}")

        return None

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Login Failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.session_state.user_id = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout Failed: {e}")

# ----------------------------------------------------
#   MAIN APP (To-Do dashboard)
# ----------------------------------------------------
def main_app(user_email, user_id):
    st.title("Dashboard")
    st.success(f"Welcome, {user_email}!")

    if st.button("Logout"):
        sign_out()

    # Functions to interact with "todos" table
    def get_todos():
        return supabase.table("todos").select("*").eq("user_id", user_id).order("id").execute().data

    def add_todo(task):
        supabase.table("todos").insert({"task": task, "user_id": user_id}).execute()

    def del_todo(task_id):
        supabase.table("todos").delete().eq("id", task_id).eq("user_id", user_id).execute()

    st.title("Supabase To-Do App")

    # Add task
    task1 = st.text_input("Add a new task:")
    if st.button("Add Task"):
        if task1:
            add_todo(task1)
            st.success("Task added!")
            st.rerun()
        else:
            st.error("Please enter a task")

    # Display tasks
    st.write("### To-Do List")
    todos = get_todos()

    if todos:
        for i, item in enumerate(todos, start=1):
            edit_key = f"editing-{item['id']}"
            input_key = f"input-{item['id']}"

            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            if input_key not in st.session_state:
                st.session_state[input_key] = item["task"]

            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

            with col1:
                st.markdown(f"{i}. {item['task']}")

            with col2:
                if st.button("Edit", key=f"edit-{item['id']}"):
                    st.session_state[edit_key] = True

                if st.session_state[edit_key]:
                    edited_task = st.text_input("Update Task:", value=st.session_state[input_key], key=input_key)

                    if st.button("Save", key=f"save-{item['id']}"):
                        supabase.table("todos").update({"task": edited_task}).eq("id", item["id"]).eq("user_id", user_id).execute()
                        st.session_state[edit_key] = False
                        st.rerun()

            with col3:
                if st.button("Delete", key=f"del-{item['id']}"):
                    del_todo(item["id"])
                    st.rerun()

    else:
        st.write("No tasks available.")

# ----------------------------------------------------
#   AUTH SCREEN
# ----------------------------------------------------
def auth_screen():
    st.title("Authentication Page")

    option = st.selectbox("Choose an action:", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Sign Up" and st.button("Register"):
        user = sign_up(email, password)
        if user and user.user:
            st.success("Registration successful, please Login")

    if option == "Login" and st.button("Login"):
        user = sign_in(email, password)
        if user and user.user:
            st.session_state.user_email = user.user.email
            st.session_state.user_id = user.user.id
            st.success(f"Welcome back, {email}!")
            st.rerun()

# ----------------------------------------------------
#   SESSION HANDLING
# ----------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_email:
    main_app(st.session_state.user_email, st.session_state.user_id)
else:
    auth_screen()

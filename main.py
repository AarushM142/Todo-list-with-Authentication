import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv() 
#this loads the variables from the .env file so that sensetive credentials like API keys are loaded securely

url= os.getenv("SUPABASE_URL")
key= os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url,key)
#this enable supabase methods to be used with this variable supabase
def sign_up(email, password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email,password):
    try:
        user=supabase.auth.sign_in_with_password({"email":email, "password":password})
        return user
    except Exception as e:
        st.error(f"Login Failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email=None
        st.rerun()
    except Exception as e:
        st.error(f"Logout Failed: {e}")

def main_app(user_email, user_id):
    st.title("Dashboard")
    st.success(f"Welcome, {user_email}!")
    if st.button("Logout"):
        sign_out()
    def get_todos():
        response= supabase.table('todos').select('*').eq("user_id", user_id).order('id', desc=False).execute()
        return response.data

    def add_todo(task):
        supabase.table('todos').insert({'task':task, 'user_id': user_id}).execute()
        #when this func is called, with insert function, it creates a dictionary(row) with every key called 'task' and the value for that is passed thru the argument varibale task

    def del_todo(task_id):
        supabase.table('todos').delete().eq("id", task_id).eq('user_id', user_id).execute()

    st.title("Supabase To-Do App")

    task1=st.text_input("Add a new task:")

    clickedAdd = st.button("Add Task")

    if clickedAdd: #checks if button was clicked
        if task1: #checks if any character was input in the text box
            add_todo(task1)
            st.success("Task added!")
            st.rerun()
        else:
            st.error("Please enter a task")



    st.write("### To-Do List:")
    todos= get_todos()




    if todos!=False: #if the todo list is empty, todos will return false hence this will check that
        
        for i,item in enumerate (todos, start=1): #todos contains many dictionaries, item loops thru each dictionary and 'task' is the key for each dictionary so in the end you get the value of the 'task' key in each dictionary in the todos table 

            edit_key = f"editing-{item['id']}"
            input_key = f"input-{item['id']}"

            if edit_key not in st.session_state:
                st.session_state[edit_key] = False
            if input_key not in st.session_state:
                st.session_state[input_key] = item['task']


            col1,col2,col3= st.columns([0.6,0.2,0.2])

            with col1:
                st.markdown(f"{i}. {item['task']}")

            with col2:
                if st.button("Edit Task", key=f"edit-{item['id']}"):
                    st.session_state[edit_key]= True
                    
                if st.session_state[edit_key]:
                    
                    edited_task=st.text_input("Update Task:", value= st.session_state[input_key], key=input_key)
                    
                    if st.button("Save", key=f"save-{item['id']}"):
                        supabase.table('todos').update({'task':edited_task}).eq("id",item['id']).eq("user_id", user_id).execute()
                        st.session_state[edit_key]= False
                        st.rerun()

            with col3:
                if st.button("Delete Task", key=f"del-{item['id']}"): #here f string is used to make sure integer causes no error, and del word is just to understand like for example the button to delete task 1 has the key = del-1
                    del_todo(item['id'])
                    st.rerun()

    else:
        st.write("No tasks available.")



    
def auth_screen():
    st.title("Authentication Page")
    option=st.selectbox("Choose an action:", ["Login","Sign Up"])
    email= st.text_input("Email")
    password= st.text_input("Password", type= "password")

    if option == "Sign Up" and st.button("Register"):
        user= sign_up(email,password)
        if user and user.user:
            st.success(f"Registration successful, please Login")
        

    if option == "Login" and st.button("Login"):
        user= sign_in(email,password)
        if user and user.user:
            st.session_state.user_email= user.user.email
            st.session_state.user_id=user.user.id
            st.success(f"Welcome back, {email}!")
            st.rerun()
if "user_email" not in st.session_state:
    st.session_state.user_email= None
if "user_id" not in st.session_state:
    st.session_state.user_id= None

if st.session_state.user_email:
    main_app(st.session_state.user_email, st.session_state.user_id)
else:
    auth_screen()




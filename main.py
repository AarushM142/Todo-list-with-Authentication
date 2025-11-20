import streamlit as st
from supabase import create_client
from supabase import Client
from dotenv import load_dotenv
import os

load_dotenv() 
#this loads the variables from the .env file so that sensetive credentials like API keys are loaded securely

url= os.getenv("SUPABASE_URL")
key= os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url,key)
#this enable supabase methods to be used with this variable supabase

def get_todos():
    response= supabase.table('todos').select('*').execute()
    return response.data

def add_todo(task):
    supabase.table('todos').insert({'task':task}).execute()
    #when this func is called, with insert function, it creates a dictionary(row) with every key called 'task' and the value for that is passed thru the argument varibale task

def del_todo(task):
    supabase.table('todos').delete().eq("id", task).execute()

st.title("Supabase To-Do App")

task1=st.text_input("Add a new task:")

clickedAdd = st.button("Add Task")

if clickedAdd: #checks if button was clicked
    if task1: #checks if any character was input in the text box
        add_todo(task1)
        st.success("Task added!")
    else:
        st.error("Please enter a task")



st.write("### To-Do List:")
todos= get_todos()

if todos!=False: #if the todo list is empty, todos will return false hence this will check that
    for i,item in enumerate (todos, start=1): #todos contains many dictionaries, item loops thru each dictionary and 'task' is the key for each dictionary so in the end you get the value of the 'task' key in each dictionary in the todos table 
        col1,col2= st.columns([1,1])

        with col1:
            st.markdown(f"{i}. {item['task']}")
        with col2:
            if st.button("Delete Task", key=f"del-{item['id']}"): #here f string is used to make sure integer causes no error, and del word is just to understand like for example the button to delete task 1 has the key = del-1
                del_todo(item['id'])
                st.rerun()

else:
    st.write("No tasks available.")

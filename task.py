import streamlit as st
import pandas as pd
import os
import time

# --- CSV Setup ---
CSV_FILE = "tasks.csv"

if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Task", "Assigned_To", "Status", "Deadline", "Assigned_By"])
    df.to_csv(CSV_FILE, index=False)

def load_tasks():
    return pd.read_csv(CSV_FILE)

def save_tasks(df):
    df.to_csv(CSV_FILE, index=False)

# --- App Title ---
st.title("✨ PM - PMO Tasks 🗒️")

st.markdown("""
    <style>
    div.stButton > button {
        background: #4A4A4A;
        border-radius: 8px;
        color: white;
        padding: 8px 16px;
        margin: 4px;
        transition: background 0.3s;
    }

    div.stButton > button:hover {
        background: #6A6A6A;
    }

    .task-card {
        padding: 12px;
        margin: 10px 0;
        border-radius: 10px;
        background: black;
        color: white;
        transition: transform 0.2s;
    }

    .task-card:hover {
        transform: scale(1.02);
    }

    .completed-task {
        text-decoration: line-through;
    }

    </style>
    """, unsafe_allow_html=True)

df = load_tasks()

# --- Navigation ---
page = st.sidebar.radio("Navigate", ["Soha's Tasks 😎", "Alex's Tasks 👨‍💼", "Tasks Assigned to Soha by Alex 📋", "Search Tasks 🔍"])

# --- Add Task ---
if page in ["Soha's Tasks 😎", "Alex's Tasks 👨‍💼", "Tasks Assigned to Soha by Alex 📋"]:
    new_task = st.text_input("➕ Add a new task")
    deadline = st.date_input("📅 Deadline", value=None, key="deadline_input")

    if st.button("Add Task") and new_task:
        if page == "Soha's Tasks 😎":
            assignee, assigned_by = "Soha", "Soha"
        elif page == "Alex's Tasks 👨‍💼":
            assignee, assigned_by = "Alex", "Alex"
        else:
            assignee, assigned_by = "Soha", "Alex"

        new_task_data = {
            "Task": new_task,
            "Assigned_To": assignee,
            "Status": "Pending",
            "Deadline": deadline if deadline else "",
            "Assigned_By": assigned_by
        }
        df = pd.concat([df, pd.DataFrame([new_task_data])], ignore_index=True)
        save_tasks(df)
        st.balloons()
        time.sleep(1)
        st.rerun()

# --- Display Tasks ---
def display_tasks(title, task_df):
    st.subheader(title)

    for index, row in task_df.iterrows():
        task_text = f"{row['Task']} - Assigned to: {row['Assigned_To']}"
        if row['Deadline']:
            task_text += f" - Deadline: {row['Deadline']}"

        completed = st.checkbox("", key=f"chk_{index}", value=(row['Status'] == 'Completed'))

        task_style = "completed-task" if completed else ""

        st.markdown(f"<div class='task-card {task_style}'>{task_text}</div>", unsafe_allow_html=True)

        if completed and row['Status'] != 'Completed':
            df.at[index, 'Status'] = 'Completed'
            save_tasks(df)
            st.toast("Task marked as completed!", icon="✅")
            st.rerun()

        if st.button("🗑️", key=f"del_{index}"):
            df.drop(index, inplace=True)
            df.reset_index(drop=True, inplace=True)
            save_tasks(df)
            st.toast("Task deleted!", icon="🗑️")
            st.rerun()

        if st.button("✏️ Edit", key=f"edit_{index}"):
            with st.form(key=f"edit_form_{index}"):
                new_task = st.text_input("Edit Task", row['Task'])
                new_deadline = st.date_input("Edit Deadline", pd.to_datetime(row['Deadline']) if row['Deadline'] else None)
                if st.form_submit_button("Save Changes"):
                    df.at[index, 'Task'] = new_task
                    df.at[index, 'Deadline'] = new_deadline if new_deadline else ""
                    save_tasks(df)
                    st.toast("Task updated!", icon="✏️")
                    st.rerun()

# --- Page Logic ---
if page == "Soha's Tasks 😎":
    soha_tasks = df[(df["Assigned_To"] == "Soha")]
    display_tasks("📝 Soha's Tasks", soha_tasks)

elif page == "Alex's Tasks 👨‍💼":
    alex_tasks = df[(df["Assigned_To"] == "Alex")]
    display_tasks("📋 Alex's Tasks", alex_tasks)

elif page == "Tasks Assigned to Soha by Alex 📋":
    assigned_by_alex = df[(df["Assigned_To"] == "Soha") & (df["Assigned_By"] == "Alex")]
    display_tasks("📌 Tasks Assigned to Soha by Alex", assigned_by_alex)

elif page == "Search Tasks 🔍":
    search_query = st.text_input("🔍 Search for a task")
    if search_query:
        search_results = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
        display_tasks("🔎 Search Results", search_results)
import streamlit as st
import subprocess
import time
import os
import re
from streamlit_extras.stylable_container import stylable_container

def extract_command(command_string):
    match = re.search(r"<span style=\"color:green\">(.*?)</span>", command_string)
    if match:
        return match.group(1)
    return ""

def run_command(command, placeholder, loader_placeholder):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = ""
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break
        if line:
            output += line
            st.session_state['output'] = output.replace('\n', '<br>')
            placeholder.markdown(f"<div style='background-color: #1a1c24; color: #ffffff; font-family: monospace; white-space: pre-wrap; height: 300px; width: 100%; overflow-y: auto; padding: 10px; border-radius: 10px;'>{st.session_state['output']}</div><div id='end-of-output'></div>", unsafe_allow_html=True)
            scroll_js = """
            <script>
            var element = document.getElementById("end-of-output");
            element.scrollIntoView({behavior: "smooth"});
            </script>
            """
            st.markdown(scroll_js, unsafe_allow_html=True)
            time.sleep(0.1)  # Add a small delay to simulate real-time streaming # Add a small delay to simulate real-time streaming
    rc = process.poll()
    output += f"\nProcess finished with return code {rc}\n"
    # Update loader to tick mark
    if loader_placeholder:
        loader_placeholder.markdown("<span class='tick-mark'>&#x2714;</span>", unsafe_allow_html=True)
    return output

commands = [
    "DKubex Embedding models catalog <br>  <span style=\"color:green\">d3x emb list</span>",
    "DKubex LLM models catalog <br> <span style=\"color:green\">d3x llms list</span>",
    "Deploy bge-large embedding model on cloud <br> <span style=\"color:green\">d3x emb deploy --model BAAI--bge-large-en-v1-5 -n bgedemo -sky --config /app/repo/cmdyamls/emb.yaml</span>",
    "Deploy llama38B LLM on cloud <br>  <span style=\"color:green\">d3x llms deploy -n llama3demo --model meta-llama/Meta-Llama-3-8B-Instruct --token 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 -sky --config /app/repo/cmdyamls/llms.yaml</span>",
    "List all the deployments <br>  <span style=\"color:green\">d3x serve list</span>",
    "Create dataset by ingesting documents <br>  <span style=\"color:green\">d3x dataset ingest -d food --config /app/repo/cmdyamls/ingest.yaml</span>",
    "List all the datasets <br>  <span style=\"color:green\">d3x dataset list</span>",
    "Create a securechat app to interact with RAG <br>  <span style=\"color:green\">d3x apps create --config /app/repo/cmdyamls/rag.yaml</span>",
    "Run evaluation on the dataset <br> <span style=\"color:green\">d3x dataset evaluate -d food --config /app/repo/cmdyamls/eval.yaml</span>"
]

# Yaml file paths for corresponding commands for display purposes
yaml_paths = [
    "/home/oc/Downloads/emb.yaml",
    None,
    "/home/oc/Downloads/ingest.yaml",
    "/app/repo/demoyamls/llms.yaml",
    None,
    "/app/repo/demoyamls/ingest.yaml",
    None,
    "/app/repo/demoyamls/rag.yaml",
    "/app/repo/demoyamls/eval.yaml"
]

# Initialize session state variables if not already present
if 'current_command_index' not in st.session_state:
    st.session_state['current_command_index'] = 0
if 'outputs' not in st.session_state:
    st.session_state['outputs'] = [""] * len(commands)
if 'commands_run' not in st.session_state:
    st.session_state['commands_run'] = [False] * len(commands)
if 'output' not in st.session_state:
    st.session_state['output'] = ""
if 'running' not in st.session_state:
    st.session_state['running'] = False
if 'show_yaml' not in st.session_state:
    st.session_state['show_yaml'] = False
# Custom CSS
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stTextArea textarea {
        font-family: monospace;
        white-space: pre-wrap;
        overflow-wrap: break-word;
    }
    @media (max-width: 600px) {
        .stButton > button {
            width: 100%;
        }
        .stTextArea textarea {
            height: 400px;
        }
    }
    .stButton {
        margin-right: 10px;
    }
    .title-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .spinner {
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-top: 4px solid blue;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
        margin-left: 10px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .tick-mark {
        font-size: 1.5em;
        color: green;
    }
    .command-placeholder {
        background-color: #1a1c24;
        color: #ffffff;
        font-family: monospace;
        white-space: pre-wrap;
        padding: 10px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        height: 60px;
        margin-bottom: 20px;
    }
    .command-text {
        margin: 0;
    }
    .button-container {
        margin-bottom: 20px;
    }
    .yaml-popup {
        max-width: 80%;
        margin: 0 auto;
    }
    .terminal-output {
        background-color: #1a1c24;
        color: #ffffff;
        font-family: monospace;
        white-space: pre-wrap;
        height: 300px; /* Fixed height */
        width: 100%;
        overflow-y: auto;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("DKubex Live Demo")

col1, col2 = st.columns([30, 1])

with col2:
    loader_placeholder = st.empty()
    if st.session_state['running']:
        loader_placeholder.markdown("<div class='spinner'></div>", unsafe_allow_html=True)
    elif st.session_state['commands_run'][st.session_state['current_command_index']]:
        loader_placeholder.markdown("<span class='tick-mark'>&#x2714;</span>", unsafe_allow_html=True)


# Extract and display the command to be executed with custom styling
current_command = extract_command(commands[st.session_state['current_command_index']])
st.markdown(
    f"""
    <div class='command-placeholder'>
       <br> <span class='command-text'>{commands[st.session_state['current_command_index']]}</span><br>
    </div>
    """,
    unsafe_allow_html=True
)



# Create a container for the Run Command button
button_container = st.columns([3, 4, 2, 2, 2, 2])
with button_container[0]:
    run_button = st.button("Run Command", key='run', use_container_width=True, disabled=st.session_state['running'] or st.session_state['commands_run'][st.session_state['current_command_index']])

with button_container[2]:
    # Display View Configuration button if YAML path is available
    yaml_path = yaml_paths[st.session_state['current_command_index']]
    if yaml_path and os.path.exists(yaml_path):
        view_config_button = st.button("View Configuration", key='view_config', use_container_width=True)
        if view_config_button:
            st.session_state['show_yaml'] = not st.session_state['show_yaml']

# Show the YAML content in an expander if the button is clicked
if st.session_state['show_yaml'] and yaml_path and os.path.exists(yaml_path):
    st.markdown(
        """
        <style>
        .streamlit-expanderHeader {
            width: 66.67vw; /* 2/3 of the viewport width */
            max-width: 66.67vw; /* Ensure the width doesn't exceed 2/3 of viewport width */
            left: 50%;
            transform: translateX(-50%);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    with st.expander("YAML Configuration", expanded=True):
        with open(yaml_path, 'r') as file:
            yaml_content = file.read()
        st.code(yaml_content, language='yaml')

with button_container[4]:
    prev_button = st.button("Previous", key='previous', use_container_width=True, disabled=st.session_state['running'] or st.session_state['current_command_index'] == 0)
with button_container[5]:
    next_button = st.button("Next", key='next', use_container_width=True, disabled=st.session_state['running'] or st.session_state['current_command_index'] >= len(commands) - 1)

# Create placeholders for the terminal output and loader
terminal_placeholder = st.empty()
loader_placeholder = st.empty()

# Run command and display output
if st.session_state['running']:
    output = run_command(current_command, terminal_placeholder, loader_placeholder)
    st.session_state['outputs'][st.session_state['current_command_index']] = output
    st.session_state['output'] = output
    st.session_state['running'] = False
    st.rerun()  # Trigger a rerun

# Always display terminal output below YAML
terminal_placeholder.markdown(f"<div style='background-color: #1a1c24; color: #ffffff; font-family: monospace; white-space: pre-wrap; height: auto; width: 100%; overflow-y: auto; padding: 10px; border-radius: 10px;'>{st.session_state['output']}</div><div id='end-of-output'></div>", unsafe_allow_html=True)

# Button functionality
if run_button and not st.session_state['running']:
    st.session_state['running'] = True
    st.session_state['commands_run'][st.session_state['current_command_index']] = True
    st.rerun()  # Trigger a rerun

if prev_button:
    st.session_state['current_command_index'] -= 1
    st.session_state['output'] = st.session_state['outputs'][st.session_state['current_command_index']]
    st.rerun()  # Trigger a rerun

if next_button:
    st.session_state['current_command_index'] += 1
    st.session_state['output'] = st.session_state['outputs'][st.session_state['current_command_index']]
    st.rerun()  # Trigger a rerun

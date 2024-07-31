import streamlit as st
import subprocess
import time
import os

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
            # Update output in the UI
            placeholder.markdown(f"<div style='background-color: #1a1c24; color: #ffffff; font-family: monospace; white-space: pre-wrap; height: 350px; overflow-y: auto; padding: 10px; border-radius: 10px;'>{st.session_state['output']}</div><div id='end-of-output'></div>", unsafe_allow_html=True)
            # Scroll to bottom using JS
            scroll_js = """
            <script>
            var element = document.getElementById("end-of-output");
            element.scrollIntoView({behavior: "smooth"});
            </script>
            """
            st.markdown(scroll_js, unsafe_allow_html=True)
            time.sleep(0.1)  # Add a small delay to simulate real-time streaming
    rc = process.poll()
    output += f"\nProcess finished with return code {rc}\n"
    # Update loader to tick mark
    loader_placeholder.markdown("<span class='tick-mark'>&#x2714;</span>", unsafe_allow_html=True)
    return output

commands = [
    "d3x emb deploy --model BAAI--bge-large-en-v1-5 -n bgecloud -sky",
    "d3x emb list",
    "d3x llms deploy -n llama3cloud --model meta-llama/Meta-Llama-3-8B-Instruct  --type=a10 --token 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 --publish -sky",
    "d3x llms list",
    "d3x serve list",
    "d3x dataset ingest -d food --config /home/food_processing/demo_ingest.yaml",
    "d3x dataset list",
    "d3x apps create --config /home/food_processing/securechat.yaml",
    "d3x dataset evaluate -d Foodprocessing --config /home/food_processing/demo_eval.yaml"
]

# Yaml file paths for corresponding commands
yaml_paths = [
    "/app/demoyamls/emb.yaml",
    None,
    "/app/demoyamls/llms.yaml",
    None,
    None,
    "/app/demoyamls/ingest.yaml",
    None,
    "/app/demoyamls/query.yaml",
    "/app/demoyamls/eval.yaml"
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

# Custom CSS to make the app full width and responsive
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
            height: 200px;
        }
    }
    .stButton {
        margin-right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .spinner {
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-top: 4px solid blue;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 1s linear infinite;
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
    </style>
    """,
    unsafe_allow_html=True
)

st.title("DKubex Live Demo")

# Display the current command with the loader beside it
col1, col2 = st.columns([30, 1])
# with col1:
#     st.write("Current Command:")
with col2:
    loader_placeholder = st.empty()
    if st.session_state['running']:
        loader_placeholder.markdown("<div class='spinner'></div>", unsafe_allow_html=True)
    elif st.session_state['commands_run'][st.session_state['current_command_index']]:
        loader_placeholder.markdown("<span class='tick-mark'>&#x2714;</span>", unsafe_allow_html=True)

# Display the command to be executed with custom styling
st.markdown(
    f"""
    <div class='command-placeholder'>
        <span class='command-text'>{commands[st.session_state['current_command_index']]}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Create a container for the Run Command button and terminal output
with st.container():
    # Button to run the command
    button_container = st.columns([3, 18, 2, 2])
    with button_container[0]:
        run_button = st.button("Run Command", key='run', use_container_width=True, disabled=st.session_state['running'] or st.session_state['commands_run'][st.session_state['current_command_index']])
    with button_container[2]:
        prev_button = st.button("Previous", key='previous', use_container_width=True, disabled=st.session_state['running'] or st.session_state['current_command_index'] == 0)
    with button_container[3]:
        next_button = st.button("Next", key='next', use_container_width=True, disabled=st.session_state['running'] or st.session_state['current_command_index'] >= len(commands) - 1)

    # Create a placeholder for the terminal output
    terminal_placeholder = st.empty()
    # Initialize terminal placeholder
    terminal_placeholder.markdown("<div style='background-color: #1a1c24; color: #ffffff; font-family: monospace; white-space: pre-wrap; height: 350px; width: 100%; overflow-y: auto; padding: 10px; border-radius: 10px; margin-bottom: 20px;'></div><div id='end-of-output'></div>", unsafe_allow_html=True)

    if st.session_state['running']:
        output = run_command(commands[st.session_state['current_command_index']], terminal_placeholder, loader_placeholder)
        st.session_state['outputs'][st.session_state['current_command_index']] = output
        st.session_state['output'] = output
        st.session_state['running'] = False
        st.experimental_rerun()

    # Display terminal output
    terminal_placeholder.markdown(f"<div style='background-color: #1a1c24; color: #ffffff; font-family: monospace; white-space: pre-wrap; height: 350px; width: 100%; overflow-y: auto; padding: 10px; border-radius: 10px; margin-bottom: 20px;'>{st.session_state['output']}</div><div id='end-of-output'></div>", unsafe_allow_html=True)

    # Display the configuration if available
    yaml_path = yaml_paths[st.session_state['current_command_index']]
    if yaml_path:
        st.markdown("<h4>Configuration</h4>", unsafe_allow_html=True)
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as file:
                yaml_content = file.read()
                st.markdown(f"<div style='background-color: #1a1c24; color: #ffffff; font-family: monospace; white-space: pre-wrap; padding: 10px; border-radius: 10px; margin-bottom: 20px;'>{st.code(yaml_content, language='yaml')}</div>", unsafe_allow_html=True)
        else:
            st.markdown("YAML file not found.", unsafe_allow_html=True)

    if run_button:
        st.session_state['running'] = True
        st.session_state['commands_run'][st.session_state['current_command_index']] = True
        st.session_state['output'] = ""
        # Display loader
        loader_placeholder.markdown("<div class='spinner'></div>", unsafe_allow_html=True)
        st.experimental_rerun()

    if prev_button:
        if st.session_state['current_command_index'] > 0:
            st.session_state['current_command_index'] -= 1
            st.session_state['output'] = st.session_state['outputs'][st.session_state['current_command_index']]
            st.experimental_rerun()

    if next_button:
        if st.session_state['current_command_index'] < len(commands) - 1:
            st.session_state['current_command_index'] += 1
            st.session_state['output'] = st.session_state['outputs'][st.session_state['current_command_index']]
            st.experimental_rerun()

# Notify if all commands have been executed
if st.session_state['current_command_index'] >= len(commands):
    st.write("All commands have been executed.")

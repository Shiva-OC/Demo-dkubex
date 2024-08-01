#!/bin/bash
mkdir -p .streamlit/
echo "[server]" > .streamlit/config.toml
echo "baseUrlPath = \"$INGRESS_PREFIX\"" >> .streamlit/config.toml
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0

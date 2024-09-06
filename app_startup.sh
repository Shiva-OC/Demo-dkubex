#!/bin/bash
mkdir -p .streamlit/
echo "[server]" > .streamlit/config.toml
echo "baseUrlPath = \"$INGRESS_PREFIX\"" >> .streamlit/config.toml
echo "[theme]" >> .streamlit/config.toml
echo "base = \"dark\"" >> .streamlit/config.toml
streamlit run demo.py --server.port=8501 --server.address=0.0.0.0

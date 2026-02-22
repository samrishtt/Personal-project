@echo off
echo ==========================================
echo   SynapseForge V2 + SAM-AI Launcher
echo ==========================================
echo.
echo [1/2] Checking dependencies...
pip install streamlit flask pandas plotly python-dotenv requests
echo.
echo [2/2] Starting SynapseForge V2...
echo.
echo IMPORTANT: To see the new 4-phase SAM-AI analysis,
echo make sure you are running this from:
echo d:\sam-ai research grade project\my personal project!!!
echo.
streamlit run app.py --server.port 8501
pause

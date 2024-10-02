FROM python:3.12-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

COPY app.py .
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501"]
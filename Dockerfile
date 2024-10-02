FROM python:3.12-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

COPY ./src/ /app/
ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8501"]
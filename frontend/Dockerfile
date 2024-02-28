FROM python:3.11.6
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /app/
EXPOSE 8501
CMD ["streamlit", "run", "--server.address", "0.0.0.0", "--server.port", "8501", "ui.py"]

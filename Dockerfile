FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pip install redis
RUN mkdir /frontend
WORKDIR /frontend
COPY . /frontend
RUN pip install -r requirements.txt
EXPOSE 8501
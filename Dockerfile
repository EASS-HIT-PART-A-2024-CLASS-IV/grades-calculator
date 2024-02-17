FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pip install redis
<<<<<<< HEAD
=======
RUN mkdir /frontend
WORKDIR /frontend
COPY . /frontend
RUN pip install -r requirements.txt
EXPOSE 8501
>>>>>>> d92ebe0 (update)

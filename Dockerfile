FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update

RUN apt-get install -y libgl1-mesa-glx libglib2.0-0 libzbar-dev && \
    rm -rf /var/lib/apt/lists/*



# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy your project files
COPY . .

# Run Django with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi"]


#dsfsdfds
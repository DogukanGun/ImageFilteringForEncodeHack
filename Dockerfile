
FROM python:3.9

WORKDIR /code

COPY requirements.txt /code/requirements.txt

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx

#
RUN pip install --upgrade -r /code/requirements.txt

#
COPY . /code/

#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

FROM python:alpine AS base

# set /src as the work directory
WORKDIR /src

# copy requirements.txt for installation
COPY requirements.txt /src/

# upgrade pip
RUN pip install --upgrade pip

# install python dependencies
RUN pip install -r /src/requirements.txt

# remove requirements.txt
RUN rm /src/requirements.txt

# copy the src files
COPY *.py /src/

# run the application
CMD [ "python", "/src/main.py" ]

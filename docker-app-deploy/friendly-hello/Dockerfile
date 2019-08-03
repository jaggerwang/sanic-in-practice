# escape=\

# Use latest python
FROM python

# Build args
ARG user
ARG buildno=1

# Set environment variables
ENV NAME World
ENV WORKDIR /app

# Set current working directory
WORKDIR ${WORKDIR}

# Copy all files in current directory on host into container
COPY . /app

# Install pip packages
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# Inform others the listening port of service in container
EXPOSE 80

# Which command to run when start a container
CMD ["python", "app.py"]
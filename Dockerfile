FROM python:3.12-slim-bookworm

WORKDIR /club2

COPY . ./

# Display server and receive server ports
EXPOSE 31337
EXPOSE 31338

ENTRYPOINT ["python3.12", "main.py"]

FROM python:3.11-slim

WORKDIR /sandbox

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    yfinance \
    scipy

# create required directories
RUN mkdir -p /code /output

CMD ["python"]
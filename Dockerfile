FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY wsi_qa ./wsi_qa
RUN pip install --no-cache-dir ".[dev]"
COPY tests ./tests
COPY datasets ./datasets
COPY requirements.csv ./
RUN useradd --create-home runner && chown -R runner /app
USER runner
ENV WSI_DATA_DIR=/data
CMD ["pytest", "-q", "-p", "no:cacheprovider", "--junitxml", "/results/junit.xml"]

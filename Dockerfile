FROM python:3.13
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

RUN useradd -m app && chown -R app:app /app
USER app

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
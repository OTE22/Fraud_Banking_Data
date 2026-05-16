FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python backend/train_model.py && python backend/generate_feast_data.py

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python backend/data/generate_datasets.py && python backend/train_model.py && python backend/train_anomaly_model.py && python backend/train_segmentation_model.py && python backend/generate_feast_data.py && cd backend/feature_repo && feast apply

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

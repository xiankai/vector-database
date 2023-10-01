FROM python:3.11-slim-bookworm

WORKDIR /app

COPY ./requirements_k8s_txtai.txt /app/requirements_k8s_txtai.txt

# RUN pip install --no-cache-dir --upgrade -r /app/requirements_k8s_txtai.txt
RUN pip install --upgrade -r /app/requirements_k8s_txtai.txt

COPY ./app /app/app

COPY ./.env /app/.env

COPY ./shared_volume /app/shared_volume

CMD ["uvicorn", "app.local_app:router", "--host", "0.0.0.0", "--port", "8080"]

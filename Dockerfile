FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (sqlite için ekstra bir şey gerekmez)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Static + media dizinleri
RUN mkdir -p staticfiles media logs

# Non-root user — home dir açıkça tanımlanmazsa gunicorn hata verir
RUN addgroup --system django && adduser --system --home /home/django --ingroup django django
RUN chown -R django:django /app
USER django

# Static collect
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD sh -c "python manage.py migrate --noinput && gunicorn py_JobAutomation.wsgi:application --bind 0.0.0.0:8000"
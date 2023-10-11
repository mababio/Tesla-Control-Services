FROM python:3.10-slim
ENV APP_HOME /app
ENV PORT 8081
WORKDIR $APP_HOME
COPY src/* .
COPY secret_manager.py .
RUN pip install --no-cache-dir -r  requirements.txt
COPY application_default_credentials.* ./
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/application_default_credentials.json
RUN python secret_manager.py download settings.toml tap_settings_files tesla-automation-397321
RUN python secret_manager.py download cache.json tesla_cred tesla-automation-397321
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
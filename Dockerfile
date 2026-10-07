# Use the official Apache Airflow image
FROM apache/airflow:2.9.3

# Install dbt-postgres for our transformations
RUN pip install --no-cache-dir dbt-postgres

# Set the default Airflow home
ENV AIRFLOW_HOME=/opt/airflow

# Expose webserver port
EXPOSE 8080

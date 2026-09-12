SELECT 'CREATE DATABASE airflow OWNER ' || CURRENT_USER
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec
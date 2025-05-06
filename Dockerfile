
FROM python:3.9


WORKDIR /HYPER-LOCAL-MARKETING

COPY ./requirements.txt /HYPER-LOCAL-MARKETING/requirements.txt

COPY ./app /HYPER-LOCAL-MARKETING/app


RUN pip install --no-cache-dir --upgrade -r /HYPER-LOCAL-MARKETING/requirements.txt


# CMD ["fastapi", "run", "app/main.py", "--port", "5000"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]

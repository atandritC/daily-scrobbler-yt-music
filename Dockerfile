FROM python:3.14-alpine

COPY . .

RUN pip install uv
RUN uv sync

CMD ["uv", "run", "scrobble_daily.py"]
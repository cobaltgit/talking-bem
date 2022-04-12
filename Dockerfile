ARG BASE_IMG=python:slim
FROM ${BASE_IMG} AS base

ENV APPLICATION_ID=
ENV TOKEN=

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential sqlite3 libjpeg-dev zlib1g zlib1g-dev libffi-dev && rm -rf /var/lib/apt/lists/* && \
    groupadd ben && useradd -md /app -g ben -s /bin/bash ben
USER ben

WORKDIR /app/bot
COPY --chown=ben:ben . .

RUN pip install --user --no-cache-dir micropipenv && \
    /app/.local/bin/micropipenv install -- --user --no-cache-dir && \
    chmod +x /app/bot/docker_boot.sh

ENTRYPOINT [ "/app/bot/docker_boot.sh" ]
CMD [ "python", "bot.py" ]

FROM python:3.9-alpine
LABEL org.opencontainers.image.source https://github.com/qernal/github-actions-release

# add packages
RUN apk add curl openssl-dev libffi-dev git gcc musl-dev make --no-cache
COPY ./src /

# install pip requirements
RUN pip install -r requirements.txt

CMD ["python", "/release.py"]
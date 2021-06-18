FROM python:3.9-alpine
LABEL org.opencontainers.image.source https://github.com/qernal/github-actions-release

# add packages
RUN apk add curl rust openssl-dev git openssh --no-cache
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs --output /tmp/rustup.sh && \
    chmod +x /tmp/rustup.sh && \
    /tmp/rustup.sh -y && \
    ln -s $HOME/.cargo/bin/cargo /usr/bin/cargo
COPY ./src /

# install pip requirements
RUN pip install -r requirements.txt

CMD ["python", "/release.py"]
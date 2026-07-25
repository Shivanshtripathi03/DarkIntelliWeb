FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends tor netcat-openbsd && rm -rf /var/lib/apt/lists/*
COPY torrc /etc/tor/torrc
EXPOSE 9050 9051
CMD ["tor", "-f", "/etc/tor/torrc"]

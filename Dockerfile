FROM nginx:1.27-alpine

RUN apk add --no-cache python3

COPY scripts/generate-nginx-config.py /usr/local/bin/generate-nginx-config
COPY scripts/start.sh /usr/local/bin/start-reverse-proxy

RUN chmod +x /usr/local/bin/generate-nginx-config /usr/local/bin/start-reverse-proxy

ENTRYPOINT ["/usr/local/bin/start-reverse-proxy"]

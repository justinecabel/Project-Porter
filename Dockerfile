FROM nginx:1.27-alpine

RUN apk add --no-cache python3

COPY scripts/generate-nginx-config.py /usr/local/bin/generate-nginx-config
COPY scripts/init-apps-json.py /usr/local/bin/init-apps-json
COPY scripts/start.sh /usr/local/bin/start-reverse-proxy

RUN sed -i 's/\r$//' /usr/local/bin/generate-nginx-config /usr/local/bin/init-apps-json /usr/local/bin/start-reverse-proxy
RUN chmod +x /usr/local/bin/generate-nginx-config /usr/local/bin/init-apps-json /usr/local/bin/start-reverse-proxy
RUN test -f /usr/local/bin/start-reverse-proxy && /bin/sh -n /usr/local/bin/start-reverse-proxy

ENTRYPOINT ["/bin/sh", "/usr/local/bin/start-reverse-proxy"]

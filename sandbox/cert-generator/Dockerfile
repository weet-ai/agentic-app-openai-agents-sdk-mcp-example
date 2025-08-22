FROM alpine:latest

RUN apk add --no-cache openssl

COPY generate-certs.sh /generate-certs.sh
RUN chmod +x /generate-certs.sh

WORKDIR /certs

CMD ["/generate-certs.sh"]

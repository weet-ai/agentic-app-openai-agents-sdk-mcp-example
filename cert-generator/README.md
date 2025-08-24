## Certificates Generator

This `Dockerfile` can be used to generate certificates and keys for implementing mTLS (Mutual TLS) between different containers.

### Usage

The command below can be used to generate the certificates and keys - which will be stored in `certs` directory.

```bash
docker build -t cert-generator .
docker run --rm -v $(pwd)/certs:/certs cert-generator
```
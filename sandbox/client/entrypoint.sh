#!/bin/sh

echo "Trying mTLS connection to container-2:"
curl --cert /etc/certs/client.crt --key /etc/certs/client.key --cacert /etc/certs/ca.crt https://container-2
echo

echo "Trying regular TLS connection to container-3 (no client cert):"
curl --cacert /etc/certs/ca.crt https://container-3
echo

# Keep container running for manual inspection or debugging
tail -f /dev/null

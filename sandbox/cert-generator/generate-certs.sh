#!/bin/sh

CERT_DIR=/certs
cd $CERT_DIR || exit 1

# Clean old certs
rm -f *.key *.crt *.csr *.srl *.cnf

# Generate CA key and self-signed cert
openssl ecparam -genkey -name secp384r1 -out ca.key
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=MyRootCA"

# Generate server key and CSR
openssl ecparam -genkey -name secp384r1 -out server.key
openssl req -new -key server.key -out server.csr -subj "/CN=container-2"

# Create server extensions config
cat > server-ext.cnf <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:container-2,IP:127.0.0.1
EOF

# Sign server cert with CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile server-ext.cnf

# Generate client key and CSR
openssl ecparam -genkey -name secp384r1 -out client.key
openssl req -new -key client.key -out client.csr -subj "/CN=client1"

# Create client extensions config
cat > client-ext.cnf <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
EOF

# Sign client cert with CA
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365 -sha256 -extfile client-ext.cnf

# Clean up extra files
rm -f *.csr *.cnf *.srl

echo "Certificates generated successfully in $CERT_DIR"

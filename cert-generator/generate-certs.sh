#!/bin/sh

CERT_DIR=/certs
cd $CERT_DIR || exit 1

# Clean old certs
rm -f *.key *.crt *.csr *.srl *.cnf

# Create CA extensions config with proper key usage
cat > ca-ext.cnf <<EOF
[req]
distinguished_name = req_distinguished_name

[req_distinguished_name]

[v3_ca]
basicConstraints = critical,CA:TRUE
keyUsage = critical,digitalSignature,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer:always
EOF

# Generate CA key and self-signed cert with proper extensions
openssl ecparam -genkey -name secp384r1 -out ca.key
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt \
    -subj "/CN=MyRootCA/O=MyOrg/C=US" \
    -config ca-ext.cnf -extensions v3_ca

# Generate server key and CSR
openssl ecparam -genkey -name secp384r1 -out server.key
openssl req -new -key server.key -out server.csr -subj "/CN=container-2"

# Create server extensions config
cat > server-ext.cnf <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:nginx-proxy,DNS:mcp-server-1,DNS:mcp-server-2,DNS:localhost,IP:127.0.0.1
EOF

# Sign server cert with CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile server-ext.cnf

# Generate client key and CSR for general client
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

# Generate client key and CSR for agentic-app
openssl ecparam -genkey -name secp384r1 -out agentic-app.key
openssl req -new -key agentic-app.key -out agentic-app.csr -subj "/CN=agentic-app"

# Create agentic-app client extensions config
cat > agentic-app-ext.cnf <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
subjectAltName=DNS:agentic-app
EOF

# Sign agentic-app cert with CA
openssl x509 -req -in agentic-app.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out agentic-app.crt -days 365 -sha256 -extfile agentic-app-ext.cnf

# Clean up extra files (keep ca-ext.cnf for reference)
rm -f *.csr server-ext.cnf client-ext.cnf agentic-app-ext.cnf *.srl

echo "Certificates generated successfully in $CERT_DIR"
ls -la $CERT_DIR/
echo "Certificate generation complete!"

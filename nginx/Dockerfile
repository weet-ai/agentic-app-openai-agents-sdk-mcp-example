FROM nginx:alpine

# Create certs directory
RUN mkdir -p /etc/nginx/certs

# Copy certificates from build context
COPY ca.crt /etc/nginx/certs/
COPY server.crt /etc/nginx/certs/
COPY server.key /etc/nginx/certs/

# Set proper permissions for certificates
RUN chmod 644 /etc/nginx/certs/ca.crt /etc/nginx/certs/server.crt && \
    chmod 600 /etc/nginx/certs/server.key

# Copy nginx configuration
COPY nginx/nginx-proxy.conf /etc/nginx/conf.d/default.conf

EXPOSE 443
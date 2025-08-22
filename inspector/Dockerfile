FROM node:current-alpine3.22

# Set working directory
WORKDIR /app

# Install the MCP inspector package globally
RUN npm install -g @modelcontextprotocol/inspector

# Expose the default port (adjust if needed)
EXPOSE 6274 6277

# Set the entrypoint to run the MCP inspector
ENTRYPOINT ["npx", "@modelcontextprotocol/inspector"]
# OpenAI Agents SDK, Dynamic Code Execution & Streamable MCP Example

🚀 This repo is part of the materials for our [Enterprise Agents Course](https://buildingaiagents.com) - be sure to check it out!


## Key Features

- **End-to-end example** of using [OpenAI's Agents SDK](https://openai.github.io/openai-agents-python/quickstart/) with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) using [Streamable HTTP transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http)
- **Minimal Sandbox environment** for dynamic code execution
- **[Mutual TLS (mTLS)](https://www.cloudflare.com/en-gb/learning/access-management/what-is-mutual-tls/)** support for secure and authenticated client-server communication
- [Docker Compose](https://docs.docker.com/compose/) setup, with separate containers for each service

#### Functional Highlights

Dynamic code execution capability allows the agentic app to:

- Generate and run data analysis scripts on the fly in response to user queries.
- Perform data extraction, transformation, and summarization using the [polars](https://pola.rs/) library.
- Return processed results derived from realtime code execution.

By combining AI-driven generation with live code evaluation, this demo showcases an interactive agent that can act like a data analyst by autonomously writing, testing, and refining code snippets tailored to user needs.

## Demo

<img width="100%" height="auto" src="https://github.com/weet-ai/agentic-app-openai-agents-sdk-mcp-example/blob/main/assets/mtls_mcp_openai.gif" />

#### Security Considerations and Mitigations

Given the inherent risks of remote code execution, this project adds layered mitigation controls:

- **Communication Encryption & Zero Trust:** All MCP client-server traffic is encrypted and mutually authenticated using mutual TLS (mTLS), preventing unauthorized access and spoofed servers.
- **Minimal Sandbox Environment:** A static analyzer (`mcp_server/src/security/analyzer.py`) uses Python’s `ast` module to whitelist supported code constructs and imports only specific, safe functions from the `polars` library. This creates a minimalistic sandbox restricting actions to a controlled subset of data operations.
- **Runtime Isolation:** The server runs in a rootless, [distroless](https://github.com/GoogleContainerTools/distroless/blob/main/README.md) Docker container, limiting system-level permissions and attack surface.

While demonstrating a flexible, real-time code execution tool integrated into an AI agent, this setup is strictly experimental and research-focused. Deploying such capabilities in production requires thorough security design and audit beyond the scope of this repo


## Getting Started

### Step 1: Generate Certificates

The repo includes a containerized utility to generate self-signed certificates for your demo CA and MCP components:

```bash
docker build -t cert-generator ./certs-generator
docker run --rm -v $(pwd)/certs:/certs cert-generator
```

### Step 2: Run the Environment with Docker Compose

```bash
docker-compose up --build
```

This will launch all components including the MCP server, the agent app, the mTLS-terminating NGINX proxy, and a monitoring inspector service.

## Overview and motivation

This repository demonstrates a reference implementation for building and deploying AI agents using [OpenAI's Agents SDK](https://openai.github.io/openai-agents-python/quickstart/) integrated with a Model Context Protocol (MCP) server.

The MCP standard enables AI models to connect and interact with external tools through a client-server setup. However, recent research revealed critical security vulnerabilities in MCP implementations. One of these vulnerabilities is called [**"line jumping"**](https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/#breaking-mcps-security-promises) (or [**"tool poisoning"**](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)). This flaw allows malicious MCP servers to inject hidden instructions into the model context *before* any tool is explicitly invoked, bypassing user approval or invocation safeguards. Such attacks can lead to covert data exfiltration, vulnerability insertion, or silent suppression of security alerts.

This project shows how to implement a secure MCP setup by employing **Mutual TLS (mTLS)** authentication between MCP clients and servers. Both clients and servers use certificates signed by the same Certificate Authority (CA), ensuring only trusted MCP servers can connect and provide tools. Combined with network-level controls (e.g., Kubernetes network policies), this effectively prevents spoofed or malicious MCP servers from hijacking your AI agents via line jumping or tool spoofing attacks.

## Approaches to mitigate (not eliminate 😃) the risk

- Enforces **mutual TLS authentication** between MCP clients and servers, ensuring only servers with trusted, CA-signed certificates can connect.
- Uses **HTTPS-only connections** for MCP traffic, which can be enforced and monitored via network policies such as those in Kubernetes.
- Prevents attackers from easily introducing rogue MCP servers or spoofing tools by name, strengthening trust boundaries.
- Provides an educational environment for experimenting with secure MCP setups with Dockerized components:
  - MCP server
  - Agent backend
  - NGINX reverse proxy enforcing TLS
  - Certificate generation utility

### mTLS Handshake Steps

Normally in TLS, the server has a TLS certificate and a public/private key pair, while the client does not. The typical TLS process works like this:

1. Client connects to server
2. Server presents its TLS certificate
3. Client verifies the server's certificate
4. Client and server exchange information over encrypted TLS connection
5. The basic steps in a TLS handshake

In mTLS, however, both the client and server have a certificate, and both sides authenticate using their public/private key pair. Compared to regular TLS, there are additional steps in mTLS to verify both parties (additional steps in bold):

1. **Client connects to server**
2. **Server presents its TLS certificate**
3. **Client verifies the server's certificate**
4. **Client presents its TLS certificate**
5. **Server verifies the client's certificate**
6. **Server grants access**

<img width="100%" height="auto" src="how_mtls_works-what_is_mutual_tls.webp" />


## Important Notes

This repository is **primarily for educational and demo purposes**. A full production-ready secure MCP deployment would also need:

- Carefully designed network segmentation and firewall policies
- Proper OAuth or similar authentication and authorization for client access
- Continuous monitoring and automated vetting of tool descriptions for suspicious content

These aspects, although critical, are outside the scope of this example.

### Remote Code Execution and Dynamic Data Analysis Agent

The MCP server implementation under `mcp-server` exposes a custom **remote code execution** tool (**full disclaimer: this is for demonstration purposes — use it at your own risk!**). This tool enables AI agents built with the OpenAI Agents SDK in the `backend` to dynamically generate and execute Python code in real-time, powering a **Data Analyst** agent application.

## Appendix A: mTLS in Action

### MCP Inspector

- MCP Inspector is part of our Docker Compose setup. Different from `mcp-server` and `backend` containers, this container doesn't bake the TLS certificates and keys. As a result, attempts at connecting to the NGINX reverse proxy that is used for exposing our MCP Server do not work:

<img src="https://github.com/weet-ai/agentic-app-openai-agents-sdk-mcp-example/blob/main/assets/inspector_http.png?raw=true" />

**Observation**: since we 1. don't restrict network connections and 2. perform TLS termination at the reverse proxy, pointing MCP Inspector directly to our MCP server at port 8000 will allow connetions (see below). In an ideal scenario, you would block HTTP connections via network policy or service mesh tooling, like envoy sidecars for instance.

<img src="https://github.com/weet-ai/agentic-app-openai-agents-sdk-mcp-example/blob/main/assets/inspector_https.png?raw=true" />

---

For detailed understanding of MCP security vulnerabilities and defenses, please see the referenced Trail of Bits blog post. Their **mcp-context-protector** tool is also a valuable addition to complement transport-level security by safeguarding the model context.

## Appendix B: References

- [Trail of Bits Blog on MCP Security](https://blog.trailofbits.com/2025/06/18/model-context-protocol-security/)
- [mcp-context-protector Tool](https://github.com/TrailofBits/mcp-context-protector)
- [Mutual TLS Overview](https://www.cloudflare.com/en-gb/learning/access-management/what-is-mutual-tls/)


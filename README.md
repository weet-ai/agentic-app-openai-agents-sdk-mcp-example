# OpenAI Agents SDK & Streamable MCP Example

## Purpose of this repo

The (awesome) [Trail of Bits article on MCP line jumping](https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/) explains how tool descriptions sent by MCP servers can contain malicious hidden prompts, tricking AI models into executing harmful commands silently before the user explicitly calls any tools. This "line jumping" attack undermines MCP’s core security promises of explicit tool invocation and isolation.

The article also recommends rigorous vetting of MCP servers and tool descriptions, alongside other safety mechanisms.

Additionally, Trail of Bits offers a tool called **mcp-context-protector** that can help detect and block suspicious tool descriptions, complementing mutual TLS authentication by protecting the model context itself.

In this repo, we borrow **zero trust** best practices commonly used in **service mesh** architectures in order to provide one more mitigation control for line jumping attacks by implementing Mutual TLS.

### Remote Code Execution and Dynamic Data Analysis Agent

The MCP server implementation under `mcp-server` exposes a custom **remote code execution** tool (**full disclaimer: this is for demonstration purposes—use it at your own risk!**). This tool enables AI agents built with the OpenAI Agents SDK in the `backend` to dynamically generate and execute Python code in real-time, powering a **Data Analyst** agent application.

#### Functional Highlights

This dynamic execution capability allows the agent to:

- Generate and run data analysis scripts on the fly in response to user queries.
- Perform data extraction, transformation, and summarization using the `polars` library.
- Return processed results or visualizations derived from realtime code execution.

By combining AI-driven generation with live code evaluation, this demo showcases an interactive agent that can act like a data analyst by autonomously writing, testing, and refining code snippets tailored to user needs.

#### Security Considerations and Mitigations

Given the inherent risks of remote code execution, this project adds layered mitigation controls:

- **Communication Encryption & Zero Trust:** All MCP client-server traffic is encrypted and mutually authenticated using mutual TLS (mTLS), preventing unauthorized access and spoofed servers.
- **Minimal Sandbox Environment:** A static analyzer (`mcp_server/src/security/analyzer.py`) uses Python’s `ast` module to whitelist supported code constructs and imports only specific, safe functions from the `polars` library. This creates a minimalistic sandbox restricting actions to a controlled subset of data operations.
- **Runtime Isolation:** The server runs in a rootless, distroless Docker container, limiting system-level permissions and attack surface.

While demonstrating a flexible, real-time code execution tool integrated into an AI agent, this setup is strictly experimental and research-focused. Deploying such capabilities in production requires thorough security design and audit beyond the scope of this repo.

---

This combination of the OpenAI Agents SDK’s dynamic tool execution with a secure MCP infrastructure illustrates how powerful, agentic AI workflows can be built safely, balancing capability and risk by design.

---

## Key Features

- **End-to-end example** of using OpenAI's Agents SDK with MCP
- **Integration** with a [Streamable MCP server](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http) in a Dockerized environment
- **[Mutual TLS (mTLS)](https://www.cloudflare.com/en-gb/learning/access-management/what-is-mutual-tls/)** support for secure and authenticated client-server communication
- [Docker Compose](https://docs.docker.com/compose/) setup with service dependency ordering and custom networks

## Overview

This repository demonstrates a reference implementation for building and deploying AI agents using [OpenAI's Agents SDK](https://openai.github.io/openai-agents-python/quickstart/) integrated with a Model Context Protocol (MCP) server.

The MCP standard enables AI models to connect and interact with external tools through a client-server setup. However, recent research revealed critical security vulnerabilities in MCP implementations. One of these vulnerabilities is called [**"line jumping"**](https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/#breaking-mcps-security-promises) (or [**"tool poisoning"**](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)). This flaw allows malicious MCP servers to inject hidden instructions into the model context *before* any tool is explicitly invoked, bypassing user approval or invocation safeguards. Such attacks can lead to covert data exfiltration, vulnerability insertion, or silent suppression of security alerts.

This project shows how to implement a secure MCP setup by employing **Mutual TLS (mTLS)** authentication between MCP clients and servers. Both clients and servers use certificates signed by the same Certificate Authority (CA), ensuring only trusted MCP servers can connect and provide tools. Combined with network-level controls (e.g., Kubernetes network policies), this effectively prevents spoofed or malicious MCP servers from hijacking your AI agents via line jumping or tool spoofing attacks.

## How This Repo Mitigates the Risk

- Enforces **mutual TLS authentication** between MCP clients and servers, ensuring only servers with trusted, CA-signed certificates can connect.
- Uses **HTTPS-only connections** for MCP traffic, which can be enforced and monitored via network policies such as those in Kubernetes.
- Prevents attackers from easily introducing rogue MCP servers or spoofing tools by name, strengthening trust boundaries.
- Provides an educational environment for experimenting with secure MCP setups with Dockerized components:
  - MCP server
  - Agent backend
  - NGINX reverse proxy enforcing TLS
  - Certificate generation utility

## Important Notes

This repository is **primarily for educational and demo purposes**. A full production-ready secure MCP deployment would also need:

- Carefully designed network segmentation and firewall policies
- Proper OAuth or similar authentication and authorization for client access
- Continuous monitoring and automated vetting of tool descriptions for suspicious content

These aspects, although critical, are outside the scope of this example.

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

# Demo

## Agentic App

Our agentic app is configured to connect to an MCP server exposed by our NGINX reverse proxy (see docker-compose.yaml). Since the right TLS certificates are present in both our backend and our NGINX server, which performs TLS termination, the handshake happens successfully, and our agentic app can consume the tools that are exposed by our MCP server:

[video]

## MCP Inspector

- MCP Inspector is part of our Docker Compose setup. Different from `mcp-server` and `backend` containers, this container doesn't bake the TLS certificates and keys. As a result, attempts at connecting to the NGINX reverse proxy that is used for exposing our MCP Server do not work:

[screenshot]

**Observation**: since we 1. don't restrict network connections and 2. perform TLS termination at the reverse proxy, pointing MCP Inspector directly to our MCP server at port 8000 will allow connetions (see below). In an ideal scenario, you would block HTTP connections via network policy or service mesh tooling, like envoy sidecars for instance.

[screenshot]

---

For detailed understanding of MCP security vulnerabilities and defenses, please see the referenced Trail of Bits blog post. Their **mcp-context-protector** tool is also a valuable addition to complement transport-level security by safeguarding the model context.

Enjoy experimenting with secure MCP integration and dynamic AI agent workflows!

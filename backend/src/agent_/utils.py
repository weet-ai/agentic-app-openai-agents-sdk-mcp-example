import os
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams, create_static_tool_filter
from agents.agent import MCPConfig
from typing import List


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://nginx-proxy/mcp")
TLS_KEY_FILE = os.getenv("TLS_KEY_FILE", "/app/certs/agentic-app.key")
TLS_CERT_FILE = os.getenv("TLS_CERT_FILE", "/app/certs/agentic-app.crt")
TLS_CA_FILE = os.getenv("TLS_CA_FILE", "/app/certs/ca.crt")


def get_mcp_server(allowed_tool_names: List[str], url: str = MCP_SERVER_URL, timeout: int = 30) -> MCPServerStreamableHttp:
    
    static_tool_filter = create_static_tool_filter(allowed_tool_names=allowed_tool_names)
    
    # The httpx_patch will handle TLS certificates automatically
    params = MCPServerStreamableHttpParams(url=url, timeout=timeout)
    
    mcp_server = MCPServerStreamableHttp(
        params = params,
        cache_tools_list=True,
        tool_filter=static_tool_filter
    )

    return mcp_server


def get_mcp_config() -> MCPConfig:

    return MCPConfig(
        tls_key_file=TLS_KEY_FILE,
        tls_cert_file=TLS_CERT_FILE,
        tls_ca_file=TLS_CA_FILE,
        tls_enabled=True
    )


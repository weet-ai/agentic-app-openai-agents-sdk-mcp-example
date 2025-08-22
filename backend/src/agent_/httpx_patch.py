"""
Monkey patch for httpx to properly handle TLS certificates in MCP client
"""
import os
import ssl
import httpx
import wrapt
from typing import Optional, Tuple, Union


def create_ssl_context() -> Optional[ssl.SSLContext]:
    """Create SSL context with client certificates if environment variables are set"""
    cert_file = os.getenv("TLS_CERT_FILE", "/app/certs/agentic-app.crt")
    key_file = os.getenv("TLS_KEY_FILE", "/app/certs/agentic-app.key")
    ca_file = os.getenv("TLS_CA_FILE", "/app/certs/ca.crt")
    
    print(f"[HTTPX Patch] Using cert files: cert={cert_file}, key={key_file}, ca={ca_file}")
    
    if not ca_file or not os.path.exists(ca_file):
        print(f"[HTTPX Patch] CA file not found: {ca_file}")
        return None
    
    # Create SSL context with CA verification
    context = ssl.create_default_context(cafile=ca_file)
    
    # Load client certificate and key if available
    if cert_file and key_file and os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            context.load_cert_chain(cert_file, key_file)
            print(f"[HTTPX Patch] Loaded client certificate: {cert_file}")
        except Exception as e:
            print(f"[HTTPX Patch] Warning: Failed to load client certificates: {e}")
    else:
        print(f"[HTTPX Patch] Client certificates not found or incomplete: cert={cert_file}, key={key_file}")
    
    # Set verification mode
    context.check_hostname = False  # We're using container names in Docker
    context.verify_mode = ssl.CERT_REQUIRED
    
    return context


@wrapt.patch_function_wrapper('httpx', 'AsyncClient.__init__')
def patched_async_client_init(wrapped, instance, args, kwargs):
    """Patch AsyncClient to use our SSL context"""
    url = kwargs.get('base_url', '') or (args[0] if args else '')
    
    print(f"[HTTPX Patch] AsyncClient init with URL: {url}")
    
    # For empty URLs or internal service URLs, apply SSL context
    if not url or (isinstance(url, str) and url.startswith('https://') and ('nginx-proxy' in url or 'mcp' in url)):
        ssl_context = create_ssl_context()
        if ssl_context:
            # Override verify parameter with our SSL context
            kwargs['verify'] = ssl_context
            print(f"[HTTPX Patch] Using custom SSL context for {url or 'empty URL'}")
    elif isinstance(url, str) and url.startswith('https://'):
        print(f"[HTTPX Patch] Skipping SSL patch for external URL: {url}")
    
    return wrapped(*args, **kwargs)


@wrapt.patch_function_wrapper('httpx', 'Client.__init__')
def patched_client_init(wrapped, instance, args, kwargs):
    """Patch Client to use our SSL context"""
    url = kwargs.get('base_url', '') or (args[0] if args else '')
    
    # For empty URLs or internal service URLs, apply SSL context
    if not url or (isinstance(url, str) and url.startswith('https://') and ('nginx-proxy' in url or 'mcp' in url)):
        ssl_context = create_ssl_context()
        if ssl_context:
            # Override verify parameter with our SSL context
            kwargs['verify'] = ssl_context
            print(f"[HTTPX Patch] Using custom SSL context for {url or 'empty URL'}")
    
    return wrapped(*args, **kwargs)


@wrapt.patch_function_wrapper('httpx._client', 'AsyncClient.stream')
def patched_async_stream(wrapped, instance, args, kwargs):
    """Patch AsyncClient.stream - just log the URL for debugging"""
    method = args[0] if args else kwargs.get('method', '')
    url = args[1] if len(args) > 1 else kwargs.get('url', '')
    
    print(f"[HTTPX Patch] Stream request to: {url}")
    
    # Note: we can't modify verify here, it needs to be set on the client
    # The client should already have the SSL context from the __init__ patch
    
    return wrapped(*args, **kwargs)


def apply_patches():
    """Apply all httpx patches"""
    print("[HTTPX Patch] Monkey patches applied for TLS certificate handling")
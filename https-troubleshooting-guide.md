# HTTPS Troubleshooting Guide

## Common Issues When HTTP Works But HTTPS Doesn't

### 1. Check Firewall Settings

```bash
# Check if port 5000 is open for HTTPS
sudo ufw status

# If needed, allow HTTPS traffic on port 5000
sudo ufw allow 5000/tcp
```

### 2. Verify SSL Certificate Configuration

```bash
# Check if SSL certificates exist and are readable
ls -la /etc/letsencrypt/live/pdu.beardsys.com/

# Verify certificate validity
openssl x509 -in /etc/letsencrypt/live/pdu.beardsys.com/fullchain.pem -text -noout
```

### 3. Test HTTPS Connection Locally on the Server

```bash
# Test HTTPS connection locally
curl -k https://localhost:5000/healthz

# Test with specific hostname
curl -k https://pdu.beardsys.com:5000/healthz
```

### 4. Check Nginx Configuration (if using as reverse proxy)

```bash
# Check Nginx config syntax
sudo nginx -t

# Check Nginx SSL configuration
cat /etc/nginx/sites-enabled/pdu.beardsys.com
```

### 5. Verify FastAPI/Uvicorn SSL Configuration

The current FastAPI app doesn't have SSL configuration. To enable HTTPS directly in the agent:

1. Update `main.py` to include SSL certificate paths:

```python
if __name__ == "__main__":
    port = config.API_PORT
    host = config.API_HOST
    debug = config.DEBUG
    
    # SSL configuration
    ssl_keyfile = "/etc/letsencrypt/live/pdu.beardsys.com/privkey.pem"
    ssl_certfile = "/etc/letsencrypt/live/pdu.beardsys.com/fullchain.pem"
    
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=debug,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )
```

### 6. Check DNS Configuration

```bash
# Verify DNS resolution
nslookup pdu.beardsys.com

# Check if the IP matches your server
ping pdu.beardsys.com
```

### 7. Cloudflare SSL Settings (if using Cloudflare)

If using Cloudflare, check SSL/TLS settings:

1. Log in to Cloudflare dashboard
2. Select your domain
3. Go to SSL/TLS section
4. Ensure SSL mode is set to "Full" or "Full (Strict)"
5. Check if Cloudflare is proxying your domain (orange cloud icon)

### 8. Check for SSL Certificate Errors

```bash
# Check system logs for SSL errors
sudo journalctl -u nginx
sudo journalctl -u agent.service
```

### 9. Test with OpenSSL

```bash
# Test SSL handshake
openssl s_client -connect pdu.beardsys.com:5000
```

### 10. Implement Direct SSL in FastAPI

If you're not using Nginx as a reverse proxy, you need to configure SSL directly in your FastAPI application.

Update your agent's `.env` file to include SSL certificate paths:

```
# SSL Configuration
SSL_CERT_FILE=/etc/letsencrypt/live/pdu.beardsys.com/fullchain.pem
SSL_KEY_FILE=/etc/letsencrypt/live/pdu.beardsys.com/privkey.pem
```

Then update `config.py` to load these values:

```python
# SSL Configuration
SSL_CERT_FILE = os.getenv("SSL_CERT_FILE", "")
SSL_KEY_FILE = os.getenv("SSL_KEY_FILE", "")
```

Finally, update `main.py` to use these certificates:

```python
if __name__ == "__main__":
    # ...
    if config.SSL_CERT_FILE and config.SSL_KEY_FILE:
        print(f"Starting with SSL using certificates: {config.SSL_CERT_FILE}")
        uvicorn.run(
            "main:app", 
            host=host, 
            port=port, 
            reload=debug,
            ssl_certfile=config.SSL_CERT_FILE,
            ssl_keyfile=config.SSL_KEY_FILE
        )
    else:
        print("Starting without SSL (HTTP only)")
        uvicorn.run("main:app", host=host, port=port, reload=debug)
```

from email.policy import HTTP

import httpx

from config import Settings

class JiraClient:
    # Accept Settings instead of three separate args — cleaner interface:
    # def __init__(self, email: str, api_token: str, domain: str):
    def __init__(self, settings: Settings):
        self.email = settings.JIRA_EMAIL
        self.api_token = settings.JIRA_API_TOKEN
        self.domain = settings.JIRA_DOMAIN

        # HTTP headers only guarantee safe transport of ASCII printable characters. 
        # Your email or token could contain characters like @, :, +, =, or non-ASCII characters that might get corrupted or misinterpreted by proxies, servers, or parsers along the way.
        # Base64 converts any bytes into a safe set of characters (A-Z, a-z, 0-9, +, /, =) — guaranteed to survive the journey through any HTTP infrastructure.
        # It's a transport safety measure, not a security measure.

        # httpx has built-in Basic Auth support, so you don't need to manually base64 encode:
        # self.credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode() 

        # Single shared AsyncClient instance — reuses TCP connections
        # across requests (connection pooling) instead of opening a
        # new socket per request. Must be closed via aclose() on shutdown.
        self._client = httpx.AsyncClient(
            base_url=f"https://{self.domain}.atlassian.net", # base_url: prepended to all relative paths (e.g., "/rest/api/3/myself")
            auth=httpx.BasicAuth(self.email, self.api_token),

            # These are two headers that tell Jira what format we're speaking in.
            # Content-Type: application/json
                ## "The data I'm sending you is in JSON format."
                ## When we later POST a request body to Jira (e.g. searching for stories), Jira needs to know how to parse it. Without this header, Jira might try to read your JSON as plain text or form data and reject it.

            #   Accept: application/json
                ## "The data I want back from you should be in JSON format."

            #   Jira can return data in multiple formats (JSON, XML, HTML). This header says "give me JSON." Without it, Jira defaults to JSON anyway — but it's good practice to be explicit.

            #   In short:
                #   - Content-Type = format of what you send
                #   - Accept = format of what you want to receive
                #   For our backend, it's always JSON both ways.

            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }    
        )

    async def ping(self) -> int:
        try:
            response = await self._client.get("/rest/api/3/myself")
            response.raise_for_status() 
            return response.status_code
        except httpx.HTTPError as e:
            print(f"Jira API ping failed: {e}")
            # If the error is a connection failure (e.g. bad domain), 
            # there's no response object at all — this will crash with UnboundLocalError.

            # A 401 Unauthorized — if your .env credentials are incorrect
            return -1  

    async def close(self) -> None:
        await self._client.aclose()


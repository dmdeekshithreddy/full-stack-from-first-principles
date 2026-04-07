from fastapi import FastAPI
from jira_client import JiraClient


app = FastAPI()
settings = Settings()

@app.get("/")
async def read_root():
    return {"message": "Agentic DE backend"}    

@app.get("/ping-jira")
async def get_jira_issues():
    # Create a new JiraClient instance for this request.
    # This is inefficient if you have many requests, but it's simple for demonstration.
    # It will create a new TCP connection (connection pool) to the Jira API for every request, which is slow and resource-intensive.
    
    # Disadvantages of creating a client per request:
    # 1. New TCP connection opened & closed every request — slow due to handshake overhead.
    # 2. No connection pooling — can't reuse existing connections across requests.
    # 3. Under high traffic, you may exhaust sockets or hit OS file descriptor limits.
    # 4. No shared cleanup — if the server crashes, open connections may leak.
    #
    # Better approach: create one shared client in lifespan() and store on app.state.
    client = JiraClient(settings=settings)

    # Fetch issues from Jira (replace with your actual project key and JQL).
    status_code = await client.ping()
    await client.close()
    return {"status_code": status_code}

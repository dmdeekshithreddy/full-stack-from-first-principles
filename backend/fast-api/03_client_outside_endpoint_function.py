from fastapi import FastAPI
from jira_client import JiraClient


app = FastAPI()
settings = Settings()

# Client created at module level (import time) — shared across all requests.
# This is better than per-request (01.simple_client_call.py), but still has disadvantages:
#
# 1. Runs at import time — the client is created when Python imports this file,
#    even if you're just running tests, linting, or CLI commands that don't need it.

# 2. No guaranteed cleanup — there's no shutdown hook to call client.close().
#    If the server stops, the connection may leak without a clean TCP teardown.

# 3. Initialization order is fragile — if JiraClient depends on something not yet
#    ready at import time (e.g., env vars not loaded, DB not connected), it will crash.

# 4. Harder to test — you can't easily swap this with a mock since it's created
#    at module level. With lifespan + app.state, you can override app.state in tests.

# 5. No async support — module-level code is synchronous. If JiraClient needs an
#    async setup step (like `await client.connect()`), you can't do it here.
#

# Better approach: create one shared client in lifespan() and store on app.state.
client = JiraClient(settings=settings) # create the reat api connection pool to jira, and reuse it for all requests. 

@app.get("/")
async def read_root():
    return {"message": "Agentic DE backend"}    

@app.get("/ping-jira")
async def get_jira_issues():
    # Fetch issues from Jira (replace with your actual project key and JQL).
    status_code = await client.ping()
    await client.close()
    return {"status_code": status_code}

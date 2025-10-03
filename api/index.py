from fastapi import FastAPI

app = FastAPI()

@app.get("/api/ping")
async def ping():
    return {"ok": True}

@app.post("/api/chat")
async def chat():
    return {"response": "Service is initializing. Please try again shortly."}

# Ensure Vercel can find the handler
handler = app
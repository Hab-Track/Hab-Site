from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def fastapi_example():
    return {"message": "Hello from FastAPI"}

@app.get("/another-route")
def fastapi_another_example():
    return {"message": "Another route in FastAPI"}
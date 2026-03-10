from fastapi import FastAPI

app = FastAPI()

@app.get("/search")
def search(name: str = None, age: int = None):
    return {
        "name": name,
        "age": age
    }
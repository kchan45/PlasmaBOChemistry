from fastapi import FastAPI

if __name__ == "__main__":
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World!"}
    
    @app.get("/troubleshooting")
    async def run_appj():
        return {"message": "test"}
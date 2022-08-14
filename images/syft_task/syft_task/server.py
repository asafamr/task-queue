
from fastapi import FastAPI, HTTPException, Body
from .syft import ImageNotFound, extract_sbom_syft


app = FastAPI()

@app.get("/")
def hello():
    return 'world'

@app.post("/run")
def run(params=Body()):
    try:
        print(str(params))
         
        return extract_sbom_syft(params['docker_image_id'])
    except ImageNotFound:
        raise HTTPException(status_code=400, detail="Image not found")


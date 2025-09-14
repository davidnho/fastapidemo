from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
items = []

@app.get('/')
async def root():
    return {'hello': 'world'}

@app.get('/about')
def about():
    return {'About Page'}

@app.post('/items')
def create_item(item: str):
    items.append(item)
    return item


'''
to test 
https://8000-davidnho-fastapidemo-52uaue5vuhf.ws-us121.gitpod.io/items?item=apple
'''
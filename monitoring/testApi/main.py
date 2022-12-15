from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'Ich kann HMTL programieren, was kannst du?'}


@app.get('/v1/burn/{_id}/{comp}')
async def _comp(_id: int, comp: str, value: str = '', limit: str = ''):
    print(_id, comp, value, limit)

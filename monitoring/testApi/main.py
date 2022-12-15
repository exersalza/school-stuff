from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def root():
    return {'message': ''}


@app.get('/v1/burn/{_id}/{comp}')
async def _comp(_id: int, comp: str, value: str = ''):
    print(_id, comp, value)

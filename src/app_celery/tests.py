import json

from pydantic import BaseModel

from src.env import SCRAPPER_RESULTS_DIR__TELEGRAM, settings

class TgPos(BaseModel):
    a: str

class Poss(BaseModel):
    poss: list[TgPos]

al = [TgPos(a='a'), TgPos(a='b'), TgPos(a='c'), TgPos(a='d')]
text = json.load((SCRAPPER_RESULTS_DIR__TELEGRAM / f"a" / f"b.json").open())
print(type(text['poss'][0]))

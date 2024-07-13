import os
import requests
from dotenv import load_dotenv
import aiohttp
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from srcreader import SrcReader
from community import community_summary
from news import news_summary

load_dotenv()


app = FastAPI()
srcs = SrcReader("./src/*.json")

ALLOWED_HOSTS = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_HOSTS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}


class MessageInput(BaseModel):
    hash: str
    params: dict

class KeywordInput(BaseModel):
    keyword: str

class ContextInput(BaseModel):
    keyword: str
    index: str

@app.post("/keyword")
def keyword(keyword: KeywordInput):
    kname = srcs.get_keyword_name(keyword.keyword)
    return {"data": kname}


async def execute_post(api_url: str, headers: dict, json: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=json) as response:
            return await response.json()



@app.post("/api")
async def api(question: MessageInput):
    project = os.getenv("WANTED_PROJECT")
    api_key = os.getenv("WANTED_API_KEY")
    header = {
        "project": project,
        "apiKey": api_key,
    }

    api_url = "https://api-laas.wanted.co.kr/api/preset/chat/completions"
    body = {
            "params": question.params,
            "hash": question.hash,
        }
    response_dict =  await execute_post(api_url, headers=header, json=body)
    return response_dict

    
@app.post("/context")
def context(input: ContextInput):
    # print(input.keyword, input.index)
    if len(keywords:=input.keyword.split(" ")) >= 2:
        context = ""
        for keyword in keywords:
            if keyword == "":
                continue
            keyword_name = srcs.get_keyword_name(keyword)
            doc = srcs.get_document(index=keyword)
            context += "\n" + srcs.get_paragraph(keyword_name, doc, index=input.index)
        
    else:
        doc = srcs.get_document(index=input.keyword)
        keyword_name = srcs.get_keyword_name(input.keyword)
        context = srcs.get_paragraph(keyword_name, doc, index=input.index)

    return {"data":context}

@app.post("/community")
def community(context: KeywordInput):
    if len(keywords:=context.keyword.split(" ")) >= 2:
        keyword = keywords[0]
    else:
        keyword = context.keyword
    community_keyword = srcs.get_community_keyword(keyword)
    result, links, titles = community_summary(community_keyword, 3)
    return {"result": result, "links": links, "titles": titles}

@app.post("/news")
def news(context: KeywordInput):
    if len(keywords:=context.keyword.split(" ")) >= 2:
        keyword = keywords[0]
    else:
        keyword = context.keyword
    news_keyword = srcs.get_community_keyword(keyword)
    result, links, titles = news_summary(news_keyword, 3)
    return {"result": result, "links": links, "titles": titles}

@app.post("/cost")
def cost(context: KeywordInput):
    cost = ""
    for keyword in context.keyword.split(" "):
        keyword_name = srcs.get_keyword_name(keyword)
        cost += keyword_name+": "+srcs.get_cost(context.keyword)
        cost += "\n"

    return {"data": cost}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)

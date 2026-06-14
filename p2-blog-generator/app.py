import uvicorn 
from fastapi import FastAPI, Request
from src.llms.groqllm import Groqllm
from src.graphs.graph_builder import Graphbuilder
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
os.environ["LANGSMITH_API_KEY"]=str(os.getenv("LANGCHAIN_API_KEY"))


## APIS
@app.post("/blogs")
async def create_blogs(request: Request):
    data = await request.json()
    topic = data.get("topic","")
    language = data.get("language","")

    # get llm object
    llm = Groqllm().get_llm()

    # get  graph
    graphbuilder = Graphbuilder(llm)
    if topic and language:
        graph = graphbuilder.setup_graph(usecase="language")
        state = graph.invoke({"topic": topic,"current_language": language.lower()})
    # elif topic:
    #     graph=graphbuilder.setup_graph(usecase="topic")
    #     state=graph.invoke({"topic": topic})
    return {"data":state}
    

if __name__=="__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
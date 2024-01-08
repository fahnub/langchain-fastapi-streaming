from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware for cross-origin resource sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt template for generating jokes
prompt = PromptTemplate.from_template(
    """
    Create a clever and humorous joke or pun that is specifically related to '{input}'. 
    The joke or pun should be original, light-hearted, and suitable for a general audience.
    It should cleverly play on words or concepts directly associated with '{input}', ensuring the humor is directly tied to the unique characteristics or well-known aspects of the topic.
    """
)

# Chat model configuration
model = ChatOpenAI(model_name="gpt-4", temperature=0)

# Processing chain setup
chain = {"input": RunnablePassthrough()} | prompt | model | StrOutputParser()


@app.get("/joke")
async def write_joke(input: str):
    """
    Endpoint to write a joke based on the input string.
    :param input: Input string to base the joke on.
    :return: StreamingResponse of the joke.
    """

    async def stream():
        async for chunk in chain.astream(input):
            formatted_chunk = format_chunk(chunk)
            yield f"data: {formatted_chunk}\n\n"

    headers = {"Content-Type": "text/event-stream; charset=utf-8"}
    return StreamingResponse(stream(), headers=headers)


def format_chunk(chunk: str) -> str:
    """
    Formats a chunk of text for streaming.
    :param chunk: The text chunk to be formatted.
    :return: Formatted text chunk.
    """
    return (
        chunk.replace("\n", "<new-line>").replace("\t", "<tab>").replace(" ", "<space>")
    )


@app.get("/", response_class=HTMLResponse)
async def read_index():
    """
    Endpoint to serve the index HTML page.
    :return: FileResponse of the index.html file.
    """
    return FileResponse("static/index.html")


# Main entry point for the application
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

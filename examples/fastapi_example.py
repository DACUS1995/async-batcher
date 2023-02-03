import asyncio
from dataclasses import dataclass
import json
from typing import List

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel, Field
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from async_batcher import Batcher


# --------------Configs and dependencies--------------

@dataclass
class Config:
	source_language: str
	target_language: str
	model_name: str
	access_token: str
	port: int = 8080
	max_batch_size: int = 5

config = Config(...)


class TranslationRequest(BaseModel):
	text: str = Field(..., min_length=1, max_length=30)


model = AutoModelForSeq2SeqLM.from_pretrained(
	config.model_name, 
	use_auth_token=config.access_token
)


tokenizer = AutoTokenizer.from_pretrained(
	config.model_name, 
	use_auth_token=config.access_token, 
	src_lang=config.source_language
)



# --------------Batcher Setup--------------

def translate(texts: List[str]) -> List[str]:
	inputs = tokenizer(texts, return_tensors = "pt")
	translated_tokens = model.generate(
	    **inputs,
		forced_bos_token_id = tokenizer.lang_code_to_id[config.target_language], 
		max_length = Config.max_sequence
	)
	translations = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
	
	return translations


batcher = Batcher(
	batch_prediction_fn=translate, 
	max_batch_size=config.max_batch_size
)


# --------------FastAPI Setup--------------

app = FastAPI()

origins = [
	f"http://localhost:{config.port}"
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.post("/translate", status_code=201)
async def translate(req: TranslationRequest):
	translated_text = await batcher.predict(req.text)
	return JSONResponse({"translation": translated_text})


@app.get("/")
async def root():
	return Response(
		content=json.dumps({"Status": "Alive"}), 
		status_code=status.HTTP_200_OK
	)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
	return JSONResponse({"Error": str(exc)})


@app.exception_handler(Exception)
async def final_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=500, content={"message": f"{base_error_message}", "Details": str(err)})


# --------------Starting batcher--------------

@app.on_event("startup")
async def startup_event():
	loop = asyncio.get_running_loop()
	asyncio.create_task(batcher.start(loop))



if __name__ == "__main__":
	uvicorn.run("fastapi_example:app", host="0.0.0.0", port=config.port, reload=True)

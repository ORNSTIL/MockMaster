from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import drafts, players, teams
import json
import logging

description = """
Mock Master is the premier drafting site for all your fantasy football desires.
"""

app = FastAPI(
    title="Mock Master",
    description=description
)

app.include_router(teams.router)
app.include_router(drafts.router)
app.include_router(players.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to MockMaster."}

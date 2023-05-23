from fastapi import FastAPI, Request, HTTPException
from pytube import Playlist
from typing import List
from aioredis import Redis
import time

app = FastAPI()

TIME_WINDOW = 60  # time window in seconds
REQUEST_LIMIT = 10  # limit the number of requests per IP within the time window

@app.on_event("startup")
async def startup_event():
    app.state.redis = Redis.from_url('redis://redis')

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.redis.close()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip_address = request.client.host
    key = f"{ip_address}_requests"

    current_requests = await app.state.redis.get(key)
    if current_requests is None:
        # this is the first request from this IP address, set a new key in Redis
        await app.state.redis.set(key, 1, ex=TIME_WINDOW)
    else:
        current_requests = int(current_requests)
        if current_requests >= REQUEST_LIMIT:
            # too many requests, return an error
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        else:
            # increment the request count
            await app.state.redis.set(key, str(current_requests + 1), ex=TIME_WINDOW)

    response = await call_next(request)
    return response

from typing import Union, List, Dict

@app.get("/playlist")
async def get_playlist(playlist_url: str) -> Union[List[str], Dict[str, str]]:
    if playlist_url is None:
        return {"error": "Playlist url is not provided"}

    try:
        playlist = Playlist(playlist_url)
        return playlist.video_urls
    except Exception as e:
        return {"error": str(e)}  

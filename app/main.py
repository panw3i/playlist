from fastapi import FastAPI, HTTPException, Query
from pytube import Playlist
from typing import List
from urllib.parse import unquote

app = FastAPI()

# from urllib.parse import quote

# url = 'https://www.youtube.com/watch?v=-Yp0LS61Nxk&list=PLwvDm4VfkdphqETTBf-DdjCoAvhai1QpO'
# encoded_url = quote(url, safe='')
# print(encoded_url)

@app.get("/playlist")
async def get_playlist(url: str = Query(..., description="The URL of the YouTube playlist")) -> List[str]:
    url = unquote(url)
    
    try:
        playlist = Playlist(url)
        return list(playlist.video_urls)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

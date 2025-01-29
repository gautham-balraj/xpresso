from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.assistant.graph import graph_builder
from src.assistant.state import SummaryState
from src.assistant.utils.x_sc import initialize_twitter_client
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str

class TweetRequest(BaseModel):
    tweets: list[str]

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Tweet Generator API!"}

@app.post("/generate-tweets")
async def generate_tweets(request: TopicRequest):
    try:
        graph = graph_builder()
        summary_state = SummaryState(
            research_topic=request.topic,
            search_query='',
            web_research_results=[],
            sources_gathered=[],
            research_loop_count=0,
            running_summary=None,
            tweets=[]
        )
        
        final_tweets = []
        thread = {"configurable": {"thread_id": "1"}}
        for event in graph.stream(summary_state, thread, stream_mode="values"):
            print(event)

            final_tweets = event['tweets']
                
                
        return {"tweets": final_tweets}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/post-tweets")
async def post_tweets(request: TweetRequest):
    try:
        client, api = initialize_twitter_client()
        results = []
        for tweet in request.tweets:
            response = client.create_tweet(text=tweet)
            results.append({"tweet": tweet, "id": response.data['id']})
        return {"status": "success", "posted": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
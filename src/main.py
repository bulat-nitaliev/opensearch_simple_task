from fastapi import FastAPI, HTTPException
from utils import get_opensearch_client, create_index, index_documents, search_documents, generate_sample_documents
from model import  Document, SearchResult
from schemas import SearchRequest


app = FastAPI()

INDEX_NAME = "documents"

@app.get("/startup")
async def startup():
    try:
        client = get_opensearch_client()
        
        # Create index if not exists
        created = create_index(client, INDEX_NAME)
        
        # Generate and index sample documents if index was just created
        if created:
            documents = generate_sample_documents(5)
            index_documents(client, INDEX_NAME, documents)

        return {"message": "success"}
    except Exception as e:
        return {"error": f"{str(e)}"}


    
    

@app.post("/search", response_model=list[SearchResult])
async def search(search_request: SearchRequest):
    client = get_opensearch_client()
    
    try:
        results = search_documents(
            client,
            INDEX_NAME,
            search_request.query,
            search_request.content_type.value if search_request.content_type else None
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=list[Document])
async def list_documents():
    client = get_opensearch_client()
    
    try:
        response = client.search(
            index=INDEX_NAME,
            body={"query": {"match_all": {}}},
            size=10
        )
        
        documents = []
        for hit in response["hits"]["hits"]:
            documents.append(hit["_source"])
        
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
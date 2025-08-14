from opensearchpy import OpenSearch
import os
from faker import Faker
import random
from model import ContentType


def get_opensearch_client():
    host = os.getenv("OPENSEARCH_HOST", "localhost")
    port = os.getenv("OPENSEARCH_PORT", 9200)
    auth = (
        os.getenv("OPENSEARCH_USER", "admin"),
        os.getenv("OPENSEARCH_PASSWORD", "admin123")
    )
    print(auth)
    client = OpenSearch(
        # hosts=[{'host': host, 'port': port}],
        hosts="http://opensearch:9200",
        http_compress=True,
        http_auth=auth,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    
    return client

def create_index(client, index_name):
    if not client.indices.exists(index=index_name):
        index_body = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            },
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "content_type": {"type": "keyword"}
                }
            }
        }
        client.indices.create(index=index_name, body=index_body)
        return True
    return False

def index_documents(client, index_name, documents):
    for i, doc in enumerate(documents):
        client.index(index=index_name, body=doc, id=i+1)

def search_documents(client, index_name, query, content_type=None):
    search_query = {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "content"]
                    }
                }
            }
        }
    }
    
    if content_type:
        search_query["query"]["bool"]["filter"] = {
            "term": {"content_type": content_type}
        }
    
    response = client.search(index=index_name, body=search_query)
    
    results = []
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        results.append({
            "title": source.get("title", ""),
            "snippet": source.get("content", "")[:50] + "..." if source.get("content") else ""
        })
    
    return results

def generate_sample_documents(count: int = 5):
    content_types = list(ContentType)
    documents = []
    fake = Faker()
    
    for _ in range(count):
        doc = {
            "title": fake.sentence(),
            "content": fake.text(max_nb_chars=200),
            "content_type": random.choice(content_types).value
        }
        documents.append(doc)
        
    return documents

    
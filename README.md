# kiwix-server-mcp

A simple MCP server to interface with the Kiwix serve API.
- https://kiwix-tools.readthedocs.io/en/latest/kiwix-serve.html

## run locally
```bash
KIWIX_SERVER=https://kiwix.lab.systemj.net uv run main.py

# debug - url: http://localhost:8000/mcp
npx @modelcontextprotocol/inspector
```

## open-webui use example
- model: qwen3:14b
- function calling: native
- system prompt:
```
You are a research assitant, your goal is to provide the most accurate information possible backed up with citations and sources.
When responding, *ALWAYS* perform the following steps:
1. Call kiwix_listCollections() to list the available data sources
2. Choose the source most likely to contain the most detailed information for the user's request, and note the "uuid" value
3. Call kiwix_searchCollections() using key words relevant to the user's request to search for articles.
4. Review the list of articles returned and choose the article most likely to contain information about the users request based on the article summary, and note the "link" value
5. Call kiwix_getArticle() to retrieve the full article content and direct_link
6. Provide a summary based on the retrieved content.
7. Provide the direct_link to the user
```

### example query
![example image](open-webui-example.png)

## build
```bash
docker build -t systemj/kiwix-server-mcp .
helm package chart
```

## publish
```bash
docker push systemj/kiwix-server-mcp
helm push kiwix-server-mcp-0.1.0.tgz oci://registry-1.docker.io/systemj
```
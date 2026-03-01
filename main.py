import html2text
import kiwix_api
import os

from dataclasses import dataclass, field
from fastmcp import FastMCP
from starlette.responses import JSONResponse

kiwix_server = os.environ.get("KIWIX_SERVER")
kiwix = kiwix_api.KiwixAPI(kiwix_server=kiwix_server)

h2t = html2text.HTML2Text()

mcp = FastMCP("Access to reference materials such as encyclopedia articles.")

@dataclass
class Collection:
    uuid: str = field(metadata={"description": "unique identifier used with searchCollection()"})
    title: str = field(metadata={"description": "collection title"})
    summary: str = field(metadata={"description": "brief description of the collection"})

@dataclass
class SearchResult:
    title: str = field(metadata={"description": "article title"})
    link: str = field(metadata={"description": "link to retrieve article content with getArticle()"})
    excerpt: str = field(metadata={"description": "short text excerpt from the article to review"})

@dataclass
class Article:
    direct_link: str = field(metadata={"description": "A direct link to the full article suitable for viewing in a web browser"})
    content: str = field(metadata={"description": "The text content of the article"})

@mcp.tool()
def listCollections() -> list[Collection]:
    """ Get a list of content collections available """
    collections = []
    for entry in kiwix.list_books()["feed"]["entry"]:
        collections.append(
            Collection(
                uuid = entry["id"].split(":")[2],
                title = entry["title"],
                summary = entry["summary"]
            )
        )
    return collections

@mcp.tool()
def searchCollection(uuid: str, pattern: str) -> list[SearchResult]:
    """
    Search for articles in a collection that match the pattern text.
    :param uuid: The uuid of the collection to search as returned from listCollections() - REQUIRED must not be empty
    :param pattern: Text keywords used to search for relevant articles - REQUIRED must not be empty
    """
    results = []
    for result in kiwix.search(uuid=uuid, pattern=pattern)["rss"]["channel"]["item"]:
        text = ""
        if isinstance(result["description"], str):
            text = result["description"]
        elif isinstance(result["description"], dict):
            text = result["description"]["#text"]
        results.append(
            SearchResult(
                title = result["title"],
                link = result["link"],
                excerpt = text,
            )
        )
    return results

@mcp.tool()
def getArticle(link: str) -> Article:
    """
    Retrieve the complete content of an article previously returned in search results.
    :param link: A link to the article as returned by searchCollection() - REQUIRED, must not be empty
    """
    content = kiwix.get_content(link)
    return Article(
        direct_link = f"{kiwix_server}{link}",
        content = h2t.handle(content)
    )

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "kiwix-server-mcp"})

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)

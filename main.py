import html2text
import json
import kiwix_api
import os
from fastmcp import FastMCP

kiwix_server = os.environ.get("KIWIX_SERVER")
kiwix = kiwix_api.KiwixAPI(kiwix_server=kiwix_server)

h2t = html2text.HTML2Text()

mcp = FastMCP(
    "Kiwix MCP"
    """
    The MCP server provides access to reference materials such as encyclopedia articles.

    The resources and tools should be used in the following way:
    - First use the data://collections resource to identify the different collections of content.
    - Select the collection most likely to contain relevant information for the given context, and note uuid value for this collection
    - call the searchCollection() tool with the uuid for the chosen collection and a short text string to search for articles
    - review the list of articles returned and chose the most relevant based on the text excerpt; note the "link" value for this article
    - finally you must call getArticle() using the "link" value from searchCollection() to retrieve the complete content the article.
    """
)


@mcp.resource("data://collections")
def listCollections() -> str:
    """
    Returns list of content collections available.
    Each item contains the following fields:
        uuid: A unique identifer for this specific collection - used when calling searchCollection()
        title: The title of the collection
        summary: A short description of the collection content
    """
    collections = []
    for entry in kiwix.list_books()["feed"]["entry"]:
        collections.append(
            {
                "uuid": entry["id"].split(":")[2],
                "title": entry["title"],
                "summary": entry["summary"],
            }
        )
    return json.dumps(collections)


@mcp.tool
def searchCollection(uuid: str, pattern: str) -> str:
    """
    Search for articles in a collection that match the pattern text.
    returns a list of matching articles with the following data:
        title: The title of the article
        link: A link for retrieving the full content of an article when calling getArticle()
        text: A short text excerpt from the article for review to determine if this article is relevant
    :param uuid: The uuid of the collection to search as returned from data://collections - REQUIRED must not be empty
    :param pattern: Text keywords used to search for relevant articles - REQUIRED must not be empty
    """
    if all([uuid, pattern]):
        try:
            results = []
            for result in kiwix.search(uuid=uuid, pattern=pattern)["rss"]["channel"]["item"]:
                results.append(
                    {
                        "title": result["title"],
                        "link": result["link"],
                        "text": result["description"]["#text"],
                    }
                )
        except Exception as e:
            results = {"error": e}
    else:
        results = {"error": 'you must provide both "uuid" and "pattern"'}
    return json.dumps(results)

@mcp.tool
def getArticle(link: str) -> str:
    """
    Retrieve the complete content of an article previously returned in search results.
    The link parameter MUST be taken from the 'link' field of searchCollection() results.
    returns the complete content of an article with the following data:
        direct_link: A direct link to the article that can be viewed in a web browser (can be provided to the user for reference)
        content: The complete content of the article
    :param link: A relative link to the article as returned by searchCollection() - REQUIRED, must not be empty
    """
    if link:
        try:
            content = kiwix.get_content(link)
            response = {"direct_link": f"{kiwix_server}{link}", "content": h2t.handle(content)}
            return json.dumps(response)
        except Exception as e:
            return {"error": e}
    else:
        return {"error": 'you must provide "link"'}


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
    # print(listcollections())
    # print(searchBook(uuid="73c3567c-dcb3-597b-5168-f15d9c4b7470", pattern="The Metamorphosis of Prime Intellect"))
    # print(getArticle(link="/content/wikipedia_en_all_nopic_2025-12/The_Metamorphosis_of_Prime_Intellect"))

import html2text
import json
import kiwix_api
import os
from fastmcp import FastMCP

mcp = FastMCP("Kiwix MCP Server")

kiwix_server = os.environ.get("KIWIX_SERVER")
kiwix = kiwix_api.KiwixAPI(kiwix_server=kiwix_server)

h2t = html2text.HTML2Text()

@mcp.tool
def listBooks() -> str:
    """ list all available books """
    books = []
    for entry in kiwix.list_books()["feed"]["entry"]:
        books.append({
            "uuid": entry["id"].split(":")[2],
            "title": entry["title"],
            "summary": entry["summary"]
        })
    return json.dumps(books)

@mcp.tool
def searchBook(uuid: str = "", pattern: str = "", limit: int = 10) -> str:
    """ search a book for articles matching pattern """
    results = []
    for result in kiwix.search(uuid=uuid, pattern=pattern)["rss"]["channel"]["item"]:
        results.append({
            "title": result["title"],
            "link": result["link"],
            "text": result["description"]["#text"]
        })
    return json.dumps(results)

@mcp.tool
def getArticle(link: str = "") -> str:
    """ get the content of an article """
    content = kiwix.get_content(link)
    response = {
        "direct_link": f"{kiwix_server}{link}",
        "content": h2t.handle(content)
    }
    return json.dumps(response)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
    # print(listBooks())
    # print(searchBook(uuid="73c3567c-dcb3-597b-5168-f15d9c4b7470", pattern="The Metamorphosis of Prime Intellect"))
    # print(getArticle(link="/content/wikipedia_en_all_nopic_2025-12/The_Metamorphosis_of_Prime_Intellect"))

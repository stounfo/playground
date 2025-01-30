import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import networkx as nx
import os


def crawl_site_for_primarynote_links(start_url):
    """
    1) BFS crawl from start_url.
    2) For each page:
       - Skip if it doesn't have <div class="jsx-2479918432 PrimaryNote">.
       - Otherwise, parse only links in that PrimaryNote div.
       - Only keep links matching "/z..." format on the same domain.
    3) Collect edges as (current_url, linked_url).
    4) Also build a mapping from URL -> node label, using
       [path : <title>] (fallback to <h1> if no <title>).
    """
    domain = urlparse(start_url).netloc
    visited = set()
    edges = []
    url_to_label = {}

    queue = [start_url]

    while queue and len(visited) < 10_000:
        current_url = queue.pop(0)
        if current_url in visited:
            continue

        visited.add(current_url)

        # Fetch the page
        try:
            resp = requests.get(current_url)
            if resp.status_code != 200:
                print(f"Failed to fetch: {current_url}")
            soup = BeautifulSoup(resp.text, "html.parser")
        except requests.exceptions.RequestException:
            print(f"Failed to fetch: {current_url}")

        # ---- Check if there's a <div class="jsx-2479918432 PrimaryNote"> ----
        primary_note_div = soup.find("div", class_="jsx-2479918432 PrimaryNote")
        if not primary_note_div:
            print(f"Skipping: {current_url}, no PrimaryNote div")

        # ---- Get <title> or fallback to <h1> ----
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            page_title = title_tag.get_text(strip=True)
        else:
            page_title = "No title"

        # ---- Build a label: path + : + page_title ----
        parsed_current = urlparse(current_url)
        path_part = parsed_current.path if parsed_current.path else "/"
        current_label = f"{path_part} : {page_title}"

        url_to_label[current_url] = current_label
        print(f"Visited: {current_label}, {current_url}, {len(visited)}")

        # ---- Extract links only inside the PrimaryNote div ----
        try:
            a_tags = primary_note_div.find_all("a", href=True)
        except Exception as e:
            print(e)
        for a in a_tags:
            href = a["href"]
            full_link = urljoin(current_url, href)
            parsed_link = urlparse(full_link)

            # Only follow links in the same domain
            if parsed_link.netloc == domain:
                if parsed_link.path.startswith("/z"):
                    # We keep this edge
                    edges.append((current_url, full_link))

                    # Enqueue to crawl further
                    if full_link not in visited:
                        queue.append(full_link)
    return visited, edges, url_to_label


def build_graph_and_export_gexf(
    visited, edges, url_to_label, output_path="./file.gexf"
):
    """
    Build a directed graph (NetworkX DiGraph) and write it to GEXF.
    - Node labels: path + : + <title> (from url_to_label).
    - Edges: from label of src to label of dst.
    """
    G = nx.DiGraph()

    # Add nodes
    for url in visited:
        label = url_to_label.get(url, url)
        G.add_node(label)

    # Add edges
    for src, dst in edges:
        if src in url_to_label and dst in url_to_label:
            src_label = url_to_label[src]
            dst_label = url_to_label[dst]
            G.add_edge(src_label, dst_label)

    nx.write_gexf(G, output_path)
    print(f"GEXF graph exported to: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    START_URL = "https://notes.andymatuschak.org/About_these_notes"

    visited_urls, link_edges, url_to_label_map = crawl_site_for_primarynote_links(
        START_URL,
    )

    build_graph_and_export_gexf(
        visited=visited_urls,
        edges=link_edges,
        url_to_label=url_to_label_map,
        output_path="./file.gexf",
    )

```python
"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.
"""

import re

from tools import (
    search_listings,
    suggest_outfit,
    create_fit_card,
)


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main FitFindr planning loop.
    """

    session = _new_session(query, wardrobe)

    # ---------------------------------------------------------
    # Step 1: Parse query
    # ---------------------------------------------------------

    query_lower = query.lower()

    size = None
    max_price = None

    common_sizes = [
        "xxs",
        "xs",
        "s",
        "m",
        "l",
        "xl",
        "xxl",
    ]

    for possible_size in common_sizes:
        if f"size {possible_size}" in query_lower:
            size = possible_size.upper()
            break

    price_match = re.search(r"\$?(\d+)", query_lower)

    if (
        price_match
        and (
            "under" in query_lower
            or "below" in query_lower
            or "$" in query_lower
        )
    ):
        max_price = float(price_match.group(1))

    description = query

    if "under" in query_lower:
        description = query_lower.split("under")[0]

    if "size" in query_lower:
        description = description.split("size")[0]

    description = description.strip()

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # ---------------------------------------------------------
    # Step 2: Search listings
    # ---------------------------------------------------------

    results = search_listings(
        description=description,
        size=size,
        max_price=max_price,
    )

    session["search_results"] = results

    if not results:
        session["error"] = (
            "No listings matched your search. "
            "Try a different size, budget, or description."
        )
        return session

    # ---------------------------------------------------------
    # Step 3: Select best item
    # ---------------------------------------------------------

    selected_item = results[0]

    session["selected_item"] = selected_item

    # ---------------------------------------------------------
    # Step 4: Suggest outfit
    # ---------------------------------------------------------

    outfit = suggest_outfit(
        selected_item,
        wardrobe,
    )

    session["outfit_suggestion"] = outfit

    # ---------------------------------------------------------
    # Step 5: Create fit card
    # ---------------------------------------------------------

    fit_card = create_fit_card(
        outfit,
        selected_item,
    )

    session["fit_card"] = fit_card

    # ---------------------------------------------------------
    # Step 6: Return completed session
    # ---------------------------------------------------------

    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import (
        get_example_wardrobe,
    )

    print("=== Happy path ===\n")

    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )

    if session["error"]:
        print("ERROR:")
        print(session["error"])

    else:
        print("FOUND ITEM:")
        print(session["selected_item"]["title"])

        print("\nOUTFIT:")
        print(session["outfit_suggestion"])

        print("\nFIT CARD:")
        print(session["fit_card"])

    print("\n\n=== No Results Path ===\n")

    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )

    print(session2["error"])
```
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.

    Args:
        query:    Natural language user request
                  (e.g., "vintage graphic tee under $30, size M")
        wardrobe: User's wardrobe dict — use get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py

    Returns:
        The session dict after the interaction completes. Check session["error"]
        first — if it is not None, the interaction ended early and the other
        output fields (outfit_suggestion, fit_card) will be None.

    TODO — implement this function using the planning loop you designed in planning.md:

        Step 1: Initialize the session with _new_session().

        Step 2: Parse the user's query to extract a description, size, and
                max_price. You can use regex, string splitting, or ask the LLM
                to parse it — document your choice in planning.md.
                Store the result in session["parsed"].

        Step 3: Call search_listings() with the parsed parameters.
                Store results in session["search_results"].
                If no results: set session["error"] to a helpful message and
                return the session early. Do NOT proceed to suggest_outfit
                with empty input.

        Step 4: Select the item to use (e.g., the top result).
                Store it in session["selected_item"].

        Step 5: Call suggest_outfit() with the selected item and wardrobe.
                Store the result in session["outfit_suggestion"].

        Step 6: Call create_fit_card() with the outfit suggestion and selected item.
                Store the result in session["fit_card"].

        Step 7: Return the session.

    Before writing code, complete the Planning Loop and State Management sections
    of planning.md — your implementation should match what you described there.
    """
    # TODO: implement the planning loop
    session = _new_session(query, wardrobe)
    session["error"] = "Planning loop not yet implemented."
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")

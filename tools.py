```python
"""
tools.py
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )

    return Groq(api_key=api_key)


# ------------------------------------------------------------------
# Tool 1
# ------------------------------------------------------------------

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:

    listings = load_listings()

    keywords = description.lower().split()

    scored_results = []

    for item in listings:

        if max_price is not None and item["price"] > max_price:
            continue

        if size is not None:
            item_size = item["size"].lower()

            if size.lower() not in item_size:
                continue

        searchable_text = " ".join(
            [
                item["title"],
                item["description"],
                item["category"],
                " ".join(item["style_tags"]),
                item["brand"],
            ]
        ).lower()

        score = sum(
            1
            for keyword in keywords
            if keyword in searchable_text
        )

        if score > 0:
            scored_results.append((score, item))

    scored_results.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [item for score, item in scored_results]


# ------------------------------------------------------------------
# Tool 2
# ------------------------------------------------------------------

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:

    client = _get_groq_client()

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:

        prompt = f"""
        A user is considering buying this thrifted item:

        {new_item}

        Their wardrobe is empty.

        Give 1-2 outfit suggestions using general styling advice.
        Mention colors, vibes, and pieces that pair well.
        Keep response under 150 words.
        """

    else:

        wardrobe_text = "\n".join(
            [
                f"- {item.get('name', str(item))}"
                for item in wardrobe_items
            ]
        )

        prompt = f"""
        New thrifted item:

        {new_item}

        User wardrobe:

        {wardrobe_text}

        Create 1-2 outfit combinations using specific pieces
        from the wardrobe.

        Mention why the outfit works.

        Keep response under 200 words.
        """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content


# ------------------------------------------------------------------
# Tool 3
# ------------------------------------------------------------------

def create_fit_card(outfit: str, new_item: dict) -> str:

    if not outfit or not outfit.strip():
        return (
            "Unable to generate fit card because "
            "no outfit suggestion was provided."
        )

    client = _get_groq_client()

    prompt = f"""
    Create a short Instagram/TikTok outfit caption.

    Item:
    {new_item['title']}

    Price:
    ${new_item['price']}

    Platform:
    {new_item['platform']}

    Outfit:
    {outfit}

    Requirements:
    - 2 to 4 sentences
    - casual tone
    - not a product advertisement
    - mention item name once
    - mention price once
    - mention platform once
    - sound like a real fashion post
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=1.0,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content
```


import json

def extract_notebooks(response_text: str) -> list[dict[str, str]]:
    try:
        outer_list = response_text.split("\n")[3]
        main_text = json.loads(outer_list)[0][2]
        nb_list = json.loads(main_text)[0]

        result = []
        for title, _, id, *_ in nb_list:
            result.append({"title": title, "id": id})
        return result

    except Exception as e:
        raise ValueError(f"Notebooks Extractor: Invalid input of response_text: {e}")

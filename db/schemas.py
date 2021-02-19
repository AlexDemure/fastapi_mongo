from datetime import datetime

def material_row(material) -> dict:
    return {
        "id": str(material["_id"]),
        "filename": material["filename"],
        "isbn": material["isbn"],
        "Title": material["Title"],
        "format": material["format"],
        "Authors": material["Authors"],
        "Narrators": material["Narrators"],
        "Imprint": material["Imprint"],
        "Hours": material["Hours"],
    }


EXAMPLES = [
    {
        "isbn": "040501008164",
        "Title": "123",
        "format": "123",
        "Authors": "123",
        "Narrators":"123",
        "Imprint": "123",
        "Hours": "123",
    },
    {
        "isbn": "040501008164",
        "Title": "123",
        "format": "123",
        "Authors": "123",
        "Narrators": "123",
        "Imprint": "123",
        "Hours": "123",
    },
    {
        "isbn": "040501008164",
        "Title": "123",
        "format": "123",
        "Authors": "123",
        "Narrators":"123",
        "Imprint": "123",
        "Hours": "123",
    },
]
EXAMPLES2 = [
    {
        "isbn": "040501008164",
        "Title": "123",
        "format": "123",
        "Authors": "123",
        "Narrators":"123",
        "Imprint": "123",
        "Hours": "123",
    },
    {
        "isbn": "040501008164",
        "Title": "123",
        "format": "123",
        "Authors": "123",
        "Narrators":"123",
        "Imprint": "123",
        "Hours": "123",
    },
    {
        "isbn": "040501008164",
        "Title": "123",
        "format": "123",
        "Authors": "123",
        "Narrators":"123",
        "Imprint": "123",
        "Hours": "123",
    },
]

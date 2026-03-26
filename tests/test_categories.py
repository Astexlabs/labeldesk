from core.models.categories import ImgCat


def test_allCatsExist():
    expected = [
        "screenshot", "document", "face", "outdoor", "indoor",
        "food", "product", "abstract", "diagram", "icon", "generic",
    ]
    for name in expected:
        assert ImgCat(name).value == name


def test_catValues():
    assert ImgCat.screenshot.value == "screenshot"
    assert ImgCat.generic.value == "generic"

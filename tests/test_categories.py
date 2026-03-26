from labeldesk.core.models.categories import ImgCat


def test_catsExist():
    assert ImgCat.screenshot.value == "screenshot"
    assert ImgCat.generic.value == "generic"
    assert len(list(ImgCat)) == 11

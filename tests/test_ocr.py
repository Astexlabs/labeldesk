from labeldesk.pipeline.ocr import summarizeTxt


def test_summarizeTrims():
    long = "x " * 400
    out = summarizeTxt(long, maxLen=100)
    assert len(out) <= 103


def test_summarizeEmpty():
    assert summarizeTxt("") == ""


def test_summarizeJoinsLines():
    assert summarizeTxt("a\nb\nc") == "a b c"

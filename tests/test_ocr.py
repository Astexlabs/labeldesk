from pipeline.ocr import summarizeTxt


def test_summarizeTrimLong():
    txt = "a " * 200
    out = summarizeTxt(txt, maxLen=50)
    assert len(out) <= 54
    assert out.endswith("...")


def test_summarizeShort():
    out = summarizeTxt("hello world")
    assert out == "hello world"


def test_summarizeStripsBlanks():
    txt = "line1\n\n\nline2\n\n"
    out = summarizeTxt(txt)
    assert out == "line1 line2"

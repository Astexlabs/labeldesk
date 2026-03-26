from labeldesk.core.models.categories import ImgCat
from labeldesk.pipeline.classifier import LocalClassifier
from labeldesk.pipeline.signals import FreeSignals


def test_classifyScreenshot():
    c = LocalClassifier()
    sig = FreeSignals(fnameHints=["screenshot"])
    assert c.classifyFromSignals(sig) == ImgCat.screenshot


def test_classifySolid():
    c = LocalClassifier()
    sig = FreeSignals(isSolid=True)
    assert c.classifyFromSignals(sig) == ImgCat.icon


def test_classifyPanoramic():
    c = LocalClassifier()
    sig = FreeSignals(aspect="panoramic")
    assert c.classifyFromSignals(sig) == ImgCat.outdoor


def test_classifyGeneric():
    c = LocalClassifier()
    sig = FreeSignals()
    assert c.classifyFromSignals(sig) == ImgCat.generic

from typer.testing import CliRunner

from labeldesk.cli.main import app

runner = CliRunner()


def test_rootHelpShowsQuickstart():
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "quick start" in res.output
    assert "label ./pics" in res.output


def test_rootHelpListsAllCmds():
    res = runner.invoke(app, ["--help"])
    for cmd in ["label", "serve", "tui", "config", "models", "job"]:
        assert cmd in res.output


def test_labelHelpHasExamples():
    res = runner.invoke(app, ["label", "--help"])
    assert res.exit_code == 0
    assert "examples:" in res.output
    assert "--dry-run" in res.output


def test_labelHelpExplainsEveryOpt():
    res = runner.invoke(app, ["label", "--help"])
    assert "ai backend" in res.output
    assert "what to generate" in res.output
    assert "scan subdirs" in res.output
    assert "collection hint" in res.output


def test_configSetHelpHasExample():
    res = runner.invoke(app, ["config", "set", "--help"])
    assert res.exit_code == 0
    assert "section.key" in res.output
    assert "default.model" in res.output


def test_subcmdGroupsHaveDesc():
    res = runner.invoke(app, ["--help"])
    assert "get/set config" in res.output
    assert "list + test ai" in res.output
    assert "browse past" in res.output


def test_labelFailsWithNoImgs(tmp_path):
    res = runner.invoke(app, ["label", str(tmp_path), "--no-web"])
    assert res.exit_code == 1
    assert "no imgs" in res.output

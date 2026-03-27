import re

from typer.testing import CliRunner

from labeldesk.cli.main import app, _findWebDir, _npmCmd

runner = CliRunner()

_ansi_re = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    return _ansi_re.sub("", text)


def test_rootHelpShowsQuickstart():
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    assert "quick start" in res.output
    assert "label ./pics" in res.output
    assert "labeldesk web" in res.output


def test_rootHelpListsAllCmds():
    res = runner.invoke(app, ["--help"])
    for cmd in ["label", "web", "tui", "config", "models", "job"]:
        assert cmd in res.output


def test_noServeCmd():
    res = runner.invoke(app, ["serve"])
    assert res.exit_code != 0


def test_noWebFlag():
    res = runner.invoke(app, ["--help"])
    assert "--web" not in res.output
    res = runner.invoke(app, ["label", "--help"])
    assert "--no-web" not in res.output


def test_labelHelpHasExamples():
    res = runner.invoke(app, ["label", "--help"])
    assert res.exit_code == 0
    assert "examples:" in res.output
    assert "--dry-run" in _plain(res.output)


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
    res = runner.invoke(app, ["label", str(tmp_path)])
    assert res.exit_code == 1
    assert "no imgs" in res.output


def test_webHelpMentionsBothParts():
    res = runner.invoke(app, ["web", "--help"])
    assert res.exit_code == 0
    assert "fastapi" in res.output
    assert "nextjs" in res.output
    assert "--api-only" in _plain(res.output)
    assert "3000" in res.output


def test_findWebDirLocatesPkg():
    d = _findWebDir()
    assert d is not None
    assert (d / "package.json").exists()


def test_npmCmdNoBuild(tmp_path):
    cmd = _npmCmd(tmp_path, 3000)
    if cmd:
        assert "dev" in cmd
        assert "3000" in cmd


def test_npmCmdWithBuild(tmp_path):
    (tmp_path / ".next").mkdir()
    cmd = _npmCmd(tmp_path, 4000)
    if cmd:
        assert "start" in cmd
        assert "4000" in cmd

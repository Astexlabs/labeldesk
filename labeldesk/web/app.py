import asyncio
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from labeldesk.core.config import loadCfg
from labeldesk.core.models.base import ModelCfg
from labeldesk.core.models.registry import getAdapter, listAdapters
from labeldesk.core.output.formatters import fmtResults
from labeldesk.core.paths import uploadDir, expandImgPaths
from labeldesk.core.storage.job_store import JobStore
from labeldesk.pipeline.runner import PipelineRunner


class JobReq(BaseModel):
    paths: list[str]
    model: str = ""
    mode: str = "title"
    output: str = "json"
    recursive: bool = False
    ctx: str = ""


class CfgReq(BaseModel):
    section: str
    key: str
    value: str


def createApp() -> FastAPI:
    app = FastAPI(title="labeldesk", version="0.2.0")
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"],
        allow_methods=["*"], allow_headers=["*"],
    )

    @app.get("/api/health")
    def health():
        return {"ok": True}

    @app.get("/api/models")
    def models():
        cfg = loadCfg()
        out = []
        for name in listAdapters():
            sec = cfg.section(name)
            try:
                mcfg = ModelCfg(
                    apiKey=cfg.get(name, "api_key", ""),
                    modelId=sec.get("model_id", ""),
                    host=sec.get("host", ""),
                )
                a = getAdapter(name, mcfg)
                avail = a.isAvail()
            except Exception:
                avail = False
            out.append({"name": name, "available": avail, "modelId": sec.get("model_id", "")})
        return out

    @app.get("/api/config")
    def getCfg():
        cfg = loadCfg()
        safe = {}
        for sec, vals in cfg.data.items():
            safe[sec] = {}
            for k, v in vals.items():
                if "key" in k and v:
                    safe[sec][k] = str(v)[:8] + "..."
                else:
                    safe[sec][k] = v
        return safe

    @app.post("/api/config")
    def setCfg(req: CfgReq):
        cfg = loadCfg()
        cfg.set(req.section, req.key, req.value)
        cfg.save()
        return {"ok": True}

    @app.post("/api/upload")
    async def upload(files: list[UploadFile] = File(...)):
        saved = []
        for f in files:
            dst = uploadDir() / f.filename
            with open(dst, "wb") as out:
                shutil.copyfileobj(f.file, out)
            saved.append(str(dst))
        return {"paths": saved}

    @app.post("/api/jobs")
    def createJob(req: JobReq, bg: BackgroundTasks):
        cfg = loadCfg()
        modelName = req.model or cfg.get("default", "model", "anthropic")
        imgPaths = expandImgPaths(req.paths, recursive=req.recursive)
        if not imgPaths:
            raise HTTPException(400, "no imgs found")

        store = JobStore()
        job = store.create(
            inputPaths=[str(p) for p in imgPaths],
            adapter=modelName, mode=req.mode, outputFmt=req.output,
            totalFiles=len(imgPaths), status="queued",
        )
        store.close()
        bg.add_task(_runJob, job.id, req, modelName)
        return {"jobId": job.id, "totalFiles": len(imgPaths)}

    @app.get("/api/jobs")
    def listJobs(limit: int = 50):
        store = JobStore()
        jobs = [_jobDict(j) for j in store.list(limit)]
        store.close()
        return jobs

    @app.get("/api/jobs/{jobId}")
    def getJob(jobId: str):
        store = JobStore()
        j = store.get(jobId)
        store.close()
        if not j:
            raise HTTPException(404, "not found")
        return _jobDict(j)

    @app.delete("/api/jobs/{jobId}")
    def delJob(jobId: str):
        store = JobStore()
        store.delete(jobId)
        store.close()
        return {"ok": True}

    return app


def _jobDict(j):
    return {
        "id": j.id, "createdAt": j.createdAt, "status": j.status,
        "adapter": j.adapter, "mode": j.mode, "outputFmt": j.outputFmt,
        "totalFiles": j.totalFiles, "doneFiles": j.doneFiles,
        "tokensUsed": j.tokensUsed, "costUsd": j.costUsd,
        "error": j.error, "results": j.results,
    }


def _runJob(jobId: str, req: JobReq, modelName: str):
    cfg = loadCfg()
    store = JobStore()
    job = store.get(jobId)
    job.status = "running"
    store.update(job)

    try:
        sec = cfg.section(modelName)
        mcfg = ModelCfg(
            apiKey=cfg.get(modelName, "api_key", ""),
            modelId=sec.get("model_id", ""),
            host=sec.get("host", ""),
        )
        adapter = getAdapter(modelName, mcfg)
    except Exception:
        adapter = None

    def tick(msg, done, total):
        job.doneFiles = done
        store.update(job)

    runner = PipelineRunner(
        adapter=adapter, modelName=modelName, mode=req.mode,
        collectionCtx=req.ctx, progressCb=tick,
    )
    try:
        results = runner.processMany(req.paths, recursive=req.recursive)
        job.results = {k: v.asDict() for k, v in results.items()}
        job.status = "done"
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
    finally:
        runner.close()
        store.update(job)
        store.close()

import argparse
from pathlib import Path

from pipeline.runner import PipelineRunner


def main():
    ap = argparse.ArgumentParser(description="labeldesk - smart img labeler")
    ap.add_argument("imgs", nargs="+", help="img paths to label")
    ap.add_argument("--mode", default="title", choices=["title", "description", "tags"])
    ap.add_argument("--model", default="default")
    ap.add_argument("--onnx", default=None, help="path to onnx classifier model")
    ap.add_argument("--cache", default=".labeldesk_cache.db")
    ap.add_argument("--batch-sz", type=int, default=5)
    ap.add_argument("--ctx", default="", help="collection context str")
    args = ap.parse_args()

    runner = PipelineRunner(
        adapter=None,
        modelName=args.model,
        mode=args.mode,
        onnxPath=args.onnx,
        cachePath=args.cache,
        batchSz=args.batch_sz,
        collectionCtx=args.ctx,
    )

    results = runner.processMany([Path(p) for p in args.imgs])
    for path, res in results.items():
        print(f"{path}: {res.title} [{res.src}]")
    runner.close()


if __name__ == "__main__":
    main()

"""openwig.diagnostics - live self-test of the reflection paths (the "resolver").

The bridge reaches into Bitwig's obfuscated internals to write arranger automation,
create arranger clips, and read the document graph. Those internal class/method names are
stable for a given Bitwig build but get re-obfuscated each release, so they can move
between versions. `run_selftest` verifies, on a throwaway track, that each path still works
on the LIVE build, resolves the descriptor-reader names, and (controller side) writes a
symbol cache the bridge loads at init. `openwig doctor` prints the report.

The probe creates a temporary instrument track, writes to it, verifies the writes via a
descriptor read, then deletes it. It never modifies your existing tracks. It fails safe: a
broken path is reported, not silently ignored.
"""
from __future__ import annotations

import time

from openwig.bridge import BridgeClient, BridgeError

PROBE_TRACK = "__openwig_probe__"


def _occupied(b):
    """Set of main-track indices currently occupied (by name; the exists flag is flaky)."""
    snap = b.request("state.snapshot")
    return {t.get("index") for t in snap.get("tracks", []) if t.get("name")}


def _delete_index(b, idx):
    try:
        b.request("track.delete", {"index": idx})
    except BridgeError:
        pass


def run_selftest(b=None, *, timeout=90.0):
    """Run the resolver self-test against live Bitwig.

    Returns the report dict from ``resolver.probe`` augmented with a top-level
    ``connected`` flag (and ``classes`` / ``bitwig`` even when the round-trip can't run).
    Creates and deletes a temporary probe track; never modifies existing tracks. The probe
    track is identified by INDEX-DIFF (the new slot that appears), not by name, because the
    post-create rename can silently fail right after a controller reload.
    """
    own = b is None
    if own:
        b = BridgeClient()
        b.start()
    try:
        if not b.wait_connected(4.0):
            return {"connected": False}
        # class-load check is cheap and works even if the round-trip can't run
        classes = b.request("resolver.classes")
        base = {"connected": True,
                "classes": classes.get("classes"),
                "bitwig": classes.get("bitwig")}
        before = _occupied(b)
        new_indices = []
        try:
            b.request("track.create", {"type": "instrument", "name": PROBE_TRACK})
            # wait for a NEW occupied slot to appear (rename may fail, so do not match by name)
            idx = None
            for _ in range(8):
                time.sleep(0.25)
                new_indices = sorted(_occupied(b) - before)
                if new_indices:
                    idx = new_indices[-1]
                    break
            if idx is None:
                base["error"] = "probe track did not appear (cannot run round-trip)"
                return base
            b.request("track.select", {"index": idx})
            time.sleep(0.3)
            b.request_op("resolver.probe", timeout=timeout)
            res = b.request("resolver.result")
            report = res.get("report") or dict(base)
            report["connected"] = True
            if res.get("error"):
                report["error"] = res["error"]
            return report
        finally:
            # remove every slot that appeared during the probe (covers a failed rename),
            # deleting from the highest index down so earlier indices stay valid.
            for idx in sorted(_occupied(b) - before, reverse=True):
                _delete_index(b, idx)
    finally:
        if own:
            b.stop()

import asyncio
import json
import random
import time

import httpx
import websockets


async def main() -> None:
    base = "http://localhost:8000"
    api_key = "dev-secret"

    async with httpx.AsyncClient(base_url=base, timeout=10.0) as client:
        r = await client.post(
            "/start-session",
            json={"language": "en", "level": "beginner"},
            headers={"X-API-Key": api_key},
        )
        r.raise_for_status()
        session = r.json()
        session_id = session["session_id"]

    ws_url = f"ws://localhost:8000/ws/session/{session_id}"
    print("session_id:", session_id)
    print("ws_url:", ws_url)

    def log_frame(tag: str, i: int, k: float | None, resp: dict, *, rtt_ms: float | None = None) -> None:
        dbg = resp.get("debug") or {}
        knee_s = f"{k:6.1f}" if k is not None else "  n/a "
        rtt_s = f"{rtt_ms:6.1f}ms" if rtt_ms is not None else "   n/a "
        print(
            f"{tag} frame={i:04d} knee={knee_s} rep={resp.get('rep_count')} paused={resp.get('paused')} "
            f"phase={dbg.get('phase')} score={resp.get('score')} issues={resp.get('issues')} "
            f"elapsed={dbg.get('elapsed_ms')} rtt={rtt_s}"
        )

    # Simulated squat sessions:
    # - perfect-ish: reaches ~95° and returns to lockout
    # - bad form: excessive forward lean + shallow depth
    # - mixed: combines both patterns
    squat_perfect = [175, 165, 140, 120, 105, 95, 105, 130, 160, 175]
    squat_bad = [175, 165, 150, 135, 130, 128, 135, 150, 165, 175]
    squat_mixed = squat_perfect + squat_bad + squat_perfect

    def jitter(x: float, *, sigma: float = 2.0) -> float:
        return x + random.gauss(0.0, sigma)

    t = 0.0
    rtts: list[float] = []
    server_elapsed: list[float] = []
    async with websockets.connect(ws_url, ping_interval=20, additional_headers={"X-API-Key": api_key}) as ws:
        # Perfect session
        print("\n--- PERFECT SQUAT SESSION ---")
        for i, k in enumerate(squat_perfect):
            frame = {"exercise": "squat", "angles": {"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 20.0}, "timestamp": t, "frame_id": i}
            t += 0.05
            t0 = time.perf_counter()
            await ws.send(json.dumps(frame))
            resp = json.loads(await ws.recv())
            rtt = (time.perf_counter() - t0) * 1000.0
            rtts.append(rtt)
            if isinstance((resp.get("debug") or {}).get("elapsed_ms"), (int, float)):
                server_elapsed.append(float(resp["debug"]["elapsed_ms"]))
            log_frame("perfect", i, float(k), resp, rtt_ms=rtt)

        # Bad form session (lean + shallow)
        print("\n--- BAD FORM SQUAT SESSION ---")
        base_i = 1000
        for j, k in enumerate(squat_bad):
            i = base_i + j
            frame = {"exercise": "squat", "angles": {"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 65.0}, "timestamp": t, "frame_id": i}
            t += 0.05
            t0 = time.perf_counter()
            await ws.send(json.dumps(frame))
            resp = json.loads(await ws.recv())
            rtt = (time.perf_counter() - t0) * 1000.0
            rtts.append(rtt)
            if isinstance((resp.get("debug") or {}).get("elapsed_ms"), (int, float)):
                server_elapsed.append(float(resp["debug"]["elapsed_ms"]))
            log_frame("bad", i, float(k), resp, rtt_ms=rtt)

        # Mixed session
        print("\n--- MIXED SQUAT SESSION ---")
        base_i = 2000
        for j, k in enumerate(squat_mixed):
            i = base_i + j
            torso = 20.0 if j < len(squat_perfect) or j >= len(squat_perfect) + len(squat_bad) else 65.0
            frame = {"exercise": "squat", "angles": {"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": torso}, "timestamp": t, "frame_id": i}
            t += 0.05
            t0 = time.perf_counter()
            await ws.send(json.dumps(frame))
            resp = json.loads(await ws.recv())
            rtt = (time.perf_counter() - t0) * 1000.0
            rtts.append(rtt)
            if isinstance((resp.get("debug") or {}).get("elapsed_ms"), (int, float)):
                server_elapsed.append(float(resp["debug"]["elapsed_ms"]))
            log_frame("mixed", i, float(k), resp, rtt_ms=rtt)

        # Noisy session (angle jitter) to test smoothing stability
        print("\n--- NOISY SQUAT SESSION (JITTER) ---")
        base_i = 3000
        for j, k in enumerate(squat_perfect * 2):
            i = base_i + j
            kj = jitter(float(k), sigma=3.5)
            frame = {"exercise": "squat", "angles": {"knee_l": kj, "knee_r": kj, "torso_l_vs_vertical": 22.0}, "timestamp": t, "frame_id": i}
            t += 0.05
            t0 = time.perf_counter()
            await ws.send(json.dumps(frame))
            resp = json.loads(await ws.recv())
            rtt = (time.perf_counter() - t0) * 1000.0
            rtts.append(rtt)
            if isinstance((resp.get("debug") or {}).get("elapsed_ms"), (int, float)):
                server_elapsed.append(float(resp["debug"]["elapsed_ms"]))
            if j < 6 or j > (len(squat_perfect) * 2 - 4):
                log_frame("noisy", i, kj, resp, rtt_ms=rtt)

        # Missing joints / out-of-frame session: send joints only (no angles) with missing required joints
        print("\n--- VISIBILITY FAILURE SESSION (MISSING JOINTS, NO ANGLES) ---")
        base_i = 4000
        for j in range(6):
            i = base_i + j
            frame = {
                "exercise": "squat",
                "joints": [{"name": "hip_l", "x": 0.0, "y": 0.0, "confidence": 0.9}],  # insufficient
                "timestamp": t,
                "frame_id": i,
            }
            t += 0.05
            t0 = time.perf_counter()
            await ws.send(json.dumps(frame))
            resp = json.loads(await ws.recv())
            rtt = (time.perf_counter() - t0) * 1000.0
            rtts.append(rtt)
            log_frame("missing", i, None, resp, rtt_ms=rtt)

        # Sudden movement spikes (unrealistic jumps): should not double count reps due to cooldown
        print("\n--- SPIKE SESSION (SUDDEN JUMPS) ---")
        base_i = 5000
        spike_series = [175, 90, 175, 90, 175, 90, 175]
        for j, k in enumerate(spike_series):
            i = base_i + j
            frame = {"exercise": "squat", "angles": {"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 20.0}, "timestamp": t, "frame_id": i}
            t += 0.05
            t0 = time.perf_counter()
            await ws.send(json.dumps(frame))
            resp = json.loads(await ws.recv())
            rtt = (time.perf_counter() - t0) * 1000.0
            rtts.append(rtt)
            log_frame("spike", i, float(k), resp, rtt_ms=rtt)

    async with httpx.AsyncClient(base_url=base, timeout=10.0) as client:
        s = await client.get(f"/session-summary/{session_id}", headers={"X-API-Key": api_key})
        s.raise_for_status()
        print("summary:", json.dumps(s.json(), indent=2))

    if rtts:
        rtts_sorted = sorted(rtts)
        p50 = rtts_sorted[int(0.50 * (len(rtts_sorted) - 1))]
        p95 = rtts_sorted[int(0.95 * (len(rtts_sorted) - 1))]
        print(f"\nPERF client RTT ms: avg={sum(rtts)/len(rtts):.1f} p50={p50:.1f} p95={p95:.1f} n={len(rtts)}")
    if server_elapsed:
        se_sorted = sorted(server_elapsed)
        p50 = se_sorted[int(0.50 * (len(se_sorted) - 1))]
        p95 = se_sorted[int(0.95 * (len(se_sorted) - 1))]
        print(
            f"PERF server elapsed_ms: avg={sum(server_elapsed)/len(server_elapsed):.2f} p50={p50:.2f} p95={p95:.2f} n={len(server_elapsed)}"
        )


if __name__ == "__main__":
    asyncio.run(main())


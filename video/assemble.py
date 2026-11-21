#!/usr/bin/env python3
"""Assemble twin-memory-demo.mp4 from frames + TTS narration.

Frame durations = narration segment durations (seg02 split across f02a/f02b).
Trace frame (f07) is 8.160s, above the 5s minimum. Total must stay < 300s.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (frame, audio segment, share of segment) — seg02 is split 50/50
PLAN = [
    ("frames/f01_title.png", "seg01", 1.0),
    ("frames/f02a_observer.png", "seg02", 0.5),
    ("frames/f02b_memories.png", "seg02", 0.5),
    ("frames/f03_search.png", "seg03", 1.0),
    ("frames/f04_story.png", "seg04", 1.0),
    ("frames/f05_draft.png", "seg05", 1.0),
    ("frames/f06_verdict.png", "seg06", 1.0),
    ("frames/f07_trace.png", "seg07", 1.0),
    ("frames/f08_rewrite.png", "seg08", 1.0),
    ("frames/f09_tokens.png", "seg09", 1.0),
    ("frames/f10_end.png", "seg10", 1.0),
]


def ffprobe_dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    durs = {}
    for i in range(1, 11):
        durs[f"seg{i:02d}"] = ffprobe_dur(ROOT / "audio" / f"seg{i:02d}.mp3")
    print("audio durations:", {k: round(v, 3) for k, v in durs.items()})
    total = sum(durs.values())
    print(f"total audio: {total:.3f}s")

    # video concat list
    lines = []
    for frame, seg, share in PLAN:
        dur = durs[seg] * share
        lines.append(f"file '{frame}'")
        lines.append(f"duration {dur:.3f}")
    # concat demuxer needs the last file repeated without duration
    lines.append(f"file '{PLAN[-1][0]}'")
    (ROOT / "frames.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # audio concat list
    alines = [f"file 'audio/seg{i:02d}.mp3'" for i in range(1, 11)]
    (ROOT / "audio.txt").write_text("\n".join(alines) + "\n", encoding="utf-8")

    def run(cmd):
        print("+", " ".join(cmd))
        subprocess.run(cmd, check=True, cwd=ROOT)

    # video-only (silent) from stills
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", "frames.txt", "-vf", "format=yuv420p", "-c:v", "libx264",
         "-r", "30", "video_silent.mp4"])
    # concatenated narration
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", "audio.txt", "-c:a", "libmp3lame", "-q:a", "3", "audio_full.mp3"])
    # mux
    run(["ffmpeg", "-y", "-v", "error", "-i", "video_silent.mp4",
         "-i", "audio_full.mp3", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-shortest", "twin-memory-demo.mp4"])

    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", "twin-memory-demo.mp4"],
        capture_output=True, text=True, check=True, cwd=ROOT).stdout)
    fmt = info["format"]
    print("FINAL duration:", fmt["duration"], "size:", fmt["size"])
    for s in info["streams"]:
        print("stream:", s["codec_type"], s["codec_name"],
              s.get("width"), s.get("height"))


if __name__ == "__main__":
    main()

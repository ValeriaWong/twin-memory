#!/usr/bin/env python3
"""Render the Twin Memory demo video frames (1280x720, dark terminal style).

All on-screen text comes from real live outputs:
- video/demo-live-take1.txt (live demo run, exit 0)
- video/context-search-live.json (live context_search, run by hand)
- video/rewrite-live.json (fresh live storyteller draft)
- traces/trace-e56411e9.md (live Guardian trace)
- Token numbers: live measure_tokens.py --mode live (415 vs 144, -65.3%)

No credentials, no account ids, no emails are rendered anywhere.
P-01's stored text contains a latin-1 mojibake of the em-dash; it is shown
truncated before that character, the same way the live demo truncates it.
"""
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "frames"
OUT.mkdir(exist_ok=True)

W, H = 1280, 720
BG = (11, 15, 20)          # near-black blue
PANEL = (17, 24, 33)
BORDER = (48, 64, 80)
GREEN = (88, 214, 141)
AMBER = (255, 193, 7)
RED = (255, 107, 107)
WHITE = (235, 238, 242)
DIM = (150, 163, 175)
CYAN = (110, 200, 220)
MUTED = (110, 120, 132)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Wrap text to fit max_w pixels (mono font: fixed char width)."""
    cw = fnt.getlength("x")
    n = max(10, int(max_w // cw))
    return textwrap.wrap(text, width=n)


def render(name, title, lines, accent=GREEN):
    """lines: list of (text, size, color, bold, wrap_width_px or None)."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # panel
    d.rounded_rectangle([28, 28, W - 28, H - 28], radius=14, fill=PANEL, outline=BORDER, width=2)
    # header badge
    badge = "● LIVE — Meko datapack twin-memory"
    bf = font(MONO_B, 20)
    d.text((52, 48), badge, font=bf, fill=GREEN)
    # title
    tf = font(SANS_B, 34)
    d.text((52, 84), title, font=tf, fill=WHITE)
    d.line([(52, 128), (W - 52, 128)], fill=BORDER, width=2)
    y = 148
    for text, size, color, bold, max_w in lines:
        fnt = font(MONO_B if bold else MONO, size)
        if max_w:
            parts = wrap(text, fnt, max_w)
        else:
            parts = [text]
        for part in parts:
            d.text((52, y), part, font=fnt, fill=color)
            y += int(size * 1.32)
        y += 4
    # footer
    ff = font(MONO, 16)
    d.text((52, H - 56), "Twin Memory · ContextCon Track 07 · github.com/ValeriaWong/twin-memory",
           font=ff, fill=MUTED)
    img.save(OUT / name)
    print("wrote", name)


# ---------------------------------------------------------------- frame 1: title
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.rounded_rectangle([28, 28, W - 28, H - 28], radius=14, fill=PANEL, outline=BORDER, width=2)
d.text((72, 120), "TWIN MEMORY", font=font(SANS_B, 92), fill=WHITE)
d.text((72, 240), "ContextCon — Track 07 · Best Auditability", font=font(SANS_B, 34), fill=GREEN)
d.text((72, 310), "One Meko datapack. Three agents. One real dog.",
       font=font(SANS, 30), fill=WHITE)
d.text((72, 360), "The dog is twinpet_001. Nothing here is a video",
       font=font(SANS, 26), fill=DIM)
d.text((72, 398), "generator and nothing is trained — this is only",
       font=font(SANS, 26), fill=DIM)
d.text((72, 436), "memory, and whether that memory can be trusted.",
       font=font(SANS, 26), fill=DIM)
d.text((72, 520), "● LIVE — Meko datapack twin-memory", font=font(MONO_B, 24), fill=GREEN)
d.text((72, 560), "Entrant: Allen Xiao", font=font(MONO, 24), fill=WHITE)
img.save(OUT / "f01_title.png")
print("wrote f01_title.png")

# ---------------------------------------------------------------- frame 2a: observer + S-02
render("f02a_observer.png", "Scene A — Agent A learns",
       [("$ python -m src.demo --mode live", 22, AMBER, True, None),
        ("Observer logged: Thunder sounded. The dog hid behind", 22, WHITE, False, 1180),
        ("the sofa and whined softly until the owner sat nearby.", 22, WHITE, False, 1180),
        ("", 22, WHITE, False, None),
        ("Shared memory — memory_get_all, live (total 8):", 22, CYAN, True, None),
        ("S-01  twinpet_001 is a cream-white dog, irregular light-tan", 20, WHITE, False, 1180),
        ("      markings, asymmetric semi-folded ears, curled tail.", 20, WHITE, False, 1180),
        ("S-02  The dog is afraid of thunder. When thunder sounds it", 20, GREEN, True, 1180),
        ("      hides behind the sofa and whines softly until the", 20, GREEN, True, 1180),
        ("      owner sits nearby.", 20, GREEN, True, 1180),
        ("", 20, WHITE, False, None),
        ("S-02 is the fact the Observer just logged —", 21, WHITE, False, 1180),
        ("now in shared memory.", 21, WHITE, False, 1180)])

# ---------------------------------------------------------------- frame 2b: rest of memory list + eye line
render("f02b_memories.png", "Scene A — shared memory (continued)",
       [("S-03  Favourite walk: the small park two streets away, morning.", 20, WHITE, False, 1180),
        ("S-04  Does not like being hugged by strangers; steps back.", 20, WHITE, False, 1180),
        ("S-05  Name rule: the twin's name only; the owner is 'the owner'.", 20, WHITE, False, 1180),
        ("S-06  Greets the owner at the door, wagging curled tail.", 20, WHITE, False, 1180),
        ("S-07  Rainy day + thunder: hides behind the sofa; when rain", 20, WHITE, False, 1180),
        ("      eases, goes to the window to watch the rain.", 20, WHITE, False, 1180),
        ("P-01  [private] Watched the rain from the window a long time…", 20, DIM, False, 1180),
        ("", 20, WHITE, False, None),
        ("Eyes: frozen identity uses healthy dark-brown eyes (owner's", 19, AMBER, False, 1180),
        ("chosen digital look). The real dog's right eye is fully white.", 19, AMBER, False, 1180),
        ("Both recorded; eye colour is never an identity check.", 19, AMBER, False, 1180)])

# ---------------------------------------------------------------- frame 3: search
render("f03_search.png", "Storyteller searches first",
       [('$ context_search("rainy day story")  — live', 21, AMBER, True, None),
        ("match_quality: low   (the server's own band)", 20, WHITE, False, None),
        ("buckets:  memory 5  ·  knowledge_base 0  ·  conversation 0 (empty)", 20, WHITE, False, None),
        ("", 20, WHITE, False, None),
        ("memory hits:", 20, CYAN, True, None),
        ("S-07  0.461  On a rainy day with thunder, the dog hides", 20, GREEN, True, 1180),
        ("             behind the sofa and whines softly…", 20, GREEN, True, 1180),
        ("P-01  0.422  The dog seemed to watch the rain from the", 20, WHITE, False, 1180),
        ("             window for a long time…", 20, WHITE, False, 1180),
        ("S-05  0.242  The dog's name in stories is the twin's name only…", 20, WHITE, False, 1180),
        ("S-02  0.233  The dog is afraid of thunder. When thunder", 20, WHITE, False, 1180),
        ("             sounds it hides behind the sofa…", 20, WHITE, False, 1180),
        ("S-03  0.221  The dog's favourite walk is the small park…", 20, WHITE, False, 1180),
        ("", 20, WHITE, False, None),
        ("Top hit is S-07 — the bridging memory added after Meko's", 19, AMBER, False, 1180),
        ("self-learning flagged this query as a weak match.", 19, AMBER, False, 1180)])

# ---------------------------------------------------------------- frame 4: story draft
render("f04_story.png", "Scene A — the story, from memory only",
       [("Storyteller draft (live):", 22, CYAN, True, None),
        ("", 22, WHITE, False, None),
        ("\"Rain drummed on the window. The dog hid behind the sofa", 24, WHITE, False, 1180),
        ("and whined softly until the owner sat nearby, and then its", 24, WHITE, False, 1180),
        ("curled tail thumped once, twice, against the floor.\"", 24, WHITE, False, 1180),
        ("", 22, WHITE, False, None),
        ("Footnotes — every line comes from a memory that exists:", 21, CYAN, True, None),
        ("S-07  rainy day + thunder, hides behind the sofa", 21, WHITE, False, 1180),
        ("P-01  watches the rain from the window", 21, WHITE, False, 1180),
        ("S-02  afraid of thunder, whines until the owner sits nearby", 21, WHITE, False, 1180),
        ("S-05  name rule · S-03  favourite walk", 21, WHITE, False, 1180),
        ("", 21, WHITE, False, None),
        ("Guardian verdict on Scene A draft: ALLOW", 24, GREEN, True, None),
        ("No human speech by the dog — a soft whine only.", 21, WHITE, False, 1180)])

# ---------------------------------------------------------------- frame 5: scene B draft
render("f05_draft.png", "Scene B — the failure case",
       [("Prompt: a story where the dog explains, in words, why it", 22, WHITE, False, 1180),
        ("is afraid. The one thing this twin must never do.", 22, WHITE, False, 1180),
        ("", 22, WHITE, False, None),
        ("Draft under review:", 22, CYAN, True, None),
        ("", 22, WHITE, False, None),
        ('"I am afraid of the thunder," said the dog.', 30, RED, True, 1180),
        ('"Please stay with me."', 30, RED, True, 1180),
        ("", 22, WHITE, False, None),
        ("The dog is speaking human words.", 22, WHITE, False, 1180)])

# ---------------------------------------------------------------- frame 6: guardian verdict
render("f06_verdict.png", "Guardian verdict: BLOCK",
       [("Rule: R-01 — The twin never speaks human speech.", 23, RED, True, 1180),
        ("Dog sounds and behaviour only.", 23, RED, True, 1180),
        ("", 22, WHITE, False, None),
        ("Memories consulted (live scores):", 22, CYAN, True, None),
        ("S-07  0.512  On a rainy day with thunder, the dog hides…", 21, WHITE, False, 1180),
        ("P-01  0.411  The dog seemed to watch the rain from the window…", 21, WHITE, False, 1180),
        ("S-02  0.393  The dog is afraid of thunder…", 21, WHITE, False, 1180),
        ("S-05  0.237  The dog's name in stories is the twin's name only…", 21, WHITE, False, 1180),
        ("S-03  0.202  The dog's favourite walk is the small park…", 21, WHITE, False, 1180),
        ("", 21, WHITE, False, None),
        ("Missing facts: none needed —", 22, WHITE, False, 1180),
        ("the block is on the rule, not on missing data.", 22, WHITE, False, 1180)])

# ---------------------------------------------------------------- frame 7: trace
render("f07_trace.png", "The trace — replayable",
       [("traces/trace-e56411e9.md  ·  also stored as a datapack artifact", 21, CYAN, True, 1180),
        ("", 21, WHITE, False, None),
        ("Verdict: BLOCK", 26, RED, True, None),
        ("Rule: R-01 — The twin never speaks human speech.", 22, WHITE, True, 1180),
        ("", 22, WHITE, False, None),
        ('Draft checked: "I am afraid of the thunder," said the dog.', 21, WHITE, False, 1180),
        ('"Please stay with me."', 21, WHITE, False, 1180),
        ("", 21, WHITE, False, None),
        ("Why: The draft gives the dog human speech. The twin never", 21, WHITE, False, 1180),
        ("speaks human words — only dog sounds and behaviour. The fear", 21, WHITE, False, 1180),
        ("itself is real and in shared memory (S-02), so the story can", 21, WHITE, False, 1180),
        ("keep the fear and lose the words: hide behind the sofa,", 21, WHITE, False, 1180),
        ("whine softly, wait for the owner.", 21, WHITE, False, 1180)])

# ---------------------------------------------------------------- frame 8: rewrite
render("f08_rewrite.png", "The rewrite — fear kept, words lost",
       [("The Storyteller rewrites from the trace.", 22, WHITE, False, 1180),
        ("The Guardian never rewrites the story itself.", 22, WHITE, False, 1180),
        ("", 22, WHITE, False, None),
        ("Fresh live run, same prompt \"rainy day story\":", 22, CYAN, True, None),
        ("", 22, WHITE, False, None),
        ("\"Rain drummed on the window. The dog hid behind the sofa", 24, WHITE, False, 1180),
        ("and whined softly until the owner sat nearby, and then its", 24, WHITE, False, 1180),
        ("curled tail thumped once, twice, against the floor.\"", 24, WHITE, False, 1180),
        ("", 22, WHITE, False, None),
        ("Keeps the fear (S-02, S-07). Loses the words.", 22, GREEN, True, 1180),
        ("No human speech. Identical to the Scene A draft.", 21, WHITE, False, 1180)])

# ---------------------------------------------------------------- frame 9: tokens
render("f09_tokens.png", "Same task, same quality check",
       [("Baseline — stuff the full context into the prompt:", 22, WHITE, False, 1180),
        ("415 tokens", 44, WHITE, True, None),
        ("", 22, WHITE, False, None),
        ("Meko retrieval — only the memories the search returns:", 22, WHITE, False, 1180),
        ("144 tokens", 44, GREEN, True, None),
        ("", 22, WHITE, False, None),
        ("Saving: 65.3%", 36, GREEN, True, None),
        ("", 22, WHITE, False, None),
        ("Method: ~4 chars/token estimate (tiktoken not installed).", 20, DIM, False, 1180),
        ("Measured live: scripts/measure_tokens.py --mode live.", 20, DIM, False, 1180),
        ("Quality check passed: draft uses only retrieved memories;", 20, DIM, False, 1180),
        ("the dog does not speak human words.", 20, DIM, False, 1180)])

# ---------------------------------------------------------------- frame 10: end card
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.rounded_rectangle([28, 28, W - 28, H - 28], radius=14, fill=PANEL, outline=BORDER, width=2)
d.text((72, 130), "Twin Memory", font=font(SANS_B, 84), fill=WHITE)
d.text((72, 250), "Built for ContextCon, Track 07.", font=font(SANS, 30), fill=GREEN)
d.text((72, 330), "github.com/ValeriaWong/twin-memory", font=font(MONO_B, 34), fill=CYAN)
d.text((72, 410), "Submit by 2027-01-17 23:59 PT", font=font(MONO, 28), fill=WHITE)
d.text((72, 470), "The code is public; the dog's real videos are not in it.",
       font=font(SANS, 26), fill=DIM)
d.text((72, 540), "● LIVE — Meko datapack twin-memory", font=font(MONO_B, 24), fill=GREEN)
img.save(OUT / "f10_end.png")
print("wrote f10_end.png")
print("done")

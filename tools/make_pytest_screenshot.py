#!/usr/bin/env python3
from pathlib import Path
import sys
import textwrap
import matplotlib.pyplot as plt

if len(sys.argv) < 3:
    print("Usage: make_pytest_screenshot.py <input.txt> <output.png>")
    raise SystemExit(2)

inp = Path(sys.argv[1])
out = Path(sys.argv[2])
if not inp.exists():
    print("Input not found:", inp)
    raise SystemExit(2)

out.parent.mkdir(parents=True, exist_ok=True)
text = inp.read_text(encoding='utf-8', errors='replace')
# Limit total chars to avoid extremely large images
MAX_CHARS = 30000
if len(text) > MAX_CHARS:
    text = text[:MAX_CHARS] + "\n\n... (truncated) ..."

lines = []
for raw in text.splitlines():
    wrapped = textwrap.wrap(raw, width=120) or [""]
    lines.extend(wrapped)

n_lines = len(lines)
# Figure sizing: width fixed, height proportional to lines
fig_w = 11.0
line_h = 0.14
fig_h = max(2.5, n_lines * line_h)

fig = plt.figure(figsize=(fig_w, fig_h), dpi=150)
plt.axis('off')
textblock = "\n".join(lines)
plt.text(0, 1, textblock, va='top', family='monospace', fontsize=8)
plt.tight_layout()
fig.savefig(out, bbox_inches='tight')
plt.close(fig)
print("Wrote", out)

#!/usr/bin/env python3
"""
Compile successful object-removal cases (hike, penguin, selfie, soda) into a
self-contained HTML dashboard.  Each case gets its own section with the case
prompt displayed in an eye-catching banner, followed by a side-by-side model
comparison.  Images are embedded as JPEG base64 to keep the file compact.
"""

import base64
import io
from pathlib import Path
from PIL import Image

WORKSPACE = Path("/Users/yifeilin/Documents/Qoder/2026-07-20/chat-1")
CASES_DIR = WORKSPACE / "successful_cases"
INPUTS_DIR = WORKSPACE / "test_case_inputs"
OUTPUT_HTML = WORKSPACE / "successful_cases_dashboard.html"

CASES = ["hike", "penguin", "selfie", "soda"]
MODELS = ["qwen-image-3.0", "qwen-image-3.0-pro"]


def embed_image(path: Path, max_size: int = 1200, quality: int = 90) -> str:
    """Open an image, resize if large, convert to JPEG, return base64 data URI."""
    img = Image.open(path)
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    if max(img.width, img.height) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def collect_case_data():
    """Return list of dicts with case info for the dashboard."""
    results = []
    for case in CASES:
        prompt_file = CASES_DIR / "prompts" / f"{case}-prompt.txt"
        prompt = prompt_file.read_text(encoding="utf-8").strip().strip('"')

        input_img = INPUTS_DIR / case / f"{case}.jpg"
        mask_img = INPUTS_DIR / case / f"{case}_mask.png"

        model_outputs = {}
        for model in MODELS:
            model_dir = CASES_DIR / model
            imgs = sorted(model_dir.glob(f"{case}_output*.png"))
            model_outputs[model] = imgs

        results.append({
            "case": case,
            "prompt": prompt,
            "input": input_img,
            "mask": mask_img,
            "models": model_outputs,
        })
    return results


def render_html(cases):
    sections = []
    for idx, c in enumerate(cases, 1):
        # Build input/mask thumbnails
        input_thumb = embed_image(c["input"], max_size=512)
        mask_thumb = embed_image(c["mask"], max_size=512)

        # Build model columns
        base_imgs = c["models"]["qwen-image-3.0"]
        pro_imgs = c["models"]["qwen-image-3.0-pro"]

        base_col = "\n".join(
            f'<div class="thumb"><img src="{embed_image(p)}" alt="base {p.name}" loading="lazy"><span class="label">{p.name}</span></div>'
            for p in base_imgs
        )
        pro_col = "\n".join(
            f'<div class="thumb"><img src="{embed_image(p)}" alt="pro {p.name}" loading="lazy"><span class="label">{p.name}</span></div>'
            for p in pro_imgs
        )

        sections.append(f"""
    <section class="case-section" id="case-{idx:02d}">
      <div class="case-inputs">
        <figure>
          <img src="{input_thumb}" alt="{c['case']} input">
          <figcaption>Input</figcaption>
        </figure>
        <figure>
          <img src="{mask_thumb}" alt="{c['case']} mask">
          <figcaption>Mask</figcaption>
        </figure>
      </div>
      <div class="prompt-banner" aria-label="Prompt">
        <div class="prompt-banner-inner">
          <p class="prompt-label">Prompt</p>
          <p class="prompt-text">{c['prompt']}</p>
        </div>
      </div>
      <div class="comparison">
        <div class="model-col base-col">
          <h3>qwen-image-3.0</h3>
          <p class="count">{len(base_imgs)} sample(s)</p>
          <div class="thumbs">{base_col or '<p class="empty">No outputs for this model.</p>'}</div>
        </div>
        <div class="model-col pro-col">
          <h3>qwen-image-3.0-pro</h3>
          <p class="count">{len(pro_imgs)} sample(s)</p>
          <div class="thumbs">{pro_col or '<p class="empty">No outputs for this model.</p>'}</div>
        </div>
      </div>
    </section>
""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Successful Cases Dashboard · Qwen Image 3.0</title>
  <style>
    :root {{
      --bg: #0f1115;
      --surface: #171a21;
      --surface-2: #1e222c;
      --text: #e8eaed;
      --muted: #9aa0a6;
      --accent: #34d399;
      --accent-2: #60a5fa;
      --border: #2d3139;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    header {{
      text-align: center;
      padding: 3rem 1rem 2rem;
      background: linear-gradient(180deg, #111827 0%, var(--bg) 100%);
    }}
    h1 {{
      margin: 0;
      font-size: clamp(24px, 4vw, 40px);
      letter-spacing: -0.02em;
      color: #fff;
    }}
    .subtitle {{
      margin-top: 0.75rem;
      color: var(--muted);
      font-size: clamp(14px, 2vw, 18px);
      max-width: 900px;
      margin-left: auto;
      margin-right: auto;
    }}
    .case-section {{
      max-width: 1400px;
      margin: 2.5rem auto;
      padding: 0 1rem;
    }}
    .case-inputs {{
      display: flex;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 1.5rem;
    }}
    .case-inputs figure {{
      margin: 0;
      text-align: center;
    }}
    .case-inputs img {{
      max-width: 220px;
      border-radius: 8px;
      border: 1px solid var(--border);
    }}
    .case-inputs figcaption {{
      margin-top: 0.4rem;
      color: var(--muted);
      font-size: 13px;
    }}
    .prompt-banner {{
      background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
    }}
    .prompt-label {{
      margin: 0 0 0.5rem;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .prompt-label::before {{
      content: "";
      width: 8px;
      height: 8px;
      background: var(--accent);
      border-radius: 50%;
      display: inline-block;
    }}
    .prompt-text {{
      margin: 0;
      color: #fff;
      font-size: clamp(15px, 2vw, 20px);
      line-height: 1.5;
      font-weight: 500;
    }}
    .comparison {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
    }}
    @media (max-width: 900px) {{
      .comparison {{ grid-template-columns: 1fr; }}
    }}
    .model-col {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1rem;
    }}
    .model-col h3 {{
      margin: 0 0 0.25rem;
      font-size: 1.1rem;
    }}
    .base-col h3 {{ color: var(--accent); }}
    .pro-col h3 {{ color: var(--accent-2); }}
    .count {{
      margin: 0 0 1rem;
      color: var(--muted);
      font-size: 13px;
    }}
    .thumbs {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 0.75rem;
    }}
    .thumb {{
      position: relative;
      border-radius: 6px;
      overflow: hidden;
      border: 1px solid var(--border);
      background: var(--surface-2);
    }}
    .thumb img {{
      width: 100%;
      height: auto;
      display: block;
      cursor: zoom-in;
    }}
    .thumb .label {{
      display: block;
      padding: 0.35rem 0.5rem;
      font-size: 11px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .empty {{
      color: var(--muted);
      font-style: italic;
      margin: 0;
    }}
    .case-title {{
      text-align: center;
      font-size: clamp(20px, 3vw, 28px);
      color: #fff;
      margin-bottom: 0.5rem;
      letter-spacing: -0.01em;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Successful Cases Dashboard · Qwen Image 3.0</h1>
    <p class="subtitle">A case-by-case visual showcase of mask-guided object removal using Qwen Image 3.0. Every case uses the same prompt, with the white region of the mask indicating the object to remove.</p>
  </header>

  <main>
    {"".join(sections)}
  </main>
</body>
</html>
"""
    return html


def main():
    cases = collect_case_data()
    print(f"Collected {len(cases)} cases")
    for c in cases:
        base_n = len(c["models"]["qwen-image-3.0"])
        pro_n = len(c["models"]["qwen-image-3.0-pro"])
        print(f"  {c['case']}: {base_n} base, {pro_n} pro")
    html = render_html(cases)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    size_mb = OUTPUT_HTML.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUTPUT_HTML} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

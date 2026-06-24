# Phase 6 — Computer-use approach

## Decision (P6 spike)

**Primary path: Approach A** — custom Python desktop loop:

1. Capture full-desktop screenshot (`mss`)
2. Collect lightweight a11y context (visible window titles via `xdotool` on X11)
3. Vision-capable LLM returns structured JSON action
4. Execute via OS input (`xdotool` / `ydotool`)
5. Save per-step screenshot evidence; retry up to `policy.max_ui_retries`

**Approach B** (vendor computer-use API) was evaluated for the smoke scenario.
Approach A is preferred because it:

- Works for **any desktop window**, including third-party host apps (IDEs, design
  tools) where plugins run — no cooperation from the host app is required
- Produces evidence in FinalStrike's artifact layout
- Avoids vendor lock-in; local vision models work via `openai_compat` `base_url`

Playwright CDP remains a **future sub-path** for browser-only a11y when FinalStrike
launches Chromium itself — not the primary strategy for plugin-in-host-app testing.

## Browser requirement

Computer-use requires **Google Chrome or Chromium** installed on the GUI VM.

Configure in `finalstrike.yaml`:

```yaml
ui:
  base_url: http://localhost:8080
  browser: chromium   # or chrome
```

FinalStrike launches the configured binary (`google-chrome`, `chromium`, etc.).
The OS default browser (`xdg-open`) is **not** used — reproducibility and
`doctor` checks require an explicit Chrome/Chromium binary on `PATH`.

## Scope boundaries

| In P6 | Deferred |
|-------|----------|
| Standalone `finalstrike computer-use run` | `finalstrike run --layers ui` (P10) |
| Per-step screenshots | Full FFmpeg desktop video (P7) |
| Smoke UI (`acceptance-smoke.md` ac-2) | Full fixture UI (`acceptance-full.md`) via planner `full-v1` cassette |
| Action cassettes (`smoke-title-v1`, `full-tasks-title-v1`) | HTML report (P8) |

## Future: plugins inside host applications

Driver interfaces (`focus_window`, `launch`, coordinate/a11y clicks) are chosen
so P11+ can target arbitrary desktop windows — e.g. focus "Cursor" or "Code",
interact with embedded webviews/panels via desktop automation and vision fallback
when AT-SPI trees are sparse.

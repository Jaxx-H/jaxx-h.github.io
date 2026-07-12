# Agent rules — jaxx-h.github.io (PUBLIC repo)

These rules bind EVERY coding agent working here (Antigravity, Claude Code, Jules, any other).
They are laws, not suggestions. When a task conflicts with a law, stop and report — don't improvise.

## Absolute laws
1. **This repo is PUBLIC.** Never write a token, API key, password, private path, or personal
   data into any file here. There are no legitimate exceptions. The only deliberately public
   "key" is the IndexNow key file.
2. **Never commit an email address** — not in content JSON, not in code comments, not in test
   fixtures (use `user AT example DOT com` style if a test needs one that must NOT match the
   regex, or run the negative test without committing the fixture). `scan_content.py` and CI
   enforce this; your job is to never trigger them.
3. **Python stdlib ONLY.** No pip, no requirements.txt, no third-party imports, no Jekyll,
   no npm. If a task seems to need a dependency, the task is specified wrong — report back.
4. **No fabricated data.** Every data page needs a real `data_source.run_id` from an actual
   Apify run. If you don't have real data, you don't make a page. Never invent rows, numbers,
   or "example" statistics that could be mistaken for real ones.
5. **No network writes** except `ping_indexnow.py` (which CI runs). Agents here never post,
   submit, or publish to any external service.
6. **Numbers must be recomputable from rows.** Any number in `answer_first`/`facts`/`faq`
   must derive from the page's own `rows` or `data_source`. Never generalize beyond the data
   ("globally distributed niche" from one non-US row = the canonical failure).

## Contract
Every page in `content/pages/*.json` must satisfy `CONTENT-CONTRACT.md` exactly.
`build.py` fails closed on violations — a broken page never ships, and a build that fails
on your change means your change is wrong.

## Verify before you're done (all three, locally)
```
python3 scan_content.py && python3 build.py && python3 check_site.py
```
Done = all three exit 0. A green build alone is NOT done; `check_site.py` is the oracle.
Never modify `check_site.py` to make a failing check pass — fix the output instead.

## Style
- Match the existing code: plain stdlib Python, `string.Template` templating, no cleverness.
- Templates: CTA renders before FAQ on data pages — intentional, don't "fix" it.
- Reserved slugs (`static`, `assets`, `404`, `feed`, `sitemap`, `robots`, `llms`) are blocked.
- Commit messages: short imperative subject + what/why body.

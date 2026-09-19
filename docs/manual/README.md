# User manual source and publishing

[Read the user manual (PDF)](../Agentic_Data_Ops_User_Manual.pdf).

The 30-page manual documents Data Maturity Agent 0.1.2 for release tag
`v0.1.2`, prepared 19 September 2026.
The committed PDF is the reviewed release manual. Its content uses synthetic examples.

## Editable source

- `content.json`: chapter titles, prose, commands, tables and callouts, in reading order.
- `build_manual.py`: typography, cover, contents, bookmarks and PDF rendering.
- `requirements.txt`: pinned documentation-only build dependencies.

Content blocks use `p` (paragraph), `h` (subheading), `small`, `code`, `note`
(title and body), or `table` (headers, rows and optional column widths).
Paragraphs support ReportLab markup such as `<b>` and `<link>`; code blocks
preserve literal whitespace. Edit this trusted source and rebuild the PDF rather
than editing generated PDF bytes. Rendering does not require an LLM or credentials.

## Build

From the repository root, use Python 3.11 or newer in a separate documentation
environment. Install the DejaVu Sans fonts through your operating system's normal
font distribution, or provide a directory containing these files:

```text
DejaVuSans.ttf
DejaVuSans-Bold.ttf
DejaVuSans-Oblique.ttf
DejaVuSansMono.ttf
```

```bash
python -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r docs/manual/requirements.txt
python docs/manual/build_manual.py \
  --font-dir /usr/share/fonts/truetype/dejavu \
  --output docs/Agentic_Data_Ops_User_Manual.pdf
```

On Windows, call `.venv-docs\Scripts\python.exe` directly and pass your actual
font directory. The builder resolves content relative to itself; it has no
machine-specific paths. The supplied font directory must contain the four files
above. Different font revisions can change line wrapping, so visually review the
result. The builder uses deterministic PDF metadata; matching dependencies and fonts reproduce the reviewed output.

## Review before committing

1. Check examples against the current CLI and approved configuration schemas.
2. Update the documented application version, source commit and date in the last
   chapter and in the builder's cover/header metadata when releasing a new version.
3. Rebuild. The builder checks code-line width, page count and bookmark destinations.
   Each chapter must fit one page; it fails if content overflows this layout.
4. Render all pages with Poppler and inspect page breaks, tables and commands:

   ```bash
   mkdir -p /tmp/manual-preview
   pdftoppm -r 100 -png docs/Agentic_Data_Ops_User_Manual.pdf \
     /tmp/manual-preview/page
   ```

5. Verify the contents links, copyable commands and README PDF link. Commit the
   editable source and regenerated PDF together. Keep temporary renderings out of Git.

## Versioned release assets

For each
release, build and review the manual against that release's code, then attach the
matching PDF to the GitHub release as `Agentic_Data_Ops_User_Manual-vVERSION.pdf`.
Link it from the release notes, alongside the software version and known limits.
Keep the current manual at the stable repository path linked by the README.
Do not replace an older release's manual with documentation for newer behavior.

The manual and its source are covered by the repository's MIT license. Fonts are
external build inputs under their own license; the PDF embeds the fonts it uses.

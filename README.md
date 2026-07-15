# FluidNC Config Wizard (prototype)

A single self-contained web page that walks a FluidNC board's physical resources
(motor sockets, generic pins, RS485 channels, expansion connectors, etc.) and
generates a draft `config.yaml` for it.

**This is a prototype, published for testing and feedback** -- not an official
FluidNC tool, not guaranteed to produce a correct config for your hardware, and
not yet reviewed by the FluidNC maintainers as a project. Please double-check
anything it generates against your board's real documentation before flashing.

## Try it

**Via GitHub Pages** (recommended): once enabled for this repo (Settings ->
Pages -> Deploy from branch `main` / root), just open the published URL.

**Running it locally:** board/chip/hotspot data lives in real sidecar files
(`boards/*.board.yaml`, `chips/*.chip.yaml`, `hotspots/*.hotspots.yaml`)
that the page fetches at runtime -- browsers block `fetch()` of local files
when a page is opened directly via a `file://` URL, so double-clicking
`index.html` won't work. Serve this folder over HTTP instead, e.g. from a
terminal in this folder:

```
python3 -m http.server 8000
```

then open `http://localhost:8000/index.html`.

Nothing is saved anywhere -- it's a static page with no backend. Use the
Copy/Download buttons to keep a draft; reloading the page starts over.

## How it works

1. Pick your board from the dropdown.
2. For each physical resource the board exposes (a motor socket, a generic
   I/O pin, an RS485 channel, ...), choose which FluidNC role it should play,
   or leave it unused.
3. The draft `config.yaml` on the right updates live. Fields the wizard can't
   infer from the board itself are left as editable `TBD` placeholders --
   fill them in or accept the suggested/firmware default shown next to each.
4. Copy or download the finished file.

## Reporting problems / suggesting boards

Please use this repo's [Issues](../../issues) tab:

- **Wrong pin mapping / board fact** -- include the board name and, if
  possible, a link to its wiki page or schematic.
- **Missing board** -- name the board and a link to documentation for it;
  new boards are added as their own independent file (this project
  deliberately does not share pin facts between board revisions).
- **Wizard bug** -- describe what you selected and what the generated YAML
  looked like vs. what you expected.

## Status

Prototype / actively evolving. Board coverage is currently limited to a
handful of boards used during development; more will be added over time.

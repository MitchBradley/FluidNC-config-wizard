# FluidNC Config Wizard

A browser-based tool to help you create error-free FluidNC
`config.yaml` files.  Unlike other tools that require you to copy and
paste configuration snippets, this one is based on "board definition
files" that describe a controller board's physical resources (motor
sockets, inputs, outputs, RS485 channels, expansion connectors, etc.)
and how they are connected back to the MCU.  That lets the wizard
generate correct-by-construction config files.  You simply assign
those resources to a corresponding FluidNC function (axis, limit
switch, control switch, spindle, etc) and the wizard takes care of
details like which pins to use.  It also prevents common errors like
assigning the same pin twice to different functions.

The configuration choices that cannot be directly inferred from that board
itself are left as editable fields.  Once a resource is assigned to a
function, the things that cannot change due to board constraints are locked
down so you cannot inadvertently mess up.  But you can unassign and reassign
as needed, and the config will change accordingly.

This tool uses a different approach from the configuration helper in
FluidNC WebInstaller.  WebInstaller approaches the problem from the
FluidNC function direction - you navigate a hierarchy of functions
(axes, limits, etc) and choose which pin to assign.  This tool approaches
from the opposite direction - a board has some connectors that you can
use for things.  Since any given board typically has far fewer connectors
than FluidNC has possible functions, the idea is that approaching from
the "narrow end" will be easier.

This tool supports visual depictions of boards to make it easy to know
exactly which connector you are using - avoiding the common problem that
board connectors often have confusing or misleading labels.

## Usage

Open **[the wizard](https://mitchbradley.github.io/FluidNC-config-wizard/)**
(GitHub Pages) in your browser.

1. Pick your board from the "- Select a board -" at the upper right.
   A resource list will appear in the left pane.  If a graphical depiction
   of your board is available, a labeled photo of it will appear in the
   middle pane alongside the resource list -- click a connector in the
   photo to jump to its row, or vice versa.
2. For each physical resource the board exposes, choose which FluidNC role
   it should play (which axis, which spindle type, etc.), or leave it
   unused.
3. The draft `config.yaml` on the right updates live as you go. Fields the
   wizard can't infer from the board itself are left as editable `TBD`
   placeholders -- fill them in, or accept the suggested/firmware default
   shown next to each.
4. Copy or download the finished file.

You can also use the "Load config.yaml..." control to reload a
previously-generated (or hand-edited) `config.yaml` file back
into the wizard to continue editing it.  This lets you pick
up where you left off, rather than starting over.

### Running it locally instead

Instead of fetching the tool from the URL linked above, you can host it
locally by cloning this repo.  Go into the repo's top-level directory and
run an HTTP server therein, with, for example

```
python3 -m http.server 8000
```

then open `http://localhost:8000/index.html`.

If you run it locally, you will be able to create and test your own
board and hotspots files for boards that are not yet supported by
the upstream tool.

## Reporting problems

Please use this repo's [Issues](../../issues) tab:

- **Wrong pin mapping / board fact** -- include the board name and, if
  possible, a link to its wiki page or schematic.
- **Missing board** -- name the board and a link to documentation for it.
  See "Contributing a new board" below if you'd like to add it yourself.
- **Wizard bug** -- describe what you selected and what the generated YAML
  looked like vs. what you expected.

## Contributing a new board

To add a new board, you should first fork this repo and clone your fork into
a local directory.  That will both allow you to test your new board files
locally, and also make it easy to feed them back to the project via a PR
(pull request).

A complete board definition consists of three files: a `board.yaml` (required
-- physical pin/connector facts) and, optionally, a board photo and
associated `hotspots.yaml` file. The hotspots file indicates the locations
of the board's connectors, with reference to the image and the board.yaml
file.  The `board.yaml` is the minimum first step. It can be used without
an image+hotspots, but the wizard will not show a photo pane.

### 1. `boards/<id>.board.yaml`

This records what the board physically exposes -- which MCU pins go to
which labeled connectors -- never a FluidNC role assignment (that's the
wizard's/config author's job, done later). Full field reference, naming
conventions, and worked examples: **[BOARD_FILE_GUIDE.md](BOARD_FILE_GUIDE.md)**.
Validate against **[schema/board.schema.json](schema/board.schema.json)**.

This is the step where an AI assistant is most useful: point it at the board's
FluidNC wiki page (if one exists), any vendor documentation/schematic you
have, BOARD_FILE_GUIDE.md, and an existing board.yaml (e.g. Corgi's) as a
style reference, and ask it to produce a draft, validated against the
schema, with sources cited in each section's `notes:`. Review the result
against the real hardware/documentation before submitting it -- an
assistant's draft is a strong starting point, not a substitute for
verification.

### 2. `hotspots/<id>.hotspots.yaml` + `images/<id>.<ext>` (optional)

This is normally a hands-on-the-photo task, not something to hand off wholesale
to an AI assistant -- use the standalone **hotspot editor**
(`hotspot-editor.html`, run the same way as the wizard itself, see "Running
it locally" above) to draw a box over each connector in a photo of the
board and label it. Full walkthrough, including image-prep advice (scale
your photo to about 1000px wide in an image editor first, for the best
results): **[HOTSPOTS_FILE_GUIDE.md](HOTSPOTS_FILE_GUIDE.md)**. Validate
against **[schema/hotspots.schema.json](schema/hotspots.schema.json)**.

### 3. Validate and test locally

```
pip install pyyaml jsonschema
python3 -c "
import json, yaml, jsonschema
schema = json.load(open('schema/board.schema.json'))
doc = yaml.safe_load(open('boards/your_board.board.yaml'))
jsonschema.validate(doc, schema)
print('board.yaml ok')
"
```

(same pattern for `hotspots.schema.json` against your hotspots.yaml, if you
made one). Then serve the repo locally (see "Running it locally" above) and
load your new board -- open
`http://localhost:8000/index.html?board=your_board` directly (substituting
your board's `id`). You don't need to add it to the dropdown to test it:
that URL loads `boards/your_board.board.yaml` straight off disk regardless
of whether it's in the manifest yet (see step 4). Confirm every resource
you expect shows up with a sensible name, and (if you added one) that the
photo pane and its click-to-highlight linking both work.

### 4. Regenerate the board manifest

The dropdown itself is populated from `boards/index.json`, a generated
manifest (the wizard is static and can't list the `boards/` folder on its
own). Regenerate it so your new board shows up for other people, not just
via the direct URL:

```
python3 tools/gen_board_index.py
```

Commit the updated `boards/index.json` along with your board file(s).

### 5. Open a pull request

Include, in the PR description:

- A link to the board's documentation (wiki page, vendor page, schematic)
  used as source material.
- Whether the board facts are confirmed against real hardware/schematic, or
  transcribed from documentation only (this maps to the `board.status`
  field -- see BOARD_FILE_GUIDE.md).
- Anything you're unsure about, so a reviewer knows where to focus.

A new board is always added as its own complete, independent file --
this project deliberately does not share pin facts between board
"family" members/revisions, even closely related ones.

## Status

Actively evolving; board coverage grows as boards are contributed. See
`Issues` for known gaps and requests.

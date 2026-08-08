# OPOlogy COMPLETE Subject Notebook

Build: **2026-08-07 V9**  
New address: **http://127.0.0.1:9012**

V8 uses port `9012`, so an older V7 or legacy notebook cannot replace this page.

## V8 changes

- The move confirmation dialog, buttons, Undo notification, and status messages
  are English-only.
- Refreshing or reopening preserves the active Subject, active outline item, and
  exact right-side scroll position.
- Each Subject remembers its own independent scroll position.
- Direct outline dragging still provides a floating shadow card, animated gap,
  nested destinations, confirmation, autosave, and Undo.

## Build identification

The lower-left corner must display:

```text
COMPLETE SUBJECT BUILD · 2026-08-07 · V9
```

## Windows

1. Extract the ZIP completely.
2. Open the extracted folder.
3. Double-click `Start_OPOlogy_COMPLETE_Windows.bat`.
4. Confirm the address is `http://127.0.0.1:9012`.

## Mac

1. Extract the ZIP completely.
 open Terminal in this folder and run:

```bash
python3 opology_server.py --port 9012 --open
```

## Keep an existing notebook

Copy the complete `data` folder from the old package into this V8 folder before
starting it. Do not copy the old HTML or server file.

The main notebook data file is:

```text
data/opology_notebook.json
```

Keep the terminal open while editing. Press `Control + C` to stop the server.

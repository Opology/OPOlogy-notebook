# OPOlogy COMPLETE Subject Notebook

Build: **2026-08-07 V9**  
Local address: **http://127.0.0.1:9012**

V9 keeps the original local port `9012`. Check the V9 build marker in the lower-left corner after opening.

## V9 changes

- Long unbroken words, URLs, numbers, and pasted character sequences now wrap
  safely inside Bento cards, columns, tables, academic blocks, and headings.
- Code blocks and long display formulas keep their intended formatting and use
  contained horizontal scrolling instead of stretching the page.
- Editors, mobile layouts, editable HTML exports, and print/PDF output use the
  same overflow protection.
- Toolbar insertions, academic blocks, layout templates, image tags, and Tab
  indentation now join the native editor history, so Command/Ctrl + Z can undo
  them like ordinary typing.
- All V8 movement, refresh-position, autosave, backup, and privacy behavior is
  preserved.

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
2. Open the extracted folder.
3. Right-click `Start_OPOlogy_COMPLETE_Mac.command` and choose **Open**.
4. Confirm the address is `http://127.0.0.1:9012`.

If macOS blocks the launcher, open Terminal in this folder and run:

```bash
python3 opology_server.py --port 9012 --open
```

## Keep an existing notebook

Copy the complete `data` folder from the old package into this V9 folder before
starting it. Do not copy the old HTML or server file.

The main notebook data file is:

```text
data/opology_notebook.json
```

Keep the terminal open while editing. Press `Control + C` to stop the server.

## Public GitHub safety

`index.html` is the blank GitHub Pages entry file. The included `.gitignore`
prevents notebook JSON and temporary Python files from being committed by Git.
Never upload files from `data` or an editable HTML export containing private
notes.

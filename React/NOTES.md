# React Project Notes

## package.json

### `"main": "index.js"`
- Leftover default from `npm init` — has no effect in a Vite app.
- `"main"` is a Node.js/library concept: tells other packages which file to load when they `require()` your package.
- This project is an app, not a library — nobody imports it.
- Vite finds the entry point from `<script src="/main.jsx">` in `index.html`, not from `"main"`.

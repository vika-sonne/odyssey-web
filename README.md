# odyssey-web
Odyssey Web graphics engine

:snake: Full-stack python web graphics editor. Client-side has build-in [Brython](https://brython.info) programming language. Inspired by the [draw.io](https://app.diagrams.net).

:warning: In development. API is not stabilized yet.

Welcome to web featured graphics editor to add/edit graphic primitives. Just start server side and open url on client side with web browser.

## Client side

Workflow of editor page: select tool, make changes.

### Tools

#### `Line Tool`
- Key shortcut: `l`.
- Add line points: click sheet on free space, press key `Enter` to finish (`Shift+Enter` for closed line).
- Edit line point: move mouse over line point, hold down mouse button and drag, press key `Esc` to cancel.
- Delete line point: move mouse over line point, press key `Delete`.
- Delete line: move mouse over line point, press keys `Shift+Delete`.

## Server side

### Install requirements before server use:
```sh
pip install -r requirements.txt
```

### Run server:
```sh
./server_run.sh
```

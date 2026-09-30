# Workspace Launcher

A Windows desktop app for grouping applications, files, folders, and websites into
workspaces. Built with Python and PySide6 as a beginner learning project.

## About the project

Workspace Launcher keeps the tools for a task together. Instead of opening an editor,
terminal, project folder, and reference pages one at a time, save them as a workspace
and launch them together. Session history helps you see how much active time you
spent in that workspace.

For example:

| Workspace | Items you could include |
| --- | --- |
| Coding | VS Code, a terminal, your project folder, and documentation |
| Study | Notes, course materials, and a learning website |
| Writing | Your editor, a drafts folder, and reference files |
| Work | Task-related applications, documents, and browser pages |

This is an end-of-phase beginner Python project. It combines desktop UI work,
JSON persistence, process launching, session timing, and Windows integration. The
repository is a rewrite of an earlier completed version, developed in sections to
practice maintainable structure and build a meaningful development history.

## Current status

Version **1.0.0** is in release preparation. A Windows executable has been built
locally; this README does not imply that a public download has already been published.
Packaged-app verification and the distribution-notice review remain release tasks.

## Features

- Create, edit, order, and delete workspaces.
- Launch workspace items together and track active time.
- Pause manually or automatically when Windows locks or sleeps.
- Save completed sessions and view their history.
- Control sessions from the system tray.
- Choose whether ending a workspace closes its tracked applications.
- Optional Windows startup, daily verses, motivational quotes, and update checks.
- First-run setup, animated splash, and single-instance protection.

## Downloads

Published builds belong on the [GitHub Releases page](https://github.com/JFarnsworth2025/workspace-launcher/releases).
When a release is available, download **Workspace Launcher.exe** from its assets.
GitHub's **Source code** archives contain the project files, not a ready-to-run app.

The planned website Download button will link to the same executable. A separate
website-specific build is not required.

The current build is a standalone Windows executable:

- Python does not need to be installed to run the packaged app.
- There is no installer or uninstall wizard in v1.
- Keep the executable in a stable folder, especially if enabling Windows startup.
- Settings and history live in AppData, not next to the executable.
- Use the checksum supplied with a release to verify the downloaded file if desired.

The current local build targets Windows x64. Development and manual source-app
checks were performed on Windows 11; other Windows environments are not yet a
verified compatibility matrix.

## Run from source

Requires Windows and Python. This version was developed with Python 3.14.
Clone or download this repository first. To clone with Git:

```powershell
git clone https://github.com/JFarnsworth2025/workspace-launcher.git
cd workspace-launcher
```

From the project directory, using [uv](https://docs.astral.sh/uv/):

```powershell
uv venv --python 3.14
uv pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

In your editor, select `.venv\Scripts\python.exe` as the Python interpreter.

## Using the app

1. Choose your greeting name and daily-content preferences on first launch.
2. Open **Workspaces > Manage Workspaces** and add a workspace and its items.
3. Select a dashboard card and click **Start**. Use **Pause**, **Resume**, or **End**
   to control the session timer.
4. Open **Workspaces > Workspace History** to see completed sessions.

**File > Settings** controls startup, tray behavior, daily content, update checks,
and application closing. With application closing enabled, **End force-stops tracked
applications without confirmation**; unsaved work can be lost. Files, folders, and
websites remain open. With the option disabled, End leaves applications open.

Closing the window can leave the app in the tray. Use **File > Exit** or the tray's
Exit action to quit. End an active session before exiting. If saving history fails,
keep the app open and use End again after resolving the error.

### Creating and editing a workspace

Open **Workspaces > Manage Workspaces**. Give a workspace a name and a display order,
then add the items it should launch. Lower display-order values appear first.
Workspace names must be valid Windows filenames; duplicate names are rejected.

| Item type | What to enter |
| --- | --- |
| Application | An executable path; Browse can help locate it |
| File or Shortcut | A file or Windows shortcut to open with its associated app |
| Folder | A directory to open in File Explorer |
| Website | A full URL beginning with `https://` or `http://` |

Application arguments are optional. Simple flags such as `--new-window --wait` are
supported. The executable path itself can contain spaces; the quoted-argument
limitation applies to the separate Arguments field.

Saving, editing, or deleting a workspace through the manager updates the dashboard.
Changing a workspace definition does not relaunch its items or change the identity
of an already-running session.

### How sessions behave

Only one workspace session can be active at a time. A session starts when at least
one item opens successfully; failed items are reported without hiding successful
launches. If every item fails, no session starts.

Pause excludes that time from the session's active duration. Windows lock and sleep
also pause tracking. Automatic resume waits for both conditions to clear, and a
session that you paused manually stays paused.

End records the completed session. Closing applications is controlled by Settings;
it is separate from whether the session is saved. Application shutdown errors and
history-write failures are shown so you can retry without silently losing the record.

### Settings reference

| Setting | Behavior |
| --- | --- |
| Greeting name | Personalizes the time-of-day greeting |
| Launch when Windows starts | Registers the current app location for your Windows user |
| Keep running in the tray | Closing the window hides it while the app remains running |
| Close launched applications | End force-stops tracked processes; disabled by default |
| Automatic update checks | Checks GitHub after startup; errors and no-update results stay quiet |
| Daily quote | Shows a quote with its author; reuses a same-day local cache |
| Daily Bible verse | Shows a date-selected passage; blank passages try another reference |

You can also check manually through **Help > Check for Updates**. If an update exists,
the app offers to open its release page. Move or replace the executable only after
exiting it; if its location changes, save the startup preference again from the new copy.

## Data and privacy

Settings, workspaces, history, quote cache, and diagnostic logs are stored under:

```text
%LOCALAPPDATA%\Pariven\Workspace Launcher
```

| Location inside AppData | Contents |
| --- | --- |
| `workspaces/` | One JSON file per workspace |
| `settings.json` | Your saved preferences |
| `workspace_history.json` | Completed session records |
| `quote_cache.json` | Cached daily quote |
| `logs/workspace_launcher.log` | Local diagnostic log, with rotated backups |

Exit the app before copying this folder for a backup. To transfer your setup to
another computer, back up its existing data first, then copy the needed files into
the same AppData location. Application and folder paths may need editing on the new
machine. Automatic synchronization and an in-app import/export flow are not in v1.

Back up this folder separately from the source repository. Personal test workspaces,
the virtual environment, and build output are ignored by Git.

Enabled daily-content features contact `bible.helloao.org` and `zenquotes.io`.
Update checks contact the GitHub releases API. Updates open a release page when
requested; the app does not automatically install them.

## Known limitations

- Windows only; lock, sleep, startup, and tray behavior depend on Windows.
- Pausing stops time tracking, not the launched applications.
- Only directly tracked application processes can be stopped. Applications that
  hand off to another process may not close through the launcher.
- Argument editing supports simple space-separated flags, not quoted arguments.
  Existing argument lists are preserved when the field is unchanged.
- Daily-content requests can briefly pause the interface on a slow connection.
- Update checking expects numeric dotted release tags, such as `v1.0.0`.
- Workspace data is local; Git does not synchronize your AppData between computers.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Already-running message | Look for the app in the system tray; use its Open action |
| An item does not launch | Check its saved path or URL and try opening it directly in Windows |
| An application stays open after End | Check the closing setting; the app may have handed off to an untracked process |
| Workspace file warning | Back up the affected file, correct the reported issue, and restart the launcher |
| History could not be saved | Keep the app open, resolve the file-access issue, and press End again |
| Verse or quote unavailable | Check connectivity; daily content is optional and can be disabled |
| Update check fails | Check connectivity and whether the repository has a published release |
| Launch-on-startup stops working | Confirm the executable still exists at its saved location |
| Python imports fail in the editor | Select this project's `.venv` interpreter and install `requirements.txt` |

For unexpected errors, check the local `logs` folder. When reporting a problem,
include the app version, Windows version, steps to reproduce, and the error message.
Review logs before sharing them: errors can include local paths or workspace names.

## Project structure

```text
main.py                    Application startup, styling, splash, and instance guard
config.py                  Version, repository identity, and data paths
ui/                        Windows, dialogs, cards, and background update worker
services/                  Launching, storage, sessions, settings, and integrations
assets/                    Application logo and icon
styles/                    Qt stylesheets
data/daily_verses.json      Local verse-reference rotation
tests/                     Automated storage and workspace-validation tests
workspace_launcher.spec    Windows executable build configuration
version_info.txt           Windows executable version metadata
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use isolated data. Manual Windows checks are also needed for native UI,
application launching, startup, tray controls, and lock/sleep behavior.

## Build a Windows executable

Build on Windows from the project directory:

```powershell
uv pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm workspace_launcher.spec
```

The executable is written to `dist\Workspace Launcher.exe`. Keep it in a stable
location before enabling Windows startup. Test the packaged app before publishing;
source-app testing does not validate the packaged build.

Before public binary distribution, resolve the Qt license/notice review recorded in
`THIRD_PARTY_NOTICES.txt`. The copied package notices alone have not been verified
as a complete release notice set.

For a GitHub release, use tag `v1.0.0` and attach the executable, license notices,
and a SHA-256 checksum. Do not commit build output or personal data.

## Future version plans

These are proposed directions, not features included in v1 or promised release dates.
Priorities can change based on real use, bug reports, and what is practical to build
and maintain as the project develops.

### v1.0.x ? Fixes and release polish

- Address issues found in packaged builds and different Windows setups.
- Improve error messages, documentation, and display-scaling behavior.
- Add regression coverage for bugs found during everyday use.

### v1.1 ? Reliability and convenience

- Workspace export/import for moving between computers.
- Backup and restore options for local workspace data.
- Missing-path detection and a simpler repair flow.
- Search/filtering in Workspace Manager and easier reordering.
- Better argument editing for paths and values containing spaces.
- Background daily-content loading and clearer offline feedback.

### v1.2 ? Personalization

- Optional light theme and more control over layout density.
- Custom workspace icons and dashboard-content choices.
- More greeting preferences and an optional start-minimized mode.

### Longer-term ideas

- Workspace templates and scheduled launches.
- Per-application startup delays and conditional launch rules.
- Window positioning where Windows and the target applications allow it.
- Installer/update-distribution improvements after the portable release is stable.

The priority is a dependable small launcher. These ideas should not delay fixes to
existing behavior or turn v1 into a much larger automation platform.

## Feedback and development

Use [GitHub Issues](https://github.com/JFarnsworth2025/workspace-launcher/issues) for
reproducible bugs and feature suggestions. Include the workflow you are trying to
improve so suggestions can be evaluated against the project's scope.

Changes should remain readable and focused. Run the automated tests, use temporary
data for development checks, and verify affected Windows behavior manually. Never
commit personal workspace files, generated build folders, or local credentials.

## License

Workspace Launcher is licensed under the [MIT License](LICENSE). Bundled third-party
components retain their own licenses; see `THIRD_PARTY_NOTICES.txt` and
`third-party-licenses/`.

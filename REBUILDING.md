# Rebuilding and replacing bundled libraries

Workspace Launcher is MIT-licensed source code. Qt/PySide/Shiboken are used under
LGPLv3; their license texts and third-party notices accompany the release.

The `v1.0.0` tag contains the application source, assets, build specification and
version metadata. The release also provides unmodified Qt Base, Qt SVG and
PySide/Shiboken 6.11.1 source archives. Those archives include upstream build
instructions, configuration files and component notices.

## Reproduce the application build

On Windows x64, clone the repository and check out the release tag. Install Python
3.14, create a virtual environment, then run:

```powershell
uv venv --python 3.14
uv pip install -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm workspace_launcher.spec
```

The release was built using Python 3.14.7 and PyInstaller 6.22.3. Dependency versions
are listed in `THIRD_PARTY_NOTICES.txt`. These instructions reproduce the packaging
process; they do not promise a byte-for-byte identical executable.

## Use modified libraries

You may modify the LGPL libraries and rebuild the application against them. Build
interface-compatible Qt/PySide/Shiboken libraries following their source archive
instructions, and install your resulting wheels into the build environment in place
of the matching standard packages. Then rebuild with the specification above.

Do not reinstall the pinned runtime requirements afterward: doing so would replace
your modified libraries. If your changes require additional Qt plugins, update the
explicit plugin list in `workspace_launcher.spec` and include their notices.

The single-file executable extracts its libraries to a temporary directory at run
time. For persistent library replacement, use the source build/rebuild route above
rather than editing that temporary directory. The application does not require a
signature, activation key or publisher permission to run a rebuilt copy. Its license
does not prohibit reverse engineering to debug modifications to LGPL components.

Full LGPLv3 and GPLv3 texts, and the upstream attribution files, are in
`third-party-licenses/Qt-6.11.1/`. Source archive checksums are recorded there too.

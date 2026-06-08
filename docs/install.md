# Install

## Requirements

- **Bitwig Studio 6**
- **Python 3.11+**
- **Windows**

## 1. Install the Python package

```bash
pip install openwig
```

## 2. Install the controller script

```bash
python -m openwig install
```

This copies the bundled `openwig_bridge.control.js` into Bitwig's controller
scripts directory (`%USERPROFILE%\Documents\Bitwig Studio\Controller Scripts\`).

!!! tip "If install says the directory doesn't exist"
    Launch Bitwig Studio once (so it creates its user directory), then re-run.

## 3. Enable the controller in Bitwig

1. Open Bitwig Studio.
2. **Settings -> Controllers -> openwig -> Add -> OpenwigBridge**.
3. One-time. Bitwig remembers it across launches.

## 4. Verify

```bash
python -m openwig doctor
```

Expected output:

```
openwig 0.1.3 (supports Bitwig: 6.x)
controller dir : C:\Users\<you>\Documents\Bitwig Studio\Controller Scripts
controller     : OK
bridge :7777   : OK (Bitwig 6.0.6) compatible
internals      : self-test on a throwaway track ...
  classes      : 6/6 internal classes load
  automation   : OK
  clip create  : OK
  descriptor   : OK
  => all reflection paths verified on this Bitwig build
```

`doctor` runs a self-test on a temporary track (created and deleted automatically,
existing tracks untouched) that confirms openwig's reflection paths work on your exact
Bitwig build. If any line says `FAIL`, that build is unsupported: please
[open an issue](https://github.com/Axyom/openwig/issues) with the output.

Then write your [first song](quickstart.md).

## Uninstall

```bash
python -m openwig uninstall   # removes the controller .js (you keep the pip package)
pip uninstall openwig
```

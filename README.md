![](templates/static/logo-2.svg)

# bitshift
Website for http://www.bitshift.rf.gd (via ftp) and https://www.bitshift.io (via firebase)

## Setup

Install dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

Then run the build script:

```bash
python3 tools/build.py
```

This will generate the `public/` folder with the static site. The script works from any directory in the project.

All build tools are in the __tools__ directory

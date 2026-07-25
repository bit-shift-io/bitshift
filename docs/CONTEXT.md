# Glossary

## Clean URLs
URLs served without a file extension, e.g. `/contact` instead of `/contact.html`. Firebase Hosting's `cleanUrls: true` config (`firebase.json`) does this on the live site by mapping `/contact` → `contact.html` automatically. All internal nav links in `templates/` are written this way (extensionless), so local tooling needs to replicate the same resolution or links break locally.

## Dev server
The local development tool (`tools/dev.py`) that builds the site, watches `templates/` for changes and rebuilds automatically, serves `public/` with clean-URL resolution matching production, and live-reloads any open browser tab after a rebuild. Distinct from `tools/build.py` (one-shot production build) and `tools/localhost.sh` (plain static file server, no watching or clean URLs), both of which remain unchanged and available for their original purposes.

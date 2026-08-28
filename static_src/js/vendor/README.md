# Vendored JS

Self-hosted per CLAUDE.md §2 (no `cdn.tailwindcss.com`, and by the same logic
no relying on third-party CDNs for the rest of the front-end stack either —
Caddy serves our own static assets).

| File                     | Source                          | Version |
|--------------------------|----------------------------------|---------|
| `alpine-3.16.3.min.js`   | `alpinejs` npm package (`dist/cdn.min.js`) | 3.16.3 |
| `htmx-2.0.10.min.js`     | `htmx.org` npm package (`dist/htmx.min.js`) | 2.0.10 |

Both packages are `devDependencies` in `package.json` purely so `npm install`
pins a known version to copy from — they are not bundled by the Tailwind
build. To update:

```bash
npm install --save-dev alpinejs@<version> htmx.org@<version>
cp node_modules/alpinejs/dist/cdn.min.js static_src/js/vendor/alpine-<version>.min.js
cp node_modules/htmx.org/dist/htmx.min.js static_src/js/vendor/htmx-<version>.min.js
# then update the <script> tags in templates/base.html to the new filenames
# and delete the old versioned files.
```

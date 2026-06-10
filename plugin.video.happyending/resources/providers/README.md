# Provider modules

Add site modules under `resources/lib/sources/` and register them in
`resources/lib/provider_loader.py`.

Each provider module should return `VideoEntry` objects with:

- `title`
- `url`
- `thumb` or `poster`
- `duration`, such as `05:30`, `1:22:00`, `22 min`, or raw seconds
- `plot`

Only add sources you are allowed to access. Do not add bypasses for login, DRM,
blocked providers, private content, or anything illegal.

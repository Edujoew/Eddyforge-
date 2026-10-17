# Launch commands

1. Create the Neon project in a region close to Vercel. Keep the direct and pooled URLs in a password manager; do not save them in this OneDrive workspace.
2. From the project root in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
.\scripts\launch_setup.ps1
```

3. Paste the copied variable block into Vercel → Settings → Environment Variables → Production.
4. Deploy the project from Vercel.
5. Run the read-only HTTP checks against the deployed domain:

```powershell
.\scripts\smoke_live.ps1 -BaseUrl "https://example.com"
```

6. Review the unpublished draft post, content gaps, project/service content, and `/privacy/`; confirm client accounts and project assignments.

## If something breaks

- Connection error: use the direct Neon URL for setup/migrations and the `-pooler` URL for Vercel; require `sslmode=require`.
- `DisallowedHost`: add the exact hostname to Vercel's `DJANGO_ALLOWED_HOSTS`, then redeploy.
- Form CSRF 403: add each HTTPS site origin to `DJANGO_CSRF_TRUSTED_ORIGINS`, then redeploy.
- Missing static files: rebuild with `python manage.py collectstatic --noinput`, then redeploy.

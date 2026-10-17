[CmdletBinding()]
param(
    [switch]$Local
)

$ErrorActionPreference = "Stop"
$projectRoot = (Get-Location).Path
$settingsPath = Join-Path $projectRoot "eddyforge_project\settings.py"
$managePath = Join-Path $projectRoot "manage.py"
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$tempDatabasePath = $null
$clipboardWasSet = $false
$savedEnvironment = @{}
$environmentNames = @(
    "DATABASE_URL",
    "DIRECT_DATABASE_URL",
    "DJANGO_SECRET_KEY",
    "DJANGO_DEBUG",
    "DJANGO_ALLOWED_HOSTS",
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "SITE_URL",
    "CONTACT_EMAIL",
    "BOOKING_URL",
    "DJANGO_SUPERUSER_USERNAME",
    "DJANGO_SUPERUSER_EMAIL",
    "DJANGO_SUPERUSER_PASSWORD"
)

function Read-PlainSecret {
    param([string]$Prompt)
    $secureValue = Read-Host -Prompt $Prompt -AsSecureString
    $pointer = [IntPtr]::Zero
    try {
        $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    }
    finally {
        if ($pointer -ne [IntPtr]::Zero) {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
        }
        if ($null -ne $secureValue) {
            $secureValue.Dispose()
        }
    }
}

function Read-RequiredValue {
    param([string]$Prompt)
    while ($true) {
        $value = (Read-Host -Prompt $Prompt).Trim()
        if ($value) { return $value }
        Write-Warning "A value is required."
    }
}

function Read-SecretValue {
    param([string]$Prompt)
    while ($true) {
        $value = Read-PlainSecret -Prompt $Prompt
        if ($value) { return $value }
        Write-Warning "A value is required."
    }
}

function Normalize-NeonUrl {
    param(
        [string]$Value,
        [bool]$ExpectPooled,
        [string]$Label
    )
    while ($true) {
        if ($Value -notmatch '^postgres(?:ql)?://') {
            Write-Warning "$Label must start with postgres:// or postgresql://."
        }
        else {
            try {
                $uri = [Uri]$Value
                if (($ExpectPooled -and $uri.Host -notmatch '-pooler') -or
                    (-not $ExpectPooled -and $uri.Host -match '-pooler')) {
                    if ($ExpectPooled) {
                        Write-Warning "Use the pooled Neon hostname (it contains -pooler)."
                    }
                    else {
                        Write-Warning "Use the direct Neon hostname (it must not contain -pooler)."
                    }
                }
                else {
                    if ($Value -notmatch '(^|[?&])sslmode=require(&|$)') {
                        if ($Value.Contains("?")) {
                            $Value = "$Value&sslmode=require"
                        }
                        else {
                            $Value = "$Value?sslmode=require"
                        }
                    }
                    return $Value
                }
            }
            catch {
                Write-Warning "That does not look like a valid PostgreSQL connection URL."
            }
        }
        $Value = Read-SecretValue -Prompt "$Label connection URL"
    }
}

function Invoke-Manage {
    param([string[]]$Arguments)
    & python $managePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "A Django management command failed: python manage.py $($Arguments -join ' ')"
    }
}

function Read-Domains {
    while ($true) {
        $rawDomains = Read-RequiredValue -Prompt "Production domain(s), comma-separated (for example example.com,www.example.com)"
        $domains = @($rawDomains.Split(",") | ForEach-Object { $_.Trim().ToLowerInvariant() } | Where-Object { $_ })
        if ($domains.Count -gt 0 -and @($domains | Where-Object { $_ -notmatch '^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$' }).Count -eq 0) {
            return $domains
        }
        Write-Warning "Enter hostname(s) only, without https:// or a path."
    }
}

function Read-VercelHost {
    while ($true) {
        $hostName = (Read-RequiredValue -Prompt "Vercel deployment hostname (for example eddyforge.vercel.app)").ToLowerInvariant()
        if ($hostName -match '^[a-z0-9][a-z0-9.-]*\.vercel\.app$') { return $hostName }
        Write-Warning "Enter the full *.vercel.app hostname, without scheme or path."
    }
}

try {
    foreach ($name in $environmentNames) {
        $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
    }
    if (-not (Test-Path -LiteralPath $managePath) -or -not (Test-Path -LiteralPath $settingsPath)) {
        throw "Run this script from the Django project root."
    }
    if (-not $pythonCommand) {
        throw "Python was not found. Activate the project's virtual environment and retry."
    }
    & python -c "import django, dj_database_url"
    if ($LASTEXITCODE -ne 0) {
        throw "Django or dj-database-url is unavailable. Activate the project's virtual environment and install requirements.txt."
    }

    $settingsText = [IO.File]::ReadAllText($settingsPath)
    $requiredSettingNames = @("DATABASE_URL", "DJANGO_SECRET_KEY", "DJANGO_DEBUG", "DJANGO_ALLOWED_HOSTS", "DJANGO_CSRF_TRUSTED_ORIGINS", "SITE_URL", "CONTACT_EMAIL", "BOOKING_URL")
    foreach ($name in $requiredSettingNames) {
        if ($settingsText -notmatch [Regex]::Escape($name)) {
            throw "Expected setting $name was not found in eddyforge_project/settings.py."
        }
    }

    if ($Local) {
        $tempDatabasePath = Join-Path ([IO.Path]::GetTempPath()) ("eddyforge-launch-" + [Guid]::NewGuid().ToString("N") + ".sqlite3")
        $env:DATABASE_URL = "sqlite:///$($tempDatabasePath.Replace('\', '/'))"
        $directUrl = ""
        $pooledUrl = ""
        $domains = @("localhost")
        $vercelHost = "eddyforge-test.vercel.app"
        $contactEmail = "launch-test@example.invalid"
        $bookingUrl = ""
    }
    else {
        $directUrl = Normalize-NeonUrl -Value (Read-SecretValue -Prompt "Direct Neon URL (pooler OFF)") -ExpectPooled $false -Label "Direct"
        $pooledUrl = Normalize-NeonUrl -Value (Read-SecretValue -Prompt "Pooled Neon URL (pooler ON)") -ExpectPooled $true -Label "Pooled"
        $domains = Read-Domains
        $vercelHost = Read-VercelHost
        while ($true) {
            $contactEmail = Read-RequiredValue -Prompt "Public contact email"
            if ($contactEmail -match '^[^@\s]+@[^@\s]+\.[^@\s]+$') { break }
            Write-Warning "Enter a valid email address."
        }
        while ($true) {
            $bookingUrl = (Read-Host -Prompt "Optional booking URL (press Enter to omit)").Trim()
            if (-not $bookingUrl) { break }
            try {
                $bookingUri = [Uri]$bookingUrl
                if ($bookingUri.IsAbsoluteUri -and $bookingUri.Scheme -eq "https") { break }
            }
            catch [System.UriFormatException] {
            }
            Write-Warning "Enter a valid absolute https:// booking URL, or leave it blank."
        }
        $env:DIRECT_DATABASE_URL = $directUrl
        $env:DATABASE_URL = $directUrl
    }

    if (-not $Local) {
        $superuserName = Read-RequiredValue -Prompt "Superuser username"
        while ($true) {
            $superuserEmail = Read-RequiredValue -Prompt "Superuser email"
            if ($superuserEmail -match '^[^@\s]+@[^@\s]+\.[^@\s]+$') { break }
            Write-Warning "Enter a valid email address."
        }
        $superuserPassword = Read-SecretValue -Prompt "Superuser password"
        $passwordAgain = Read-SecretValue -Prompt "Confirm superuser password"
        if ($superuserPassword -cne $passwordAgain) {
            throw "The superuser passwords did not match."
        }
    }
    else {
        $superuserName = "launch-test-admin"
        $superuserEmail = "launch-admin@example.invalid"
        $superuserPassword = (& python -c "import secrets; print('Local-' + secrets.token_urlsafe(24) + '-9A')").Trim()
        if ($LASTEXITCODE -ne 0) { throw "Could not generate temporary local test credentials." }
    }

    $env:DJANGO_DEBUG = "False"
    $env:DJANGO_SECRET_KEY = (& python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())").Trim()
    if ($LASTEXITCODE -ne 0 -or $env:DJANGO_SECRET_KEY.Length -lt 50) {
        throw "Could not generate a fresh Django secret key."
    }

    Invoke-Manage -Arguments @("migrate", "--noinput")
    Invoke-Manage -Arguments @("import_content")

    $env:DJANGO_SUPERUSER_USERNAME = $superuserName
    $env:DJANGO_SUPERUSER_EMAIL = $superuserEmail
    $env:DJANGO_SUPERUSER_PASSWORD = $superuserPassword
    $existingSuperuser = (& python $managePath shell -c "from django.contrib.auth import get_user_model; import os; print('yes' if get_user_model().objects.filter(username=os.environ['DJANGO_SUPERUSER_USERNAME']).exists() else 'no')").Trim()
    if ($LASTEXITCODE -ne 0) { throw "Could not check for an existing superuser." }
    if ($existingSuperuser -eq "no") {
        Invoke-Manage -Arguments @("createsuperuser", "--noinput")
    }
    else {
        Write-Host "Superuser username already exists; leaving that account unchanged."
    }

    & python $managePath shell -c "from core.models import Project, Service, Post; print('Content rows: Project={0}, Service={1}, Post={2}'.format(Project.objects.count(), Service.objects.count(), Post.objects.count()))"
    if ($LASTEXITCODE -ne 0) { throw "Could not report imported content counts." }

    while ($true) {
        $answer = (Read-Host -Prompt "Create a client account now? (y/n)").Trim().ToLowerInvariant()
        if ($answer -in @("n", "no")) { break }
        if ($answer -notin @("y", "yes")) {
            Write-Warning "Enter y or n."
            continue
        }
        $clientUsername = Read-RequiredValue -Prompt "Client username"
        while ($true) {
            $clientEmail = Read-RequiredValue -Prompt "Client email"
            if ($clientEmail -match '^[^@\s]+@[^@\s]+\.[^@\s]+$') { break }
            Write-Warning "Enter a valid email address."
        }
        $clientProject = Read-RequiredValue -Prompt "Client project title"
        Invoke-Manage -Arguments @("create_client", "--username", $clientUsername, "--email", $clientEmail, "--project-title", $clientProject)
    }

    Invoke-Manage -Arguments @("content_gaps")

    if (-not $Local) {
        $allowedHosts = @($domains + @($vercelHost) | Select-Object -Unique) -join ","
        $csrfOrigins = @($domains + @($vercelHost) | Select-Object -Unique | ForEach-Object { "https://$_" }) -join ","
        $siteUrl = "https://$($domains[0])"
        $vercelVariables = @(
            "DATABASE_URL=$pooledUrl",
            "DJANGO_SECRET_KEY=$env:DJANGO_SECRET_KEY",
            "DJANGO_DEBUG=False",
            "DJANGO_ALLOWED_HOSTS=$allowedHosts",
            "DJANGO_CSRF_TRUSTED_ORIGINS=$csrfOrigins",
            "SITE_URL=$siteUrl",
            "CONTACT_EMAIL=$contactEmail"
        )
        if ($bookingUrl) { $vercelVariables += "BOOKING_URL=$bookingUrl" }
        $clipboardText = $vercelVariables -join [Environment]::NewLine
        Set-Clipboard -Value $clipboardText
        $clipboardWasSet = $true
        Write-Host ""
        Write-Host "Copied Vercel environment variable block. Variable names:"
        foreach ($line in $vercelVariables) {
            Write-Host ($line.Substring(0, $line.IndexOf("=")))
        }
        Write-Host "Paste the clipboard into Vercel > Settings > Environment Variables (Production), then press Enter."
        [void](Read-Host)
        Set-Clipboard -Value ""
        $clipboardWasSet = $false
    }
    else {
        Write-Host "Local launch setup completed using a temporary SQLite database; no clipboard step was run."
    }
}
catch {
    Write-Error $_
    exit 1
}
finally {
    foreach ($name in $environmentNames) {
        [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], "Process")
    }
    if ($tempDatabasePath -and (Test-Path -LiteralPath $tempDatabasePath)) {
        Remove-Item -LiteralPath $tempDatabasePath -Force
    }
    if ($clipboardWasSet -and (Get-Command Set-Clipboard -ErrorAction SilentlyContinue)) {
        Set-Clipboard -Value ""
    }
}

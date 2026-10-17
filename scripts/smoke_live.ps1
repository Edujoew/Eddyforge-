[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$BaseUrl
)

$ErrorActionPreference = "Stop"

try {
    $baseUri = [Uri]$BaseUrl
    if (-not $baseUri.IsAbsoluteUri -or $baseUri.Scheme -notin @("http", "https")) {
        throw "BaseUrl must be an absolute http:// or https:// URL."
    }
}
catch {
    throw "Invalid BaseUrl. Supply an absolute http:// or https:// URL."
}

Add-Type -AssemblyName System.Net.Http
$handler = New-Object System.Net.Http.HttpClientHandler
$handler.AllowAutoRedirect = $false
$client = New-Object System.Net.Http.HttpClient($handler)
$client.Timeout = [TimeSpan]::FromSeconds(20)
$results = New-Object System.Collections.Generic.List[object]
$checked = @{}

function Invoke-Get {
    param([string]$Path)
    $uri = [Uri]::new($baseUri, $Path)
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            $response = $client.GetAsync($uri).GetAwaiter().GetResult()
            $body = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            $location = $null
            if ($null -ne $response.Headers.Location) {
                $location = [Uri]::new($uri, $response.Headers.Location).PathAndQuery
            }
            return [PSCustomObject]@{
                StatusCode = [int]$response.StatusCode
                Body = $body
                Location = $location
            }
        }
        catch {
            if ($attempt -eq 3) { throw }
            Start-Sleep -Milliseconds 250
        }
    }
}

function Add-Check {
    param(
        [string]$Label,
        [string]$Path,
        [int]$ExpectedStatus = 200,
        [string]$ExpectedLocationPrefix = ""
    )
    if ($checked.ContainsKey($Path)) { return }
    $checked[$Path] = $true
    try {
        $response = Invoke-Get -Path $Path
        $passed = $response.StatusCode -eq $ExpectedStatus
        $detail = "HTTP $($response.StatusCode)"
        if ($ExpectedLocationPrefix) {
            if ($ExpectedLocationPrefix -eq "LOGIN") {
                $passed = $passed -and $response.Location -match '^/(?:portal/login|admin/login)/'
            }
            else {
                $passed = $passed -and $response.Location -and $response.Location.StartsWith($ExpectedLocationPrefix, [StringComparison]::OrdinalIgnoreCase)
            }
            $detail += "; Location $($response.Location)"
        }
        $results.Add([PSCustomObject]@{
            Check = $Label
            Result = if ($passed) { "PASS" } else { "FAIL" }
            Detail = $detail
        })
        return $response
    }
    catch {
        $results.Add([PSCustomObject]@{
            Check = $Label
            Result = "FAIL"
            Detail = $_.Exception.Message
        })
        return $null
    }
}

try {
    $staticPaths = @(
        "/",
        "/about/",
        "/services/",
        "/projects/",
        "/blog/",
        "/blog/feed.xml",
        "/start/",
        "/start/thanks/",
        "/contact/",
        "/resume/",
        "/privacy/",
        "/uses/",
        "/now/",
        "/lab/",
        "/sitemap.xml",
        "/robots.txt"
    )
    foreach ($path in $staticPaths) {
        [void](Add-Check -Label $path -Path $path)
    }

    foreach ($listingPath in @("/services/", "/projects/", "/blog/", "/lab/")) {
        try {
            $listing = Invoke-Get -Path $listingPath
        }
        catch {
            continue
        }
        if ($listing.StatusCode -ne 200) { continue }
        $matches = [Regex]::Matches(
            $listing.Body,
            'href\s*=\s*["''](?<path>/(?:services|projects|blog|lab)/[^"''?#]+/)["'']',
            [Text.RegularExpressions.RegexOptions]::IgnoreCase
        )
        foreach ($match in $matches) {
            $detailPath = [Net.WebUtility]::HtmlDecode($match.Groups["path"].Value)
            if ($detailPath -ne $listingPath) {
                [void](Add-Check -Label $detailPath -Path $detailPath)
            }
        }
    }

    [void](Add-Check -Label "Custom not-found page" -Path "/launch-smoke-not-found-9f12/" -ExpectedStatus 404)
    [void](Add-Check -Label "/login/ redirects to portal login" -Path "/login/" -ExpectedStatus 302 -ExpectedLocationPrefix "/portal/login/")
    [void](Add-Check -Label "/admin-panel/ requires login" -Path "/admin-panel/" -ExpectedStatus 302 -ExpectedLocationPrefix "LOGIN")
}
finally {
    $client.Dispose()
    $handler.Dispose()
}

$results | Format-Table -AutoSize -Wrap
if (@($results | Where-Object { $_.Result -eq "FAIL" }).Count -gt 0) {
    exit 1
}
exit 0

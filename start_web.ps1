# One-click loopback static server for Windows PowerShell 5.1+. No Python required.
$ErrorActionPreference = 'Stop'
$project = [IO.Path]::GetFullPath($PSScriptRoot)
$listener = $null
foreach ($port in 8000..8010) {
    $candidate = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $port)
    try { $candidate.Start(); $listener = $candidate; break }
    catch { $candidate.Stop() }
}
if ($null -eq $listener) { throw 'Ports 8000-8010 are busy. Close another local server and retry.' }
$port = ([Net.IPEndPoint]$listener.LocalEndpoint).Port
$url = "http://127.0.0.1:$port/web/"
Write-Host "FORM is ready: $url"
Write-Host 'Keep this window open while using the page. Close it to stop the local server.'
try { Start-Process $url } catch { Write-Host "Open $url in Chrome or Edge." }

function Send-Response($stream, [int]$code, [string]$reason, [string]$body, [string]$contentType) {
    $data = [Text.Encoding]::UTF8.GetBytes($body)
    $header = "HTTP/1.1 $code $reason`r`nContent-Type: $contentType`r`nContent-Length: $($data.Length)`r`nConnection: close`r`nCache-Control: no-store`r`n`r`n"
    $head = [Text.Encoding]::ASCII.GetBytes($header)
    $stream.Write($head, 0, $head.Length)
    $stream.Write($data, 0, $data.Length)
}

try {
    while ($true) {
        $client = $listener.AcceptTcpClient()
        try {
            $client.ReceiveTimeout = 10000
            $client.SendTimeout = 30000
            $stream = $client.GetStream()
            $reader = [IO.StreamReader]::new($stream, [Text.Encoding]::ASCII, $false, 4096, $true)
            $request = $reader.ReadLine()
            while (($line = $reader.ReadLine()) -ne $null -and $line.Length -ne 0) { }
            if ($request -match '^(GET|HEAD) (/[^ ]*) HTTP/1\.[01]$') {
                $method = $Matches[1]
                $route = [Uri]::UnescapeDataString(($Matches[2] -split '\?', 2)[0])
            } else {
                Send-Response $stream 405 'Method Not Allowed' 'GET and HEAD only' 'text/plain; charset=utf-8'
                continue
            }
            if ($route -eq '/') { $route = '/web/index.html' }
            if ($route -eq '/web' -or $route -eq '/web/') { $route = '/web/index.html' }
            $relative = $route.TrimStart('/').Replace('/', [IO.Path]::DirectorySeparatorChar)
            $area = ($relative -split '[\\/]', 2)[0]
            if ($area -notin @('web','models','locales')) {
                Send-Response $stream 404 'Not Found' 'Not found' 'text/plain; charset=utf-8'
                continue
            }
            $path = [IO.Path]::GetFullPath((Join-Path $project $relative))
            if (-not $path.StartsWith($project + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or -not [IO.File]::Exists($path)) {
                Send-Response $stream 404 'Not Found' 'Not found' 'text/plain; charset=utf-8'
                continue
            }
            $type = switch ([IO.Path]::GetExtension($path).ToLowerInvariant()) {
                '.html' { 'text/html; charset=utf-8' }
                '.css'  { 'text/css; charset=utf-8' }
                '.js'   { 'text/javascript; charset=utf-8' }
                '.mjs'  { 'text/javascript; charset=utf-8' }
                '.json' { 'application/json; charset=utf-8' }
                '.wasm' { 'application/wasm' }
                default { 'application/octet-stream' }
            }
            $file = [IO.File]::OpenRead($path)
            try {
                $header = "HTTP/1.1 200 OK`r`nContent-Type: $type`r`nContent-Length: $($file.Length)`r`nConnection: close`r`nCache-Control: no-store`r`n`r`n"
                $head = [Text.Encoding]::ASCII.GetBytes($header)
                $stream.Write($head, 0, $head.Length)
                if ($method -eq 'GET') { $file.CopyTo($stream) }
            } finally { $file.Dispose() }
        } catch { Write-Host "Request failed: $($_.Exception.Message)" }
        finally { $client.Close() }
    }
} finally { $listener.Stop() }

<?php
/* Teste temporário: mostra em texto o que o og.php devolve. Abra /og-teste.php?c=<código do pedido> e depois APAGUE este arquivo. */
header('Content-Type: text/plain; charset=utf-8');
ini_set('display_errors', '1'); error_reporting(E_ALL);
$c = preg_replace('/[^a-f0-9]/', '', $_GET['c'] ?? '');
echo "PHP " . PHP_VERSION . " | memory_limit=" . ini_get('memory_limit') . " | max_execution_time=" . ini_get('max_execution_time') . "\n";
echo "og.php: " . (is_file(__DIR__ . '/og.php') ? filesize(__DIR__ . '/og.php') . " bytes" : 'NAO ENCONTRADO') . "\n";
echo "assets/img/og-bistro-connect.jpg: " . (is_file(__DIR__ . '/assets/img/og-bistro-connect.jpg') ? filesize(__DIR__ . '/assets/img/og-bistro-connect.jpg') . " bytes" : 'NAO ENCONTRADO') . "\n\n";

echo "--- teste de desenho ---\n";
$im = @imagecreatetruecolor(2400, 1260); echo "imagecreatetruecolor 2400x1260: " . ($im ? 'ok' : 'FALHOU') . " (memoria usada " . round(memory_get_usage() / 1048576, 1) . " MB)\n";
if ($im) {
    $f = __DIR__ . '/assets/fonts/Inter-Bold.otf';
    $r = imagettftext($im, 40, 0, 50, 100, imagecolorallocate($im, 255, 255, 255), $f, 'Teste Bistrô');
    echo "imagettftext: " . ($r ? 'ok' : 'FALHOU') . "\n";
    $p = imagescale($im, 1200, 630, IMG_BICUBIC); echo "imagescale: " . ($p ? 'ok' : 'FALHOU') . "\n";
    ob_start(); imagepng($p, null, 6); $n = strlen(ob_get_clean()); echo "imagepng: $n bytes\n";
}

$base = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' ? 'https://' : 'http://') . $_SERVER['HTTP_HOST'];
foreach (['' => 'og.php normal', '&debug=1' => 'og.php com debug=1'] as $q => $nome) {
    echo "\n--- $nome ---\n";
    $ctx = stream_context_create(['http' => ['ignore_errors' => true, 'timeout' => 20], 'ssl' => ['verify_peer' => false, 'verify_peer_name' => false]]);
    $corpo = @file_get_contents($base . '/og.php?c=' . $c . $q, false, $ctx);
    foreach (($http_response_header ?? []) as $h) echo $h . "\n";
    if ($corpo === false) { echo "sem resposta\n"; continue; }
    echo "tamanho: " . strlen($corpo) . " bytes\n";
    echo "primeiros bytes (hex): " . bin2hex(substr($corpo, 0, 16)) . "  (imagem PNG começa com 89504e47)\n";
    $txt = preg_replace('/[^\x20-\x7E\n]/', '.', substr($corpo, 0, 600));
    echo "início como texto: " . $txt . "\n";
}

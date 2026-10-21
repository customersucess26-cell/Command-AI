<?php
/* Diagnóstico temporário: abra /diag.php e depois APAGUE este arquivo. */
header('Content-Type: text/plain; charset=utf-8');
echo "PHP: " . PHP_VERSION . "\n";
echo "GD: " . (extension_loaded('gd') ? 'sim' : 'NAO') . "\n";
if (function_exists('gd_info')) { $g = gd_info(); echo "FreeType: " . (!empty($g['FreeType Support']) ? 'sim' : 'NAO') . "\nPNG: " . (!empty($g['PNG Support']) ? 'sim' : 'NAO') . "\nJPEG: " . (!empty($g['JPEG Support']) ? 'sim' : 'NAO') . "\n"; }
echo "imagettftext: " . (function_exists('imagettftext') ? 'sim' : 'NAO') . "\n";
echo "mbstring: " . (extension_loaded('mbstring') ? 'sim' : 'NAO') . "\n";
echo "curl: " . (function_exists('curl_init') ? 'sim' : 'NAO') . "\n";
foreach (['Inter-Regular.otf', 'Inter-Bold.otf'] as $f) {
    $p = __DIR__ . '/assets/fonts/' . $f;
    echo "$f: " . (is_file($p) ? filesize($p) . " bytes (certo: " . ($f === 'Inter-Bold.otf' ? '626056' : '605092') . ")" : 'NAO ENCONTRADO') . "\n";
    if (is_file($p) && function_exists('imagettfbbox')) echo "  abre na GD: " . (@imagettfbbox(10, 0, $p, 'A') ? 'sim' : 'NAO') . "\n";
}
foreach (['og.php', 'cartao.php', 'pedido.php', 'pedido-lib.php'] as $f) echo "$f: " . (is_file(__DIR__ . "/$f") ? filesize(__DIR__ . "/$f") . ' bytes' : 'NAO ENCONTRADO') . "\n";

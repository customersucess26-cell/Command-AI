<?php
/* Bistrô Connect · /p/<código> (reescrito pelo .htaccess): a mesma página pedido.html, mas com as etiquetas que o
   WhatsApp usa para mostrar o cartão do pedido (título, resumo e a imagem de og.php) quando o link é enviado. */
require __DIR__ . '/pedido-lib.php';

$html = @file_get_contents(__DIR__ . '/pedido.html');
if ($html === false) { http_response_code(500); header('Content-Type: text/plain; charset=utf-8'); exit('Página indisponível.'); }

$c = $_GET['c'] ?? '';
$p = codigo_valido($c) ? busca_pedido($c) : null;
$site = site_url();

if ($p) {
    $n = 0; foreach (($p['items'] ?? []) as $i) $n += (int)($i['qty'] ?? 0);
    $titulo = 'Pedido ' . $p['code'] . ' · ' . ($p['store_name'] ?? 'Bistrô Connect');
    $desc = $n . ($n === 1 ? ' item' : ' itens') . ' · Total ' . reais($p['total'] ?? 0) . ' · ' . rotulo_status($p);
    $img = $site . '/og.php?c=' . $c;
} else {
    $titulo = 'Acompanhe seu pedido · Bistrô Connect';
    $desc = 'Veja o andamento do seu pedido em tempo real.';
    $img = '';
}
$meta = '<meta property="og:type" content="website">' . "\n"
      . '<meta property="og:site_name" content="Bistrô Connect">' . "\n"
      . '<meta property="og:title" content="' . esc($titulo) . '">' . "\n"
      . '<meta property="og:description" content="' . esc($desc) . '">' . "\n"
      . '<meta property="og:url" content="' . esc($site . '/p/' . $c) . '">' . "\n";
if ($img !== '') {
    $meta .= '<meta property="og:image" content="' . esc($img) . '">' . "\n"
           . '<meta property="og:image:type" content="image/png">' . "\n"
           . '<meta property="og:image:width" content="1200">' . "\n"
           . '<meta property="og:image:height" content="630">' . "\n"
           . '<meta name="twitter:card" content="summary_large_image">' . "\n";
}
$html = preg_replace('#<title>.*?</title>#s', '<title>' . esc($titulo) . '</title>', $html, 1);
$html = preg_replace('#</head>#i', $meta . '</head>', $html, 1);

header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-cache');
echo $html;

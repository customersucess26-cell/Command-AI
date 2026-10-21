<?php
/* Bistrô Connect · cartão do pedido (imagem 1200x630) que o WhatsApp mostra abaixo do link /p/<código>.
   Mostra loja, número do pedido, itens, entrega, total e status. Nunca telefone nem endereço.
   Se algo falhar (sem GD, sem memória, fonte ruim), entrega a imagem fixa da marca em vez de erro 500.
   Para ver o motivo de um erro: /og.php?c=<código>&debug=1 */
$DEBUG = isset($_GET['debug']);
if ($DEBUG) { ini_set('display_errors', '1'); error_reporting(E_ALL); ob_start(); }
else {
    ini_set('display_errors', '0');
    ob_start();
    register_shutdown_function(function () {
        $e = error_get_last();
        if ($e && in_array($e['type'], [E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR, E_USER_ERROR], true)) {
            while (ob_get_level()) ob_end_clean();
            header_remove(); http_response_code(200);
            header('Content-Type: image/jpeg'); header('Cache-Control: public, max-age=300');
            @readfile(__DIR__ . '/assets/img/og-bistro-connect.jpg');
        } else { while (ob_get_level()) ob_end_flush(); }
    });
}
require __DIR__ . '/pedido-lib.php';
if (!function_exists('imagecreatetruecolor') || !function_exists('imagettftext')) {      // sem GD/FreeType: usa a imagem fixa da marca
    header('Content-Type: image/jpeg'); header('Cache-Control: public, max-age=300');
    readfile(__DIR__ . '/assets/img/og-bistro-connect.jpg'); exit;
}

const S = 2;                       // desenha no dobro do tamanho e reduz no fim: bordas lisas
$FONTE = __DIR__ . '/assets/fonts/Inter-Regular.otf';
$NEGRITO = __DIR__ . '/assets/fonts/Inter-Bold.otf';

$c = $_GET['c'] ?? '';
$p = codigo_valido($c) ? busca_pedido($c) : null;

function saida($im) {
    global $DEBUG;
    if ($DEBUG) {      // ?debug=1: se algo foi impresso antes da imagem, mostra em texto
        $avisos = ob_get_clean();
        if ($avisos !== '' && $avisos !== false) {
            header('Content-Type: text/plain; charset=utf-8');
            echo "AVISOS ANTES DA IMAGEM:\n" . $avisos . "\nmemory_limit=" . ini_get('memory_limit') . " PHP=" . PHP_VERSION . "\n";
            exit;
        }
    }
    header('Content-Type: image/png');
    header('Cache-Control: public, max-age=120');
    header('X-Content-Type-Options: nosniff');
    imagepng($im, null, 6);
    exit;
}

$big = imagecreatetruecolor(1200 * S, 630 * S);
imagealphablending($big, true);
function cor($im, $hex) { return imagecolorallocate($im, hexdec(substr($hex, 0, 2)), hexdec(substr($hex, 2, 2)), hexdec(substr($hex, 4, 2))); }
$FUNDO = cor($big, 'F2F6F9'); $AZUL = cor($big, '0B2F45'); $AZUL2 = cor($big, '0E5A7A'); $BRANCO = cor($big, 'FFFFFF');
$TINTA = cor($big, '10212B'); $SUAVE = cor($big, '5B6B76'); $LINHA = cor($big, 'E2E9EE'); $CLARO = cor($big, 'D7EEF5'); $TURQ = cor($big, '2BB3D6');

function rr($im, $x1, $y1, $x2, $y2, $r, $col) {      // retângulo arredondado, coordenadas lógicas
    $x1 = (int)round($x1 * S); $y1 = (int)round($y1 * S); $x2 = (int)round($x2 * S); $y2 = (int)round($y2 * S); $r = (int)round($r * S);
    imagefilledrectangle($im, $x1 + $r, $y1, $x2 - $r, $y2, $col);
    imagefilledrectangle($im, $x1, $y1 + $r, $x2, $y2 - $r, $col);
    foreach ([[$x1 + $r, $y1 + $r], [$x2 - $r, $y1 + $r], [$x1 + $r, $y2 - $r], [$x2 - $r, $y2 - $r]] as $q)
        imagefilledellipse($im, $q[0], $q[1], $r * 2, $r * 2, $col);
}
function larg($fonte, $tam, $t) { $b = @imagettfbbox($tam * S, 0, $fonte, $t); return $b ? ($b[2] - $b[0]) / S : 0; }   // largura em px lógicos
function txt($im, $fonte, $tam, $x, $y, $col, $t) { imagettftext($im, $tam * S, 0, (int)($x * S), (int)($y * S), $col, $fonte, $t); }
function corta($fonte, $tam, $t, $max) {
    if (larg($fonte, $tam, $t) <= $max) return $t;
    while (mb_strlen($t) > 1 && larg($fonte, $tam, $t . '…') > $max) $t = mb_substr($t, 0, -1);
    return rtrim($t) . '…';
}

if (!is_file($FONTE) || !is_file($NEGRITO) || !@imagettfbbox(10, 0, $NEGRITO, 'A')) {      // sem fonte: cartão simples, sem texto
    imagefill($big, 0, 0, $AZUL);
    $im = imagescale($big, 1200, 630); saida($im);
}

imagefill($big, 0, 0, $FUNDO);
// faixa azul do topo
imagefilledrectangle($big, 0, 0, 1200 * S, 150 * S, $AZUL);
imagefilledrectangle($big, 0, 146 * S, 1200 * S, 150 * S, $TURQ);

if (!$p) {
    txt($big, $NEGRITO, 46, 60, 100, $BRANCO, 'Bistrô Connect');
    txt($big, $NEGRITO, 40, 60, 330, $TINTA, 'Pedido não encontrado');
    txt($big, $FONTE, 26, 60, 380, $SUAVE, 'Confira o link que a loja enviou.');
    $im = imagescale($big, 1200, 630, IMG_BICUBIC); saida($im);
}

// topo: loja, número do pedido e status
$loja = corta($NEGRITO, 46, (string)($p['store_name'] ?? 'Loja'), 720);
txt($big, $NEGRITO, 46, 56, 78, $BRANCO, $loja);
$nome = trim((string)($p['first_name'] ?? ''));
txt($big, $FONTE, 26, 56, 124, cor($big, 'A9DDEB'), 'Pedido ' . $p['code'] . ($nome !== '' ? '  ·  ' . mb_substr($nome, 0, 18) : ''));
$st = rotulo_status($p);
$lw = larg($NEGRITO, 26, $st);
rr($big, 1144 - $lw - 56, 40, 1144, 106, 33, $CLARO);
txt($big, $NEGRITO, 26, 1144 - $lw - 28, 83, $AZUL2, $st);

// cartão dos itens
rr($big, 40, 176, 1160, 492, 28, $LINHA);
rr($big, 41, 177, 1159, 491, 27, $BRANCO);
txt($big, $NEGRITO, 20, 76, 220, $SUAVE, 'ITENS DO PEDIDO');
$itens = array_values($p['items'] ?? []);
$mostra = array_slice($itens, 0, 4);
$y = 272;
foreach ($mostra as $i) {
    $qtd = (int)($i['qty'] ?? 1);
    $nomeItem = corta($NEGRITO, 29, $qtd . '×  ' . ($i['name'] ?? ''), 800);
    txt($big, $NEGRITO, 29, 76, $y, $TINTA, $nomeItem);
    $preco = reais(((float)($i['price'] ?? 0)) * $qtd);
    txt($big, $NEGRITO, 29, 1124 - larg($NEGRITO, 29, $preco), $y, $AZUL2, $preco);
    $ops = array_filter(array_map('strval', (array)($i['options'] ?? [])));
    if ($ops) { txt($big, $FONTE, 21, 110, $y + 30, $SUAVE, corta($FONTE, 21, implode(', ', $ops), 780)); $y += 76; } else { $y += 56; }
    if ($y > 456) break;
}
$resto = count($itens) - count($mostra);
if ($resto > 0 && $y <= 470) txt($big, $FONTE, 22, 76, $y - 6, $SUAVE, '+ ' . $resto . ($resto === 1 ? ' item' : ' itens'));

// entrega e total
rr($big, 40, 508, 590, 580, 36, $CLARO);
$entrega = ($p['delivery_type'] ?? '') === 'entrega';
$tx = $entrega ? (((float)($p['delivery_fee'] ?? 0)) > 0 ? 'Entrega  ' . reais($p['delivery_fee']) : 'Entrega grátis') : 'Retirada na loja';
txt($big, $NEGRITO, 27, 74, 554, $AZUL2, $tx);
rr($big, 610, 504, 1160, 584, 40, $AZUL);
txt($big, $FONTE, 27, 648, 556, cor($big, 'CFE6EE'), 'Total');
$tot = reais($p['total'] ?? 0);
txt($big, $NEGRITO, 44, 1124 - larg($NEGRITO, 44, $tot), 560, $BRANCO, $tot);

txt($big, $FONTE, 19, 460, 614, $SUAVE, 'Bistrô Connect  ·  bistroconnect.com.br');

$im = imagescale($big, 1200, 630, IMG_BICUBIC);
saida($im);

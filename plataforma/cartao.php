<?php
/* Bistrô Connect · cartão do pedido em imagem (1024 px de largura) para a loja receber no WhatsApp.
   Uso: /cartao.php?c=<código de 16 caracteres>. Tem nome, telefone e endereço do cliente: só quem recebeu o código vê. */
require __DIR__ . '/pedido-lib.php';
if (!function_exists('imagecreatetruecolor') || !function_exists('imagettftext')) {
    http_response_code(503); header('Content-Type: text/plain; charset=utf-8'); exit('Esta hospedagem está sem a biblioteca de imagens (GD/FreeType).');
}

const S = 2;
$R = __DIR__ . '/assets/fonts/';
$F = $R . 'Inter-Regular.otf'; $B = $R . 'Inter-Bold.otf';
$W = 1024;

$c = $_GET['c'] ?? '';
$p = preg_match('/^[a-f0-9]{16}$/', $c) ? busca_cartao($c) : null;

function reduz($src, $w, $h) {      // reduz com suavização (imagecopyresampled funciona em qualquer GD; imagescale falha em alguns servidores)
    $dst = imagecreatetruecolor($w, $h);
    imagecopyresampled($dst, $src, 0, 0, 0, 0, $w, $h, imagesx($src), imagesy($src));
    return $dst;
}
function saida($im) {
    header('Content-Type: image/png');
    header('Cache-Control: private, no-store');
    header('X-Content-Type-Options: nosniff');
    header('X-Robots-Tag: noindex');
    imagepng($im, null, 6);
    exit;
}
function cor($im, $hex) { return imagecolorallocate($im, hexdec(substr($hex, 0, 2)), hexdec(substr($hex, 2, 2)), hexdec(substr($hex, 4, 2))); }
function larg($f, $t, $s) { $b = @imagettfbbox($t * S, 0, $f, $s); return $b ? ($b[2] - $b[0]) / S : 0; }
function txt($im, $f, $t, $x, $y, $col, $s) { imagettftext($im, $t * S, 0, (int)round($x * S), (int)round($y * S), $col, $f, $s); }
function corta($f, $t, $s, $max) {
    if (larg($f, $t, $s) <= $max) return $s;
    while (mb_strlen($s) > 1 && larg($f, $t, $s . '…') > $max) $s = mb_substr($s, 0, -1);
    return rtrim($s) . '…';
}
function rr($im, $x1, $y1, $x2, $y2, $r, $col) {
    $x1 = (int)round($x1 * S); $y1 = (int)round($y1 * S); $x2 = (int)round($x2 * S); $y2 = (int)round($y2 * S); $r = (int)round($r * S);
    imagefilledrectangle($im, $x1 + $r, $y1, $x2 - $r, $y2, $col);
    imagefilledrectangle($im, $x1, $y1 + $r, $x2, $y2 - $r, $col);
    foreach ([[$x1 + $r, $y1 + $r], [$x2 - $r, $y1 + $r], [$x1 + $r, $y2 - $r], [$x2 - $r, $y2 - $r]] as $q)
        imagefilledellipse($im, $q[0], $q[1], $r * 2, $r * 2, $col);
}
function circ($im, $cx, $cy, $r, $col) { imagefilledellipse($im, (int)($cx * S), (int)($cy * S), (int)($r * 2 * S), (int)($r * 2 * S), $col); }

/* carrega imagem do próprio site (caminho relativo) ou do armazenamento do Supabase; nada além disso */
function carrega_img(?string $u) {
    if (!$u || !is_string($u)) return null;
    $dados = false;
    if ($u[0] === '/' && strpos($u, '//') !== 0) {
        $caminho = realpath(__DIR__ . '/' . ltrim(strtok($u, '?#'), '/'));
        $base = realpath(__DIR__ . '/assets');
        if ($caminho && $base && strpos($caminho, $base . DIRECTORY_SEPARATOR) === 0 && is_file($caminho)) $dados = @file_get_contents($caminho);
    } elseif (preg_match('#^https://([a-z0-9.-]+)/#i', $u, $m)) {
        $host = parse_url(cfg()['url'], PHP_URL_HOST);
        if ($host && strtolower($m[1]) === strtolower($host)) {
            $ctx = stream_context_create(['http' => ['timeout' => 4, 'follow_location' => 0], 'ssl' => ['verify_peer' => true]]);
            $dados = @file_get_contents($u, false, $ctx, 0, 6000000);
        }
    }
    if ($dados === false || $dados === '') return null;
    $im = @imagecreatefromstring($dados);
    return $im ?: null;
}
/* desenha $src cobrindo o retângulo (corte central), cantos arredondados */
function cobre($dst, $src, $x, $y, $w, $h, $r, $fundo) {
    $sw = imagesx($src); $sh = imagesy($src);
    $X = (int)($x * S); $Y = (int)($y * S); $Wd = (int)($w * S); $Hd = (int)($h * S);
    $k = max($Wd / $sw, $Hd / $sh); $cw = (int)round($Wd / $k); $ch = (int)round($Hd / $k);
    imagecopyresampled($dst, $src, $X, $Y, (int)(($sw - $cw) / 2), (int)(($sh - $ch) / 2), $Wd, $Hd, $cw, $ch);
    $r = (int)($r * S);
    foreach ([[0, 0, 1, 1], [1, 0, -1, 1], [0, 1, 1, -1], [1, 1, -1, -1]] as $q) {      // pinta o que sobra fora do canto
        $ox = $q[0] ? $X + $Wd - 1 : $X; $oy = $q[1] ? $Y + $Hd - 1 : $Y;
        $cx = $ox + $q[2] * ($r - 1); $cy = $oy + $q[3] * ($r - 1);
        for ($i = 0; $i < $r; $i++) for ($j = 0; $j < $r; $j++) {
            $px = $ox + $q[2] * $i; $py = $oy + $q[3] * $j;
            if (($px - $cx) ** 2 + ($py - $cy) ** 2 > $r * $r) imagesetpixel($dst, $px, $py, $fundo);
        }
    }
}
function fone_br(string $f): string {
    $d = preg_replace('/\D/', '', $f);
    if (strlen($d) > 11 && substr($d, 0, 2) === '55') $d = substr($d, 2);
    if (strlen($d) === 11) return '(' . substr($d, 0, 2) . ') ' . substr($d, 2, 5) . '-' . substr($d, 7);
    if (strlen($d) === 10) return '(' . substr($d, 0, 2) . ') ' . substr($d, 2, 4) . '-' . substr($d, 6);
    return $f;
}
function quebra($f, $t, $s, $max, $linhas) {
    $pal = preg_split('/\s+/', trim($s)); $out = []; $at = '';
    foreach ($pal as $w) {
        $try = $at === '' ? $w : $at . ' ' . $w;
        if (larg($f, $t, $try) <= $max) { $at = $try; continue; }
        if ($at !== '') $out[] = $at;
        $at = $w;
    }
    if ($at !== '') $out[] = $at;
    if (count($out) > $linhas) { $out = array_slice($out, 0, $linhas); $out[$linhas - 1] = corta($f, $t, $out[$linhas - 1] . '…', $max); }
    return $out ?: [''];
}

if (!is_file($F) || !is_file($B) || !@imagettfbbox(10, 0, $B, 'A')) { http_response_code(500); header('Content-Type: text/plain'); exit('Fonte indisponível.'); }

if (!$p) {
    $im = imagecreatetruecolor($W, 400);
    imagefill($im, 0, 0, cor($im, '0B2F45'));
    $branco = cor($im, 'FFFFFF');
    imagettftext($im, 32, 0, 60, 200, $branco, $B, 'Pedido não encontrado');
    http_response_code(404);
    saida($im);
}

/* ---- conteúdo ---- */
$itens = array_values($p['items'] ?? []);
$entrega = ($p['delivery_type'] ?? '') === 'entrega';
$fee = (float)($p['delivery_fee'] ?? 0);
$loja = trim((string)($p['store_name'] ?? 'Loja'));
$hero = null;
foreach ([$p['capa_url'] ?? null] as $u) { if (!$hero) $hero = carrega_img($u); }
if (!$hero) foreach ($itens as $i) { $hero = carrega_img($i['image_url'] ?? null); if ($hero) break; }

$linhaH = 96;
$hHeader = 150; $hUrl = 70; $hHero = $hero ? 330 : 0; $hOla = 150;
$hItens = 100 + count($itens) * $linhaH;
foreach ($itens as $i) if (array_filter((array)($i['options'] ?? []))) $hItens += 30;
$endTxt = $entrega ? trim((string)($p['address'] ?? '')) : 'Retirada na loja';
$endLinhas = quebra($F, 26, $endTxt !== '' ? $endTxt : '-', $W - 300, 2);
$hInfo = 40 + 3 * 86 + (count($endLinhas) - 1) * 32;
$hTotal = 130; $hZap = 120; $hRod = 100;
$H = $hHeader + $hUrl + $hHero + $hOla + $hItens + $hTotal + $hInfo + $hZap + $hRod + 60;

$im = imagecreatetruecolor($W * S, $H * S);
imagealphablending($im, true);
$AZUL = cor($im, '0B2F45'); $AZUL2 = cor($im, '0E5A7A'); $TURQ = cor($im, '2BB3D6'); $BRANCO = cor($im, 'FFFFFF');
$FUNDO = cor($im, 'EEF4F8'); $TINTA = cor($im, '10212B'); $SUAVE = cor($im, '5B6B76'); $LINHA = cor($im, 'DCE6EC'); $CLARO = cor($im, 'D7EEF5');
$ESC = cor($im, '0F2A3B'); $TEXTOCLARO = cor($im, 'CFE6EE');
imagefill($im, 0, 0, $FUNDO);
$y = 0;

/* topo com a marca */
imagefilledrectangle($im, 0, 0, $W * S, $hHeader * S, $AZUL);
imagefilledrectangle($im, 0, ($hHeader - 5) * S, $W * S, $hHeader * S, $TURQ);
$logo = carrega_img('/assets/img/logo-bistro-connect-clara.png');
if ($logo) {
    $lh = 96; $lw = (int)(imagesx($logo) * $lh / imagesy($logo));
    imagealphablending($im, true);
    imagecopyresampled($im, $logo, (int)(($W - $lw) / 2 * S), (int)(25 * S), 0, 0, $lw * S, $lh * S, imagesx($logo), imagesy($logo));
} else { $t = 'Bistrô Connect'; txt($im, $B, 46, ($W - larg($B, 46, $t)) / 2, 90, $BRANCO, $t); }
$y = $hHeader;

/* link */
$site = preg_replace('#^https?://#', '', site_url());
$u = $site; $uw = larg($B, 24, $u) + 70;
rr($im, ($W - $uw) / 2, $y + 14, ($W + $uw) / 2, $y + 62, 24, $AZUL);
txt($im, $B, 24, ($W - larg($B, 24, $u)) / 2, $y + 46, $BRANCO, $u);
$y += $hUrl;

/* foto */
if ($hero) {
    cobre($im, $hero, 30, $y, $W - 60, $hHero - 20, 28, $FUNDO);
    $y += $hHero;
}

/* saudação */
$ola = 'Olá, ' . $loja . '!';
txt($im, $B, 54, ($W - larg($B, 54, corta($B, 54, $ola, $W - 80))) / 2, $y + 66, $AZUL2, corta($B, 54, $ola, $W - 80));
$msg = 'Fiz o pedido #' . ltrim((string)$p['code'], '#') . ' pelo site.';
$msg = corta($F, 30, $msg, $W - 80);
txt($im, $F, 30, ($W - larg($F, 30, $msg)) / 2, $y + 116, $TINTA, $msg);
$y += $hOla;

/* itens */
rr($im, 30, $y, $W - 30, $y + $hItens, 34, $ESC);
txt($im, $B, 30, 70, $y + 58, $BRANCO, 'Itens do pedido');
$iy = $y + 96;
foreach ($itens as $i) {
    $qtd = (int)($i['qty'] ?? 1);
    $ops = array_filter(array_map('strval', (array)($i['options'] ?? [])));
    $th = carrega_img($i['image_url'] ?? null);
    if ($th) cobre($im, $th, 62, $iy, 70, 70, 14, $ESC); else rr($im, 62, $iy, 132, $iy + 70, 14, $AZUL2);
    $nome = corta($B, 27, (string)($i['name'] ?? ''), 520);
    txt($im, $B, 27, 152, $iy + 32, $BRANCO, $nome);
    $sub = $qtd . ' x ' . reais($i['price'] ?? 0);
    txt($im, $F, 22, 152, $iy + 62, $TEXTOCLARO, $sub);
    $total = reais(((float)($i['price'] ?? 0)) * $qtd);
    txt($im, $B, 27, $W - 62 - larg($B, 27, $total), $iy + 46, $BRANCO, $total);
    $iy += $linhaH - 8;
    if ($ops) { txt($im, $F, 20, 152, $iy + 6, $TURQ, corta($F, 20, '+ ' . implode(', ', $ops), $W - 240)); $iy += 30; }
    $iy += 8;
}
$y += $hItens;

/* entrega e total */
$ty = $y + 28;
rr($im, 30, $ty, 500, $ty + 76, 38, $CLARO);
$tx = $entrega ? ($fee > 0 ? 'Entrega: ' . reais($fee) : 'Entrega grátis') : 'Retirada na loja';
txt($im, $B, 27, 30 + (470 - 30 - larg($B, 27, $tx)) / 2 + 0, $ty + 49, $AZUL2, $tx);
rr($im, 520, $ty, $W - 30, $ty + 76, 38, $AZUL);
$tt = 'Total: ' . reais($p['total'] ?? 0);
txt($im, $B, 30, 520 + (($W - 30) - 520 - larg($B, 30, $tt)) / 2, $ty + 51, $BRANCO, $tt);
$y += $hTotal;

/* informações */
rr($im, 30, $y, $W - 30, $y + $hInfo, 30, $LINHA); rr($im, 32, $y + 2, $W - 32, $y + $hInfo - 2, 28, $BRANCO);
$quando = '';
if (!empty($p['scheduled_for'])) { $ts = strtotime($p['scheduled_for']); $quando = $ts ? date('d/m H:i', $ts) : ''; }
$pag = ['pix' => 'Pix', 'dinheiro' => 'Dinheiro', 'cartao' => 'Cartão', 'credito' => 'Cartão de crédito', 'debito' => 'Cartão de débito'];
$pg = $pag[$p['payment_method'] ?? ''] ?? ucfirst((string)($p['payment_method'] ?? ''));
$ly = $y + 40;
$rotulos = [[$entrega ? 'Entrega em' : 'Retirada', $endLinhas], ['Para', [trim((string)($p['customer_name'] ?? ''))]], ['Pagamento', [$pg !== '' ? $pg : '-']]];
foreach ($rotulos as $k => $r) {
    circ($im, 84, $ly + 14, 24, $CLARO);
    if ($k === 0) { circ($im, 84, $ly + 8, 8, $AZUL2); imagefilledpolygon($im, [(int)(76 * S), (int)(($ly + 12) * S), (int)(92 * S), (int)(($ly + 12) * S), (int)(84 * S), (int)(($ly + 28) * S)], $AZUL2); circ($im, 84, $ly + 8, 3.5, $CLARO); }
    if ($k === 1) { circ($im, 84, $ly + 6, 7, $AZUL2); rr($im, 72, $ly + 17, 96, $ly + 28, 5, $AZUL2); }
    if ($k === 2) { rr($im, 72, $ly + 6, 96, $ly + 24, 4, $AZUL2); imagefilledrectangle($im, 72 * S, (int)(($ly + 11) * S), 96 * S, (int)(($ly + 15) * S), $CLARO); }
    txt($im, $F, 22, 130, $ly + 8, $SUAVE, $r[0]);
    foreach ($r[1] as $n => $lnh) txt($im, $B, 27, 130, $ly + 44 + $n * 32, $TINTA, corta($B, 27, $lnh, $W - 200));
    if ($k === 0 && $quando !== '') txt($im, $F, 22, $W - 60 - larg($F, 22, $quando), $ly + 6, $SUAVE, $quando);
    $ly += 86 + ($k === 0 ? (count($endLinhas) - 1) * 32 : 0);
}
$y += $hInfo + 28;

/* contato */
rr($im, 30, $y, $W - 30, $y + $hZap - 20, 40, $ESC);
circ($im, 96, $y + ($hZap - 20) / 2, 26, cor($im, '25D366'));
rr($im, 87, $y + ($hZap - 20) / 2 - 5, 105, $y + ($hZap - 20) / 2 + 5, 5, $BRANCO);
$cn = corta($B, 28, (string)($p['customer_name'] ?? ''), $W - 260);
txt($im, $B, 28, 148, $y + 42, $BRANCO, $cn);
txt($im, $F, 26, 148, $y + 78, $TEXTOCLARO, fone_br((string)($p['customer_phone'] ?? '')));
$y += $hZap;

/* rodapé */
$sl = 'Pedido feito pelo site, direto no seu WhatsApp.';
txt($im, $F, 24, ($W - larg($F, 24, $sl)) / 2, $y + 40, $SUAVE, $sl);
$sl2 = 'Bistrô Connect';
txt($im, $B, 26, ($W - larg($B, 26, $sl2)) / 2, $y + 80, $AZUL2, $sl2);

$out = reduz($im, $W, $H);
saida($out);

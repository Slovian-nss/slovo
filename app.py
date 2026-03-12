<?php
// --- CONFIG I ŁADOWANIE BAZ ---
$osnova = json_decode(file_get_contents('osnova.json'), true) ?: [];
$vuzor = json_decode(file_get_contents('vuzor.json'), true) ?: [];
$memory = json_decode(file_get_contents('memory.json'), true) ?: [];

$translatedText = "";
$srcText = $_POST['srcText'] ?? "";
$direction = $_POST['dir'] ?? "pl_sl";
$statusMsg = "";

// --- LOGIKA ADMINA (ZAPIS DO PLIKU) ---
if (isset($_POST['action']) && $_POST['action'] === 'add_word') {
    if ($_POST['pass'] === "Rozeta*8") {
        $pl = trim($_POST['newPl']);
        $sl = trim($_POST['newSl']);
        if ($pl && $sl) {
            $memory[mb_strtolower($pl, 'UTF-8')] = $sl;
            file_put_contents('memory.json', json_encode($memory, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
            $statusMsg = "<div style='color:green;'>✅ Zapisano pomyślnie w memory.json!</div>";
        }
    } else {
        $statusMsg = "<div style='color:red;'>❌ Błędne hasło!</div>";
    }
}

// --- LOGIKA TŁUMACZENIA ---
if (!empty($srcText) && !isset($_POST['action'])) {
    $tokens = preg_split('/(\W+)/u', $srcText, -1, PREG_SPLIT_DELIM_CAPTURE);
    
    foreach ($tokens as $t) {
        if (preg_match('/^\W+$/u', $t)) {
            $translatedText .= $t;
            continue;
        }

        $low = mb_strtolower($t, 'UTF-8');
        $found = false;

        // 1. Pamięć
        if (isset($memory[$low])) {
            $res = $memory[$low];
            $found = true;
        } 
        // 2. Osnova
        else {
            foreach ($osnova as $item) {
                $src = ($direction === 'pl_sl') ? $item['polish'] : $item['slovian'];
                $trg = ($direction === 'pl_sl') ? $item['slovian'] : $item['polish'];

                if (mb_strtolower($src, 'UTF-8') === $low) {
                    $res = $trg;
                    // Vuzor (odmiana)
                    if ($direction === 'pl_sl' && isset($item['vuzor']) && isset($vuzor[$item['vuzor']])) {
                        $res .= ($vuzor[$item['vuzor']]['nom'] ?? "");
                    }
                    $found = true;
                    break;
                }
            }
        }

        $final = $found ? $res : $t;

        // Zachowanie wielkości liter
        if (mb_strtoupper($t, 'UTF-8') === $t) {
            $translatedText .= mb_strtoupper($final, 'UTF-8');
        } elseif (mb_strtoupper(mb_substr($t, 0, 1, 'UTF-8')) === mb_substr($t, 0, 1, 'UTF-8')) {
            $translatedText .= mb_convert_case($final, MB_CASE_TITLE, "UTF-8");
        } else {
            $translatedText .= $final;
        }
    }
}
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Perkladačь (PHP Full Version)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #0055ff; --bg: #f3f6f9; --text: #1a1a1a; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { max-width: 1000px; width: 100%; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
        textarea { width: 100%; height: 200px; padding: 15px; border-radius: 12px; border: 1px solid #d1d9e0; font-size: 16px; resize: none; margin-top: 10px; }
        .btn { padding: 15px 30px; background: var(--primary); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: 600; width: 100%; margin-top: 10px; }
        .admin-panel { margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; width: 100%; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    </style>
</head>
<body>

<div class="container">
    <h1>🌐 Perkladačь slověnьskogo (PHP)</h1>
    <?php echo $statusMsg; ?>

    <form method="POST">
        <div style="text-align:center;">
            <label><input type="radio" name="dir" value="pl_sl" <?php if($direction=='pl_sl') echo 'checked'; ?>> PL ➔ SL</label>
            <label style="margin-left:20px;"><input type="radio" name="dir" value="sl_pl" <?php if($direction=='sl_pl') echo 'checked'; ?>> SL ➔ PL</label>
        </div>

        <div class="grid">
            <div>
                <strong>Tekst źródłowy:</strong>
                <textarea name="srcText" id="srcText"><?php echo htmlspecialchars($srcText); ?></textarea>
            </div>
            <div>
                <strong>Wynik:</strong>
                <textarea readonly id="resText"><?php echo htmlspecialchars($translatedText); ?></textarea>
            </div>
        </div>
        <button type="submit" class="btn">🚀 TŁUMACZ</button>
    </form>

    <div style="margin-top:10px; display:flex; gap:10px;">
        <button onclick="copyResult()" style="flex:1;">✂️ Kopiuj wynik</button>
        <button onclick="pasteSource()" style="flex:1;">📋 Wklej źródło</button>
    </div>

    <div class="admin-panel">
        <h3>🛠️ Panel Admina (Trwały zapis do JSON)</h3>
        <form method="POST">
            <input type="hidden" name="action" value="add_word">
            <input type="password" name="pass" placeholder="Hasło" required>
            <input type="text" name="newPl" placeholder="Słowo PL" required>
            <input type="text" name="newSl" placeholder="Słowo SL" required>
            <button type="submit">✅ Dodaj na stałe do bazy</button>
        </form>
    </div>
</div>

<script>
function copyResult() {
    const text = document.getElementById('resText');
    text.select();
    document.execCommand('copy');
    alert("Skopiowano!");
}
async function pasteSource() {
    const text = await navigator.clipboard.readText();
    document.getElementById('srcText').value = text;
}
</script>

</body>
</html>

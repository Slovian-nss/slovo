<?php
// 1. ŁADOWANIE BAZ DANYCH Z PLIKÓW JSON
$osnova = json_decode(file_get_contents('osnova.json'), true) ?: [];
$vuzor = json_decode(file_get_contents('vuzor.json'), true) ?: [];
$memory = json_decode(file_get_contents('memory.json'), true) ?: [];

$translatedText = "";
$srcText = $_POST['srcText'] ?? "";
$direction = $_POST['dir'] ?? "pl_sl";
$statusMsg = "";

// 2. OBSŁUGA PANELU ADMINA (DODAWANIE SŁÓW)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'add_word') {
    if ($_POST['pass'] === "Rozeta*8") {
        $pl = trim($_POST['newPl']);
        $sl = trim($_POST['newSl']);
        if (!empty($pl) && !empty($sl)) {
            $memory[mb_strtolower($pl, 'UTF-8')] = $sl;
            // Trwały zapis do pliku na serwerze
            file_put_contents('memory.json', json_encode($memory, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
            $statusMsg = "<p style='color:green;'>✅ Słowo dodane do pamięci!</p>";
        }
    } else {
        $statusMsg = "<p style='color:red;'>❌ Błędne hasło admina!</p>";
    }
}

// 3. FUNKCJA TŁUMACZĄCA POJEDYNCZE SŁOWO
function translateWord($word, $direction, $osnova, $vuzor, $memory) {
    $lowWord = mb_strtolower(trim($word), 'UTF-8');
    
    // Najpierw sprawdź pamięć (poprawki ręczne)
    if (isset($memory[$lowWord])) {
        return $memory[$lowWord];
    }

    // Szukaj w głównej bazie osnova
    foreach ($osnova as $item) {
        $src = ($direction === 'pl_sl') ? $item['polish'] : $item['slovian'];
        $trg = ($direction === 'pl_sl') ? $item['slovian'] : $item['polish'];

        if (mb_strtolower(trim($src), 'UTF-8') === $lowWord) {
            $result = $trg;
            // Obsługa odmiany (vuzor) tylko dla PL -> SL
            if ($direction === 'pl_sl' && !empty($item['vuzor']) && isset($vuzor[$item['vuzor']])) {
                $suffix = $vuzor[$item['vuzor']]['nom'] ?? "";
                $result .= $suffix;
            }
            return $result;
        }
    }
    return $word; // Zwróć oryginał, jeśli nie znaleziono
}

// 4. PROCES TŁUMACZENIA CAŁEGO TEKSTU
if (!empty($srcText) && !isset($_POST['action'])) {
    // Rozbijanie na słowa i znaki interpunkcyjne
    $tokens = preg_split('/(\W+)/u', $srcText, -1, PREG_SPLIT_DELIM_CAPTURE);
    
    foreach ($tokens as $t) {
        if (preg_match('/^\W+$/u', $t)) {
            $translatedText .= $t;
        } else {
            $trans = translateWord($t, $direction, $osnova, $vuzor, $memory);
            
            // Zachowanie wielkości liter (na wzór Pythona)
            if (mb_strtoupper($t, 'UTF-8') === $t) {
                $translatedText .= mb_strtoupper($trans, 'UTF-8');
            } elseif (mb_strtoupper(mb_substr($t, 0, 1, 'UTF-8'), 'UTF-8') === mb_substr($t, 0, 1, 'UTF-8')) {
                $translatedText .= mb_convert_case($trans, MB_CASE_TITLE, "UTF-8");
            } else {
                $translatedText .= $trans;
            }
        }
    }
}
?>

<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Perkladačь slověnьskogo ęzyka</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f9; margin: 0; padding: 40px; display: flex; flex-direction: column; align-items: center; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 900px; }
        h1 { color: #333; text-align: center; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        textarea { width: 100%; height: 200px; padding: 15px; border-radius: 10px; border: 1px solid #ddd; font-size: 16px; box-sizing: border-box; resize: none; }
        .controls { text-align: center; margin: 20px 0; }
        .main-btn { background-color: #007bff; color: white; border: none; padding: 15px 40px; border-radius: 10px; cursor: pointer; font-size: 18px; width: 100%; transition: background 0.3s; }
        .main-btn:hover { background-color: #0056b3; }
        .admin-section { margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
        .admin-form input { padding: 8px; margin: 5px; border-radius: 5px; border: 1px solid #ccc; }
    </style>
</head>
<body>

<div class="container">
    <h1>🌐 Perkladačь slověnьskogo ęzyka</h1>
    
    <form method="POST">
        <div class="controls">
            <label><input type="radio" name="dir" value="pl_sl" <?php echo ($direction == 'pl_sl' ? 'checked' : ''); ?>> PL ➔ SL</label>
            <label style="margin-left: 20px;"><input type="radio" name="dir" value="sl_pl" <?php echo ($direction == 'sl_pl' ? 'checked' : ''); ?>> SL ➔ PL</label>
        </div>

        <div class="grid">
            <div>
                <label>Tekst źródłowy:</label>
                <textarea name="srcText" placeholder="Wpisz tekst..."><?php echo htmlspecialchars($srcText); ?></textarea>
            </div>
            <div>
                <label>Wynik:</label>
                <textarea readonly placeholder="Tłumaczenie..."><?php echo htmlspecialchars($translatedText); ?></textarea>
            </div>
        </div>

        <button type="submit" class="main-btn">🚀 TŁUMACZ</button>
    </form>

    <div class="admin-section">
        <h3>🛠️ Popraw tłumaczenie (Admin)</h3>
        <?php echo $statusMsg; ?>
        <form method="POST" class="admin-form">
            <input type="hidden" name="action" value="add_word">
            <input type="password" name="pass" placeholder="Hasło" required>
            <input type="text" name="newPl" placeholder="Słowo PL" required>
            <input type="text" name="newSl" placeholder="Słowo SL" required>
            <button type="submit">Dodaj do bazy</button>
        </form>
    </div>
</div>

<script>
    // Prosta obsługa wklejania/kopiowania przez JS dla wygody użytkownika
    function copyResult() {
        const copyText = document.querySelectorAll('textarea')[1];
        copyText.select();
        document.execCommand("copy");
    }
</script>

</body>
</html>

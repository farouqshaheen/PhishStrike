<?php
include 'ip.php';

// Get target parameter if exists
$target = isset($_GET['target']) ? $_GET['target'] : '';

if ($target) {
    header('Location: login.php?target=' . urlencode($target));
} else {
    header('Location: login.php');
}
exit();
?>

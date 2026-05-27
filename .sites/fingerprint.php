<?php
// Get JSON payload
$data = json_decode(file_get_contents('php://input'), true);

if ($data) {
    // Get IP
    if(isset($_SERVER['HTTP_CLIENT_IP'])) {
        $ipaddr = $_SERVER['HTTP_CLIENT_IP'];
    } elseif(isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ipaddr = $_SERVER['HTTP_X_FORWARDED_FOR'];
    } else {
        $ipaddr = $_SERVER['REMOTE_ADDR'];
    }
    if(strpos($ipaddr,',') !== false) {
        $ipaddr = preg_split("/\,/", $ipaddr)[0];
    }
    
    $data['ip'] = $ipaddr;

    $fp = fopen('fingerprint.txt', 'a');
    fwrite($fp, json_encode($data) . "\n");
    fclose($fp);
}
?>

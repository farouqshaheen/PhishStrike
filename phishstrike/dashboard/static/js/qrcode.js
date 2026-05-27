// qrcode.js – Simple wrapper for QR Code generation using QRCode.js CDN
// Include this script after the QRCode.js library is loaded.
function generateQRCode(url, targetElementId) {
  const container = document.getElementById(targetElementId);
  if (!container) return console.error('QR container not found:', targetElementId);
  // Clear previous QR code
  container.innerHTML = '';
  // QRCode constructor from QRCode.js library
  new QRCode(container, {
    text: url,
    width: 180,
    height: 180,
    colorDark: '#000000',
    colorLight: '#ffffff',
    correctLevel: QRCode.CorrectLevel.H
  });
}

// Example usage:
// generateQRCode('https://example.com', 'qr-container');

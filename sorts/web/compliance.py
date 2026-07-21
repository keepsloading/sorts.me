"""
HTML pages for Terms of Service and Privacy Policy compliance required by Discord Developer Portal.
Serves mobile-friendly HTML endpoints at /terms and /privacy strictly using #000543, white, Horizon font, and Sortling Mascot icon.
"""

COMMON_STYLE = """
<style>
    @import url('https://fonts.cdnfonts.com/css/horizon');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #000543;
        --card-bg: rgba(255, 255, 255, 0.04);
        --border: rgba(255, 255, 255, 0.18);
        --text: #ffffff;
        --text-muted: rgba(255, 255, 255, 0.75);
    }
    * {
        box-sizing: border-box;
    }
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #000543;
        color: #ffffff;
        margin: 0;
        padding: 40px 20px;
        line-height: 1.6;
        min-height: 100vh;
    }
    .container {
        max-width: 820px;
        margin: 0 auto;
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 44px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    }
    .brand-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 28px;
    }
    .brand-icon {
        width: 52px;
        height: 52px;
        background: #ffffff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        flex-shrink: 0;
    }
    .brand-icon img {
        width: 38px;
        height: 38px;
        object-fit: contain;
    }
    .brand-title-group {
        display: flex;
        flex-direction: column;
    }
    .brand-name {
        font-family: 'Horizon', 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: 1px;
    }
    .discord-badge {
        font-family: 'Inter', sans-serif;
        background: #ffffff;
        color: #000543;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }
    .brand-subtitle {
        font-size: 0.9rem;
        color: var(--text-muted);
    }
    h1 {
        font-family: 'Horizon', 'Inter', sans-serif;
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0 0 20px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        letter-spacing: 0.5px;
    }
    h2 {
        font-family: 'Horizon', 'Inter', sans-serif;
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 32px;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 6px;
        letter-spacing: 0.5px;
    }
    p, li {
        color: var(--text-muted);
        font-size: 0.98rem;
    }
    ul {
        padding-left: 24px;
        margin-top: 8px;
    }
    li {
        margin-bottom: 6px;
    }
    code {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
        padding: 2px 8px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
        font-size: 0.88rem;
    }
    .nav-tabs {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
    }
    .nav-tab {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    .nav-tab.active {
        background: transparent;
        border: 1px solid #ffffff;
        color: #ffffff;
    }
    .nav-tab:not(.active) {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: rgba(255, 255, 255, 0.65);
    }
    .nav-tab:not(.active):hover {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-color: #ffffff;
    }
    .date-badge {
        font-family: 'Inter', sans-serif;
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .callout {
        background: rgba(255, 255, 255, 0.06);
        border-left: 4px solid #ffffff;
        padding: 16px 20px;
        border-radius: 0 12px 12px 0;
        margin: 24px 0;
    }
    .callout p {
        margin: 0;
        color: #ffffff;
    }
    .footer {
        margin-top: 40px;
        text-align: center;
        font-size: 0.85rem;
        color: var(--text-muted);
        border-top: 1px solid var(--border);
        padding-top: 24px;
    }
    a {
        color: #ffffff;
        text-decoration: underline;
        font-weight: 500;
    }
    a:hover {
        opacity: 0.85;
    }

    /* Mobile Responsive Optimizations */
    @media (max-width: 640px) {
        body {
            padding: 16px 12px;
        }
        .container {
            padding: 24px 18px;
            border-radius: 16px;
        }
        .brand-header {
            gap: 12px;
            padding-bottom: 18px;
            margin-bottom: 20px;
        }
        .brand-icon {
            width: 44px;
            height: 44px;
        }
        .brand-icon img {
            width: 32px;
            height: 32px;
        }
        .brand-name {
            font-size: 1.2rem;
        }
        .brand-subtitle {
            font-size: 0.8rem;
        }
        h1 {
            font-size: 1.3rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }
        h2 {
            font-size: 1.05rem;
            margin-top: 24px;
        }
        .nav-tabs {
            gap: 8px;
        }
        .nav-tab {
            padding: 6px 12px;
            font-size: 0.82rem;
        }
        .callout {
            padding: 12px 14px;
            margin: 18px 0;
        }
        p, li {
            font-size: 0.92rem;
        }
    }
</style>
"""

TERMS_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - Sortling</title>
    {COMMON_STYLE}
</head>
<body>
    <div class="container">
        <div class="brand-header">
            <div class="brand-icon">
                <img src="https://raw.githubusercontent.com/keepsloading/sorts.me/main/Sortling%20Mascot/Icon_Neutral.png" alt="Sortling Mascot">
            </div>
            <div class="brand-title-group">
                <div class="brand-name">Sortling <span class="discord-badge">APP</span></div>
                <div class="brand-subtitle">Mahindra University Campus Discovery Engine</div>
            </div>
        </div>

        <div class="nav-tabs">
            <a href="/terms" class="nav-tab active">Terms of Service</a>
            <a href="/privacy" class="nav-tab">Privacy Policy</a>
        </div>

        <h1>Terms of Service <span class="date-badge">Effective: July 2026</span></h1>
        <p>Welcome to <strong>Sortling</strong>. By adding or using the Sortling Discord Application in your server, you agree to comply with and be bound by these Terms of Service.</p>
        
        <h2>1. Agreement to Terms</h2>
        <p>By interacting with Sortling, executing slash commands (such as <code>/sort</code>, <code>/clubs</code>, <code>/events</code>, <code>/about</code>), or completing questionnaires, you acknowledge that you have read, understood, and agreed to these Terms and the Discord Developer Terms of Service.</p>

        <h2>2. Permitted Use</h2>
        <p>Sortling is designed strictly for campus club discovery, organization recommendations, and student engagement. You agree not to:</p>
        <ul>
            <li>Use the bot for any illegal, harmful, or unauthorized activities.</li>
            <li>Attempt to exploit, reverse engineer, or flood the bot's slash command API.</li>
            <li>Use automated scripts or bots to spam interactions or bypass rate limits.</li>
        </ul>

        <h2>3. Accuracy & Verification</h2>
        <p>Sortling provides information derived from official university directories and publicly verifiable student organization resources. While we strive for 100% accuracy, official club registration and membership procedures remain governed by university administration.</p>

        <div class="callout">
            <p><strong>Note:</strong> Recommendation scores generated during <code>/sort</code> quiz sessions are calculated dynamically using multi-vector matching algorithms to guide your discovery experience.</p>
        </div>

        <h2>4. Service Availability & Updates</h2>
        <p>We continuously update Sortling to improve recommendation algorithms and add new campus features. We reserve the right to modify, suspend, or discontinue any part of the service at any time.</p>

        <h2>5. Limitation of Liability</h2>
        <p>Sortling is provided on an "as is" and "as available" basis without warranties of any kind. The developers shall not be liable for any indirect or consequential damages arising out of your use of the application.</p>

        <div class="footer">
            Sortling Discord Application &bull; <a href="/privacy">Privacy Policy</a> &bull; Mahindra University Campus Discovery
        </div>
    </div>
</body>
</html>
"""

PRIVACY_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - Sortling</title>
    {COMMON_STYLE}
</head>
<body>
    <div class="container">
        <div class="brand-header">
            <div class="brand-icon">
                <img src="https://raw.githubusercontent.com/keepsloading/sorts.me/main/Sortling%20Mascot/Icon_Neutral.png" alt="Sortling Mascot">
            </div>
            <div class="brand-title-group">
                <div class="brand-name">Sortling <span class="discord-badge">APP</span></div>
                <div class="brand-subtitle">Mahindra University Campus Discovery Engine</div>
            </div>
        </div>

        <div class="nav-tabs">
            <a href="/terms" class="nav-tab">Terms of Service</a>
            <a href="/privacy" class="nav-tab active">Privacy Policy</a>
        </div>

        <h1>Privacy Policy <span class="date-badge">Effective: July 2026</span></h1>
        <p>Your privacy is paramount. This Privacy Policy explains how <strong>Sortling</strong> collects, uses, and safeguards user data in strict compliance with Discord Developer Policy standards.</p>

        <h2>1. Information We Collect</h2>
        <p>Sortling practices strict data minimization. We only collect data necessary to provide personalized club recommendations:</p>
        <ul>
            <li><strong>Discord Identifiers:</strong> Ephemeral Discord User ID and Guild ID to scope quiz sessions and manage server admin permissions.</li>
            <li><strong>Questionnaire Preferences:</strong> Option choices selected during <code>/sort</code> quiz sessions to calculate recommendation scores.</li>
            <li><strong>Feedback & Corrections:</strong> Optional feedback submitted via <code>/feedback</code> or interest refinements (e.g. <em>"Am I wrong?"</em> menu).</li>
        </ul>

        <div class="callout">
            <p><strong>Zero Personal Data Guarantee:</strong> Sortling never collects or stores personal names, phone numbers, email credentials, or private message chat history from your Discord channels.</p>
        </div>

        <h2>2. How We Use Data</h2>
        <p>Collected preference data is used exclusively to:</p>
        <ul>
            <li>Generate multi-vector club recommendation matches and personalized explanations.</li>
            <li>Perform online gradient self-training adjustments to improve club trait mapping over time.</li>
        </ul>

        <h2>3. Data Storage & Security</h2>
        <p>Session data is stored in isolated, secure SQLite database storage hosted on Render cloud infrastructure. We implement appropriate technical safeguards to prevent unauthorized access.</p>

        <h2>4. Data Rights & Deletion</h2>
        <p>Users have full control over their stored data. You can request immediate deletion of your session preferences at any time by executing administrative reset commands or contacting bot administrators.</p>

        <h2>5. Third-Party Sharing</h2>
        <p>We do <strong>NOT</strong> sell, trade, or share user data with third-party advertisers or external services.</p>

        <div class="footer">
            Sortling Discord Application &bull; <a href="/terms">Terms of Service</a> &bull; Mahindra University Campus Discovery
        </div>
    </div>
</body>
</html>
"""

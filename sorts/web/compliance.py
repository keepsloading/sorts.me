"""
HTML pages for Terms of Service and Privacy Policy compliance required by Discord Developer Portal.
Serves responsive, Sortling UI Native HTML endpoints at /terms and /privacy.
"""

COMMON_STYLE = """
<style>
    :root {
        --bg: #0b1329;
        --card-bg: #131f37;
        --card-border: #1f3459;
        --brand-blue: #1B365D;
        --accent-blue: #4f80ff;
        --accent-cyan: #38bdf8;
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
        --code-bg: #1e2d4a;
        --code-border: #2d436c;
        --app-badge-bg: #5865f2;
    }
    * {
        box-sizing: border-box;
    }
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--bg);
        background-image: 
            radial-gradient(at 0% 0%, rgba(27, 54, 93, 0.4) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(79, 128, 255, 0.15) 0px, transparent 50%);
        color: var(--text-main);
        margin: 0;
        padding: 40px 20px;
        line-height: 1.6;
        min-height: 100vh;
    }
    .container {
        max-width: 820px;
        margin: 0 auto;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 44px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    .brand-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--card-border);
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
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        font-size: 26px;
    }
    .brand-title-group {
        display: flex;
        flex-direction: column;
    }
    .brand-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .discord-badge {
        background: var(--app-badge-bg);
        color: #ffffff;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }
    .brand-subtitle {
        font-size: 0.9rem;
        color: var(--text-muted);
    }
    h1 {
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 700;
        margin: 0 0 20px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    h2 {
        color: var(--accent-cyan);
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 28px;
        margin-bottom: 10px;
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
        background: var(--code-bg);
        border: 1px solid var(--code-border);
        color: #a5c2f5;
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
        font-weight: 500;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    .nav-tab.active {
        background: var(--brand-blue);
        border: 1px solid var(--accent-blue);
        color: #ffffff;
    }
    .nav-tab:not(.active) {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--card-border);
        color: var(--text-muted);
    }
    .nav-tab:not(.active):hover {
        background: rgba(255, 255, 255, 0.08);
        color: #ffffff;
    }
    .date-badge {
        background: rgba(56, 189, 248, 0.1);
        color: var(--accent-cyan);
        font-size: 0.8rem;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .callout {
        background: rgba(27, 54, 93, 0.35);
        border-left: 4px solid var(--accent-blue);
        padding: 16px 20px;
        border-radius: 0 12px 12px 0;
        margin: 24px 0;
    }
    .callout p {
        margin: 0;
        color: var(--text-main);
    }
    .footer {
        margin-top: 40px;
        text-align: center;
        font-size: 0.85rem;
        color: var(--text-muted);
        border-top: 1px solid var(--card-border);
        padding-top: 24px;
    }
    a {
        color: var(--accent-blue);
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
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
            <div class="brand-icon">🧭</div>
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
        <p>By interacting with Sortling, executing slash commands (such as <code>/sort</code>, <code>/clubs</code>, <code>/about</code>), or completing questionnaires, you acknowledge that you have read, understood, and agreed to these Terms and the Discord Developer Terms of Service.</p>

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
            <div class="brand-icon">🧭</div>
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

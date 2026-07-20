"""
HTML pages for Terms of Service and Privacy Policy compliance required by Discord Developer Portal.
Serves responsive, dark-themed HTML endpoints at /terms and /privacy.
"""

COMMON_STYLE = """
<style>
    :root {
        --bg: #0f172a;
        --card-bg: #1e293b;
        --accent: #3b82f6;
        --text: #f8fafc;
        --text-muted: #94a3b8;
        --border: #334155;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--bg);
        color: var(--text);
        margin: 0;
        padding: 40px 20px;
        line-height: 1.6;
    }
    .container {
        max-width: 800px;
        margin: 0 auto;
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 40px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    h1 {
        color: #ffffff;
        font-size: 2rem;
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    h2 {
        color: var(--accent);
        font-size: 1.25rem;
        margin-top: 28px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 8px;
    }
    p, li {
        color: var(--text-muted);
        font-size: 1rem;
    }
    ul {
        padding-left: 20px;
    }
    .badge {
        background: rgba(59, 130, 246, 0.15);
        color: var(--accent);
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .footer {
        margin-top: 40px;
        text-align: center;
        font-size: 0.875rem;
        color: var(--text-muted);
        border-top: 1px solid var(--border);
        padding-top: 20px;
    }
    a {
        color: var(--accent);
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
        <h1><span>🧭</span> Sortling Terms of Service <span class="badge">Effective: July 2026</span></h1>
        <p>Welcome to <strong>Sortling</strong>. By adding or using the Sortling Discord Bot in your server, you agree to comply with and be bound by these Terms of Service.</p>
        
        <h2>1. Agreement to Terms</h2>
        <p>By interacting with Sortling, executing slash commands (such as <code>/sort</code>, <code>/clubs</code>), or completing questionnaires, you acknowledge that you have read, understood, and agreed to these Terms and the Discord Terms of Service.</p>

        <h2>2. Permitted Use</h2>
        <p>Sortling is designed strictly for campus discovery, organization recommendations, and student engagement. You agree not to:</p>
        <ul>
            <li>Use the bot for any illegal, harmful, or unauthorized activities.</li>
            <li>Attempt to exploit, reverse engineer, or flood the bot's slash command API.</li>
            <li>Use automated scripts or bots to spam interactions or bypass rate limits.</li>
        </ul>

        <h2>3. Accuracy & Verification</h2>
        <p>Sortling provides information derived from official university directories and publicly verifiable student organization resources. While we strive for 100% accuracy, official club registration and membership procedures remain governed by university administration.</p>

        <h2>4. Availability & Modifications</h2>
        <p>We continuously update Sortling to improve recommendation algorithms and add features. We reserve the right to modify, suspend, or discontinue any part of the service at any time without prior notice.</p>

        <h2>5. Limitation of Liability</h2>
        <p>Sortling is provided on an "as is" and "as available" basis without warranties of any kind. The developers shall not be liable for any indirect or consequential damages arising out of your use of the bot.</p>

        <h2>6. Contact Us</h2>
        <p>If you have questions regarding these Terms, please reach out via GitHub or through our support channels.</p>

        <div class="footer">
            Sortling Discord Bot &bull; <a href="/privacy">Privacy Policy</a> &bull; Mahindra University Campus Discovery
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
        <h1><span>🔒</span> Sortling Privacy Policy <span class="badge">Effective: July 2026</span></h1>
        <p>Your privacy is paramount. This Privacy Policy explains how <strong>Sortling</strong> collects, uses, and safeguards user data in compliance with Discord Developer Policy standards.</p>

        <h2>1. Information We Collect</h2>
        <p>Sortling practices strict data minimization. We only collect data necessary to provide personalized club recommendations:</p>
        <ul>
            <li><strong>Discord Identifiers:</strong> Ephemeral Discord User ID and Guild ID to scope quiz sessions and manage server admin permissions.</li>
            <li><strong>Questionnaire Preferences:</strong> Option choices selected during <code>/sort</code> quiz sessions to calculate recommendation scores.</li>
            <li><strong>Feedback & Corrections:</strong> Optional feedback submitted via <code>/feedback</code> or interest refinements (e.g. <em>"Am I wrong?"</em> menu).</li>
        </ul>

        <h2>2. Data We DO NOT Collect</h2>
        <p>We respect student boundaries and strictly do <strong>NOT</strong> collect or store:</p>
        <ul>
            <li>Personal names, phone numbers, or residential addresses.</li>
            <li>Email credentials or payment information.</li>
            <li>Private message contents or chat history from Discord channels.</li>
        </ul>

        <h2>3. How We Use Data</h2>
        <p>Collected preference data is used exclusively to:</p>
        <ul>
            <li>Generate multi-vector club recommendation matches and personalized explanations.</li>
            <li>Perform online gradient self-training adjustments to improve club trait mapping over time.</li>
        </ul>

        <h2>4. Data Storage & Security</h2>
        <p>Session data is stored in isolated, secure SQLite database storage hosted on Render cloud infrastructure. We implement appropriate technical safeguards to prevent unauthorized access.</p>

        <h2>5. Data Rights & Deletion</h2>
        <p>Users have full control over their stored data. You can request immediate deletion of your session preferences at any time by executing administrative reset commands or contacting bot administrators.</p>

        <h2>6. Third-Party Sharing</h2>
        <p>We do <strong>NOT</strong> sell, trade, or share user data with third-party advertisers or external services.</p>

        <div class="footer">
            Sortling Discord Bot &bull; <a href="/terms">Terms of Service</a> &bull; Mahindra University Campus Discovery
        </div>
    </div>
</body>
</html>
"""

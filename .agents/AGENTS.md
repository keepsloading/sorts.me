# Sortling UI & Design Principles

## 1. Discord UI Buttons & Interactive Controls
- **NO EMOJIS ON BUTTON LABELS**: Discord UI Buttons (`nextcord.ui.Button`) MUST NOT contain any emojis in their `label` property under any circumstances (e.g., use `"Register Now"` instead of `"Register Now 🚀"`, `"I want more!"` instead of `"I want more! 🚀"`).
- Button labels should be fun, punchy, concise, and professional text-only.

## 2. Color Palette & Web Compliance Styling
- **Web Brand Colors**: The web UI (including `/terms` and `/privacy` compliance endpoints) strictly uses `#000543` (Deep Midnight Blue) and `#ffffff` (White).
- **Transparent Control Backgrounds**: Web navigation buttons (`.nav-tab`) must use transparent backgrounds (`background: transparent`) with clean 1px white borders (`border: 1px solid #ffffff`).
- **Discord Bot Embed Color**: Embeds use `BRAND_COLOR` (`0x000543`).

## 3. Emoji Usage in Message Embeds & Text Content
- Use emojis cleanly and consistently for category badges, field section titles, and status indicators.
- **Do not overload emojis**: Maximum 1 emoji per field title or line item.
- Standard Emoji Map:
  - Header / Compass: `🧭`
  - Hackathons / Competitions: `🚀`
  - Prizes & Rewards: `🏆`
  - Dates & Schedules: `📅` / `🕒`
  - Category: `🏷️`
  - Verification & Trust: `🛡️`
  - Official Links / Web: `🌐`
  - Team Rules: `👥`
  - Email Requirements: `📧`

## 4. Embed Layout & Encapsulation
- Keep status notices, feedback confirmations, and refined profile updates inside `embed.description`.
- Place mascot thumbnails (`thinking.gif` / `Icon_Neutral.png`) inside the embed card via `embed.set_thumbnail(url=...)` to avoid stand-alone image message attachments.

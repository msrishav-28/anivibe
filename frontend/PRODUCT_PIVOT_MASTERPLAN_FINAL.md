# ⚔️ AniVibe: The "Neo-Tokyo" Commercial Pivot Masterplan
**Version:** FINAL (Production Execution)
**Target:** $10k Premium MVP | Gen Z India
**Philosophy:** "Ferrari Engine in a Cyberpunk Chassis"

---

## 1. Executive Strategy: The "Iceberg" Pivot

### The Asset Reality
*   **The Engine (Backend):** You have built a monster. 43 Endpoints, 5 ML Models (CLIP, BERT, GNN), Explainability. This is commercial-grade tech.
*   **The Chassis (Frontend):** Currently a generic dashboard. It hides the engine.
*   **The Fix:** We are pivoting to an **"Immersive Digital Experience."** We stop building a database tool and start building a "Vibe Synthesizer."

### The "Kill List" (Scope Discipline)
To ship a premium product in <10 days, we ruthlessly cut:
1.  **Sidebar Nav:** Replaced by Mobile-First Bottom Glass Bar.
2.  **Chat/Forums:** Replaced by "Passive Social" (Heatmaps/Trends).
3.  **Auth Wall:** Replaced by "Guest Mode" (Hook first, login later).
4.  **Complex Reviews:** Replaced by "Community Pulse" (Aggregated stats).
5.  **3D Atlas (Mobile):** Downgraded to a "Radar Chart" on mobile; kept as a "Galaxy Map" only for Desktop High-Tier users.

---

## 2. Visual DNA: "Neo-Tokyo Ethereal"

### A. The "Void" Atmosphere
*   **Base:** `#050505` (Deep AMOLED Black).
*   **Texture:** Global **Film Grain Overlay** (3% opacity) + **Scanlines** (1% opacity). *Mandatory for the "expensive" feel.*
*   **Lighting:** Reactive Ambient Light that shifts color based on the User's Mood (e.g., Sad = Indigo, Hype = Crimson).

### B. Typography (Manga Editorial)
*   **Headers:** **Clash Display** (Semibold). Sharp, structural, aggressive.
*   **Body:** **Satoshi** (Regular). Geometric utility.
*   **Accents:** Massive, low-opacity **Kanji** watermarks behind English headers (e.g., "流行" behind TRENDING).

### C. The "Hardware Tiering" System (Critical)
We cannot crash low-end Android phones with R3F particles.
*   **High Tier (Desktop/iPhone):** Full R3F Particles, Blur-XL, Noise.
*   **Mid Tier (Mid-Android):** Static Background, CSS Blur.
*   **Low Tier (Budget):** Solid Black Background, Opacity only (No Blur).

---

## 3. Core Component Architecture

### A. The "Vibe Tuner" (Search Bar)
*   **Concept:** A "Mood Synthesizer," not a text box.
*   **Visual:** Glassmorphic Pill (`backdrop-blur-xl`).
*   **Interaction:**
    *   **Glitch Reveal:** Placeholder text decodes (`_` -> `#` -> `Type your mood`).
    *   **Haptic Pulse:** Input box shakes slightly on typing.
    *   **Sentiment Sync:** Typing "Rain" turns the global UI blue.

### B. The "Holographic" Anime Card
*   **Structure:** Vertical Manga Ratio (2:3).
*   **Effect:** **Holo Foil Gradient** that moves opposite to mouse (Parallax).
*   **Data Layer:**
    *   **Score:** Neon Badge "98% MATCH" (No raw numbers).
    *   **Explainability:** A "Sparkle" icon. Hovering/Tapping reveals the SHAP explanation ("Why?").
*   **Motion:** On hover, the character *pops* out of the frame (Z-axis translation).

### C. The "Weeb Cred" Profile
*   **Visual:** Looks like a Cyberpunk ID Card.
*   **Features:**
    *   **Heatmap:** Green/Purple dot graph showing watch consistency (Gamification).
    *   **Taste Radar:** Spider chart of genres.
    *   **Share:** Native **WhatsApp Button** to share the ID card.

---

## 4. Technical Integration & Cleanup

### A. Backend (.py) Optimization
*   **Model Loading:** Ensure `ml_models.py` uses **Lazy Loading**. Do not load BERT/CLIP into memory until the first request.
*   **Embeddings:** Verify that `generate_embeddings.py` has run and populated the Vector DB (Postgres/Mongo) so the Vibe Search works instantly.

### B. Frontend Architecture
*   **State:** Use `useHardwareTier` hook to control visual density globally.
*   **Network:** Wrap all `api-client.ts` calls in **React Query** (`useQuery`) to handle Loading/Error states gracefully.
*   **Security:** Move JWT storage from `localStorage` to `HttpOnly Cookies`.

---

## 5. Execution Roadmap (The Final Sprint)

### Phase 1: The Foundation (Day 1)
- [ ] Implement `HardwareTier` hook.
- [ ] Add `GlobalFilmGrain` and `Scanlines` components.
- [ ] Install Fonts (Clash Display, Satoshi).

### Phase 2: The Hero Components (Day 2)
- [ ] Build `CinematicContainer` (R3F Background).
- [ ] Build `VibeTuner` (Search Bar with Sentiment Sync).
- [ ] Build `HolographicCard` (Foil + Pop-out).

### Phase 3: The Pages (Days 3-4)
- [ ] **Landing:** Hero + Trending Carousel (Guest Mode).
- [ ] **Explore:** Grid with "Vibe" results + "Reasoning Chips."
- [ ] **Profile:** Heatmap + ID Card layout.

### Phase 4: The Integration (Day 5)
- [ ] Connect `api.semanticSearch` to Vibe Tuner.
- [ ] Connect `api.getRecommendations` to Holographic Cards.
- [ ] Final Performance Audit (Lighthouse Score).

---

## 6. The $10k Quality Checklist

1.  **Does it feel alive?** (Grain, Pulse, Particle drift).
2.  **Does it respect the user?** (No forced login, fast load on low-end).
3.  **Is the AI visible?** (Explainability tooltips are easy to find).
4.  **Is it shareable?** (WhatsApp button works).

*This document supersedes all previous plans. Execute against this strictly.*

:root {
  --bg: #050913;
  --panel: #0d1526;
  --panel2: #111c30;
  --line: #26344c;
  --text: #f7f9fc;
  --muted: #93a4bc;
  --accent: #46d7ad;
  --blue: #6fa8ff;
  --gold: #f4c95d;
  --red: #ff7f86;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  color: var(--text);
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at top left, rgba(48,111,169,.28), transparent 35%),
    linear-gradient(180deg, #060b15, var(--bg));
}

a { color: inherit; text-decoration: none; }

.nav-shell {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 76px;
  max-width: 1440px;
  margin: auto;
  padding: 0 28px;
  display: flex;
  align-items: center;
  gap: 28px;
  border-bottom: 1px solid rgba(96,119,153,.22);
  background: rgba(5,9,19,.82);
  backdrop-filter: blur(16px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  margin-right: auto;
}

.brand-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(145deg, #66efc6, #20b88d);
  color: #041a13;
  font-weight: 900;
}

.brand b { display: block; }
.brand small {
  display: block;
  color: var(--muted);
  font-size: .61rem;
  letter-spacing: .22em;
}

.nav-links {
  display: flex;
  gap: 6px;
}

.nav-links a {
  padding: 9px 13px;
  border-radius: 9px;
  color: var(--muted);
  font-weight: 700;
}

.nav-links a:hover,
.nav-links a.active {
  background: var(--panel2);
  color: var(--text);
}

.badge {
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: .7rem;
  font-weight: 800;
}

.badge.live { color: var(--accent); }
.badge.warning { color: var(--gold); }

.badge i {
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 6px;
  border-radius: 50%;
  background: var(--accent);
}

.alert {
  max-width: 1384px;
  margin: 18px auto 0;
  padding: 14px 17px;
  border: 1px solid rgba(244,201,93,.3);
  border-radius: 14px;
  background: rgba(244,201,93,.09);
  color: #ffe6a0;
}

main {
  max-width: 1440px;
  margin: auto;
  padding: 0 28px 64px;
}

.hero {
  padding: 64px 0 36px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 48px;
}

.hero h1 {
  margin: 12px 0 20px;
  font-size: clamp(3rem, 6vw, 5.6rem);
  line-height: .92;
  letter-spacing: -.06em;
}

.hero h1 span {
  color: var(--accent);
}

.hero p {
  max-width: 760px;
  color: var(--muted);
  line-height: 1.7;
}

.hero-status {
  min-width: 280px;
  padding: 18px;
  border: 1px solid rgba(96,119,153,.22);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(17,28,48,.9), rgba(9,16,29,.9));
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: .72rem;
  text-transform: uppercase;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
}

.hero-status strong {
  display: block;
  margin: 10px 0 7px;
}

.hero-status small { color: var(--muted); }

.eyebrow {
  color: var(--accent);
  font-size: .7rem;
  font-weight: 900;
  letter-spacing: .18em;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}

.metrics article,
.panel {
  border: 1px solid rgba(96,119,153,.22);
  background: linear-gradient(180deg, rgba(17,28,48,.97), rgba(8,15,28,.98));
  box-shadow: 0 20px 60px rgba(0,0,0,.28);
}

.metrics article {
  padding: 20px;
  border-radius: 17px;
}

.metrics span {
  display: block;
  margin-bottom: 8px;
  color: var(--muted);
  font-size: .68rem;
  text-transform: uppercase;
  letter-spacing: .1em;
}

.metrics strong {
  display: block;
  font-size: 1.55rem;
}

.metrics small {
  display: block;
  margin-top: 7px;
  color: var(--muted);
}

.positive { color: var(--accent); }
.negative { color: var(--red); }

.panel {
  margin-bottom: 18px;
  padding: 25px;
  border-radius: 20px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
}

.section-head h2 {
  margin: 5px 0 0;
  font-size: 1.55rem;
}

.count-chip {
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(70,215,173,.08);
  color: var(--accent);
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.pick-card,
.game-card {
  border: 1px solid rgba(96,119,153,.22);
  background: rgba(6,13,24,.82);
}

.pick-card {
  padding: 20px;
  border-radius: 17px;
}

.pick-top,
.team-row,
.stake,
.prob-labels,
.quality-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.grade {
  min-width: 40px;
  height: 40px;
  display: inline-grid;
  place-items: center;
  border-radius: 11px;
  background: var(--accent);
  color: #031b13;
  font-weight: 900;
}

.book {
  color: var(--blue);
  font-size: .7rem;
  font-weight: 800;
}

.market-pill {
  margin-top: 16px;
  color: var(--muted);
  font-size: .68rem;
  text-transform: uppercase;
}

.pick-card h3 {
  margin: 8px 0 5px;
  font-size: 1.4rem;
}

.matchup {
  margin: 0;
  color: var(--muted);
}

.price {
  margin: 18px 0;
  font-size: 2.3rem;
  font-weight: 900;
}

dl {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 7px;
  margin: 0;
}

dl div {
  padding: 10px;
  border-radius: 10px;
  background: var(--panel2);
}

dt {
  color: var(--muted);
  font-size: .6rem;
  text-transform: uppercase;
}

dd {
  margin: 4px 0 0;
  font-weight: 800;
}

.stake {
  margin-top: 14px;
  padding: 12px;
  border-radius: 11px;
  background: rgba(70,215,173,.08);
}

.stake span { color: var(--muted); }

.empty {
  padding: 40px 20px;
  text-align: center;
  border: 1px dashed var(--line);
  border-radius: 16px;
  color: var(--muted);
}

.empty.compact { grid-column: 1 / -1; }

.slate-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 11px;
}

.game-card {
  padding: 16px;
  border-radius: 15px;
}

.game-time {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(96,119,153,.22);
  color: var(--muted);
  font-size: .67rem;
}

.team-row { padding: 7px 0; }

.prob-bar {
  height: 7px;
  margin-top: 11px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--blue);
}

.prob-bar span {
  display: block;
  height: 100%;
  background: var(--accent);
}

.prob-labels,
.quality-row {
  margin-top: 7px;
  color: var(--muted);
  font-size: .7rem;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid rgba(96,119,153,.22);
  border-radius: 14px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: .84rem;
}

th {
  padding: 12px 13px;
  text-align: left;
  color: var(--muted);
  background: var(--panel2);
  font-size: .63rem;
  text-transform: uppercase;
}

td {
  padding: 13px;
  border-top: 1px solid rgba(96,119,153,.16);
  white-space: nowrap;
}

.muted { color: var(--muted); }
.text-link { color: var(--accent); }

footer {
  max-width: 1384px;
  margin: auto;
  padding: 25px 28px 40px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  color: var(--muted);
  font-size: .72rem;
}

@media (max-width: 1100px) {
  .metrics { grid-template-columns: repeat(3, 1fr); }
  .cards { grid-template-columns: 1fr 1fr; }
  .slate-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 780px) {
  .hero { flex-direction: column; align-items: flex-start; }
  .hero-status { width: 100%; min-width: 0; }
  .metrics { grid-template-columns: 1fr 1fr; }
  .cards { grid-template-columns: 1fr; }
  .slate-grid { grid-template-columns: 1fr 1fr; }
  main { padding: 0 14px 46px; }
  .panel { padding: 18px; }
}

@media (max-width: 520px) {
  .nav-shell { padding: 0 14px; }
  .badge { display: none; }
  .hero h1 { font-size: 2.8rem; }
  .slate-grid { grid-template-columns: 1fr; }
  dl { grid-template-columns: 1fr 1fr; }
  footer { flex-direction: column; padding: 22px 16px 30px; }
}

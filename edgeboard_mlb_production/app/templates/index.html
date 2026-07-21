{% extends "base.html" %}
{% block title %}Today's Card · {{ app_name }}{% endblock %}
{% block content %}
<header class="hero">
  <div>
    <div class="eyebrow">AUTOMATED MLB BETTING MODEL</div>
    <h1>Today’s edge,<br><span>ranked and tracked.</span></h1>
    <p>FanDuel and DraftKings prices only. Official plays are frozen when selected and graded automatically after final scores.</p>
  </div>
  <div class="hero-status">
    <span>Last odds refresh</span>
    <strong>{% if last_refresh %}{{ last_refresh|local_time }}{% else %}Waiting for first refresh{% endif %}</strong>
    <small>Scheduled every 30 minutes</small>
  </div>
</header>

<section class="metrics">
  <article><span>Official record</span><strong>{{ wins }}–{{ losses }}–{{ pushes }}</strong><small>{{ graded_count }} settled bets</small></article>
  <article><span>Units</span><strong class="{% if profit >= 0 %}positive{% else %}negative{% endif %}">{{ "%+.2f"|format(profit) }}u</strong><small>{{ "%.2f"|format(units_risked) }}u risked</small></article>
  <article><span>ROI</span><strong>{{ "%.1f%%"|format(roi * 100) }}</strong><small>Official picks only</small></article>
  <article><span>Average CLV</span><strong>{% if avg_clv is not none %}{{ "%+.2f%%"|format(avg_clv * 100) }}{% else %}—{% endif %}</strong><small>Closing implied probability</small></article>
  <article><span>Unit value</span><strong>${{ "%.2f"|format(unit_value) }}</strong><small>Based on configured bankroll</small></article>
</section>

<section class="panel official-panel">
  <div class="section-head">
    <div><div class="eyebrow">{{ today }}</div><h2>Official card</h2></div>
    <span class="muted">{{ official|length }} tracked pick{% if official|length != 1 %}s{% endif %}</span>
  </div>
  {% if official %}
    <div class="cards">
    {% for p in official %}
      {% set game = games.get(p.game_id) %}
      <article class="pick-card">
        <div class="pick-top"><span class="grade">{{ p.grade }}</span><span class="book">{{ p.bookmaker|upper }}</span></div>
        <div class="market-pill">{{ p.market|market_name }}</div>
        <h3>{{ p.selection }}{% if p.line is not none %} {{ "%+g"|format(p.line) }}{% endif %}</h3>
        <p class="matchup">{% if game %}{{ game.away_team }} at {{ game.home_team }}{% else %}{{ p.game_id }}{% endif %}</p>
        <div class="price">{{ "%+d"|format(p.odds) }}</div>
        <dl>
          <div><dt>Model</dt><dd>{{ "%.1f%%"|format(p.model_prob * 100) }}</dd></div>
          <div><dt>Fair</dt><dd>{{ "%+d"|format(p.fair_odds) }}</dd></div>
          <div><dt>Edge</dt><dd>{{ "%+.1f%%"|format(p.edge * 100) }}</dd></div>
          <div><dt>EV</dt><dd>{{ "%+.1f%%"|format(p.expected_value * 100) }}</dd></div>
        </dl>
        <div class="stake"><b>{{ "%.2f"|format(p.units) }} units</b><span>${{ "%.2f"|format(p.units * unit_value) }}</span></div>
        <details><summary>Model explanation</summary><ul>{% for reason in p.explanation_json|from_json %}<li>{{ reason }}</li>{% endfor %}</ul></details>
      </article>
    {% endfor %}
    </div>
  {% else %}
    <div class="empty"><div class="empty-icon">Ø</div><h3>No official plays yet</h3><p>The model does not force action. A card appears only after a market clears the edge, EV and data-quality thresholds.</p></div>
  {% endif %}
</section>

<section class="panel">
  <div class="section-head"><div><div class="eyebrow">TODAY'S SLATE</div><h2>Game projections</h2></div><span class="muted">Projected score and win probability</span></div>
  <div class="slate-grid">
  {% for game_id, game in games.items() %}
    {% set projection = projections.get(game_id) %}
    <article class="game-card">
      <div class="game-time">{{ game.commence_time|local_time }}</div>
      <div class="team-row"><span>{{ game.away_team }}</span><b>{% if projection %}{{ "%.1f"|format(projection.away_runs) }}{% else %}—{% endif %}</b></div>
      <div class="team-row"><span>{{ game.home_team }}</span><b>{% if projection %}{{ "%.1f"|format(projection.home_runs) }}{% else %}—{% endif %}</b></div>
      {% if projection %}
      <div class="prob-bar"><span style="width:{{ projection.away_win_prob * 100 }}%"></span></div>
      <div class="prob-labels"><span>{{ "%.0f%%"|format(projection.away_win_prob * 100) }}</span><span>{{ "%.0f%%"|format(projection.home_win_prob * 100) }}</span></div>
      <small>Data quality {{ projection.data_quality }}/100</small>
      {% else %}<small>Waiting for model refresh</small>{% endif %}
    </article>
  {% else %}
    <div class="empty compact"><p>No games have been loaded for today.</p></div>
  {% endfor %}
  </div>
</section>

<section class="panel">
  <div class="section-head"><div><div class="eyebrow">WATCHLIST</div><h2>Qualifying candidates</h2></div><span class="muted">Not part of the official record</span></div>
  <div class="table-wrap"><table>
    <thead><tr><th>Game</th><th>Market</th><th>Selection</th><th>Book</th><th>Odds</th><th>Model</th><th>Edge</th><th>EV</th><th>Units</th></tr></thead>
    <tbody>
    {% for p in candidates %}{% set game = games.get(p.game_id) %}
      <tr><td>{% if game %}{{ game.away_team }} @ {{ game.home_team }}{% else %}{{ p.game_id }}{% endif %}</td><td>{{ p.market|market_name }}</td><td>{{ p.selection }}{% if p.line is not none %} {{ "%+g"|format(p.line) }}{% endif %}</td><td>{{ p.bookmaker|upper }}</td><td>{{ "%+d"|format(p.odds) }}</td><td>{{ "%.1f%%"|format(p.model_prob * 100) }}</td><td>{{ "%+.1f%%"|format(p.edge * 100) }}</td><td>{{ "%+.1f%%"|format(p.expected_value * 100) }}</td><td>{{ "%.2f"|format(p.units) }}</td></tr>
    {% else %}<tr><td colspan="9" class="muted">No candidates currently clear the thresholds.</td></tr>{% endfor %}
    </tbody>
  </table></div>
</section>

<section class="panel">
  <div class="section-head"><div><div class="eyebrow">AUDIT TRAIL</div><h2>Recent results</h2></div><a class="text-link" href="/history">View full history →</a></div>
  <div class="table-wrap"><table>
    <thead><tr><th>Date</th><th>Selection</th><th>Book</th><th>Odds</th><th>Result</th><th>P/L</th><th>Close</th><th>CLV</th></tr></thead>
    <tbody>
    {% for p in recent %}<tr><td>{{ p.pick_date }}</td><td>{{ p.selection }}{% if p.line is not none %} {{ "%+g"|format(p.line) }}{% endif %}</td><td>{{ p.bookmaker|upper }}</td><td>{{ "%+d"|format(p.odds) }}</td><td><span class="result {{ p.result }}">{{ p.result|upper }}</span></td><td>{{ "%+.2f"|format(p.profit_units or 0) }}u</td><td>{% if p.closing_odds is not none %}{{ "%+d"|format(p.closing_odds) }}{% else %}—{% endif %}</td><td>{% if p.clv is not none %}{{ "%+.2f%%"|format(p.clv * 100) }}{% else %}—{% endif %}</td></tr>
    {% else %}<tr><td colspan="8" class="muted">No settled official picks yet.</td></tr>{% endfor %}
    </tbody>
  </table></div>
</section>
{% endblock %}

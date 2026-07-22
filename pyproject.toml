{% extends "base.html" %}
{% block title %}Bet History · {{ app_name }}{% endblock %}
{% block content %}
<header class="page-header"><div><div class="eyebrow">PERMANENT AUDIT TRAIL</div><h1>Official bet history</h1><p>Every official recommendation remains stored with its original model probability, price, stake, result and closing-line value.</p></div></header>
<section class="metrics history-metrics">
  <article><span>Record</span><strong>{{ wins }}–{{ losses }}–{{ pushes }}</strong></article>
  <article><span>Profit</span><strong class="{% if profit >= 0 %}positive{% else %}negative{% endif %}">{{ "%+.2f"|format(profit) }}u</strong></article>
  <article><span>ROI</span><strong>{{ "%.1f%%"|format(roi * 100) }}</strong></article>
  <article><span>Average CLV</span><strong>{% if avg_clv is not none %}{{ "%+.2f%%"|format(avg_clv * 100) }}{% else %}—{% endif %}</strong></article>
</section>
<section class="panel">
  <div class="section-head"><div><div class="eyebrow">ALL OFFICIAL PICKS</div><h2>{{ picks|length }} stored recommendations</h2></div></div>
  <div class="table-wrap"><table>
    <thead><tr><th>Date</th><th>Game</th><th>Market</th><th>Selection</th><th>Book</th><th>Odds</th><th>Model</th><th>Edge</th><th>Units</th><th>Status</th><th>P/L</th><th>CLV</th></tr></thead>
    <tbody>
    {% for p in picks %}{% set game = games.get(p.game_id) %}
      <tr><td>{{ p.pick_date }}</td><td>{% if game %}{{ game.away_team }} @ {{ game.home_team }}{% else %}{{ p.game_id }}{% endif %}</td><td>{{ p.market|market_name }}</td><td>{{ p.selection }}{% if p.line is not none %} {{ "%+g"|format(p.line) }}{% endif %}</td><td>{{ p.bookmaker|upper }}</td><td>{{ "%+d"|format(p.odds) }}</td><td>{{ "%.1f%%"|format(p.model_prob*100) }}</td><td>{{ "%+.1f%%"|format(p.edge*100) }}</td><td>{{ "%.2f"|format(p.units) }}</td><td>{% if p.result %}<span class="result {{ p.result }}">{{ p.result|upper }}</span>{% else %}<span class="result pending">PENDING</span>{% endif %}</td><td>{% if p.profit_units is not none %}{{ "%+.2f"|format(p.profit_units) }}u{% else %}—{% endif %}</td><td>{% if p.clv is not none %}{{ "%+.2f%%"|format(p.clv*100) }}{% else %}—{% endif %}</td></tr>
    {% else %}<tr><td colspan="12" class="muted">No official picks have been stored.</td></tr>{% endfor %}
    </tbody>
  </table></div>
</section>
{% endblock %}

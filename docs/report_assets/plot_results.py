#!/usr/bin/env python3
"""Reproduce report figures from saved evaluations; no model calls or raw data access.
Run: python3 /path/to/three_trial_comparison/plot_results.py
Dependencies: matplotlib, numpy. Outputs: figures/*.png (300 dpi) and *.svg.
"""
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
summary = json.loads((ROOT / 'summary.json').read_text())
cases = json.loads((ROOT / 'all_results.json').read_text())['cases']
trials = summary['trials']
names = ['Greenland\nhalibut', 'Walleye', 'Crappie']
rows = [sorted([c for c in cases if c['trial'] == t['trial']], key=lambda c: c['case_id']) for t in trials]
round_age = lambda x: math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)
# Recalculate chart metrics against case-level records before rendering.
for t, cs in zip(trials, rows):
    assert len(cs) == len({c['case_id'] for c in cs}) == 10
    for role, key in [('astra', 'astra_age'), ('baseline', 'baseline_raw')]:
        valid = [c for c in cs if c[key] is not None]
        m = t[role]
        assert len(valid) == m['n']
        errors = [abs(round_age(c[key]) - c['reference_age']) for c in valid]
        assert sum(e == 0 for e in errors) == m['exact_count']
        assert sum(e <= 1 for e in errors) == m['within1_count']
        assert m['exact'] == m['exact_count'] / 10
        assert m['within1'] == m['within1_count'] / 10
        mae = sum(abs(c[key] - c['reference_age']) for c in valid) / len(valid)
        assert math.isclose(mae, m['mae'] if m['mae'] is not None else m['conditional_mae'])
    u = t['usage']
    assert 0 <= u['cached_input_tokens'] <= u['input_tokens']
    assert 0 <= u['reasoning_output_tokens'] <= u['output_tokens']
    assert u['input_tokens'] + u['output_tokens'] == u['total_tokens']
for field, value in summary['total_usage'].items():
    assert sum(t['usage'][field] for t in trials) == value
assert sum(t['requests'] for t in trials) == summary['requests']

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.titleweight': 'bold', 'axes.labelcolor': '#24313b',
                     'text.color': '#24313b', 'svg.fonttype': 'none'})
BLUE, ORANGE = '#2878A0', '#B55A25'

def save(fig, name):
    for ext in ['png', 'svg']:
        fig.savefig(OUT / f'{name}.{ext}', dpi=300, facecolor='white')
    plt.close(fig)

def clean(ax, ymax, label):
    ax.set_ylim(0, ymax)
    ax.set_ylabel(label)
    ax.set_axisbelow(True)
    ax.grid(axis='y', color='#e3e8eb', linewidth=.7)

# Figure 1: agreement uses all ten cases, including abstentions.
fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.8), gridspec_kw={'width_ratios': [1, 1, 1.12]})
fig.subplots_adjust(left=.055, right=.99, bottom=.26, top=.78, wspace=.30)
fig.suptitle('Agreement with expert reference ages', x=.055, ha='left', y=.97, fontsize=16, weight='bold')
x = np.arange(3)
for ax, metric, title in zip(axes[:2], ['exact', 'within1'], ['A  Exact agreement', 'B  Within one year']):
    for offset, role, color, hatch in [(-.19, 'astra', BLUE, ''), (.19, 'baseline', ORANGE, '//')]:
        values = [100 * t[role][metric] for t in trials]
        ax.bar(x + offset, values, .35, color=color, hatch=hatch, edgecolor='white', linewidth=.6)
        for xx, v in zip(x + offset, values):
            ax.text(xx, v + 2, f'{int(v)}%', ha='center', fontsize=9)
    clean(ax, 112, 'Cases (%)')
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xticks(x, names)
    ax.set_title(title, loc='left', fontsize=11)
axes[0].legend(handles=[Patch(facecolor=BLUE, label='Astra'), Patch(facecolor=ORANGE, hatch='//', edgecolor='white', label='Historical model')], loc='lower left', bbox_to_anchor=(0, 1.04), ncol=2, frameon=False, fontsize=9)
ax = axes[2]
counts = np.array([[t['astra']['exact_count'], t['astra']['within1_count']-t['astra']['exact_count'], t['astra']['n']-t['astra']['within1_count'], 10-t['astra']['n']] for t in trials])
assert np.all(counts.sum(axis=1) == 10)
colors = ['#2878A0', '#86BDD1', '#C8814F', '#D9DDE0']
labels = ['Exact', 'Error = 1 year', 'Error > 1 year', 'Abstain']
bottom = np.zeros(3)
for vals, color, label in zip(counts.T, colors, labels):
    ax.bar(x, vals, .60, bottom=bottom, color=color, edgecolor='white', label=label)
    for xx, v, b in zip(x, vals, bottom):
        if v:
            ax.text(xx, b+v/2, str(v), ha='center', va='center', color='white' if color == colors[0] else '#24313b', weight='bold')
    bottom += vals
clean(ax, 11.2, 'Number of cases')
ax.set_yticks([0, 2, 4, 6, 8, 10]); ax.set_xticks(x, names)
ax.set_title('C  Astra outcomes', loc='left', fontsize=11)
ax.legend(ncol=2, frameon=False, fontsize=9, loc='upper center', bbox_to_anchor=(.5, -.23))
fig.text(.055, .055, 'Ten test cases per dataset; abstentions remain in agreement denominators.\nHistorical predictions are contextual references with incomplete provenance; these are exploratory samples.', fontsize=9)
save(fig, '01_agreement')

# Figure 2: annotated signed errors preserve case identities and abstentions.
errors = np.array([[np.nan if c['astra_age'] is None else c['astra_age']-c['reference_age'] for c in cs] for cs in rows])
fig, ax = plt.subplots(figsize=(12, 4.4))
fig.subplots_adjust(left=.16, right=.86, bottom=.27, top=.78)
cmap = plt.get_cmap('RdBu_r').copy(); cmap.set_bad('#DDDFE1')
im = ax.imshow(np.ma.masked_invalid(errors), cmap=cmap, norm=TwoSlopeNorm(vmin=-9, vcenter=0, vmax=9), aspect='auto')
for i in range(3):
    for j in range(10):
        v = errors[i, j]
        label = 'NA' if np.isnan(v) else ('0' if v == 0 else f'{v:+.0f}')
        ax.text(j, i, label, ha='center', va='center', fontsize=12, weight='bold', color='white' if np.isfinite(v) and abs(v) >= 5 else '#24313b')
ax.set_xticks(range(10), [c['case_id'] for c in rows[0]])
ax.set_yticks(range(3), ['Greenland halibut', 'Walleye', 'Crappie'])
ax.set_xticks(np.arange(-.5, 10), minor=True); ax.set_yticks(np.arange(-.5, 3), minor=True)
ax.grid(which='minor', color='white', linewidth=3); ax.tick_params(which='both', length=0)
for s in ax.spines.values(): s.set_visible(False)
cax = fig.add_axes([.89, .27, .015, .51])
cb = fig.colorbar(im, cax=cax, ticks=[-9, -6, -3, 0, 3, 6, 9]); cb.set_label('Error (years)')
fig.suptitle('Astra age error by test case', x=.035, ha='left', y=.96, fontsize=16, weight='bold')
fig.text(.035, .86, 'Prediction minus expert reference age. Negative values indicate underestimation.', fontsize=10)
fig.text(.035, .10, 'NA = abstention, with no numeric error assigned. Case IDs restart within each dataset.\nCrappie: all eight numeric estimates were too low; seven by one year and one by two years.', fontsize=10)
save(fig, '02_case_errors')

# Figure 3: cached input and reasoning output are nested usage fields.
fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.7))
fig.subplots_adjust(left=.065, right=.99, bottom=.25, top=.76, wspace=.35)
fig.suptitle('Resource use across the three prediction sessions', x=.065, ha='left', y=.97, fontsize=16, weight='bold')
cached = np.array([t['usage']['cached_input_tokens'] for t in trials])/1e6
noncached = np.array([t['usage']['input_tokens']-t['usage']['cached_input_tokens'] for t in trials])/1e6
ax = axes[0]
ax.bar(x, cached, .58, color='#A7CFDF', label='Cached input')
ax.bar(x, noncached, .58, bottom=cached, color=BLUE, label='Noncached input')
for xx, v in zip(x, cached+noncached): ax.text(xx, v+.09, f'{v:.2f}M', ha='center')
clean(ax, 6, 'Input tokens (millions)'); ax.set_title('A  Cumulative input', loc='left', fontsize=11)
ax.legend(frameon=False, fontsize=9, loc='lower left', bbox_to_anchor=(0, 1.04), ncol=2)
ax = axes[1]
reason = np.array([t['usage']['reasoning_output_tokens'] for t in trials])/1000
other = np.array([t['usage']['output_tokens']-t['usage']['reasoning_output_tokens'] for t in trials])/1000
ax.bar(x, reason, .58, color='#DBAC8F', label='Reasoning output')
ax.bar(x, other, .58, bottom=reason, color=ORANGE, label='Other output')
for xx, v in zip(x, reason+other): ax.text(xx, v+.35, f'{v:.2f}k', ha='center')
clean(ax, 20, 'Output tokens (thousands)'); ax.set_title('B  Cumulative output', loc='left', fontsize=11)
ax.legend(frameon=False, fontsize=9, loc='lower left', bbox_to_anchor=(0, 1.04), ncol=2)
ax = axes[2]
mins = np.array([t['seconds'] for t in trials])/60
ax.bar(x, mins, .58, color='#647681')
for xx, v, t in zip(x, mins, trials): ax.text(xx, v+.4, f"{v:.1f} min\n{t['requests']} requests", ha='center', fontsize=9)
clean(ax, 24, 'Session duration (minutes)'); ax.set_title('C  Execution time', loc='left', fontsize=11)
for ax in axes: ax.set_xticks(x, names)
fig.text(.065, .075, 'Request totals include repeated context. Cached input and reasoning output are counted once.\nPrediction sessions only; preparation and reporting are excluded. Token totals do not establish monetary cost.', fontsize=9)
save(fig, '03_usage')
print('Verified all 30 cases, agreement counts, MAEs and usage totals. Saved 3 figures as PNG + SVG.')

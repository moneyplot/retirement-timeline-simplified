import numpy as np
import matplotlib.pyplot as plt

# --- Money Plot Labs Brand Style Configuration ---
mp_dark  = '#0F172A'
mp_blue  = '#3B82F6'
mp_green = '#10B981'
mp_red   = '#EF4444'

plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'grid.alpha': 0.15,
    'grid.linestyle': ':',
})

# --- Target Boundary Parameters (Matching your whitepaper definitions) ---
A_start = 20
A_end = 95
H = A_end - A_start  # 75 planning years

P0 = 0               # Starting balance ($)
P_death = 0     # Desired inheritance/legacy floor ($)
c = 10000            # Annual savings ($)
b = 50000            # Annual retirement spending ($)

# =========================================================================
# 1. GENERATE TRUE LINEAR BASELINE (r = 0%)
# =========================================================================
# Formula 9: w = (b*H + P_death - P0) / (c + b)
w_linear = (b * H + P_death - P0) / (c + b)
age_retire_linear = A_start + w_linear

# Generate data arrays using the exact step functions from your whitepaper
ages_lin = np.arange(A_start, A_end + 1)
nw_lin = []
for age in ages_lin:
    t = age - A_start
    if t <= w_linear:
        # Equation 3: Accumulation Phase
        val = P0 + c * t
    else:
        # Equation 4: Depletion Phase
        val = P_death + b * (H - t)
    nw_lin.append(val)

P_w_linear = P0 + c * w_linear

# =========================================================================
# 2. GENERATE TRUE EXPONENTIAL CURVES (r > 0%)
# =========================================================================
r = 0.03  # 3% Real growth rate

# Equation 22: Money Plot Master Legacy Equation
numerator_inner = (r * P0 + c) * ((1 + r)**H) + b * (1 + r) - r * P_death
denominator_inner = c + b * (1 + r)
w_exponential = H - (np.log(numerator_inner / denominator_inner) / np.log(1 + r))
age_retire_exp = A_start + w_exponential

ages_exp = np.arange(A_start, A_end + 1)
nw_exp = []

# Regenerate exact timeline states step-by-step
for age in ages_exp:
    t = age - A_start
    if t <= w_exponential:
        # Equation 10: Exponential Accumulation Engine
        val = P0 * ((1 + r)**t) + c * (((1 + r)**t - 1) / r)
    else:
        # Equation 15: Exponential Depletion Engine (Annuity Due tracking from P_w)
        P_w_exp = P0 * ((1 + r)**w_exponential) + c * (((1 + r)**w_exponential - 1) / r)
        t_ret = t - w_exponential
        val = P_w_exp * ((1 + r)**t_ret) - b * (((1 + r)**(t_ret + 1) - (1 + r)) / r)
    nw_exp.append(val)

P_w_exponential = P0 * ((1 + r)**w_exponential) + c * (((1 + r)**w_exponential - 1) / r)

# =========================================================================
# 3. RENDERING PLOT 1: True Linear Intersection
# =========================================================================
fig1, ax1 = plt.subplots(figsize=(6.5, 3.5), layout='tight')

# Slice the linear arrays exactly at the crossover point for two distinct colored lines
split_idx_lin = int(np.floor(w_linear)) + 1
ax1.plot(ages_lin[:split_idx_lin], nw_lin[:split_idx_lin], color=mp_green, linewidth=2.5, label='Linear Accumulation')
ax1.plot(ages_lin[split_idx_lin-1:], nw_lin[split_idx_lin-1:], color=mp_red, linewidth=2.5, label='Linear Depletion')

ax1.plot(age_retire_linear, P_w_linear, marker='o', color=mp_dark, markersize=7, zorder=5)
ax1.annotate(f'Peak $P_w$\nAge {age_retire_linear:.1f}\n${int(P_w_linear):,}', 
             xy=(age_retire_linear, P_w_linear), xytext=(age_retire_linear - 12, P_w_linear - 150000),
             color=mp_dark, weight='bold', ha='center', arrowprops=dict(arrowstyle='->', color=mp_dark, lw=0.8))

ax1.set_title('The Linear Intersection Baseline ($r=0\%$)', color=mp_dark, weight='bold', pad=12)
ax1.set_xlabel('Age (Years)', color=mp_dark)
ax1.set_ylabel('Net Worth ($)', color=mp_dark)
ax1.set_xlim(A_start, A_end)
ax1.set_ylim(0, 1010000)
ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax1.grid(True)
ax1.legend(loc='lower left', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0')

for spine in ['top', 'right']: ax1.spines[spine].set_visible(False)
for spine in ['left', 'bottom']: ax1.spines[spine].set_color('#cbd5e1')
plt.savefig('./visual-assets/linear_plot.pdf', format='pdf', bbox_inches='tight')
plt.close()

# =========================================================================
# 4. RENDERING PLOT 2: True Exponential Curves
# =========================================================================
fig2, ax2 = plt.subplots(figsize=(6.5, 3.5), layout='tight')

split_idx_exp = int(np.floor(w_exponential)) + 1
ax2.plot(ages_exp[:split_idx_exp], nw_exp[:split_idx_exp], color=mp_green, linewidth=2.5, label='Exponential Accumulation')
ax2.plot(ages_exp[split_idx_exp-1:], nw_exp[split_idx_exp-1:], color=mp_red, linewidth=2.5, label='Exponential Depletion')

ax2.plot(age_retire_exp, P_w_exponential, marker='o', color=mp_dark, markersize=7, zorder=5)
ax2.annotate(f'Peak $P_w$\nAge {age_retire_exp:.1f}\n${int(P_w_exponential):,}', 
             xy=(age_retire_exp, P_w_exponential), xytext=(age_retire_exp - 12, P_w_exponential - 200000),
             color=mp_dark, weight='bold', ha='center', arrowprops=dict(arrowstyle='->', color=mp_dark, lw=0.8))

ax2.set_title(f'The Exponential Compounding Trajectory ($r={int(r*100)}\\%$)', color=mp_dark, weight='bold', pad=12)
ax2.set_xlabel('Age (Years)', color=mp_dark)
ax2.set_ylabel('Net Worth ($)', color=mp_dark)
ax2.set_xlim(A_start, A_end)
ax2.set_ylim(0, 1010000)
ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax2.grid(True)
ax2.legend(loc='lower left', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0')

for spine in ['top', 'right']: ax2.spines[spine].set_visible(False)
for spine in ['left', 'bottom']: ax2.spines[spine].set_color('#cbd5e1')
plt.savefig('./visual-assets/exponential_plot.pdf', format='pdf', bbox_inches='tight')
plt.close()

print(f"Success! Linear w solved as {w_linear:.2f} years. Exponential w solved as {w_exponential:.2f} years.")
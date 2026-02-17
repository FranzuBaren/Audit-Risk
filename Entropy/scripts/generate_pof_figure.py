"""
Generate the PoF integration figure for Post 4.
Shows how entropy anomalies feed into the Bayesian Probability of Failure
framework from Post 3, making the arc feel like genuine accumulation.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

np.random.seed(42)
plt.rcParams.update({
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'figure.dpi': 120
})

N_DAYS = 300
FAILURE_START = 150

# --- Simulate two evidence streams ---

# Stream 1: Traditional operational telemetry (error rate from sampling)
# This is what the Bayesian PoF from Post 3 would use alone
base_error_rate = 0.02  # 2% baseline
telemetry_errors = np.zeros(N_DAYS)
for d in range(N_DAYS):
    if d < FAILURE_START:
        telemetry_errors[d] = np.random.binomial(50, base_error_rate) / 50
    else:
        # True rate drifts up slowly (the failure is subtle in per-record checks)
        true_rate = base_error_rate + 0.008 * min((d - FAILURE_START) / 100, 1.0)
        telemetry_errors[d] = np.random.binomial(50, true_rate) / 50

# Stream 2: Entropy delta signal (from our simulation)
# Pre-failure: ~0, post-failure: drops to ~ -0.005 with noise
entropy_signal = np.zeros(N_DAYS)
for d in range(N_DAYS):
    if d < FAILURE_START:
        entropy_signal[d] = np.random.normal(0, 0.0003)
    else:
        entropy_signal[d] = np.random.normal(-0.005, 0.002)

# --- Bayesian PoF: two versions ---

# Version A: PoF using ONLY traditional telemetry (Post 3 approach)
# Beta-Binomial: prior Beta(2, 98) = 2% baseline
alpha_a, beta_a = 2.0, 98.0
pof_telemetry_only = []
for d in range(N_DAYS):
    n_obs = 50  # daily sample
    k_fail = int(telemetry_errors[d] * n_obs)
    alpha_a += k_fail
    beta_a += (n_obs - k_fail)
    # Decay toward prior to maintain responsiveness (exponential forgetting)
    decay = 0.98
    alpha_a = decay * alpha_a + (1 - decay) * 2.0
    beta_a = decay * beta_a + (1 - decay) * 98.0
    pof_telemetry_only.append(alpha_a / (alpha_a + beta_a))

# Version B: PoF using telemetry + entropy signal
alpha_b, beta_b = 2.0, 98.0
pof_combined = []
for d in range(N_DAYS):
    n_obs = 50
    k_fail = int(telemetry_errors[d] * n_obs)
    alpha_b += k_fail
    beta_b += (n_obs - k_fail)
    
    # Entropy signal as additional evidence:
    # When entropy delta is significantly negative, it's equivalent to
    # observing additional "failures" in a virtual sample
    if entropy_signal[d] < -0.001:  # Below noise floor
        # Convert entropy magnitude to pseudo-observations
        # Stronger entropy signal = more pseudo-failures
        magnitude = abs(entropy_signal[d]) / 0.005  # Normalized to expected failure signal
        pseudo_failures = min(magnitude * 8, 15)  # Cap at 15 pseudo-observations
        pseudo_total = 20
        alpha_b += pseudo_failures
        beta_b += (pseudo_total - pseudo_failures)
    
    decay = 0.98
    alpha_b = decay * alpha_b + (1 - decay) * 2.0
    beta_b = decay * beta_b + (1 - decay) * 98.0
    pof_combined.append(alpha_b / (alpha_b + beta_b))

pof_telemetry_only = np.array(pof_telemetry_only)
pof_combined = np.array(pof_combined)
days = np.arange(N_DAYS)

# --- Find detection days (when PoF crosses 5% threshold) ---
threshold_pof = 0.05

det_telemetry = None
for d in range(FAILURE_START, N_DAYS):
    if pof_telemetry_only[d] > threshold_pof:
        det_telemetry = d
        break

det_combined = None
for d in range(FAILURE_START, N_DAYS):
    if pof_combined[d] > threshold_pof:
        det_combined = d
        break

# --- Plot ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True,
                                gridspec_kw={'height_ratios': [1, 2]})

# Top: Entropy signal (context)
ax1.plot(days, entropy_signal, color='#434343', alpha=0.4, linewidth=0.6)
smooth = np.convolve(entropy_signal, np.ones(14)/14, mode='same')
ax1.plot(days[7:-7], smooth[7:-7], color='#2E86AB', linewidth=1.8, label='Entropy ΔH (14-day avg)')
ax1.axhline(0, color='gray', linestyle='-', alpha=0.3)
ax1.axhline(-0.001, color='#E84855', linestyle=':', alpha=0.4, label='Noise floor')
ax1.axvspan(FAILURE_START, N_DAYS, alpha=0.06, color='red')
ax1.axvline(FAILURE_START, color='red', linestyle='--', alpha=0.4, linewidth=0.8)
ax1.set_ylabel('ΔH (bits)')
ax1.set_title('Evidence Stream: Entropy Signal', fontweight='bold')
ax1.legend(fontsize=8, loc='lower left')
ax1.grid(True, alpha=0.12)

# Bottom: Two PoF curves
ax2.plot(days, pof_telemetry_only * 100, color='#999999', linewidth=2, 
         label='PoF with telemetry only (Post 3)', linestyle='--')
ax2.plot(days, pof_combined * 100, color='#E84855', linewidth=2.2,
         label='PoF with telemetry + entropy')
ax2.axhline(threshold_pof * 100, color='#FFC107', linestyle='-', alpha=0.6, linewidth=1.2,
            label=f'Investigation threshold ({threshold_pof:.0%})')
ax2.axvspan(FAILURE_START, N_DAYS, alpha=0.06, color='red')
ax2.axvline(FAILURE_START, color='red', linestyle='--', alpha=0.4, linewidth=0.8)

# Annotate detection days
if det_combined:
    ax2.axvline(det_combined, color='#E84855', linestyle='-', alpha=0.4, linewidth=1)
    ax2.annotate(f'Entropy-enhanced\nalert: Day {det_combined}',
                 xy=(det_combined, threshold_pof * 100),
                 xytext=(det_combined + 12, threshold_pof * 100 + 3),
                 fontsize=9, color='#E84855', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#E84855', lw=1.2))

if det_telemetry:
    ax2.axvline(det_telemetry, color='#999999', linestyle='-', alpha=0.3, linewidth=1)
    ax2.annotate(f'Telemetry-only\nalert: Day {det_telemetry}',
                 xy=(det_telemetry, threshold_pof * 100),
                 xytext=(det_telemetry + 12, threshold_pof * 100 - 3.5),
                 fontsize=9, color='#666666',
                 arrowprops=dict(arrowstyle='->', color='#999999', lw=1.2))

if det_combined and det_telemetry:
    gap = det_telemetry - det_combined
    mid = (det_combined + det_telemetry) / 2
    y_arrow = threshold_pof * 100 - 1.5
    ax2.annotate('', xy=(det_telemetry, y_arrow), xytext=(det_combined, y_arrow),
                 arrowprops=dict(arrowstyle='<->', color='#2E86AB', lw=1.5))
    ax2.text(mid, y_arrow - 1.2, f'{gap}-day\nadvantage', ha='center', fontsize=9,
             color='#2E86AB', fontweight='bold')

ax2.set_xlabel('Day')
ax2.set_ylabel('Probability of Failure (%)')
ax2.set_title('Bayesian PoF: How Entropy Evidence Accelerates Detection', fontweight='bold')
ax2.legend(fontsize=9, loc='upper left')
ax2.set_ylim(0, max(pof_combined.max() * 100 + 5, 15))
ax2.grid(True, alpha=0.12)

plt.tight_layout()
plt.savefig('entropy_pof_integration.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n--- PoF Integration Results ---")
print(f"Failure onset:                    Day {FAILURE_START}")
if det_combined:
    print(f"PoF alert (telemetry + entropy):  Day {det_combined} ({det_combined - FAILURE_START} days after onset)")
if det_telemetry:
    print(f"PoF alert (telemetry only):       Day {det_telemetry} ({det_telemetry - FAILURE_START} days after onset)")
if det_combined and det_telemetry:
    print(f"Advantage from entropy evidence:  {det_telemetry - det_combined} days")
elif det_combined and not det_telemetry:
    print(f"Telemetry-only PoF never crossed threshold in {N_DAYS} days")

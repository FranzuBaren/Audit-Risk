"""
Stochastic Governance Simulation: From Checklists to Bayesian Priors

This simulation demonstrates the difference between:
1. Static checklist audits (quarterly snapshots)
2. Continuous Bayesian Probability of Failure (PoF) monitoring

Scenario: Electronic Batch Record (EBR) Data Integrity monitoring in a pharmaceutical enterprise
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

class ProcessState:
    """Simulates the true underlying state of a control process"""
    
    def __init__(self, base_failure_rate=0.02):
        self.base_failure_rate = base_failure_rate
        self.current_failure_rate = base_failure_rate
        self.time = 0
        
    def evolve(self, stress_period=False):
        """Simulate how the true failure rate evolves over time"""
        self.time += 1
        
        # Add random walk
        drift = np.random.normal(0, 0.001)
        
        # Add stress event (simulates staffing shortage, system issues, etc.)
        if stress_period:
            stress = 0.002  # Gradual deterioration
        else:
            stress = 0
            
        # Mean reversion (systems naturally stabilize somewhat)
        mean_reversion = -0.05 * (self.current_failure_rate - self.base_failure_rate)
        
        self.current_failure_rate = np.clip(
            self.current_failure_rate + drift + stress + mean_reversion,
            0.001, 0.20
        )
        
        return self.current_failure_rate
    
    def generate_observations(self, n_batches):
        """Generate observed failures for n_batches"""
        failures = np.random.binomial(n_batches, self.current_failure_rate)
        return failures, n_batches


class BayesianAuditor:
    """Implements continuous Bayesian updating of Probability of Failure"""
    
    def __init__(self, prior_alpha=2, prior_beta=98):
        """
        Initialize with Beta prior: Beta(alpha, beta)
        Default: Beta(2, 98) implies prior belief of ~2% failure rate
        """
        self.alpha = prior_alpha
        self.beta = prior_beta
        self.history = []
        
    def get_pof(self):
        """Get current Probability of Failure (mean of Beta distribution)"""
        return self.alpha / (self.alpha + self.beta)
    
    def get_credible_interval(self, confidence=0.95):
        """Get Bayesian credible interval"""
        lower = stats.beta.ppf((1 - confidence) / 2, self.alpha, self.beta)
        upper = stats.beta.ppf(1 - (1 - confidence) / 2, self.alpha, self.beta)
        return lower, upper
    
    def update(self, failures, total):
        """Bayesian update: posterior becomes new prior"""
        # Beta-Binomial conjugate update
        self.alpha += failures
        self.beta += (total - failures)
        
        # Record history
        self.history.append({
            'pof': self.get_pof(),
            'alpha': self.alpha,
            'beta': self.beta,
            'failures': failures,
            'total': total
        })
        
        return self.get_pof()
    
    def get_uncertainty(self):
        """Get standard deviation of current belief"""
        variance = (self.alpha * self.beta) / ((self.alpha + self.beta)**2 * (self.alpha + self.beta + 1))
        return np.sqrt(variance)


class ChecklistAuditor:
    """Implements traditional quarterly snapshot audits"""
    
    def __init__(self):
        self.audit_results = []
        
    def audit(self, failures, total, day):
        """Perform a snapshot audit"""
        failure_rate = failures / total if total > 0 else 0
        
        # Traditional traffic light classification
        if failure_rate < 0.03:
            status = "Green"
        elif failure_rate < 0.06:
            status = "Amber"
        else:
            status = "Red"
            
        self.audit_results.append({
            'day': day,
            'failure_rate': failure_rate,
            'status': status,
            'failures': failures,
            'total': total
        })
        
        return status, failure_rate


def run_simulation(days=365, daily_batches=50, stress_start=150, stress_end=250):
    """
    Run full simulation comparing Bayesian vs Checklist approaches
    
    Parameters:
    - days: simulation duration
    - daily_batches: number of batches processed per day
    - stress_start/end: period where underlying failure rate increases
    """
    
    # Initialize
    process = ProcessState(base_failure_rate=0.02)
    bayesian = BayesianAuditor(prior_alpha=2, prior_beta=98)
    checklist = ChecklistAuditor()
    
    # Data collection
    true_failure_rates = []
    bayesian_pofs = []
    bayesian_lower = []
    bayesian_upper = []
    days_list = []
    
    # Quarterly audit schedule (days 90, 180, 270, 360)
    audit_days = [90, 180, 270, 360]
    audit_failures = {day: 0 for day in audit_days}
    audit_totals = {day: 0 for day in audit_days}
    
    # Run simulation
    for day in range(days):
        # Determine if in stress period
        stress_period = stress_start <= day <= stress_end
        
        # Evolve true process state
        true_rate = process.evolve(stress_period=stress_period)
        true_failure_rates.append(true_rate)
        
        # Generate daily observations
        failures, total = process.generate_observations(daily_batches)
        
        # Bayesian auditor: updates EVERY day
        pof = bayesian.update(failures, total)
        lower, upper = bayesian.get_credible_interval()
        
        bayesian_pofs.append(pof)
        bayesian_lower.append(lower)
        bayesian_upper.append(upper)
        days_list.append(day)
        
        # Checklist auditor: accumulates data for quarterly audits
        for audit_day in audit_days:
            if day < audit_day and day >= (audit_day - 90):
                audit_failures[audit_day] += failures
                audit_totals[audit_day] += total
        
        # Execute quarterly audits
        if day in audit_days:
            checklist.audit(audit_failures[day], audit_totals[day], day)
    
    return {
        'days': days_list,
        'true_rates': true_failure_rates,
        'bayesian_pofs': bayesian_pofs,
        'bayesian_lower': bayesian_lower,
        'bayesian_upper': bayesian_upper,
        'checklist_results': checklist.audit_results,
        'stress_start': stress_start,
        'stress_end': stress_end
    }


def plot_simulation_results(results):
    """Create visualization comparing both approaches"""
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Top panel: Bayesian continuous monitoring
    ax1 = axes[0]
    
    # Plot true failure rate
    ax1.plot(results['days'], results['true_rates'], 
             'k-', linewidth=2, label='True Failure Rate', alpha=0.7)
    
    # Plot Bayesian PoF with credible interval
    ax1.plot(results['days'], results['bayesian_pofs'], 
             'b-', linewidth=2, label='Bayesian PoF (Updated Daily)')
    ax1.fill_between(results['days'], 
                      results['bayesian_lower'], 
                      results['bayesian_upper'],
                      color='blue', alpha=0.2, label='95% Credible Interval')
    
    # Highlight stress period
    ax1.axvspan(results['stress_start'], results['stress_end'], 
                alpha=0.1, color='red', label='Stress Period')
    
    # Add threshold lines
    ax1.axhline(y=0.03, color='orange', linestyle='--', alpha=0.5, label='Warning Threshold (3%)')
    ax1.axhline(y=0.06, color='red', linestyle='--', alpha=0.5, label='Critical Threshold (6%)')
    
    # Calculate when Bayesian system would have triggered alert
    pof_array = np.array(results['bayesian_pofs'])
    first_warning = np.where(pof_array > 0.03)[0]
    if len(first_warning) > 0:
        warning_day = first_warning[0]
        ax1.axvline(x=warning_day, color='orange', linestyle=':', linewidth=2, 
                   label=f'Bayesian Alert Day {warning_day}')
    
    ax1.set_xlabel('Day', fontsize=11)
    ax1.set_ylabel('Probability of Failure', fontsize=11)
    ax1.set_title('Continuous Bayesian Monitoring: Real-Time Risk Tracking', 
                  fontsize=13, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 0.12)
    
    # Bottom panel: Quarterly checklist audits
    ax2 = axes[1]
    
    # Plot true failure rate
    ax2.plot(results['days'], results['true_rates'], 
             'k-', linewidth=2, label='True Failure Rate', alpha=0.7)
    
    # Plot quarterly audit results
    audit_days = [r['day'] for r in results['checklist_results']]
    audit_rates = [r['failure_rate'] for r in results['checklist_results']]
    audit_status = [r['status'] for r in results['checklist_results']]
    
    # Color code by status
    colors = {'Green': 'green', 'Amber': 'orange', 'Red': 'red'}
    for day, rate, status in zip(audit_days, audit_rates, audit_status):
        ax2.scatter(day, rate, s=200, c=colors[status], marker='s', 
                   edgecolors='black', linewidth=2, zorder=5,
                   label=f'Q Audit: {status}' if day == audit_days[0] or status != audit_status[audit_days.index(day)-1] else '')
    
    # Connect audit points
    ax2.plot(audit_days, audit_rates, 'gray', linestyle='--', 
             linewidth=1.5, alpha=0.5, zorder=3)
    
    # Highlight stress period
    ax2.axvspan(results['stress_start'], results['stress_end'], 
                alpha=0.1, color='red', label='Stress Period')
    
    # Add threshold lines
    ax2.axhline(y=0.03, color='orange', linestyle='--', alpha=0.5, label='Warning Threshold')
    ax2.axhline(y=0.06, color='red', linestyle='--', alpha=0.5, label='Critical Threshold')
    
    ax2.set_xlabel('Day', fontsize=11)
    ax2.set_ylabel('Failure Rate (Snapshot)', fontsize=11)
    ax2.set_title('Traditional Quarterly Audits: Delayed Detection', 
                  fontsize=13, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 0.12)
    
    plt.tight_layout()
    plt.savefig('/home/claude/bayesian_vs_checklist.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'bayesian_vs_checklist.png'")
    
    return fig


def generate_summary_metrics(results):
    """Calculate key performance metrics comparing both approaches"""
    
    true_rates = np.array(results['true_rates'])
    bayesian_pofs = np.array(results['bayesian_pofs'])
    
    # Calculate detection lag (days until alert after stress begins)
    stress_start = results['stress_start']
    first_warning = np.where(bayesian_pofs > 0.03)[0]
    
    if len(first_warning) > 0:
        bayesian_detection_lag = first_warning[0] - stress_start
    else:
        bayesian_detection_lag = None
    
    # Checklist detection
    checklist_alerts = [r for r in results['checklist_results'] 
                        if r['day'] >= stress_start and r['status'] in ['Amber', 'Red']]
    
    if checklist_alerts:
        checklist_detection_lag = checklist_alerts[0]['day'] - stress_start
    else:
        checklist_detection_lag = None
    
    # Calculate RMSE (tracking accuracy)
    bayesian_rmse = np.sqrt(np.mean((bayesian_pofs - true_rates)**2))
    
    # For checklist, interpolate between audit points
    checklist_days = [r['day'] for r in results['checklist_results']]
    checklist_rates = [r['failure_rate'] for r in results['checklist_results']]
    checklist_interpolated = np.interp(results['days'], checklist_days, checklist_rates)
    checklist_rmse = np.sqrt(np.mean((checklist_interpolated - true_rates)**2))
    
    summary = f"""
    {'='*70}
    SIMULATION SUMMARY: Bayesian vs Checklist Audit Performance
    {'='*70}
    
    Scenario: {len(results['days'])} days of EBR monitoring
              Stress period: Days {stress_start}-{results['stress_end']}
              True baseline failure rate: 2%
    
    DETECTION SPEED:
    ----------------
    Bayesian (continuous):  Detected issue on Day {first_warning[0] if len(first_warning) > 0 else 'N/A'}
                           → Alert lag: {bayesian_detection_lag if bayesian_detection_lag else 'N/A'} days after stress began
    
    Checklist (quarterly):  Detected issue on Day {checklist_alerts[0]['day'] if checklist_alerts else 'N/A'}
                           → Alert lag: {checklist_detection_lag if checklist_detection_lag else 'N/A'} days after stress began
    
    Detection advantage:    Bayesian detected {abs(checklist_detection_lag - bayesian_detection_lag) if (checklist_detection_lag and bayesian_detection_lag) else 'N/A'} days earlier
    
    TRACKING ACCURACY (RMSE vs True Failure Rate):
    ----------------------------------------------
    Bayesian:    {bayesian_rmse:.4f}
    Checklist:   {checklist_rmse:.4f}
    
    Improvement: {((checklist_rmse - bayesian_rmse) / checklist_rmse * 100):.1f}% more accurate tracking
    
    CREDIBLE INTERVAL COVERAGE:
    ---------------------------
    """
    
    # Calculate how often true rate falls within Bayesian credible interval
    lower = np.array(results['bayesian_lower'])
    upper = np.array(results['bayesian_upper'])
    coverage = np.mean((true_rates >= lower) & (true_rates <= upper))
    
    summary += f"    True rate within 95% interval: {coverage*100:.1f}% of days\n"
    summary += f"    (Target: 95% for well-calibrated Bayesian model)\n"
    summary += f"\n    {'='*70}\n"
    
    print(summary)
    
    return {
        'bayesian_detection_lag': bayesian_detection_lag,
        'checklist_detection_lag': checklist_detection_lag,
        'bayesian_rmse': bayesian_rmse,
        'checklist_rmse': checklist_rmse,
        'coverage': coverage
    }


def demonstrate_prior_sensitivity():
    """Show how different priors affect initial beliefs"""
    
    print("\n" + "="*70)
    print("PRIOR SENSITIVITY ANALYSIS")
    print("="*70)
    print("\nHow do different starting beliefs (priors) affect initial PoF?\n")
    
    priors = [
        ("Optimistic (1% expected)", 1, 99),
        ("Neutral (2% expected)", 2, 98),
        ("Pessimistic (5% expected)", 5, 95),
        ("Highly Uncertain", 1, 1)
    ]
    
    # Simulate receiving strong evidence of 5% failure rate
    failures_observed = 50
    total_observed = 1000
    actual_rate = failures_observed / total_observed
    
    print(f"Observation: {failures_observed} failures in {total_observed} batches ({actual_rate:.1%})\n")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, (name, alpha, beta) in enumerate(priors):
        auditor = BayesianAuditor(prior_alpha=alpha, prior_beta=beta)
        
        prior_mean = auditor.get_pof()
        prior_lower, prior_upper = auditor.get_credible_interval()
        
        # Update with evidence
        auditor.update(failures_observed, total_observed)
        
        posterior_mean = auditor.get_pof()
        posterior_lower, posterior_upper = auditor.get_credible_interval()
        
        print(f"{name}:")
        print(f"  Prior:     {prior_mean:.3f} [{prior_lower:.3f}, {prior_upper:.3f}]")
        print(f"  Posterior: {posterior_mean:.3f} [{posterior_lower:.3f}, {posterior_upper:.3f}]")
        print(f"  Shift:     {abs(posterior_mean - prior_mean):.3f}\n")
        
        # Plot distributions
        ax = axes[idx]
        x = np.linspace(0, 0.15, 1000)
        
        # Prior
        prior_dist = stats.beta.pdf(x, alpha, beta)
        ax.plot(x, prior_dist, 'b--', linewidth=2, label='Prior Belief')
        ax.fill_between(x, prior_dist, alpha=0.2, color='blue')
        
        # Posterior
        posterior_dist = stats.beta.pdf(x, alpha + failures_observed, beta + (total_observed - failures_observed))
        ax.plot(x, posterior_dist, 'r-', linewidth=2, label='Posterior Belief')
        ax.fill_between(x, posterior_dist, alpha=0.2, color='red')
        
        # True value
        ax.axvline(actual_rate, color='black', linestyle=':', linewidth=2, label='Observed Rate')
        
        ax.set_title(name, fontweight='bold')
        ax.set_xlabel('Failure Rate')
        ax.set_ylabel('Probability Density')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/claude/prior_sensitivity.png', dpi=300, bbox_inches='tight')
    print("Prior sensitivity plot saved as 'prior_sensitivity.png'\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STOCHASTIC GOVERNANCE SIMULATION")
    print("From Checklists to Bayesian Priors")
    print("="*70)
    
    # Run main simulation
    print("\nRunning 365-day simulation...")
    results = run_simulation(
        days=365,
        daily_batches=50,
        stress_start=150,
        stress_end=250
    )
    
    # Generate visualizations
    plot_simulation_results(results)
    
    # Calculate metrics
    metrics = generate_summary_metrics(results)
    
    # Demonstrate prior sensitivity
    demonstrate_prior_sensitivity()
    
    print("\nSimulation complete. Check generated PNG files for visualizations.")
    print("="*70)

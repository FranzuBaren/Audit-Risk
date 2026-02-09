# Mathematical Foundation: Bayesian Governance Framework

## Table of Contents

1. [Overview](#overview)
2. [The Beta-Binomial Conjugate System](#the-beta-binomial-conjugate-system)
3. [Why Conjugacy Matters](#why-conjugacy-matters)
4. [Bayesian Updating Mechanics](#bayesian-updating-mechanics)
5. [Prior Selection and Calibration](#prior-selection-and-calibration)
6. [Credible Intervals vs Confidence Intervals](#credible-intervals-vs-confidence-intervals)
7. [Information Theory Perspective](#information-theory-perspective)
8. [Convergence Properties](#convergence-properties)
9. [Extension to Hierarchical Models](#extension-to-hierarchical-models)
10. [Limitations and Assumptions](#limitations-and-assumptions)

---

## Overview

The Bayesian governance framework uses **Beta-Binomial conjugacy** as its mathematical foundation. This section provides the rigorous statistical theory underlying the simulation, suitable for readers with background in probability theory and statistical inference.

### Why Bayesian Methods?

Traditional frequentist audit asks: "Given a fixed but unknown failure rate θ, what is the probability of observing k failures in n trials?"

Bayesian audit inverts the question: "Given that we observed k failures in n trials, what is the probability distribution over possible values of θ?"

This inversion—from P(data|θ) to P(θ|data)—is achieved via **Bayes' Theorem**.

---

## The Beta-Binomial Conjugate System

### The Setup

We model audit observations as a **Binomial process**:

**Data Model (Likelihood)**:
```
k ~ Binomial(n, θ)
```
where:
- n = number of batches audited
- k = number of failures observed
- θ = true (unknown) failure rate

The probability mass function is:
```
P(k | θ, n) = C(n,k) θ^k (1-θ)^(n-k)
```

### The Prior

We place a **Beta distribution** prior on θ:

```
θ ~ Beta(α, β)
```

The probability density function is:
```
p(θ | α, β) = [Γ(α+β) / (Γ(α)Γ(β))] θ^(α-1) (1-θ)^(β-1)
```

where Γ is the gamma function.

**Key Properties of Beta Distribution**:

1. **Support**: θ ∈ [0, 1] (perfect for probabilities/rates)

2. **Mean**: E[θ] = α/(α+β)

3. **Variance**: Var(θ) = αβ / [(α+β)²(α+β+1)]

4. **Mode** (for α,β > 1): (α-1)/(α+β-2)

5. **Flexibility**: Different (α,β) values produce vastly different shapes:
   - α=β=1: Uniform (uninformative)
   - α=β>>1: Concentrated near 0.5
   - α>>β: Concentrated near 1
   - α<<β: Concentrated near 0

### The Posterior

The beauty of conjugacy: **if the prior is Beta and the likelihood is Binomial, the posterior is also Beta**.

**Bayes' Theorem**:
```
p(θ | k, n, α, β) ∝ p(k | θ, n) × p(θ | α, β)
```

Substituting:
```
p(θ | k, n, α, β) ∝ θ^k (1-θ)^(n-k) × θ^(α-1) (1-θ)^(β-1)
                  ∝ θ^(k+α-1) (1-θ)^(n-k+β-1)
```

This is the kernel of a Beta distribution with updated parameters:

```
θ | k, n, α, β ~ Beta(α + k, β + n - k)
```

**The Posterior Update Rule**:
```
α_new = α_old + k
β_new = β_old + (n - k)
```

This is **analytical, exact, and closed-form**—no numerical integration required.

---

## Why Conjugacy Matters

### Computational Efficiency

Without conjugacy, computing the posterior requires numerical integration:

```
p(θ | data) = p(data | θ) p(θ) / ∫ p(data | θ') p(θ') dθ'
```

The denominator (the **marginal likelihood** or **evidence**) is often intractable, requiring:
- MCMC sampling (Metropolis-Hastings, Gibbs, HMC)
- Variational inference
- Grid approximation

With Beta-Binomial conjugacy, the posterior is **instant**.

### Real-Time Governance

For enterprise governance, we need to update beliefs **continuously** as data streams arrive. If each update required MCMC sampling:
- Minutes/hours of computation per update
- Infrastructure complexity (distributed MCMC)
- Convergence diagnostics overhead

Beta-Binomial conjugacy enables **millisecond updates**, making real-time monitoring feasible.

### Sequential Learning

Conjugacy enables elegant sequential updating:

```
Day 1: θ ~ Beta(α₀, β₀)
       Observe (k₁, n₁)
       → θ | data₁ ~ Beta(α₀ + k₁, β₀ + n₁ - k₁)

Day 2: Use previous posterior as new prior
       θ ~ Beta(α₀ + k₁, β₀ + n₁ - k₁)
       Observe (k₂, n₂)
       → θ | data₁,₂ ~ Beta(α₀ + k₁ + k₂, β₀ + n₁ + n₂ - k₁ - k₂)

...and so on
```

**Key Insight**: The order of observations doesn't matter. The posterior after seeing data₁ then data₂ is identical to the posterior after seeing data₂ then data₁. This is the **likelihood principle** in action.

---

## Bayesian Updating Mechanics

### Prior as Pseudo-Observations

The prior Beta(α, β) can be interpreted as having already observed:
- α "pseudo-failures"
- β "pseudo-successes"

Total "pseudo-sample size": n₀ = α + β

**Prior strength**: How much weight does the prior carry relative to new data?

If n₀ is large (e.g., α=200, β=9800, so n₀=10,000), the prior is **strong** and requires substantial new evidence to shift beliefs.

If n₀ is small (e.g., α=2, β=98, so n₀=100), the prior is **weak** and updates quickly with new data.

### Posterior Mean as Weighted Average

The posterior mean can be written as a **weighted average** of prior mean and observed rate:

```
E[θ | data] = (α + k) / (α + β + n)
            = [(α + β) / (α + β + n)] × [α/(α+β)] + [n / (α + β + n)] × [k/n]
            = w_prior × θ_prior + w_data × θ_observed
```

where:
- w_prior = n₀ / (n₀ + n)
- w_data = n / (n₀ + n)
- w_prior + w_data = 1

**Interpretation**: The posterior belief is a compromise between:
1. What you believed before (prior mean α/(α+β))
2. What you just observed (sample rate k/n)

The weights depend on **relative information content**:
- Large n₀, small n → prior dominates
- Small n₀, large n → data dominates
- n₀ ≈ n → balanced compromise

### Variance Reduction (Uncertainty Collapse)

As data accumulates, posterior variance shrinks:

```
Var(θ | data) = (α + k)(β + n - k) / [(α + β + n)²(α + β + n + 1)]
```

The denominator grows with (α + β + n)³, so variance decreases as O(1/n²).

**Key Properties**:

1. **Uncertainty always decreases**: More data → tighter credible intervals
2. **Asymptotic convergence**: As n → ∞, posterior concentrates at true θ
3. **Rate of convergence**: Depends on prior strength n₀

### Example Numerical Update

**Prior**: Beta(2, 98) implies:
- Prior mean: 2/100 = 0.02 (2% failure rate)
- Prior variance: (2×98)/(100²×101) ≈ 0.000192
- Prior std dev: 0.0139 (±1.4%)

**Observation**: 5 failures in 50 batches (10% observed rate)

**Posterior**: Beta(2+5, 98+50-5) = Beta(7, 143)
- Posterior mean: 7/150 = 0.0467 (4.67% failure rate)
- Posterior variance: (7×143)/(150²×151) ≈ 0.000295
- Posterior std dev: 0.0172 (±1.7%)

**Analysis**:
- Prior said 2%, data said 10%, posterior compromised at 4.67%
- Weight on prior: 100/150 = 67%
- Weight on data: 50/150 = 33%
- Even strong evidence (10%) only shifted belief modestly due to prior weight

---

## Prior Selection and Calibration

### Method 1: Historical Data

If you have previous audit results:
```
Last year: 2 failures in 100 batches
→ Use Beta(2, 98) as this year's prior
```

This is the **empirical Bayes** approach—use past data to inform the prior.

### Method 2: Expert Elicitation

Ask domain experts:
1. "What failure rate do you expect?" → Sets α/(α+β)
2. "How confident are you?" → Sets α+β

Example:
- Expert: "I expect 2%, and I'm as confident as if I'd seen 500 samples"
- → α/(α+β) = 0.02 and α+β = 500
- → α = 10, β = 490

### Method 3: Objective Priors

Several "uninformative" priors exist:

**Uniform Prior**: Beta(1, 1)
- Every value of θ equally likely
- Posterior mean = k/n (same as frequentist MLE after first observation)

**Jeffreys Prior**: Beta(0.5, 0.5)
- Invariant under reparameterization
- Represents "maximum ignorance" in information-theoretic sense

**Haldane Prior**: Beta(0, 0) [improper]
- Undefined as a proper density, but posterior is Beta(k, n-k)
- Extremely non-informative

### Prior Predictive Checks

To validate your prior, simulate data from it and ask: "Does this match my beliefs?"

**Prior Predictive Distribution**:
```
P(k | n, α, β) = ∫ P(k | n, θ) P(θ | α, β) dθ
               = Beta-Binomial(n, α, β)
```

This is the distribution of failures you'd expect **before seeing any data**.

For Beta(2, 98):
```
E[k | n=50] = n × α/(α+β) = 50 × 0.02 = 1 failure
Var[k | n=50] = ...calculation... ≈ 1.02
```

So we'd expect 1±1 failures in 50 batches. If this seems unreasonable (e.g., you've never seen fewer than 5 failures in 50 batches), your prior is miscalibrated.

### Posterior Predictive Checks

After updating, check if the posterior generates plausible future data:

**Posterior Predictive**:
```
P(k_new | n_new, data_old) = ∫ P(k_new | n_new, θ) P(θ | data_old) dθ
```

This is how you validate model calibration (see next section).

---

## Credible Intervals vs Confidence Intervals

### Frequentist Confidence Interval

"If we repeat this experiment many times, 95% of the intervals constructed this way will contain the true θ."

**Critical point**: θ is fixed (though unknown). The interval is random (varies across hypothetical repeated samples).

You **cannot** say "there's a 95% probability θ is in this interval" under frequentist interpretation.

### Bayesian Credible Interval

"Given the data we observed, there's a 95% probability that θ lies in this interval."

**Critical point**: θ is random (we have a probability distribution over it). The data is fixed (we observed it).

For Beta posterior, the 95% credible interval is:
```
[Beta.ppf(0.025, α_post, β_post), Beta.ppf(0.975, α_post, β_post)]
```

where `Beta.ppf` is the percent point function (inverse CDF).

### Why This Matters for Governance

Governance decisions require statements like:
- "There's a 90% probability the failure rate exceeds 5%"
- "We're 95% confident the true rate is between 3% and 7%"

These are **probability statements about θ**, which are:
- Natural and valid under Bayesian interpretation
- Philosophically problematic under frequentist interpretation

Bayesian credible intervals directly answer the governance question: "How uncertain are we about the true risk?"

### Highest Density Interval (HDI)

The default credible interval is the **equal-tailed interval**: 2.5% below, 2.5% above.

An alternative is the **HDI**: the shortest interval containing 95% of the posterior mass.

For symmetric distributions (like Beta when α ≈ β), these coincide. For skewed distributions, HDI can be more intuitive.

```python
from scipy.optimize import minimize

def hdi_95(alpha, beta):
    """Find 95% Highest Density Interval for Beta distribution"""
    
    def width(lower):
        # Find upper bound such that interval contains 95% mass
        mass = 0.95
        upper = beta.ppf(beta.cdf(lower, alpha, beta) + mass, alpha, beta)
        return upper - lower
    
    result = minimize(width, x0=0.025, bounds=[(0, 1)])
    lower = result.x[0]
    upper = beta.ppf(beta.cdf(lower, alpha, beta) + 0.95, alpha, beta)
    
    return lower, upper
```

---

## Information Theory Perspective

### Kullback-Leibler Divergence

The **information gain** from updating prior to posterior can be quantified via KL divergence:

```
KL(posterior || prior) = ∫ p(θ | data) log[p(θ | data) / p(θ)] dθ
```

For Beta distributions, this has a closed form:

```
KL(Beta(α', β') || Beta(α, β)) = 
    log[Γ(α+β) / Γ(α)Γ(β)] - log[Γ(α'+β') / Γ(α')Γ(β')]
    + (α'-α)ψ(α') + (β'-β)ψ(β') - (α'+β'-α-β)ψ(α'+β')
```

where ψ is the digamma function.

**Interpretation**: KL divergence measures how many "bits" of information the data provided. High KL → data was surprising given prior. Low KL → data confirmed prior beliefs.

### Entropy Reduction

Shannon entropy quantifies uncertainty:

```
H(θ) = -∫ p(θ) log p(θ) dθ
```

For Beta(α, β):
```
H(Beta(α,β)) = log[B(α,β)] - (α-1)ψ(α) - (β-1)ψ(β) + (α+β-2)ψ(α+β)
```

where B is the beta function.

**Learning Dynamics**:
```
Information Gain = H(prior) - H(posterior)
```

As data accumulates, entropy monotonically decreases → uncertainty collapses.

### Fisher Information

The expected information from a single observation is the **Fisher information**:

```
I(θ) = E[(d/dθ log p(k|θ,n))²]
     = n / [θ(1-θ)]
```

**Interpretation**: 
- Maximum at θ=0.5 (most informative when failure rate is 50%)
- Minimum at θ→0 or θ→1 (rare events provide less information per observation)
- Scales linearly with sample size n

This explains why detecting small failure rates (θ≈0.02) requires large samples—each observation carries little information.

---

## Convergence Properties

### Consistency (Bernstein-von Mises Theorem)

Under regularity conditions, as n → ∞:

```
θ | data ~ N(θ_MLE, [nI(θ_MLE)]⁻¹)
```

approximately, where θ_MLE = k/n is the maximum likelihood estimate.

**Implications**:
1. **Asymptotic agreement**: Bayesian and frequentist inferences converge for large n
2. **Prior wash-out**: For n >> n₀, the prior becomes negligible
3. **Normality**: Posterior becomes approximately Gaussian (even if prior is not)

### Rate of Convergence

The posterior mean converges to the true θ at rate O(1/√n):

```
E[θ | data] - θ_true = O(1/√n)
```

The posterior variance shrinks at rate O(1/n):

```
Var(θ | data) = O(1/n)
```

**Practical Consequence**: To halve your uncertainty, you need 4× the data.

### Regret Bounds

In online learning theory, **regret** measures cumulative prediction error:

```
Regret(T) = Σₜ Loss(θ_est,t, θ_true)
```

For Beta-Binomial with log-loss, Bayesian updating achieves **logarithmic regret**:

```
Regret(T) = O(log T)
```

This is **minimax optimal**—no algorithm can do better in the worst case.

---

## Extension to Hierarchical Models

### The Limitation of Single-Level Models

Our Beta-Binomial model assumes all observations come from the **same** θ. But in enterprises:
- Different departments may have different failure rates
- Failure rates may vary over time
- Multiple processes may share some common structure

### Hierarchical Beta-Binomial

For J different processes (e.g., different manufacturing sites):

```
θⱼ ~ Beta(α₀, β₀)         [Process-specific rates]
kⱼ ~ Binomial(nⱼ, θⱼ)     [Observations per process]
```

**Partial pooling**: Information from process j informs beliefs about process j', but they're not identical.

### Hyperpriors

We can go one level deeper and treat (α₀, β₀) as unknown:

```
α₀, β₀ ~ some prior       [Hyperprior]
θⱼ | α₀, β₀ ~ Beta(α₀, β₀)
kⱼ | θⱼ ~ Binomial(nⱼ, θⱼ)
```

Now we're learning **both** the process-specific rates and the distribution of rates across the enterprise.

**Implementation**: Requires MCMC or variational inference (conjugacy is lost at the hyperprior level).

### Time-Varying Models

For non-stationary processes:

```
θₜ | θₜ₋₁ ~ some transition model   [e.g., random walk]
kₜ | θₜ ~ Binomial(nₜ, θₜ)
```

This is a **state-space model** or **dynamic linear model**. 

**Particle Filters** or **Kalman Filters** (if linearized) can handle real-time updating.

---

## Limitations and Assumptions

### 1. Independence Assumption

**Assumption**: Each batch failure is independent.

**Violation**: 
- Autocorrelation (yesterday's failure predicts today's)
- Batch effects (failures cluster within production runs)
- Seasonal patterns

**Consequence**: Credible intervals are too narrow (underestimate uncertainty).

**Fix**: Use time-series models or adjust variance via **overdispersion** parameters.

### 2. Stationarity Assumption

**Assumption**: θ is constant over time.

**Violation**:
- Process improvements (θ decreases over time)
- Degradation (θ increases over time)
- Regime shifts (θ jumps at specific events)

**Consequence**: Posterior doesn't track true θ if it's changing.

**Fix**: Use dynamic models (see Hierarchical Models section) or **discount past data** exponentially:

```python
# Instead of: α_new = α + k
# Use: α_new = λ*α + k    where λ < 1 (e.g., 0.95)
```

This gives more weight to recent data.

### 3. Binomial Model Adequacy

**Assumption**: Failures follow Binomial distribution.

**Violation**:
- Overdispersion (variance > npθ(1-θ))
- Underdispersion (variance < npθ(1-θ))
- Zero-inflation (excess zeros beyond Binomial expectation)

**Consequence**: Model misspecification leads to poor calibration.

**Fix**: Use **Beta-Binomial** model (adds an overdispersion parameter) or **negative binomial** for count data.

### 4. No Covariates

**Assumption**: θ doesn't depend on other variables.

**Violation**:
- Failure rate varies by operator, shift, equipment age, batch size, etc.

**Consequence**: Pooling all data obscures important patterns.

**Fix**: Use **Bayesian regression** (e.g., Beta regression or logistic regression with Bayesian estimation).

### 5. Proper Scoring Rules

For the model to be "honest", predictions should be calibrated:

```
P(true θ ∈ credible interval) ≈ nominal coverage (e.g., 95%)
```

**Check**: Simulate data from the true model, compute credible intervals, measure coverage.

If coverage ≠ 95%, the model is **miscalibrated** (usually due to violations of assumptions 1-4).

---

## Summary: Why Beta-Binomial Works for Governance

| Property | Benefit for Governance |
|----------|------------------------|
| **Conjugacy** | Real-time updates (milliseconds, not hours) |
| **Interpretability** | Pseudo-counts intuition for stakeholders |
| **Exact inference** | No MCMC convergence issues or diagnostics |
| **Uncertainty quantification** | Credible intervals answer "how sure are we?" |
| **Sequential learning** | Yesterday's posterior = today's prior (natural for continuous monitoring) |
| **Asymptotic optimality** | Minimax regret bounds (theoretically sound) |
| **Prior flexibility** | Can encode weak or strong beliefs |

The Beta-Binomial framework is **not** the most sophisticated Bayesian model. But for enterprise governance where:
- Speed matters (real-time dashboards)
- Transparency matters (explain to non-statisticians)
- Reliability matters (no MCMC failures)

...it hits the optimal **simplicity-power tradeoff**.

---

## Further Reading

### Textbooks

- **Gelman et al., "Bayesian Data Analysis"** (3rd ed.) - The canonical reference
- **Kruschke, "Doing Bayesian Data Analysis"** - Accessible intro with strong intuition
- **Robert, "The Bayesian Choice"** - Rigorous decision-theoretic foundation

### Papers

- **Bernardo & Smith (1994)**: Bayesian Theory - Mathematical foundations
- **Consonni & Veronese (2008)**: "Conjugate Priors for Exponential Families" - Generalizations
- **Fong et al. (2020)**: "Bayesian Inference for Generalized Linear Mixed Models" - Extensions

### Software

- **PyMC**: Probabilistic programming in Python (for non-conjugate models)
- **Stan**: HMC-based inference (when conjugacy doesn't apply)
- **Edward/TensorFlow Probability**: Scalable Bayesian deep learning

---

**Next**: See `pharmaceutical_context.md` for how these mathematical concepts apply specifically to GxP-regulated environments.

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

Traditional frequentist audit asks: "Given a fixed but unknown failure rate $\theta$, what is the probability of observing $k$ failures in $n$ trials?"

Bayesian audit inverts the question: "Given that we observed $k$ failures in $n$ trials, what is the probability distribution over possible values of $\theta$?"

This inversion—from $P(\text{data}|\theta)$ to $P(\theta|\text{data})$—is achieved via **Bayes' Theorem**.

---

## The Beta-Binomial Conjugate System

### The Setup

We model audit observations as a **Binomial process**:

**Data Model (Likelihood)**:

$$k \sim \text{Binomial}(n, \theta)$$

where:
- $n$ = number of batches audited
- $k$ = number of failures observed
- $\theta$ = true (unknown) failure rate

The probability mass function is:

$$P(k | \theta, n) = \binom{n}{k} \theta^k (1-\theta)^{n-k}$$

### The Prior

We place a **Beta distribution** prior on $\theta$:

$$\theta \sim \text{Beta}(\alpha, \beta)$$

The probability density function is:

$$p(\theta | \alpha, \beta) = \frac{\Gamma(\alpha+\beta)}{\Gamma(\alpha)\Gamma(\beta)} \theta^{\alpha-1} (1-\theta)^{\beta-1}$$

where $\Gamma$ is the gamma function.

**Key Properties of Beta Distribution**:

1. **Support**: $\theta \in [0, 1]$ (perfect for probabilities/rates)

2. **Mean**: $E[\theta] = \frac{\alpha}{\alpha+\beta}$

3. **Variance**: $\text{Var}(\theta) = \frac{\alpha\beta}{(\alpha+\beta)^2(\alpha+\beta+1)}$

4. **Mode** (for $\alpha,\beta > 1$): $\frac{\alpha-1}{\alpha+\beta-2}$

5. **Flexibility**: Different $(\alpha,\beta)$ values produce vastly different shapes:
   - $\alpha=\beta=1$: Uniform (uninformative)
   - $\alpha=\beta \gg 1$: Concentrated near 0.5
   - $\alpha \gg \beta$: Concentrated near 1
   - $\alpha \ll \beta$: Concentrated near 0

### The Posterior

The beauty of conjugacy: **if the prior is Beta and the likelihood is Binomial, the posterior is also Beta**.

**Bayes' Theorem**:

$$p(\theta | k, n, \alpha, \beta) \propto p(k | \theta, n) \times p(\theta | \alpha, \beta)$$

Substituting:

$$\begin{align}
p(\theta | k, n, \alpha, \beta) &\propto \theta^k (1-\theta)^{n-k} \times \theta^{\alpha-1} (1-\theta)^{\beta-1} \\
&\propto \theta^{k+\alpha-1} (1-\theta)^{n-k+\beta-1}
\end{align}$$

This is the kernel of a Beta distribution with updated parameters:

$$\theta | k, n, \alpha, \beta \sim \text{Beta}(\alpha + k, \beta + n - k)$$

**The Posterior Update Rule**:

$$\begin{align}
\alpha_{\text{new}} &= \alpha_{\text{old}} + k \\
\beta_{\text{new}} &= \beta_{\text{old}} + (n - k)
\end{align}$$

This is **analytical, exact, and closed-form**—no numerical integration required.

---

## Why Conjugacy Matters

### Computational Efficiency

Without conjugacy, computing the posterior requires numerical integration:

$$p(\theta | \text{data}) = \frac{p(\text{data} | \theta) p(\theta)}{\int p(\text{data} | \theta') p(\theta') d\theta'}$$

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

$$\begin{align}
\text{Day 1:} \quad &\theta \sim \text{Beta}(\alpha_0, \beta_0) \\
&\text{Observe } (k_1, n_1) \\
&\theta | \text{data}_1 \sim \text{Beta}(\alpha_0 + k_1, \beta_0 + n_1 - k_1) \\
\\
\text{Day 2:} \quad &\text{Use previous posterior as new prior} \\
&\theta \sim \text{Beta}(\alpha_0 + k_1, \beta_0 + n_1 - k_1) \\
&\text{Observe } (k_2, n_2) \\
&\theta | \text{data}_{1,2} \sim \text{Beta}(\alpha_0 + k_1 + k_2, \beta_0 + n_1 + n_2 - k_1 - k_2)
\end{align}$$

**Key Insight**: The order of observations doesn't matter. The posterior after seeing $\text{data}_1$ then $\text{data}_2$ is identical to the posterior after seeing $\text{data}_2$ then $\text{data}_1$. This is the **likelihood principle** in action.

---

## Bayesian Updating Mechanics

### Prior as Pseudo-Observations

The prior $\text{Beta}(\alpha, \beta)$ can be interpreted as having already observed:
- $\alpha$ "pseudo-failures"
- $\beta$ "pseudo-successes"

Total "pseudo-sample size": $n_0 = \alpha + \beta$

**Prior strength**: How much weight does the prior carry relative to new data?

If $n_0$ is large (e.g., $\alpha=200, \beta=9800$, so $n_0=10{,}000$), the prior is **strong** and requires substantial new evidence to shift beliefs.

If $n_0$ is small (e.g., $\alpha=2, \beta=98$, so $n_0=100$), the prior is **weak** and updates quickly with new data.

### Posterior Mean as Weighted Average

The posterior mean can be written as a **weighted average** of prior mean and observed rate:

$$\begin{align}
E[\theta | \text{data}] &= \frac{\alpha + k}{\alpha + \beta + n} \\
&= \frac{\alpha + \beta}{\alpha + \beta + n} \cdot \frac{\alpha}{\alpha+\beta} + \frac{n}{\alpha + \beta + n} \cdot \frac{k}{n} \\
&= w_{\text{prior}} \times \theta_{\text{prior}} + w_{\text{data}} \times \theta_{\text{observed}}
\end{align}$$

where:
- $w_{\text{prior}} = \frac{n_0}{n_0 + n}$
- $w_{\text{data}} = \frac{n}{n_0 + n}$
- $w_{\text{prior}} + w_{\text{data}} = 1$

**Interpretation**: The posterior belief is a compromise between:
1. What you believed before (prior mean $\alpha/(\alpha+\beta)$)
2. What you just observed (sample rate $k/n$)

The weights depend on **relative information content**:
- Large $n_0$, small $n$ → prior dominates
- Small $n_0$, large $n$ → data dominates
- $n_0 \approx n$ → balanced compromise

### Variance Reduction (Uncertainty Collapse)

As data accumulates, posterior variance shrinks:

$$\text{Var}(\theta | \text{data}) = \frac{(\alpha + k)(\beta + n - k)}{(\alpha + \beta + n)^2(\alpha + \beta + n + 1)}$$

The denominator grows with $(\alpha + \beta + n)^3$, so variance decreases as $O(1/n^2)$.

**Key Properties**:

1. **Uncertainty always decreases**: More data → tighter credible intervals
2. **Asymptotic convergence**: As $n \to \infty$, posterior concentrates at true $\theta$
3. **Rate of convergence**: Depends on prior strength $n_0$

### Example Numerical Update

**Prior**: $\text{Beta}(2, 98)$ implies:
- Prior mean: $2/100 = 0.02$ (2% failure rate)
- Prior variance: $(2 \times 98)/(100^2 \times 101) \approx 0.000192$
- Prior std dev: $0.0139$ (±1.4%)

**Observation**: 5 failures in 50 batches (10% observed rate)

**Posterior**: $\text{Beta}(2+5, 98+50-5) = \text{Beta}(7, 143)$
- Posterior mean: $7/150 = 0.0467$ (4.67% failure rate)
- Posterior variance: $(7 \times 143)/(150^2 \times 151) \approx 0.000295$
- Posterior std dev: $0.0172$ (±1.7%)

**Analysis**:
- Prior said 2%, data said 10%, posterior compromised at 4.67%
- Weight on prior: $100/150 = 67\%$
- Weight on data: $50/150 = 33\%$
- Even strong evidence (10%) only shifted belief modestly due to prior weight

---

## Prior Selection and Calibration

### Method 1: Historical Data

If you have previous audit results:

$$\text{Last year: 2 failures in 100 batches} \rightarrow \text{Use Beta}(2, 98) \text{ as this year's prior}$$

This is the **empirical Bayes** approach—use past data to inform the prior.

### Method 2: Expert Elicitation

Ask domain experts:
1. "What failure rate do you expect?" → Sets $\alpha/(\alpha+\beta)$
2. "How confident are you?" → Sets $\alpha+\beta$

Example:
- Expert: "I expect 2%, and I'm as confident as if I'd seen 500 samples"
- $\rightarrow \alpha/(\alpha+\beta) = 0.02$ and $\alpha+\beta = 500$
- $\rightarrow \alpha = 10, \beta = 490$

### Method 3: Objective Priors

Several "uninformative" priors exist:

**Uniform Prior**: $\text{Beta}(1, 1)$
- Every value of $\theta$ equally likely
- Posterior mean = $k/n$ (same as frequentist MLE after first observation)

**Jeffreys Prior**: $\text{Beta}(0.5, 0.5)$
- Invariant under reparameterization
- Represents "maximum ignorance" in information-theoretic sense

**Haldane Prior**: $\text{Beta}(0, 0)$ [improper]
- Undefined as a proper density, but posterior is $\text{Beta}(k, n-k)$
- Extremely non-informative

### Prior Predictive Checks

To validate your prior, simulate data from it and ask: "Does this match my beliefs?"

**Prior Predictive Distribution**:

$$P(k | n, \alpha, \beta) = \binom{n}{k} \frac{B(k+\alpha, n-k+\beta)}{B(\alpha, \beta)}$$

where $B$ is the beta function: $B(a,b) = \Gamma(a)\Gamma(b)/\Gamma(a+b)$.

This is the **Beta-Binomial distribution**. Simulate values and verify they align with expert expectations.

**Example**:
- Prior: $\text{Beta}(2, 98)$
- Sample size: $n=100$
- Prior predictive mean: $n \cdot \alpha/(\alpha+\beta) = 100 \times 0.02 = 2$ failures expected
- Prior predictive variance: [more complex formula, involves overdispersion]

If experts say "we'd never see more than 10 failures in 100 batches", but your prior predicts 20+ failures with non-negligible probability, recalibrate.

---

## Credible Intervals vs Confidence Intervals

### Frequentist Confidence Interval

A **95% confidence interval** for $\theta$ means:

> "If we repeated this experiment infinitely many times and constructed confidence intervals each time, 95% of those intervals would contain the true $\theta$."

**What it does NOT mean**: "There's a 95% probability the true $\theta$ is in this specific interval."

### Bayesian Credible Interval

A **95% credible interval** for $\theta$ means:

> "Given the data we observed, there's a 95% probability that $\theta$ lies in this interval."

**Direct probabilistic statement about $\theta$**—what decision-makers actually want.

### Computing Credible Intervals

For $\text{Beta}(\alpha, \beta)$, the $(1-\gamma)$ credible interval can be computed via:

**Equal-Tailed Interval** (most common):

$$[\text{Beta}^{-1}(\gamma/2 | \alpha, \beta), \text{Beta}^{-1}(1-\gamma/2 | \alpha, \beta)]$$

where $\text{Beta}^{-1}$ is the inverse CDF (quantile function).

**Highest Posterior Density (HPD) Interval** (narrowest):

Find $[a, b]$ such that:
1. $\int_a^b p(\theta|\text{data}) d\theta = 1-\gamma$
2. $p(a|\text{data}) = p(b|\text{data})$ (equal density at endpoints)

HPD is slightly narrower but requires numerical optimization. For symmetric distributions, equal-tailed ≈ HPD.

### Example

**Posterior**: $\text{Beta}(7, 143)$

**95% credible interval**: $[0.019, 0.089]$

**Interpretation**: "We're 95% confident the true failure rate is between 1.9% and 8.9%."

Compare to frequentist exact binomial confidence interval (Clopper-Pearson) for $k=5, n=50$:
- Frequentist 95% CI: $[0.033, 0.215]$
- Much wider because it doesn't incorporate prior information

---

## Information Theory Perspective

### Kullback-Leibler Divergence

The **information gain** from updating prior to posterior can be quantified via KL divergence:

$$\text{KL}(p_{\text{posterior}} \| p_{\text{prior}}) = \int p(\theta | \text{data}) \log\frac{p(\theta | \text{data})}{p(\theta)} d\theta$$

For Beta distributions, this has a closed form:

$$\begin{align}
\text{KL}(\text{Beta}(\alpha', \beta') \| \text{Beta}(\alpha, \beta)) = &\log\frac{\Gamma(\alpha+\beta)}{\Gamma(\alpha)\Gamma(\beta)} - \log\frac{\Gamma(\alpha'+\beta')}{\Gamma(\alpha')\Gamma(\beta')} \\
&+ (\alpha'-\alpha)\psi(\alpha') + (\beta'-\beta)\psi(\beta') \\
&- (\alpha'+\beta'-\alpha-\beta)\psi(\alpha'+\beta')
\end{align}$$

where $\psi$ is the digamma function.

**Interpretation**: KL divergence measures how many "bits" of information the data provided. High KL → data was surprising given prior. Low KL → data confirmed prior beliefs.

### Entropy Reduction

Shannon entropy quantifies uncertainty:

$$H(\theta) = -\int p(\theta) \log p(\theta) d\theta$$

For $\text{Beta}(\alpha, \beta)$:

$$H(\text{Beta}(\alpha,\beta)) = \log B(\alpha,\beta) - (\alpha-1)\psi(\alpha) - (\beta-1)\psi(\beta) + (\alpha+\beta-2)\psi(\alpha+\beta)$$

where $B$ is the beta function.

**Learning Dynamics**:

$$\text{Information Gain} = H(\text{prior}) - H(\text{posterior})$$

As data accumulates, entropy monotonically decreases → uncertainty collapses.

### Fisher Information

The expected information from a single observation is the **Fisher information**:

$$I(\theta) = E\left[\left(\frac{d}{d\theta} \log p(k|\theta,n)\right)^2\right] = \frac{n}{\theta(1-\theta)}$$

**Interpretation**: 
- Maximum at $\theta=0.5$ (most informative when failure rate is 50%)
- Minimum at $\theta \to 0$ or $\theta \to 1$ (rare events provide less information per observation)
- Scales linearly with sample size $n$

This explains why detecting small failure rates ($\theta \approx 0.02$) requires large samples—each observation carries little information.

---

## Convergence Properties

### Consistency (Bernstein-von Mises Theorem)

Under regularity conditions, as $n \to \infty$:

$$\theta | \text{data} \sim N\left(\hat{\theta}_{\text{MLE}}, [nI(\hat{\theta}_{\text{MLE}})]^{-1}\right)$$

approximately, where $\hat{\theta}_{\text{MLE}} = k/n$ is the maximum likelihood estimate.

**Implications**:
1. **Asymptotic agreement**: Bayesian and frequentist inferences converge for large $n$
2. **Prior wash-out**: For $n \gg n_0$, the prior becomes negligible
3. **Normality**: Posterior becomes approximately Gaussian (even if prior is not)

### Rate of Convergence

The posterior mean converges to the true $\theta$ at rate $O(1/\sqrt{n})$:

$$E[\theta | \text{data}] - \theta_{\text{true}} = O(1/\sqrt{n})$$

The posterior variance shrinks at rate $O(1/n)$:

$$\text{Var}(\theta | \text{data}) = O(1/n)$$

**Practical Consequence**: To halve your uncertainty, you need 4× the data.

### Regret Bounds

In online learning theory, **regret** measures cumulative prediction error:

$$\text{Regret}(T) = \sum_{t=1}^T \text{Loss}(\hat{\theta}_t, \theta_{\text{true}})$$

For Beta-Binomial with log-loss, Bayesian updating achieves **logarithmic regret**:

$$\text{Regret}(T) = O(\log T)$$

This is **minimax optimal**—no algorithm can do better in the worst case.

---

## Extension to Hierarchical Models

### The Limitation of Single-Level Models

Our Beta-Binomial model assumes all observations come from the **same** $\theta$. But in enterprises:
- Different departments may have different failure rates
- Failure rates may vary over time
- Multiple processes may share some common structure

### Hierarchical Beta-Binomial

For $J$ different processes (e.g., different manufacturing sites):

$$\begin{align}
\theta_j &\sim \text{Beta}(\alpha_0, \beta_0) \quad &&\text{[Process-specific rates]} \\
k_j &\sim \text{Binomial}(n_j, \theta_j) \quad &&\text{[Observations per process]}
\end{align}$$

**Partial pooling**: Information from process $j$ informs beliefs about process $j'$, but they're not identical.

### Hyperpriors

We can go one level deeper and treat $(\alpha_0, \beta_0)$ as unknown:

$$\begin{align}
\alpha_0, \beta_0 &\sim \text{some prior} \quad &&\text{[Hyperprior]} \\
\theta_j | \alpha_0, \beta_0 &\sim \text{Beta}(\alpha_0, \beta_0) \\
k_j | \theta_j &\sim \text{Binomial}(n_j, \theta_j)
\end{align}$$

Now we're learning **both** the process-specific rates and the distribution of rates across the enterprise.

**Implementation**: Requires MCMC or variational inference (conjugacy is lost at the hyperprior level).

### Time-Varying Models

For non-stationary processes:

$$\begin{align}
\theta_t | \theta_{t-1} &\sim \text{some transition model} \quad &&\text{[e.g., random walk]} \\
k_t | \theta_t &\sim \text{Binomial}(n_t, \theta_t)
\end{align}$$

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

**Assumption**: $\theta$ is constant over time.

**Violation**:
- Process improvements ($\theta$ decreases over time)
- Degradation ($\theta$ increases over time)
- Regime shifts ($\theta$ jumps at specific events)

**Consequence**: Posterior doesn't track true $\theta$ if it's changing.

**Fix**: Use dynamic models (see Hierarchical Models section) or **discount past data** exponentially:

```python
# Instead of: α_new = α + k
# Use: α_new = λ*α + k    where λ < 1 (e.g., 0.95)
```

This gives more weight to recent data.

### 3. Binomial Model Adequacy

**Assumption**: Failures follow Binomial distribution.

**Violation**:
- Overdispersion (variance > $np\theta(1-\theta)$)
- Underdispersion (variance < $np\theta(1-\theta)$)
- Zero-inflation (excess zeros beyond Binomial expectation)

**Consequence**: Model misspecification leads to poor calibration.

**Fix**: Use **Beta-Binomial** model (adds an overdispersion parameter) or **negative binomial** for count data.

### 4. No Covariates

**Assumption**: $\theta$ doesn't depend on other variables.

**Violation**:
- Failure rate varies by operator, shift, equipment age, batch size, etc.

**Consequence**: Pooling all data obscures important patterns.

**Fix**: Use **Bayesian regression** (e.g., Beta regression or logistic regression with Bayesian estimation).

### 5. Proper Scoring Rules

For the model to be "honest", predictions should be calibrated:

$$P(\theta_{\text{true}} \in \text{credible interval}) \approx \text{nominal coverage (e.g., 95%)}$$

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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings("ignore")

# Load data from Excel
file_path = "err_dist.xlsx"
df = pd.read_excel(file_path, sheet_name=0)
df = df.dropna()

# Distributions to consider
distributions = [
    'norm', 'expon', 'gamma', 'lognorm',
    'beta', 'weibull_min', 'weibull_max',
    'pearson3', 'triang'
]

# Function to compute AIC
def compute_aic(dist, data, params):
    log_likelihood = np.sum(dist.logpdf(data, *params))
    k = len(params)
    return 2 * k - 2 * log_likelihood

# Output containers
best_fits = {}
all_metrics = []

for col in df.columns:
    data = df[col].dropna()
    dist_metrics = []

    for dist_name in distributions:
        try:
            dist = getattr(stats, dist_name)
            params = dist.fit(data)

            # AIC
            aic = compute_aic(dist, data, params)

            # Kolmogorov–Smirnov test
            ks_stat, ks_p = stats.kstest(data, dist_name, args=params)

            # Anderson–Darling test (only supported for some distributions)
            ad_stat = np.nan
            if dist_name in ['norm', 'expon', 'logistic']:
                ad_result = stats.anderson(data, dist=dist_name)
                ad_stat = ad_result.statistic

            dist_metrics.append({
                "Column": col,
                "Distribution": dist_name,
                "AIC": aic,
                "KS_Statistic": ks_stat,
                "KS_p_value": ks_p,
                "AD_Statistic": ad_stat,
                "Parameters": params
            })

        except Exception as e:
            print(f"❌ Error fitting {dist_name} on {col}: {e}")

    # Select best distribution using lowest AIC
    best = min(dist_metrics, key=lambda x: x["AIC"])
    best_fits[col] = best
    all_metrics.extend(dist_metrics)

# Summary DataFrame
metrics_df = pd.DataFrame(all_metrics)
print("\n🔍 All Fit Metrics:")
print(metrics_df)

print("\n✅ Best Fits by AIC:")
print(pd.DataFrame(best_fits).T[["Distribution", "AIC", "KS_p_value", "AD_Statistic"]])

# Visualization: Histogram + PDF + QQ Plot
num_cols = len(df.columns)
fig, axes = plt.subplots(num_cols, 2, figsize=(14, num_cols * 3))

if num_cols == 1:
    axes = [axes]

for i, col in enumerate(df.columns):
    data = df[col].dropna()
    dist_name = best_fits[col]["Distribution"]
    params = best_fits[col]["Parameters"]
    dist = getattr(stats, dist_name)

    x = np.linspace(data.min(), data.max(), 100)
    y_pdf = dist.pdf(x, *params)

    # Histogram with best-fit PDF
    sns.histplot(data, kde=False, stat="density", ax=axes[i][0], bins=30, color='lightgrey')
    axes[i][0].plot(x, y_pdf, label=f'{dist_name} PDF', color='orange')
    axes[i][0].legend()
    axes[i][0].set_title(f"{col} - PDF Fit: {dist_name}", fontsize=11)

    # Q-Q Plot
    sorted_data = np.sort(data)
    quantiles = dist.ppf(np.linspace(0.01, 0.99, len(data)), *params)
    axes[i][1].scatter(quantiles, sorted_data, color='teal', s=10)
    axes[i][1].plot([min(quantiles), max(quantiles)], [min(quantiles), max(quantiles)], 'r--')
    axes[i][1].set_title(f"{col} - Q–Q Plot: {dist_name}", fontsize=11)
    axes[i][1].set_xlabel("Theoretical Quantiles")
    axes[i][1].set_ylabel("Empirical Quantiles")

plt.suptitle("L/T P", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()
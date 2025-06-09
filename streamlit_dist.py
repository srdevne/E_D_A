import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import io
import base64
import warnings

warnings.filterwarnings("ignore")

# ---------- Distribution List ----------
all_distributions = {
    'norm': stats.norm,
    'expon': stats.expon,
    'gamma': stats.gamma,
    'lognorm': stats.lognorm,
    'beta': stats.beta,
    'weibull_min': stats.weibull_min,
    'weibull_max': stats.weibull_max,
    'pearson3': stats.pearson3,
    'triang': stats.triang
}

# ---------- AIC Calculation ----------
def compute_aic(dist, data, params):
    log_likelihood = np.sum(dist.logpdf(data, *params))
    k = len(params)
    return 2 * k - 2 * log_likelihood

# ---------- Plot Download Helper ----------
def get_image_download_link(fig, filename):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">📥 Download Plot</a>'
    return href

# ---------- Streamlit UI ----------
st.set_page_config(layout="wide")
st.title("L/T P")

uploaded_file = st.file_uploader("Upload an Excel file with column headers", type=["xlsx"])

if uploaded_file:
    sheet = pd.read_excel(uploaded_file, sheet_name=0)
    sheet = sheet.dropna()
    
    numeric_cols = sheet.select_dtypes(include=np.number).columns.tolist()
    
    with st.sidebar:
        st.header("🔧 Controls")
        selected_cols = st.multiselect("Choose columns to analyze", options=numeric_cols, default=numeric_cols)
        selected_dists = st.multiselect("Distributions to fit", options=list(all_distributions.keys()),
                                        default=['norm', 'expon', 'gamma', 'lognorm'])
        bin_count = st.slider("Histogram bins", 10, 100, 30)

    results = []
    
    for col in selected_cols:
        st.subheader(f"📊 Column: {col}")
        data = sheet[col].dropna()

        dist_metrics = []

        for name in selected_dists:
            dist = all_distributions[name]
            try:
                params = dist.fit(data)
                aic = compute_aic(dist, data, params)
                ks_stat, ks_p = stats.kstest(data, name, args=params)
                ad_stat = np.nan
                if name in ['norm', 'expon', 'logistic']:
                    ad_result = stats.anderson(data, dist=name)
                    ad_stat = ad_result.statistic
                
                dist_metrics.append({
                    "Column": col,
                    "Distribution": name,
                    "AIC": aic,
                    "KS_p_value": ks_p,
                    "AD_Statistic": ad_stat,
                    "Params": params
                })

            except Exception as e:
                st.warning(f"Error fitting {name} on {col}: {e}")

        # Best fit
        best_fit = min(dist_metrics, key=lambda x: x['AIC'])
        best_name = best_fit["Distribution"]
        best_params = best_fit["Params"]
        best_dist = all_distributions[best_name]

        # Plot histogram + PDF
        fig, ax = plt.subplots()
        sns.histplot(data, bins=bin_count, stat="density", ax=ax, color="skyblue", edgecolor="black")
        x = np.linspace(data.min(), data.max(), 100)
        ax.plot(x, best_dist.pdf(x, *best_params), color='red', label=f'{best_name} fit')
        ax.set_title(f"{col} - Best Fit: {best_name}", fontsize=12)
        ax.legend()
        st.pyplot(fig)
        st.markdown(get_image_download_link(fig, f"{col}_pdf_fit.png"), unsafe_allow_html=True)

        # Q–Q plot
        fig2, ax2 = plt.subplots()
        sorted_data = np.sort(data)
        q_theory = best_dist.ppf(np.linspace(0.01, 0.99, len(data)), *best_params)
        ax2.scatter(q_theory, sorted_data, color='darkgreen')
        ax2.plot([min(q_theory), max(q_theory)], [min(q_theory), max(q_theory)], 'r--')
        ax2.set_title(f"{col} - Q–Q Plot ({best_name})", fontsize=12)
        ax2.set_xlabel("Theoretical Quantiles")
        ax2.set_ylabel("Empirical Quantiles")
        st.pyplot(fig2)
        st.markdown(get_image_download_link(fig2, f"{col}_qq_plot.png"), unsafe_allow_html=True)

        results.extend(dist_metrics)

    if results:
        df_summary = pd.DataFrame(results)
        st.subheader("📄 Fit Summary Table")
        st.dataframe(df_summary)

        csv = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Summary CSV", data=csv, file_name="distribution_fit_summary.csv")
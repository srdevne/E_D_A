import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import itertools
import openpyxl
from scipy.stats import stats

def create_summary_table(df):
    total_counts = df.count()
    null_values = df.isnull().sum()
    null_percentages = (null_values / df.shape[0]) * 100
    unique_counts = df.nunique()
    summary_table = pd.DataFrame({
        'Total Counts': total_counts,
        'Null Values': null_values,
        'Null Value Percentage': null_percentages,
        'Unique Value Counts': unique_counts
    })
    return summary_table


def perform_univariate_analysis(data, columns):
    #summary = create_summary_table(data)
    output_uni = []
    for column in columns:
        column_data = data[column]
        if column_data.dtype == "object":
            # Categorical column, create a bar plot
            value_counts = column_data.value_counts().reset_index()
            value_counts.columns = ["Category", "Count"]
            fig = px.bar(value_counts, x="Category", y="Count", title=f"Bar Plot - {column}")
        else:
            # Continuous column, create a histogram and KDE plot
            fig = sp.make_subplots(rows=1, cols=3, subplot_titles=(
                f"Scatter Plot - {column}", f"Histogram - {column}", f"Box Plot - {column}"))
            # Scatter plot
            fig.add_trace(go.Scatter(x=column_data, y=column_data, mode="markers", name="Scatter Plot"), row=1, col=1)
            # Histogram
            fig.add_trace(go.Histogram(x=column_data, nbinsx=10, name="Histogram"), row=1, col=2)
            # Box plot
            fig.add_trace(go.Box(x=column_data, name="Box Plot"), row=1, col=3)
            fig.update_layout(title=f"Univariate Analysis - {column}", showlegend=False)
        output_uni.append({"column": column, "plot": fig})

    return output_uni

def perform_bivariate_analysis(data, columns):
    continuous_columns = []
    categorical_columns = []
    output_bi = []
    for column in columns:
        if data[column].dtype == 'object':
            categorical_columns.append(column)
        else:
            continuous_columns.append(column)
    pairs = list(itertools.combinations(continuous_columns, 2))
    for pair in pairs:
        x, y = pair[0], pair[1]
        # Create a scatter plot
        fig = px.scatter(data, x=x, y=y, title=f"Scatter Plot: {x} vs {y}")
        output_bi.append({"column": pair, "plot": fig})
    # Bar plots for continuous vs categorical variables
    for continuous_col in continuous_columns:
        for categorical_col in categorical_columns:
            fig = px.bar(data, x=categorical_col, y=continuous_col,
                         title=f"Bar Plot: {continuous_col} by {categorical_col}")
            output_bi.append({"column": continuous_col+'vs'+categorical_col, "plot": fig})
    # Contingency tables for categorical variables
    pairs_cat = list(itertools.combinations(categorical_columns, 2))
    for pair in pairs_cat:
        x, y = pair[0], pair[1]
        contingency_table = pd.crosstab(data[x], data[y])
        fig = go.Figure(data=go.Heatmap(z=contingency_table.values, x=contingency_table.columns, y=contingency_table.index,
            colorscale='Viridis'))
        fig.update_layout(title=f"Contingency Table: {x} vs {y}", xaxis_title=x, yaxis_title=y)
        # Perform chi-square test
        chi2, p, _, _ = stats.chi2_contingency(contingency_table)
        fig.add_annotation(text=f"Chi-square test: p-value = {p:.4f}", xref="paper", yref="paper",
            x=0.5, y=-0.15, showarrow=False, font=dict(size=12), bgcolor="#ffffff", bordercolor="#000000",
            borderwidth=1, borderpad=5)
        output_bi.append({"column": x+'vs'+y, "plot": fig})

    # Heatmap
    correlation = data[continuous_columns].corr()
    fig = go.Figure(data=go.Heatmap(z=correlation.values, x=correlation.columns, y=correlation.columns,
        colorscale='Viridis'))
    fig.update_layout(title='Correlation Heatmap', xaxis_title='Variable', yaxis_title='Variable')
    output_bi.append({"column": correlation, "plot": fig})
    return output_bi

def perform_multivariate_analysis(data, columns):
    # Add your code for multivariate analysis here
    # This function should return the output in a similar format as the other analysis functions
    pass

def write_output_to_excel(output_uni, output_bi):
    filename = 'EDA_Analysis.xlsx'
    with pd.ExcelWriter(filename) as writer:
        for item in output_uni:
            column = item["column"]
            plot1 = item["plot"]
            sheet_name = f"Univariate Analysis"
            plot1.write_excel(writer, sheet_name=sheet_name)
        for item in output_bi:
            column = item["column"]
            plot2 = item["plot"]
            sheet_name = f"Bivariate Analysis"
            plot2.write_excel(writer, sheet_name=sheet_name)


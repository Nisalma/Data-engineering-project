# Tokyo Airbnb Market Intelligence Pipeline

This repository contains the end-to-end data engineering infrastructure and inferential statistical framework developed to analyze the short-term rental market in Tokyo, Japan. The project transitions raw, unstructured marketplace data into an optimized analytical data warehouse, providing actionable insights for revenue strategists and real estate investors.

## 1. Project Overview and Business Context

In dense urban vacation rental markets like Tokyo, stakeholders require precise data to optimize property acquisition and pricing strategies. This project addresses three primary business challenges:
* Quantifying structural pricing differences between core property segments.
* Validating whether platform trust markers, such as Superhost status, justify premium pricing strategies.
* Mapping geographic and temporal demand patterns to inform dynamic revenue management.

To deliver reliable insights, this platform implements a formal data engineering pipeline that cleanses raw public data, resolves structural inconsistencies, enforces relational integrity, and applies rigorous inferential testing.

## 2. Repository Architecture and Directory Structure

The project artifacts are organized according to standard enterprise data science conventions:

<img width="317" height="186" alt="image" src="https://github.com/user-attachments/assets/79087198-4aa5-4355-b335-a03def8de00d" />


## 3. Data Engineering and Dimensional Modeling

The raw data source consists of highly unnormalized flat CSV files containing embedded text anomalies, missing indices, and mixed data types. The python pipeline automates the ingestion process, applying regular expressions to strip currency symbols, handle thousands separators, and safely cast pricing metrics into float data types.

To facilitate sub-second analytical queries across millions of temporary rows, the data is structured into a optimized Star Schema using an in-memory DuckDB database engine.

### Fact Table
* fact_enriched_master: Compiles the core quantitative metrics per listing, including baseline pricing per bedroom, calculated occupancy velocities, lifetime review volumes, and localized demand metrics.

### Dimension Tables
* dim_hosts_cleaned: Contains host-specific attributes, including tenure, multi-listing portfolio sizes, and verified registration badges.
* dim_calendar: Manages chronological rows tracking forward-looking nightly availability and daily pricing adjustments over a 365-day horizon.
* dim_neighbourhoods: Contains administrative ward classifications, geographic coordinates, and regional market density metrics.

This star schema minimizes data redundancy, enforces structural keys, and allows business intelligence tools to slice and dice quantitative facts by key categorical dimensions instantly.

## 4. Inferential Statistical Methodology and Findings

Rather than relying on basic descriptive averages, which can be easily distorted by extreme luxury outliers, this framework applies formal statistical modeling to test five core marketplace hypotheses.

### Hypothesis 1: Room Type Pricing Variances
* Question: Do entire home listings command a significantly higher nightly price per bedroom compared to shared private rooms?
* Methodology: Welch's Independent Two-Sample t-Test. This test is selected because it accounts for unequal variances and highly unbalanced group sizes between property classifications.
* Verdict: Rejected the null hypothesis (p < 0.001). Entire homes command a clear structural premium, confirming that consumers heavily prioritize physical isolation and privacy in the Tokyo market.

### Hypothesis 2: The Superhost Premium Paradox
* Question: Does achieving Superhost status allow operators to demand a significantly higher nightly base rate?
* Methodology: Welch's Independent Two-Sample t-Test.
* Verdict: Failed to reject the null hypothesis (p = 0.4574). The test demonstrates that Superhost status does not grant direct pricing power. Instead, its operational utility lies in conversion funnel optimization, driving higher booking volumes and stabilizing occupancy consistency.

### Hypothesis 3: Social Proof and Review Accumulation Thresholds
* Question: Do established properties with more than 10 reviews maintain distinct pricing models compared to unreviewed listings?
* Methodology: Two-Sample t-Test.
* Verdict: Rejected the null hypothesis (p < 0.05). Properties that clear the 10-review threshold benefit from social proof, reducing consumer perceived risk and allowing hosts to price at market equilibrium without offering steep introductory discounts.

### Hypothesis 4: Spatial Pricing Variations Across Wards
* Question: Do regional boundaries and ward classifications create statistically significant baseline price variations?
* Methodology: One-Way Analysis of Variance (ANOVA). This method is required to mathematically evaluate and compare the numerical means of three or more independent categorical groups.
* Verdict: Rejected the null hypothesis (p < 0.001). Geographic location is established as the single most powerful driver of structural real estate value, meaning blanket municipal pricing models are invalid; pricing must be optimized at the specific micro-neighborhood level.

### Hypothesis 5: Temporal Weekend Surge Adjustments
* Question: Are weekend nightly rates systematically higher than weekday rates within forward-looking calendar records?
* Methodology: Calendar aggregate group mean variance evaluation.
* Verdict: Rejected the null hypothesis. The data confirms that professional operators actively engage in dynamic revenue management, increasing nightly rates on Friday and Saturday nights to maximize yields during peak leisure demand windows.

## 5. Driver Analysis and Regression Modeling

To complement hypothesis testing, an Ordinary Least Squares (OLS) Multiple Linear Regression model is applied to quantify the marginal dollar impact of key operational predictors on pricing metrics.

To safeguard the validity of the regression weights, a Variance Inflation Factor (VIF) check is executed programmatically. All independent predictor features yield VIF values below the critical threshold of 5.0. This status confirms the complete absence of multicollinearity, ensuring that the features are independent and that the model coefficients are stable, reliable, and safe for strategic financial forecasting.

## 6. Reproducibility Protocol

Follow these sequential steps to deploy the data pipeline and regenerate the analytical environment locally:

1. Environment Preparation: Clone this repository to your local directory and ensure a Python environment is active.
2. Dependency Installation: Install the optimized analytical and statistical packages via terminal:
   pip install pandas duckdb scipy statsmodels
3. Pipeline Execution: Open and execute the Jupyter Notebook located within the /notebooks directory. The script will programmatically initialize the database, process the source files, assemble the star schema, and output the complete inferential statistical reports automatically.

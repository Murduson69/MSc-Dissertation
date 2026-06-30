import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

'''List of WTs with their coordinates (from Cost-Effectiveness Paper) 
and their probability of downtime Pr t,i(D) (from Integrated preventive Paper)'''



list_WT = [
    {
     'ID': 'WT01', 
     'X': 7, 
     'Y': 13, 
     'Pr_Di': [0.40, 0.16, 0.39, 0.16, 0.17, 0.09, 0.15],
     'repaired': False
     },
    {
     'ID': 'WT02', 
     'X': 3.5, 
     'Y': 2, 
     'Pr_Di': [0.18, 0.21, 0.18, 0.14, 0.60, 0.20, 0.15],
     'repaired': False
     },
    {
     'ID': 'WT03', 
     'X': 6.5, 
     'Y': 7, 
     'Pr_Di': [0.21, 0.14, 0.16, 0.11, 0.13, 0.14, 0.15],
     'repaired': False
     },
    {
     'ID': 'WT04', 
     'X': 13.5, 
     'Y': 0, 
     'Pr_Di': [0.33, 0.13, 0.31, 0.26, 0.12, 0.45, 0.24],
     'repaired': False
     },
    {
     'ID': 'WT05', 
     'X': 13, 
     'Y': 12.5, 
     'Pr_Di': [0.10, 0.24, 0.11, 0.31, 0.39, 0.29, 0.18],
     'repaired': False
     },
    {
     'ID': 'WT06', 
     'X': 18, 
     'Y': 10, 
     'Pr_Di': [0.19, 0.27, 0.23, 0.21, 0.14, 0.15, 0.17],
     'repaired': False
     },
    {
     'ID': 'WT07', 
     'X': 10, 
     'Y': 14, 
     'Pr_Di': [0.25, 0.13, 0.14, 0.16, 0.18, 0.12, 0.19],
     'repaired': False
     },
    {
     'ID': 'WT08', 
     'X': 3.5, 
     'Y': 1, 
     'Pr_Di': [0.11, 0.20, 0.23, 0.20, 0.33, 0.24, 0.37],
     'repaired': False
     },
    {
     'ID': 'WT09', 
     'X': 18, 
     'Y': 3, 
     'Pr_Di': [0.18, 0.16, 0.13, 0.11, 0.29, 0.17, 0.10],
     'repaired': False
     },
    {
     'ID': 'WT10', 
     'X': 19.5, 
     'Y': 6.5, 
     'Pr_Di': [0.19, 0.22, 0.19, 0.18, 0.21, 0.20, 0.20],
     'repaired': False
     },
    {
     'ID': 'WT11', 
     'X': 10, 
     'Y': 7.5, 
     'Pr_Di': [0.30, 0.23, 0.39, 0.20, 0.18, 0.23, 0.17],
     'repaired': False
     },
    {
     'ID': 'WT12', 
     'X': 20, 
     'Y': 12, 
     'Pr_Di': [0.24, 0.20, 0.12, 0.22, 0.36, 0.32, 0.18],
     'repaired': False
     },
    {
     'ID': 'WT13', 
     'X': 11, 
     'Y': 12, 
     'Pr_Di': [0.11, 0.22, 0.20, 0.18, 0.20, 0.16, 0.15],
     'repaired': False
     },
    {
     'ID': 'WT14', 
     'X': 19, 
     'Y': 13, 
     'Pr_Di': [0.22, 0.23, 0.19, 0.16, 0.09, 0.16, 0.15],
     'repaired': False
     },
    {
     'ID': 'WT15', 
     'X': 12.5, 
     'Y': 14.5, 
     'Pr_Di': [0.10, 0.12, 0.28, 0.23, 0.12, 0.16, 0.11],
     'repaired': False
     },
    {
     'ID': 'WT16', 
     'X': 0, 
     'Y': 8.5, 
     'Pr_Di': [0.12, 0.14, 0.12, 0.32, 0.25, 0.28, 0.18],
     'repaired': False
     },
    {
     'ID': 'WT17', 
     'X': 16, 
     'Y': 2.5, 
     'Pr_Di': [0.11, 0.12, 0.09, 0.18, 0.13, 0.20, 0.33],
     'repaired': False
     },
    {
     'ID': 'WT18', 
     'X': 18.5, 
     'Y': 7.5, 
     'Pr_Di': [0.21, 0.21, 0.19, 0.20, 0.10, 0.23, 0.36],
     'repaired': False
     },
    {
     'ID': 'WT19', 
     'X': 7, 
     'Y': 12, 
     'Pr_Di': [0.27, 0.20, 0.17, 0.13, 0.26, 0.22, 0.37],
     'repaired': False
     },
    {
     'ID': 'WT20', 
     'X': 1, 
     'Y': 5, 
     'Pr_Di': [0.27, 0.15, 0.27, 0.28, 0.19, 0.08, 0.16],
     'repaired': False
     },
]

# 1. Data extraction and formatting
wt_ids = [wt['ID'] for wt in list_WT]
pr_di_data = [wt['Pr_Di'] for wt in list_WT]

# Create a Pandas DataFrame for better structure
# Rows represent Wind Turbines, columns represent the 7-day horizon
df_pr = pd.DataFrame(pr_di_data, index=wt_ids, columns=[f'Day {i+1}' for i in range(7)])

# 2. Figure configuration (Academic style)
plt.figure(figsize=(12, 9), dpi=300)
sns.set_theme(style="white")

# 3. Create Heatmap
# 'annot=True' displays the precise values
# 'cmap' uses a professional color scale (Yellow-Orange-Red)
ax = sns.heatmap(df_pr, annot=True, fmt=".2f", cmap="YlOrRd",
                 cbar_kws={'label': 'Probability of Failure (Pr_Di)'},
                 linewidths=.5, vmin=0, vmax=0.6)

# 4. Axes and title adjustment
plt.title("Daily Predictive Risk Profile (Pr_Di) Across the Wind Farm", fontsize=16, pad=20, weight='bold')
plt.xlabel("Maintenance Campaign Day", fontsize=14, labelpad=10)
plt.ylabel("Wind Turbine ID (WT)", fontsize=14, labelpad=10)

# Adjust tick labels
plt.yticks(rotation=0, fontsize=11)
plt.xticks(fontsize=11)

# 5. Save in high-definition (300 dpi) for the MSc dissertation
plt.tight_layout()
plt.savefig("Predictive_Risk_Heatmap.png", dpi=300, bbox_inches='tight')
print("The 'Predictive_Risk_Heatmap.png' image has been successfully generated for your dissertation.")

# Show plot
plt.show()
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from datetime import datetime

class FinancialAnalyzer:
    def analyse(self, data):
        self.data = data
        monthly_summary = self.process_transaction_data(self.data)

        # Generate overall recommendations
        overall_recommendations = self.generate_overall_recommendations(self.data)

        # Generate monthly recommendations
        monthly_recommendations = self.generate_monthly_recommendations(monthly_summary)
        return {'overall_recommendations' : overall_recommendations, 'monthly_recommendations' : monthly_recommendations}

    def process_transaction_data(self,data):

        # Ensure the Date column is in datetime format
        data['Date'] = pd.to_datetime(data['Date'], format='%d %b %Y')

        # Extract the month from the Date column
        data['Month'] = data['Date'].dt.to_period('M')

        # Step 4: Aggregate data by month
        monthly_summary = data.groupby('Month').agg(
            avg_balance=('Balance', 'mean'),     #Monthly avg.balance
            total_debit=('Debit', 'sum'),
            total_credit=('Credit', 'sum')
        ).reset_index()

        # Calculate net_flow as the difference between total_credit and total_debit
        monthly_summary['net_flow'] = monthly_summary['total_credit'] - monthly_summary['total_debit']

        return monthly_summary  # Return both raw data and monthly summary
    
    def generate_overall_recommendations(self,data):

        overall_summary = {
        'Total Debit': data['Debit'].sum(),
        'Total Credit': data['Credit'].sum(),
        'Average Balance': data['Balance'].mean(),    #statement average balance
        'Total Transactions': data.shape[0],
        'Net Flow': data['Credit'].sum() - data['Debit'].sum(),}
        recommendations = []

        # Analyze overall summary to give recommendations
        if overall_summary['Net Flow'] < 0:
            recommendations.append("You are spending more than you are earning. Consider reducing discretionary expenses.")
        
        if overall_summary['Average Balance'] < 1000:
            recommendations.append("Your average balance is low. Consider setting up a budget and increasing savings.")

        if overall_summary['Total Credit'] > overall_summary['Total Debit']:
            recommendations.append("You have a positive net flow. Consider investing surplus funds for better returns.")

        return recommendations

    def generate_monthly_recommendations(self,monthly_summary):
        # Prepare features for clustering
        features = monthly_summary[['avg_balance', 'total_debit', 'total_credit', 'net_flow']]
        
        # Scale the features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        # Determine number of clusters dynamically based on the number of samples
        n_clusters = min(3, len(monthly_summary))  # Limit to a max of 3 clusters

        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        monthly_summary['Cluster'] = kmeans.fit_predict(scaled_features)

        # Define recommendation function based on cluster analysis
        def recommend_tips(cluster):
            if cluster == 0:
                return "Your spending is balanced. Continue saving and review investments."
            elif cluster == 1:
                return "High spending detected. Consider budgeting strategies to improve savings."
            elif cluster == 2:
                return "You have a consistent surplus. Look into potential investment opportunities."
            else:
                return "Review your transactions for improved financial health."

        # Apply recommendations based on clusters
        monthly_summary['Recommendation'] = monthly_summary['Cluster'].apply(recommend_tips)

        return monthly_summary

"""ob = FinancialAnalyzer()
dic = ob.analyse(val)
for i in dic:
  print(dic[i])"""
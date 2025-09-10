# analyze_logs.py - Run this after stopping the bot to visualize profits

import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime

def parse_logs(log_file='trades.log'):
    data = []
    with open(log_file, 'r') as f:
        for line in f:
            if 'Net Profit:' in line:
                # Extract timestamp from line start (adjust format if your logs differ)
                timestamp_str = line.split(' - ')[0]
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                except ValueError:
                    print(f"Skipping invalid timestamp: {timestamp_str}")
                    continue
                
                # Extract net profit
                profit_match = re.search(r'Net Profit: \$(\d+\.\d+)', line)
                if profit_match:
                    net_profit = float(profit_match.group(1))
                    data.append({'timestamp': timestamp, 'net_profit': net_profit})
    
    df = pd.DataFrame(data)
    if df.empty:
        print("No profits found in log.")
        return None
    
    # Sort by timestamp (in case logs are out of order)
    df = df.sort_values('timestamp')
    
    # Calculate cumulative profit
    df['cumulative_profit'] = df['net_profit'].cumsum()
    df.to_csv('profits.csv', index=False)  # Export to CSV
    return df

def plot_profits(df, plot_vs_index=False):
    plt.figure(figsize=(12, 6))  # Wider for better visibility
    
    if plot_vs_index:
        # Plot vs trade index (useful if timestamps are too close)
        x = range(1, len(df) + 1)  # 1-based trade numbers
        plt.plot(x, df['cumulative_profit'], marker='o', linestyle='-', color='b')
        plt.xlabel('Trade Number')
    else:
        # Plot vs timestamp (default)
        x = df['timestamp']
        plt.plot(x, df['cumulative_profit'], marker='o', linestyle='-', color='b')
        plt.xlabel('Timestamp')
        plt.xticks(rotation=45)
    
    plt.title(f'Cumulative Simulated Profits Over Time (Total: ${df["cumulative_profit"].iloc[-1]:.2f})')
    plt.ylabel('Cumulative Profit ($)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('profits_plot.png')  # Save as image
    plt.show()  # Display plot

if __name__ == "__main__":
    df = parse_logs()
    if df is not None:
        plot_profits(df, plot_vs_index=False)  # Set to True if timestamps are too clustered
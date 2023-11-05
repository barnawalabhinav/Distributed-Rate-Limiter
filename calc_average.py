import os
import csv
import re

# Define the base directory where the files are located
base_directory = 'data/'  # Update this to your local directory path

# List all the files that match the pattern 'client_X_common_db.csv'
file_pattern = re.compile(r"client_\d+_common_db.csv")
file_paths = [f for f in os.listdir(base_directory) if file_pattern.match(f)]

# Define the CSV output file
output_file = os.path.join(base_directory, 'averages.csv')

# Function to calculate averages from a file


def calculate_averages(file_path):
    total_latency = 0
    total_rtt = 0
    count = 0

    # Read file and calculate total latency and RTT
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Extract latency and RTT values after ':accepted-'
                parts = line.strip().split(':accepted-')
                if len(parts) == 2:
                    latency, rtt = map(int, parts[1].split('-'))
                    total_latency += latency
                    total_rtt += rtt
                    count += 1
            except ValueError:
                continue  # Skip lines that do not match the expected format

    # Calculate averages
    average_latency = total_latency / count if count else 0
    average_rtt = total_rtt / count if count else 0

    return average_latency, average_rtt


# Calculate averages for each file and write to a new CSV
with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(['File Name', 'Average Latency', 'Average RTT'])

    # Process each file and write the averages
    for client_file in file_paths:
        file_path = os.path.join(base_directory, client_file)
        average_latency, average_rtt = calculate_averages(file_path)
        csvwriter.writerow([client_file, average_latency, average_rtt])

print(f"Averages have been calculated and saved to {output_file}")

# Function to calculate overall averages from the averages.csv file


def calculate_overall_averages_from_csv(csv_path):
    total_latency = 0
    total_rtt = 0
    count = 0

    with open(csv_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header
        for row in csvreader:
            if row:  # Check if row is not empty
                file_name, avg_latency, avg_rtt = row
                total_latency += float(avg_latency)
                total_rtt += float(avg_rtt)
                count += 1

    # Calculate overall averages
    overall_average_latency = total_latency / count if count else 0
    overall_average_rtt = total_rtt / count if count else 0

    return overall_average_latency, overall_average_rtt


# Calculate the overall averages from the averages.csv file
overall_avg_latency, overall_avg_rtt = calculate_overall_averages_from_csv(
    output_file)
print(overall_avg_latency, overall_avg_rtt)

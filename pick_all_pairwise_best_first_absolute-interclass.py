import rank_orders
import copy
import time
import os
import csv
import shutil
import sys
import random
import string
import OD_detection

def sort_orders_based_on_method_score(orders, method_summary, module):
    start_time = time.time()

    # Create nested directory structure
    parent_dir_name = "pairwise best first absolute interclass"
    parent_dir_path = os.path.join(parent_dir_name)

    # Create the parent directory without module name
    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)


    # Directory and CSV file paths
    dir_name = os.path.join(parent_dir_name, module)
    csv_file_path = os.path.join(parent_dir_name, f"{module}_order_statistics.csv")

    # Delete existing directory and CSV file if they exist
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)

    # Create new directory
    os.makedirs(dir_name, exist_ok=True)

    # CSV file setup
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Order Number", "Time Taken to Sort"])

    # Sort the orders based on method count score for interclass pairs
    sorted_orders = sorted(
        orders,
        key=lambda order: rank_orders.get_method_count_score_for_interclass_pairs(
            rank_orders.find_interclass_pairs(order), method_summary
        ),
        reverse=True
    )

    # Store the sorted orders and update the CSV
    for file_count, order in enumerate(sorted_orders):
        order_end_time = time.time()
        time_taken_to_sort = order_end_time - start_time

        # Save the order in a file
        file_path = os.path.join(dir_name, f"order_{file_count}")
        with open(file_path, 'w') as file:
            file.write('\n'.join(str(item) for item in order))

        # Write to CSV
        with open(csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_count, time_taken_to_sort])

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort by method count score")

    return sorted_orders, total_time_taken, dir_name

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)
    parent_dir_name = "pairwise best first absolute interclass OD"
    parent_dir_path = os.path.join(parent_dir_name)

    # Create the parent directory without module name
    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)

    #CSV file paths
    csv_file_path = os.path.join(parent_dir_name, f"OD_detection_stats.csv")

    # Delete existing CSV file if they exist
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)


    # CSV file setup
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Project Name", "Module Name", "String to in conversion time ", "First OD detection Order No","Total order no to detect all OD","Total time Taken"])

    input_csv = sys.argv[1]  # Get CSV file path from command line argument

    with open(input_csv, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            github_slug = row[0]
            module = row[1]
            t = int(row[2])
            target_path = row[3]
            target_path_polluter_cleaner = row[4]
            original_order = row[5]
            print(original_order)
            result,unique_od_test_list = rank_orders.get_victims_or_brittle(github_slug, module,target_path_polluter_cleaner)
            string_conversion_time=0
            orders_with_num = rank_orders.get_orders_for_line_no(target_path)#
            orders,string_conversion_time=rank_orders.replace_numbers_with_strings(orders_with_num,original_order)
            #orders, string_conversion_time = rank_orders.replace_numbers_with_strings(orders_with_num, original_order)

            order_summary_copy = copy.deepcopy(orders)
            method_summary = rank_orders.summarize_test_methods(order_summary_copy[0])

            # Sort the orders using the updated function
            if not module:
                module = github_slug.split('/')[-1]
            sorted_orders, total_time_taken_to_sort, sorted_orders_path = sort_orders_based_on_method_score(orders, method_summary, module)



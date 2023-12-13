import rank_orders
import copy
import time
import os
import csv
import shutil
import sys
import random
import string

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)
    parent_dir_name = "Random OD"
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
            result,unique_od_test_list = rank_orders.get_victims_or_brittle(github_slug, module,target_path_polluter_cleaner)
            orders_with_num = rank_orders.get_orders_for_line_no(target_path)#
            orders,string_conversion_time=rank_orders.replace_numbers_with_strings(orders_with_num,original_order)
            num_shuffle_iterations = 1000
            total_rank_point=0
            total_first_od_point=0
            start_time = time.time()
            for i in range(num_shuffle_iterations):
                shuffled_orders = copy.deepcopy(orders)  # Create a copy of the original orders
                copy_of_results = copy.deepcopy(result)
                copy_of_unique_od_test_list = copy.deepcopy(unique_od_test_list)
                random_seed = i  # Use the iteration index as the random seed
                random.seed(random_seed)
                random.shuffle(shuffled_orders)
                order_count, first_removal_order_count = find_OD_in_sorted_orders(shuffled_orders, copy_of_results, copy_of_unique_od_test_list,False)
                #print(f"Index- {i}")
                #print(order_count)
                total_rank_point=total_rank_point+order_count
                total_first_od_point=total_first_od_point+first_removal_order_count
            print(f"Number of avg orders needed to find all OD from random seed: {total_rank_point/num_shuffle_iterations}")
            total_time_taken = time.time() - start_time
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([github_slug, module, string_conversion_time, total_first_od_point/num_shuffle_iterations,total_rank_point/num_shuffle_iterations,total_time_taken])

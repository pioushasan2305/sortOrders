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

def sort_orders_based_on_static_field_covered(orders, current_superset, method_summary, module, github_slug):
    sorted_orders = []
    t = 2
    start_time = time.time()
    total_no_of_orders = len(orders)
    total_permutations = len(current_superset)
    parent_dir_name = "Static fields covered absolute interclass orders"
    parent_dir_path = os.path.join(parent_dir_name)

    # Create the parent directory without module name
    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)
    if not module:
        module = github_slug.split('/')[-1]

    # Directory and CSV file paths
    dir_name = os.path.join(parent_dir_name, module)
    csv_file_path = os.path.join(parent_dir_name, f"{module}_order_statistics.csv")

    # Delete existing directory and CSV file if they exist
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    if (os.path.exists(csv_file_path)):
        os.remove(csv_file_path)

    # Create new directory
    os.makedirs(dir_name, exist_ok=True)

    # CSV file setup
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Order Number", "Time Taken to Sort", "Tie Break Count", "Tie of Tie Break Count", "Index Chosen"])

    # Sorting logic
    file_count = tie_break_count = tie_of_tie_break_count = 0

    # Loop through each order and insert it into the sorted list in the correct position
    for order in orders:
        order_start_time = time.time()
        current_combinations = rank_orders.get_consecutive_t_combinations(order, t)
        current_cover = len(current_combinations & current_superset)
        if current_cover == 0:
            continue  # Skip orders that do not cover anything

        current_interclass_combinations = rank_orders.find_interclass_pairs(order)
        current_method_count = rank_orders.get_method_count_score_for_interclass_pairs(current_interclass_combinations, method_summary)

        inserted = False
        for i in range(len(sorted_orders)):
            sorted_combinations = rank_orders.get_consecutive_t_combinations(sorted_orders[i], t)
            sorted_cover = len(sorted_combinations & current_superset)
            sorted_interclass_combinations = rank_orders.find_interclass_pairs(sorted_orders[i])
            sorted_method_count = rank_orders.get_method_count_score_for_interclass_pairs(sorted_interclass_combinations, method_summary)

            if (current_cover > sorted_cover) or (current_cover == sorted_cover and current_method_count > sorted_method_count):
                sorted_orders.insert(i, order)
                inserted = True
                break

        if not inserted:
            sorted_orders.append(order)

        best_order_combinations = rank_orders.get_consecutive_t_combinations(order, t)
        current_superset -= best_order_combinations

        # Save the sorted order in a file
        file_path = os.path.join(dir_name, f"order_{file_count}")
        with open(file_path, 'w') as file:
            file.write('\n'.join(str(item) for item in order))
        file_count += 1

        # Write to CSV
        order_end_time = time.time()
        time_taken_to_sort = order_end_time - order_start_time
        with open(csv_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([file_count, time_taken_to_sort, tie_break_count, tie_of_tie_break_count])

    # If there are still orders left, but the superset is empty
    if current_superset:
        coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
        print(f"All orders are exhausted with a coverage of {coverage:.2f}% for static field pairs")
    else:
        coverage = 100
        print(f"Coverage: {coverage:.2f}%")

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds for static field pairs")

    return sorted_orders, total_time_taken, dir_name

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)

    parent_dir_name = "Static fields covered absolute interclass OD"
    parent_dir_path = os.path.join(parent_dir_name)

    # Create the parent directory without module name
    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)

    # CSV file paths
    csv_file_path = os.path.join(parent_dir_name, f"OD_detection_stats.csv")

    # Delete existing CSV file if they exist
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)

    # CSV file setup
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Project Name", "Module Name", "String to in conversion time", "First OD detection Order No", "Total order no to detect all OD", "Total time Taken"])

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
            file_path_pairs = row[6]
            print(module)

            # Reading tests from file and finding all pairs
            result, unique_od_test_list = rank_orders.get_victims_or_brittle(github_slug, module, target_path_polluter_cleaner)
            orders_with_num = rank_orders.get_orders_for_line_no(target_path)
            orders, string_conversion_time = rank_orders.replace_numbers_with_strings(orders_with_num, original_order)
            tests_with_fields = rank_orders.read_tests_from_file(file_path_pairs)
            test_pairs_with_shared_fields = rank_orders.find_shared_field_pairs(tests_with_fields)
            pairs_superset = copy.deepcopy(test_pairs_with_shared_fields)
            order_summary_copy = copy.deepcopy(orders)
            order_sorted_copy = copy.deepcopy(orders)
            method_summary = rank_orders.summarize_test_methods(order_summary_copy[0])
            sorted_orders_based_on_static, time_taken_static, sorted_orders_path = sort_orders_based_on_static_field_covered(order_sorted_copy, pairs_superset, method_summary, module, github_slug)

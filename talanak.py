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
def replace_strings_with_numbers(matrix, file_path):
    start_time = time.time()  # Start time

    # Read the file and store each line in a dictionary for quick lookup
    line_to_number = {}
    with open(file_path, 'r') as file:
        for number, line in enumerate(file.read().splitlines()):
            line_to_number[line] = number

    # Replace the strings in the matrix with corresponding line numbers
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            # Only replace if the string is found in the dictionary
            if matrix[i][j] in line_to_number:
                matrix[i][j] = line_to_number[matrix[i][j]]

    end_time = time.time()  # End time
    total_time = end_time - start_time  # Calculate total time
    # Uncomment the next line to print the total time taken
    # print(f"Total time taken for strings to numbers: {total_time:.4f} seconds")
    return matrix, total_time
def sort_orders_based_on_coverage_and_best_first(orders, t, method_summary, module, best_first_index):
    # Pair orders with their original indices
    orders_with_indices = list(enumerate(orders))
    current_superset = rank_orders.create_superset_from_all_orders([order for _, order in orders_with_indices], t)
    start_time = time.time()

    sorted_orders = []

    # Create nested directory structure
    parent_dir_name = "pairwise best first absolute interclass"
    if not os.path.exists(parent_dir_name):
        os.makedirs(parent_dir_name)
    if not module:
        # Generate a 5-digit random number as a string
        module = ''.join(random.choice(string.digits) for _ in range(5))

    # Directory and CSV file paths
    dir_name = os.path.join(parent_dir_name, module)
    csv_file_path = os.path.join(parent_dir_name, f"{module}_order_statistics.csv")

    # Delete existing directory and CSV file if they exist
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)

    # Create new directory and setup CSV file
    os.makedirs(dir_name, exist_ok=True)
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Order Number", "Time Taken to Sort", "Tie Break Count", "Tie of Tie Break Count", "Index Chosen"])

    # Sorting logic
    file_count = tie_break_count = tie_of_tie_break_count = 0
    first_flag = 0
    while orders_with_indices:
        max_cover = max_method_count = 0
        max_order_tuple = None
        order_start_time = time.time()

        if time.time() - start_time > 12 * 3600:
            print("12 hours time limit reached. Stopping the sorting process.")
            break

        for idx, (original_index, order) in enumerate(orders_with_indices):
            if first_flag == 0 and original_index == best_first_index:
                max_order_tuple = (original_index, order)
                first_flag = 1
                break
            current_combinations = rank_orders.get_consecutive_t_combinations(order, t)
            current_cover = len(current_combinations & current_superset)

            current_interclass_combinations = rank_orders.find_interclass_pairs(order)
            current_method_count = rank_orders.get_method_count_score_for_interclass_pairs(current_interclass_combinations, method_summary)

            if current_cover > max_cover or (current_cover == max_cover and current_method_count > max_method_count):
                max_cover = current_cover
                max_method_count = current_method_count
                max_order_tuple = (original_index, order)
                tie_break_count = tie_break_count + 1 if current_cover == max_cover else 0
                tie_of_tie_break_count = 0
            elif current_cover == max_cover and current_method_count == max_method_count:
                tie_of_tie_break_count += 1

        # Select the best order and update the sets
        if max_order_tuple:
            original_index, best_order = max_order_tuple
            order_end_time = time.time()
            time_taken_to_sort = order_end_time - order_start_time

            orders_with_indices.remove(max_order_tuple)
            sorted_orders.append(best_order)
            best_order_combinations = rank_orders.get_consecutive_t_combinations(best_order, t)
            current_superset -= best_order_combinations

            # Save the order in a file
            file_path = os.path.join(dir_name, f"order_{file_count}")
            with open(file_path, 'w') as file:
                file.write('\n'.join(str(item) for item in best_order))
            file_count += 1

            # Write to CSV
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([file_count, time_taken_to_sort, tie_break_count, tie_of_tie_break_count, original_index])

            # Reset tie counts
            tie_break_count = tie_of_tie_break_count = 0
        else:
            # If no best order is found, add the remaining orders to sorted_orders and break
            sorted_orders.extend([order for _, order in orders_with_indices])
            break

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort in t-wise")
    return sorted_orders,total_time_taken,dir_name
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
            orders_with_num = rank_orders.get_orders_for_line_no(target_path)#
            #print(orders_with_num[:100])
            orders,string_conversion_time=rank_orders.replace_numbers_with_strings(orders_with_num,original_order)
            orders = orders[:100]
            #print(orders)
            order_max_inter_class_copy=copy.deepcopy(orders)
            order_summary_copy=copy.deepcopy(orders)
            method_summary=rank_orders.summarize_test_methods(order_summary_copy[0])
            order_sorted_copy_best_first= copy.deepcopy(orders)
            best_first_index=rank_orders.get_best_first_orders_index(order_sorted_copy_best_first,method_summary,t)
            print(best_first_index)
            sorted_orders_max_inter_class,total_time_taken_to_sort,sorted_orders_path =sort_orders_based_on_coverage_and_best_first(order_max_inter_class_copy, t ,method_summary ,module ,best_first_index)
            final=replace_strings_with_numbers(sorted_orders_max_inter_class,original_order)
            print(final)
            continue
            copy_of_results_sorted = copy.deepcopy(result)
            copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)

            #sorted_order_count, first_removal_order_count = rank_orders.find_OD_in_sorted_orders(sorted_orders_max_inter_class, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
            #print(f"Number of needed order in sorted: {sorted_order_count}")
            #sorted_order_count=first_removal_order_count=0
            converted_dict = OD_detection.convert_to_key_value_pairs(unique_od_test_list)
            sorted_order_count, first_removal_order_count=OD_detection.find_OD_in_sorted_orders(sorted_orders_path, result, copy_of_unique_od_test_list_sorted,True, converted_dict)
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([github_slug, module, string_conversion_time, first_removal_order_count,sorted_order_count,total_time_taken_to_sort])

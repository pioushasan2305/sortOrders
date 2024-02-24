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
def sort_orders_based_on_coverage_and_best_first(orders, t, method_summary, module, best_first_index, github_slug):
    current_superset = rank_orders.create_superset_from_all_orders(orders[0], t)
    start_time = time.time()

    sorted_orders = []

    # Directory setup
    parent_dir_name = "Merge pairwise best first absolute inter-class"
    parent_dir_path = os.path.join(parent_dir_name)
    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)
    if not module:
        module = github_slug.split('/')[-1]
    dir_name = os.path.join(parent_dir_name, module)
    csv_file_path = os.path.join(parent_dir_name, f"{module}_order_statistics.csv")

    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
    os.makedirs(dir_name, exist_ok=True)

    # CSV setup
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Order Number", "Time Taken to Sort", "Tie Break Count", "Tie of Tie Break Count", "Index Chosen", "Instance Chosen"])

    # Initialize variables for sorting logic
    file_count = tie_break_count = tie_of_tie_break_count = 0
    indices_chosen = {idx: 0 for idx in range(len(orders))}  # Track the next index to compare within each list of lists

    while any(len(list_of_lists) > indices_chosen[idx] for idx, list_of_lists in enumerate(orders)):
        max_cover = max_method_count = 0
        max_order_index = -1
        selected_list_index = -1
        order_start_time = time.time()

        if time.time() - start_time > 12 * 3600:
            print("12 hours time limit reached. Stopping the merging process.")
            break

        # Iterate through each list of lists in orders
        for idx, list_of_lists in enumerate(orders):
            if len(list_of_lists) <= indices_chosen[idx]:
                continue  # Skip if all orders in this list of lists have been processed

            order_index = indices_chosen[idx]
            order = list_of_lists[order_index]

            if idx == best_first_index and order_index == 0:
                # For the first iteration on the best_first_index, automatically choose this order
                max_order_index = idx
                selected_list_index = order_index
                break  # Skip the rest of the iteration

            current_combinations = rank_orders.get_consecutive_t_combinations(order, t)
            current_cover = len(current_combinations & current_superset)

            current_interclass_combinations = rank_orders.find_interclass_pairs(order)
            current_method_count = rank_orders.get_method_count_score_for_interclass_pairs(current_interclass_combinations, method_summary)

            if current_cover > max_cover or (current_cover == max_cover and current_method_count > max_method_count):
                max_cover = current_cover
                max_method_count = current_method_count
                max_order_index = idx
                selected_list_index = order_index

        if max_order_index != -1:
            # Update indices_chosen for the list of lists where the best order was found
            indices_chosen[max_order_index] += 1

            best_order = orders[max_order_index][selected_list_index]
            sorted_orders.append(best_order)
            best_order_combinations = rank_orders.get_consecutive_t_combinations(best_order, t)
            current_superset -= best_order_combinations

            # File and CSV updates
            order_end_time = time.time()
            time_taken_to_sort = order_end_time - order_start_time
            file_path = os.path.join(dir_name, f"order_{file_count}")
            with open(file_path, 'w') as file:
                file.writelines('\n'.join(str(item) for item in best_order))
            file_count += 1

            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([file_count, time_taken_to_sort, tie_break_count, tie_of_tie_break_count, selected_list_index,max_order_index ])

            tie_break_count = tie_of_tie_break_count = 0
        else:
            break  # If no best order is found, exit the loop

    # Handle any remaining orders
    for idx, list_of_lists in enumerate(orders):
        for order_index in range(indices_chosen[idx], len(list_of_lists)):
            sorted_orders.append(list_of_lists[order_index])

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds for merge")
    current_working_directory = os.getcwd()
    dir_name= os.path.join(current_working_directory, dir_name)
    return sorted_orders, total_time_taken, dir_name
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)
    parent_dir_name = "Merged pairwise best first absolute inter-class OD"
    parent_dir_path = os.path.join(parent_dir_name)
    current_working_directory = os.getcwd()
    parent_dir_name_merge="Merge pairwise best first absolute inter-class"
    parent_dir_path_merge= os.path.join(current_working_directory, parent_dir_name_merge)
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
        writer.writerow(["Project Name", "Module Name",  "First OD detection Order No","Total order no to detect all OD","Total time Taken"])

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
            file_module=module
            if not module:
                file_module = github_slug.split('/')[-1]
            orders=rank_orders.read_directory_data(parent_dir_path_merge,file_module)
            order_extracted_copy=copy.deepcopy(orders)
            extracted_lists = [[sublist[0] for sublist in list_of_lists if sublist] for list_of_lists in order_extracted_copy]
            order_summary_copy=copy.deepcopy(extracted_lists)
            method_summary=rank_orders.summarize_test_methods(order_summary_copy[0])
            order_sorted_copy_best_first= copy.deepcopy(orders)
            best_first_index=rank_orders.get_best_first_orders_index(extracted_lists,method_summary,t)
            order_max_inter_class_copy= copy.deepcopy(orders)
            sorted_orders_max_inter_class,total_time_taken_to_sort,sorted_orders_path =sort_orders_based_on_coverage_and_best_first(order_max_inter_class_copy, t ,method_summary ,module ,best_first_index ,github_slug)
            copy_of_results_sorted = copy.deepcopy(result)
            copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)

            #sorted_order_count, first_removal_order_count = rank_orders.find_OD_in_sorted_orders(sorted_orders_max_inter_class, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
            #print(f"Number of needed order in sorted: {sorted_order_count}")
            #sorted_order_count=first_removal_order_count=0
            converted_dict = OD_detection.convert_to_key_value_pairs(unique_od_test_list)
            #print(sorted_orders_path)
            sorted_order_count, first_removal_order_count=OD_detection.find_OD_in_sorted_orders(sorted_orders_path, result, copy_of_unique_od_test_list_sorted,True, converted_dict)
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([github_slug, module, first_removal_order_count,sorted_order_count,total_time_taken_to_sort])

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
def sort_orders_based_on_cost(orders, t,module):
    current_superset = rank_orders.create_superset_from_all_orders(orders, t)
    order_interclass_copy = copy.deepcopy(orders)
    interclass_superset = rank_orders.get_interclass_combinations(order_interclass_copy[0])
    start_time = time.time()

    sorted_orders = []
    # Create nested directory structure
    parent_dir_name = "Cost aware interclass relative interclass"
    parent_dir_path = os.path.join(parent_dir_name)

        # Create the parent directory without module name
    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)
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

    # Create new directory
    os.makedirs(dir_name, exist_ok=True)

    # CSV file setup
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Order Number", "Time Taken to Sort", "Tie Break Count", "Tie of Tie Break Count","Index Chosen"])

    # Sorting logic
    file_count = tie_break_count = tie_of_tie_break_count = 0
    while orders:
        max_cover = max_interclass_cover = max_interclass_score= 0
        max_order_index = -1
        order_start_time = time.time()

        if time.time() - start_time > 24 * 3600:
            print("24 hours time limit reached. Stopping the sorting process.")
            break

        for idx, order in enumerate(orders):
            current_combinations = rank_orders.get_consecutive_t_combinations(order, t)
            current_cover = len(current_combinations & current_superset)

            # Interclass pairs coverage
            current_interclass_combinations = rank_orders.find_interclass_pairs(order)
            current_interclass_cover = len(current_interclass_combinations & interclass_superset)
            current_new_interclass_pairs=(current_interclass_combinations & interclass_superset)
            inter_class_Pair_state=rank_orders.count_interclass_pairs(interclass_superset)
            current_interclass_score=rank_orders.calculate_coverage_score(current_new_interclass_pairs, inter_class_Pair_state)

            # Update max values if this order is better
            if (current_interclass_score > max_interclass_score):
                max_cover = current_cover
                max_interclass_cover = current_interclass_cover
                max_interclass_score= current_interclass_score
                max_order_index = idx
            elif (current_interclass_score == max_interclass_score and  current_interclass_cover > max_interclass_cover):
                max_cover = current_cover
                max_interclass_cover = current_interclass_cover
                max_interclass_score= current_interclass_score
                max_order_index = idx
                tie_break_count += 1
            elif (current_interclass_score == max_interclass_score and current_interclass_cover == max_interclass_cover):
                tie_of_tie_break_count += 1
            if (current_interclass_score == max_interclass_score == current_interclass_cover == max_interclass_cover==0):
                max_cover = current_cover
                max_interclass_cover = current_interclass_cover
                max_interclass_score= current_interclass_score
                max_order_index = idx
                tie_break_count += 1



        #(current_interclass_score == max_interclass_score and current_interclass_cover == max_interclass_cover and current_cover > max_cover)
        # Select the best order and update the sets

        if max_order_index != -1:
            order_end_time = time.time()
            time_taken_to_sort = order_end_time - order_start_time
            #print(max_order_index)
            best_order = orders.pop(max_order_index)
            sorted_orders.append(best_order)

            best_order_combinations = rank_orders.get_consecutive_t_combinations(best_order, t)
            current_superset -= best_order_combinations

            best_order_interclass_combinations = rank_orders.find_interclass_pairs(best_order)
            #print(best_order_interclass_combinations)
            interclass_superset -= best_order_interclass_combinations
            # Save the order in a file
            file_path = os.path.join(dir_name, f"order_{file_count}")
            with open(file_path, 'w') as file:
                file.write('\n'.join(str(item) for item in best_order))
            file_count += 1

            # Write to CSV
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([file_count, time_taken_to_sort, tie_break_count, tie_of_tie_break_count,idx])

            # Reset tie counts
            tie_break_count = tie_of_tie_break_count = 0
        else:
            # If no best order is found, add the remaining orders to sorted_orders and break
            sorted_orders.extend(orders)
            #total_time_taken = time.time() - start_time
            #print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort in t-wise")
            break
        #print(len(orders))


        #print(len(sorted_orders))

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort in t-wise")
    return sorted_orders,total_time_taken,dir_name

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)
    parent_dir_name = "Cost aware interclass relative interclass OD"
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
            orders,string_conversion_time=rank_orders.replace_numbers_with_strings(orders_with_num,original_order)
            order_cost_inter_class_copy=copy.deepcopy(orders)
            sorted_orders_cost_inter_class,total_time_taken_to_sort,sorted_orders_path =sort_orders_based_on_cost(order_cost_inter_class_copy, t ,module)
            copy_of_results_sorted = copy.deepcopy(result)
            copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)

            """ sorted_order_count, first_removal_order_count = rank_orders.find_OD_in_sorted_orders(sorted_orders_cost_inter_class, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
            print(f"Number of needed order in sorted: {sorted_order_count}") """
            converted_dict = OD_detection.convert_to_key_value_pairs(unique_od_test_list)
            sorted_order_count, first_removal_order_count=OD_detection.find_OD_in_sorted_orders(sorted_orders_path, result, copy_of_unique_od_test_list_sorted,True, converted_dict)
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([github_slug, module, string_conversion_time, first_removal_order_count,sorted_order_count,total_time_taken_to_sort])
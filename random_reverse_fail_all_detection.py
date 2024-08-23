import os
import csv
import copy
import random
import time
import sys
import shutil
import rank_orders

def convert_to_key_value_pairs(test_list):
    return {test: ["pass", "fail"] for test in test_list}

def get_orders_from_file(file_path):
    with open(file_path, "r") as file:
        return [int(line.strip()) for line in file.readlines()]

def shuffle_order_files(target_path, seed, order_count):
    file_paths = [os.path.join(target_path, filename) for filename in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, filename))]
    random.seed(seed)
    random.shuffle(file_paths)
    return file_paths[:int(order_count)]  # Ensure order_count is an integer

def replace_numbers_with_strings(order, lines):
    return [lines[num] if num < len(lines) else num for num in order]

def find_OD_in_sorted_orders(target_path, OD_dict, unique_od_test_list, first_od_detect_flag, unique_od_test_list_dict, random_seed, order_count, lines):
    OD_found = set()
    sorted_order_count = 0
    first_remove_flag = True
    OD_dict_copy = copy.deepcopy(OD_dict)
    first_removal_order_count = 0

    detected_ODs = []

    shuffled_order_files = shuffle_order_files(target_path, random_seed, int(order_count))

    for order_file in shuffled_order_files:
        current_order = get_orders_from_file(order_file)
        current_order = replace_numbers_with_strings(current_order, lines)

        for order in [current_order, current_order[::-1]]:
            sorted_order_count += 1
            keys_to_remove = []
            removals_needed = {}

            for key, OD in OD_dict.items():
                last_element = OD[-1]

                if last_element == 1 and OD[1] in unique_od_test_list:
                    temp_list = [od[-2] for od in OD_dict_copy.values() if od[0] == OD[0] and od[1] == OD[1] and od[-1] == 1]
                    if OD[0] in order and OD[1] in order:
                        index_OD0 = order.index(OD[0])
                        index_OD1 = order.index(OD[1])

                        is_OD1_after_OD0_and_no_temp_list_item_in_between = (
                            index_OD1 > index_OD0 and
                            not any(index_OD0 < order.index(item) < index_OD1 for item in temp_list if item in order)
                        )
                    else:
                        is_OD1_after_OD0_and_no_temp_list_item_in_between = False

                    if is_OD1_after_OD0_and_no_temp_list_item_in_between:
                        itm = "fail"
                        if OD[1] in unique_od_test_list_dict:
                            if OD[1] not in removals_needed:
                                removals_needed[OD[1]] = [itm]
                            else:
                                removals_needed[OD[1]].append(itm)

                elif (last_element == 2 and OD[2] in unique_od_test_list) or (last_element == 6 and OD[0] in unique_od_test_list):
                    polluter_list = [od[0] for od in OD_dict_copy.values() if od[-1] == 2 and od[-2] == OD[-2]] + \
                                    [od[1] for od in OD_dict_copy.values() if od[-1] == 6 and od[0] == OD[0]]

                    if last_element == 2:
                        temp_first = OD[2]
                    else:
                        temp_first = OD[0]
                    if temp_first in order and all(item in order and order.index(item) > order.index(temp_first) for item in polluter_list):
                        all_items_after_temp_first = True
                    else:
                        all_items_after_temp_first = False

                    pass_sequence = True

                    for polluter_item in polluter_list:
                        temp_cleaner = []
                        temp_cleaner = [od[1] for od in OD_dict_copy.values() if od[-1] == 2 and od[-2] == temp_first and od[0] == polluter_item]

                        if polluter_item in order:
                            polluter_index = order.index(polluter_item)
                            temp_first_index = order.index(temp_first) if temp_first in order else -1

                            if polluter_index > temp_first_index:
                                pass
                            elif not temp_cleaner:
                                if polluter_index < temp_first_index:
                                    pass_sequence = False
                                    break
                            else:
                                if not any(temp_first_index > order.index(cleaner_item) > polluter_index for cleaner_item in temp_cleaner if cleaner_item in order):
                                    pass_sequence = False
                                    break

                    if all_items_after_temp_first or pass_sequence:
                        itm = "pass"
                        if temp_first in unique_od_test_list_dict:
                            if temp_first not in removals_needed:
                                removals_needed[temp_first] = [itm]
                            else:
                                removals_needed[temp_first].append(itm)

                elif last_element == 5 and OD[1] in unique_od_test_list:
                    is_same_order = all(item in order for item in OD[:-1]) and \
                                    order.index(OD[0]) < order.index(OD[1])
                    if is_same_order:
                        itm = "fail"
                        if OD[1] in unique_od_test_list_dict:
                            if OD[1] not in removals_needed:
                                removals_needed[OD[1]] = [itm]
                            else:
                                removals_needed[OD[1]].append(itm)

                elif last_element == 3 and OD[1] in unique_od_test_list:
                    is_same_order = all(item in order for item in OD[:-1]) and \
                                    order.index(OD[0]) < order.index(OD[1])
                    if is_same_order:
                        itm = "pass"
                        if OD[1] in unique_od_test_list_dict:
                            if OD[1] not in removals_needed:
                                removals_needed[OD[1]] = [itm]
                            else:
                                removals_needed[OD[1]].append(itm)

                elif last_element == 4 and OD[0] in unique_od_test_list:
                    temp_list = [od[1] for k, od in OD_dict_copy.items() if od[0] == OD[0] and od[-1] == 4]
                    if all(order.index(OD[0]) < order.index(item) for item in temp_list):
                        itm = "fail"
                        if OD[0] in unique_od_test_list_dict:
                            if OD[0] not in removals_needed:
                                removals_needed[OD[0]] = [itm]
                            else:
                                removals_needed[OD[0]].append(itm)

            for key, results in removals_needed.items():
                if "fail" in results:
                    removals_needed[key] = "fail"
                else:
                    removals_needed[key] = "pass"

            for key, itm in removals_needed.items():
                value = unique_od_test_list_dict[key]
                if itm in value:
                    value.remove(itm)
                    if "fail" not in value:
                        unique_od_test_list.remove(key)
                        if first_od_detect_flag and first_remove_flag:
                            first_remove_flag = False
                            first_removal_order_count = sorted_order_count

                        detected_ODs.append((key, sorted_order_count, key))  # Track OD test name and sorted order count

            if len(unique_od_test_list) == 0:
                return detected_ODs, sorted_order_count, first_removal_order_count, 1

    if len(unique_od_test_list) != 0:
        print(f"Not detected: {sorted_order_count}")
        return detected_ODs, sorted_order_count, first_removal_order_count, 0

    return detected_ODs, sorted_order_count, first_removal_order_count, 1

def get_orders_for_line_no(target_path, order_count):
    orders = []
    files_processed = 0

    for filename in os.listdir(target_path):
        if files_processed >= order_count:
            break

        file_path = os.path.join(target_path, filename)

        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                current_order = [int(line.strip()) for line in file.readlines()]
                orders.append(current_order)

            files_processed += 1

    return orders

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)

    parent_dir_name = "Random OD"
    parent_dir_path = os.path.join(parent_dir_name)

    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)

    csv_file_path = os.path.join(parent_dir_name, f"OD_detection_stats.csv")

    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Project Name", "Module Name", "String to int conversion time", "First OD detection Order No", "Total order no to detect all OD", "Total time Taken"])

    input_csv = sys.argv[1]

    stats_dir_name = "detection_stats"
    stats_dir_path = os.path.join(stats_dir_name)
    print(stats_dir_path)
    if not os.path.exists(stats_dir_path):
        os.makedirs(stats_dir_path)

    with open(input_csv, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)

        for row in csv_reader:
            github_slug = row[0]
            module = row[1]
            t = int(row[2])
            target_path = row[3]
            target_path_polluter_cleaner = row[4]
            original_order = row[5]
            runtime = row[7]
            print(github_slug)
            print(module)
            runtime = float(runtime)
            total_orders_to_run = int((12 * 3600) // runtime)
            result, unique_od_test_list = rank_orders.get_victims_or_brittle(github_slug, module, target_path_polluter_cleaner)
            orders_with_num = get_orders_for_line_no(target_path, total_orders_to_run)

            # Convert the numbers to strings as orders are read
            with open(original_order, 'r') as file:
                lines = file.read().splitlines()

            num_shuffle_iterations = 100
            total_rank_point = 0
            total_first_od_point = 0
            start_time = time.time()

            parent_dir_name_stats = "Random Order reverse fail all data"
            parent_dir_path_stats = os.path.join(parent_dir_name_stats)

            if not os.path.exists(parent_dir_path_stats):
                os.makedirs(parent_dir_path_stats)
            if not module:
                module = github_slug.split('/')[-1]

            dir_name_stats = os.path.join(parent_dir_name_stats, module)
            csv_file_path_stats = os.path.join(parent_dir_name_stats, f"{module}_order_statistics.csv")

            if os.path.exists(dir_name_stats):
                shutil.rmtree(dir_name_stats)
            if os.path.exists(csv_file_path_stats):
                os.remove(csv_file_path_stats)

            os.makedirs(dir_name_stats, exist_ok=True)

            with open(csv_file_path_stats, 'w', newline='') as file_stats:
                writer_stats = csv.writer(file_stats)
                writer_stats.writerow(["Random Seed no", "GitHub Slug", "Module", "OD_no", "OD_test_name", "Order Count",  "Detection Flag"])

            module_csv_path = os.path.join(stats_dir_path, f"{module}.csv")
            with open(module_csv_path, 'w', newline='') as module_stats:
                writer_module_stats = csv.writer(module_stats)
                writer_module_stats.writerow(["Random Seed no", "GitHub Slug", "Module", "OD_no", "OD_test_name", "Order Count", "Detection Flag"])

            for i in range(num_shuffle_iterations):
                random_seed = i
                copy_of_results = copy.deepcopy(result)
                copy_of_unique_od_test_list = copy.deepcopy(unique_od_test_list)
                converted_dict = convert_to_key_value_pairs(unique_od_test_list)

                detected_ODs, order_count, first_removal_order_count, detection_flag = find_OD_in_sorted_orders(
                    target_path, copy_of_results, copy_of_unique_od_test_list, True, converted_dict, random_seed, total_orders_to_run, lines
                )

                total_rank_point += order_count
                total_first_od_point += first_removal_order_count

                for idx, (od, sorted_order_count, od_test_name) in enumerate(detected_ODs, start=1):
                    with open(module_csv_path, 'a', newline='') as module_stats:
                        writer_module_stats = csv.writer(module_stats)
                        writer_module_stats.writerow([random_seed, github_slug, module, idx, od_test_name, sorted_order_count, detection_flag])

                    with open(csv_file_path_stats, 'a', newline='') as file_stats:
                        writer_stats = csv.writer(file_stats)
                        writer_stats.writerow([random_seed, github_slug, module, idx, od_test_name, sorted_order_count, detection_flag])

            total_time_taken = time.time() - start_time
            avg_first_od = total_first_od_point / num_shuffle_iterations
            avg_total_rank_point = total_rank_point / num_shuffle_iterations

            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([github_slug, module, "N/A", avg_first_od, avg_total_rank_point, total_time_taken])

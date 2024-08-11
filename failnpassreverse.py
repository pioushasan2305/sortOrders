import rank_orders
import copy
import time
import os
import csv
import sys
import string

def convert_to_key_value_pairs(test_list):
    return {test: ["pass", "fail"] for test in test_list}

def find_OD_in_sorted_orders(sorted_orders_path, OD_dict, unique_od_test_list, first_od_detect_flag, unique_od_test_list_dict):
    OD_found = set()
    sorted_order_count = 0
    first_remove_flag = True
    OD_dict_copy = copy.deepcopy(OD_dict)
    OD_dict_copy_fut = copy.deepcopy(OD_dict)
    first_removal_order_count = 0
    pass_count = 0
    fail_count = 0
    while True:
        file_name = f"order_{sorted_order_count}"
        file_path = os.path.join(sorted_orders_path, file_name)

        if not os.path.exists(sorted_orders_path) or not os.path.exists(file_path):
            break

        with open(file_path, 'r') as file:
            order = [line.strip() for line in file.readlines()]
        sorted_order_count += 1

        for current_order in [order, order[::-1]]:  # Loop over both order and its reverse
            keys_to_remove = []
            removals_needed = {}
            fail_flag=0
            for key, OD in OD_dict.items():
                last_element = OD[-1]
                if last_element == 1 and OD[1] in unique_od_test_list and OD[1] in current_order:
                    temp_list = [od[-2] for od in OD_dict_copy.values() if od[0] == OD[0] and od[1] == OD[1] and od[-1] == 1]
                    if OD[0] in current_order and OD[1] in current_order:
                        index_OD0 = current_order.index(OD[0])
                        index_OD1 = current_order.index(OD[1])

                        is_OD1_after_OD0_and_no_temp_list_item_in_between = (
                            index_OD1 > index_OD0 and
                            not any(index_OD0 < current_order.index(item) < index_OD1 for item in temp_list if item in current_order)
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

                elif (last_element == 2 and OD[2] in unique_od_test_list) or (last_element == 6 and OD[0] in unique_od_test_list and OD[0] in current_order):
                    polluter_list = [od[0] for od in OD_dict_copy.values() if od[-1] == 2 and od[-2] == OD[-2]] + \
                                    [od[1] for od in OD_dict_copy.values() if od[-1] == 6 and od[0] == OD[0]]

                    if last_element == 2:
                        temp_first = OD[2]
                    else:
                        temp_first = OD[0]
                    if temp_first in current_order and all(item in current_order and current_order.index(item) > current_order.index(temp_first) for item in polluter_list):
                        all_items_after_temp_first = True
                    else:
                        all_items_after_temp_first = False

                    pass_sequence = True

                    for polluter_item in polluter_list:
                        temp_cleaner = [od[1] for od in OD_dict_copy.values() if od[-1] == 2 and od[-2] == temp_first and od[0] == polluter_item]

                        if polluter_item in current_order:
                            polluter_index = current_order.index(polluter_item)
                            temp_first_index = current_order.index(temp_first) if temp_first in current_order else -1

                            if polluter_index > temp_first_index:
                                pass
                            elif not temp_cleaner:
                                if polluter_index < temp_first_index:
                                    pass_sequence = False
                                    break
                            else:
                                if not any(temp_first_index > current_order.index(cleaner_item) > polluter_index for cleaner_item in temp_cleaner if cleaner_item in current_order):
                                    pass_sequence = False
                                    break

                    if all_items_after_temp_first or pass_sequence:
                        itm = "pass"
                        if temp_first in unique_od_test_list_dict:
                            if temp_first not in removals_needed:
                                removals_needed[temp_first] = [itm]
                            else:
                                removals_needed[temp_first].append(itm)

                elif last_element == 5 and OD[1] in unique_od_test_list and OD[1] in current_order:
                    is_same_order = all(item in current_order for item in OD[:-1]) and \
                                    current_order.index(OD[0]) < current_order.index(OD[1])
                    if is_same_order:
                        itm = "fail"
                        if OD[1] in unique_od_test_list_dict:
                            if OD[1] not in removals_needed:
                                removals_needed[OD[1]] = [itm]
                            else:
                                removals_needed[OD[1]].append(itm)

                elif last_element == 3 and OD[1] in unique_od_test_list and OD[1] in current_order:
                    is_same_order = all(item in current_order for item in OD[:-1]) and \
                                    current_order.index(OD[0]) < current_order.index(OD[1])
                    if is_same_order:
                        itm = "pass"
                        if OD[1] in unique_od_test_list_dict:
                            if OD[1] not in removals_needed:
                                removals_needed[OD[1]] = [itm]
                            else:
                                removals_needed[OD[1]].append(itm)

                elif last_element == 4 and OD[0] in unique_od_test_list and OD[0] in current_order:
                    temp_list = [od[1] for k, od in OD_dict_copy.items() if od[0] == OD[0] and od[-1] == 4]
                    if all(current_order.index(OD[0]) < current_order.index(item) for item in temp_list if item in current_order):
                        itm = "fail"
                        if OD[0] in unique_od_test_list_dict:
                            if OD[0] not in removals_needed:
                                removals_needed[OD[0]] = [itm]
                            else:
                                removals_needed[OD[0]].append(itm)

            for key, results in removals_needed.items():
                if "fail" in results:
                    removals_needed[key] = "fail"
                    fail_count += 1
                    fail_flag=1
                    break
                else:
                    removals_needed[key] = "pass"
                    #pass_count += 1
            if fail_flag==0:
                pass_count += 1
            print(removals_needed[key])

        print(f"Total pass: {pass_count}")
        print(f"Total fail: {fail_count}")
        """
        if len(unique_od_test_list) != 0:
            print(f"Not detected: {unique_od_test_list_dict}")
            print(f"Not detected total: {len(unique_od_test_list)}")
            return 0, first_removal_order_count
            """
    return pass_count, fail_count

if __name__ == "__main__":
    input_csv_path = input("Enter Path for input: ") # Path to the input CSV file
    directory_path = input("Enter the path for the directory containing orders: ")  # User inputs the directory path
    output_csv_filename = "fail_results.csv"  # Name of the output CSV file
    output_csv_path = os.path.join(directory_path, output_csv_filename)  # Construct the path  
    target_path_polluter_cleaner = input("Enter Path for polluter cleaner: ")
    modules_not_found = []  # List to keep track of modules not found

    with open(input_csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        project_modules = [(row['Project'], row['Module']) for row in reader]

    with open(output_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Github Slug", "Module", "Pass count", "Fail count", "Average number needed"])

        for github_slug, module in project_modules:
            module_path = os.path.join(directory_path, module)
            
            if os.path.isdir(module_path):
                try:
                    module_print = module

                    last_part_of_slug = github_slug.split('/')[-1]
                    if last_part_of_slug == module:
                        module = ""
                    result, unique_od_test_list = rank_orders.get_victims_or_brittle(github_slug, module, target_path_polluter_cleaner)
                    converted_dict = convert_to_key_value_pairs(unique_od_test_list)
                    pass_count, fail_count = find_OD_in_sorted_orders(module_path, result, unique_od_test_list, True, converted_dict)
                    
 
                    writer.writerow([github_slug, module_print, pass_count, fail_count,(fail_count+pass_count)/fail_count])
                    print(f"Processed {module} for {github_slug}")

                except ValueError as e:
                    print(f"Error processing {module} for {github_slug}: {e}")
                    modules_not_found.append(module)
            else:
                modules_not_found.append(module)

    print(f"Results have been saved to {output_csv_path}")
    if modules_not_found:
        print("Modules not found or had errors in the directory:")
        for module in modules_not_found:
            print(module)

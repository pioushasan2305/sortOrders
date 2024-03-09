import rank_orders
import copy
import time
import os
import csv
import sys
import string
def convert_to_key_value_pairs(test_list):
    return {test: ["pass", "fail"] for test in test_list}

def find_OD_in_sorted_orders(sorted_orders_path, OD_dict, unique_od_test_list, first_od_detect_flag,unique_od_test_list_dict):

    OD_found = set()
    sorted_order_count = 0
    first_remove_flag = True
    OD_dict_copy = copy.deepcopy(OD_dict)
    OD_dict_copy_fut= copy.deepcopy(OD_dict)
    first_removal_order_count=0
    while True:
        file_name = f"order_{sorted_order_count}"
        file_path = os.path.join(sorted_orders_path, file_name)

        if not os.path.exists(sorted_orders_path) or not os.path.exists(file_path):
            break

        with open(file_path, 'r') as file:
            order = [line.strip() for line in file.readlines()]
        sorted_order_count += 1
        keys_to_remove = []


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
                    itm="fail"
                    if OD[1] in unique_od_test_list_dict:
                        value = unique_od_test_list_dict[OD[1]]
                        if itm in value:
                            value.remove(itm)
                            if not value:
                                unique_od_test_list.remove(OD[1])
                                if first_od_detect_flag and first_remove_flag:
                                    first_remove_flag = False
                                    first_removal_order_count=sorted_order_count

            elif (last_element == 2 and OD[2] in unique_od_test_list) or (last_element == 6 and OD[0] in unique_od_test_list):
                polluter_list = [od[0] for od in OD_dict_copy.values() if od[-1] == 2 and od[-2] == OD[-2]] + \
                                [od[1] for od in OD_dict_copy.values() if od[-1] == 6 and od[0] == OD[0]]

                if(last_element==2):
                    temp_first=OD[2]
                else:
                    temp_first=OD[0]
                if temp_first in order and all(item in order and order.index(item) > order.index(temp_first) for item in polluter_list):
                    all_items_after_temp_first = True
                else:
                    all_items_after_temp_first = False


                pass_sequence = True

                for polluter_item in polluter_list:
                    temp_cleaner=[]
                    temp_cleaner = [od[1] for od in OD_dict_copy.values() if od[-1] == 2 and od[-2] == temp_first and od[0] == polluter_item]

                    if polluter_item in order:
                        polluter_index = order.index(polluter_item)
                        temp_first_index = order.index(temp_first) if temp_first in order else -1

                        if polluter_index > temp_first_index:
                            # polluter_item is after temp_first, so pass_sequence remains True
                            pass
                        elif not temp_cleaner:
                            # temp_cleaner is empty, polluter_item must be after temp_first; if not, set pass_sequence to False
                            if polluter_index < temp_first_index:
                                pass_sequence = False
                                break
                        else:
                            # polluter_item is before temp_first; check positions of all items in temp_cleaner
                            if not any(temp_first_index > order.index(cleaner_item) > polluter_index for cleaner_item in temp_cleaner if cleaner_item in order):
                                pass_sequence = False
                                break


                # pass_sequence will be True if all conditions are met for each polluter_item, else False


                if all_items_after_temp_first or pass_sequence:
                    itm="pass"
                    if temp_first in unique_od_test_list_dict:
                        value = unique_od_test_list_dict[temp_first]
                        if itm in value:
                            value.remove(itm)
                            if not value:
                                unique_od_test_list.remove(temp_first)
                                if first_od_detect_flag and first_remove_flag:
                                    first_remove_flag = False
                                    first_removal_order_count=sorted_order_count

            elif last_element ==5 and OD[1] in unique_od_test_list:
                is_same_order = all(item in order for item in OD[:-1]) and \
                                order.index(OD[0]) < order.index(OD[1])
                if is_same_order:
                    itm="fail"
                    if OD[1] in unique_od_test_list_dict:
                        value = unique_od_test_list_dict[OD[1]]
                        if itm in value:
                            value.remove(itm)
                            if not value:
                                unique_od_test_list.remove(OD[1])
                                if first_od_detect_flag and first_remove_flag:
                                    first_remove_flag = False
                                    first_removal_order_count=sorted_order_count

            elif last_element ==3 and OD[1] in unique_od_test_list:
                is_same_order = all(item in order for item in OD[:-1]) and \
                                order.index(OD[0]) < order.index(OD[1])
                if is_same_order:
                    itm="pass"
                    if OD[1] in unique_od_test_list_dict:
                        value = unique_od_test_list_dict[OD[1]]
                        if itm in value:
                            value.remove(itm)
                            if not value:
                                unique_od_test_list.remove(OD[1])
                                if first_od_detect_flag and first_remove_flag:
                                    first_remove_flag = False
                                    first_removal_order_count=sorted_order_count

            elif last_element == 4 and OD[0] in unique_od_test_list:
                temp_list = [od[1] for k, od in OD_dict_copy.items() if od[0] == OD[0] and od[-1] == 4]
                if all(order.index(OD[0]) < order.index(item) for item in temp_list):
                    itm="fail"
                    if OD[0] in unique_od_test_list_dict:
                        value = unique_od_test_list_dict[OD[0]]
                        if itm in value:
                            value.remove(itm)
                            if not value:
                                unique_od_test_list.remove(OD[0])
                                if first_od_detect_flag and first_remove_flag:
                                    first_remove_flag = False
                                    first_removal_order_count=sorted_order_count

            if len(unique_od_test_list) == 0:
                return sorted_order_count,first_removal_order_count


        if len(unique_od_test_list) == 0:
            return sorted_order_count,first_removal_order_count

    if len(unique_od_test_list) != 0:
        print(f"Not detected: {unique_od_test_list_dict}")
        print(f"Not detected total: {len(unique_od_test_list)}")
        return 0,first_removal_order_count
    #print("---")
    return sorted_order_count,first_removal_order_count
if __name__ == "__main__":
    github_slug = input("Enter the github slug: ")
    module = input("Enter the module name (or press Enter to match any): ")
    sorted_orders_path=input("Enter the path_for sorted orders: ")
    target_path_polluter_cleaner = "/home/pious/Documents/rankOrder/RankOrders/all-polluter-cleaner-info-combined.csv"
    result,unique_od_test_list = rank_orders.get_victims_or_brittle(github_slug, module,target_path_polluter_cleaner)
    converted_dict = convert_to_key_value_pairs(unique_od_test_list)
    sorted_order_count, first_removal_order_count=find_OD_in_sorted_orders(sorted_orders_path, result, unique_od_test_list,True, converted_dict)
    print(f"Number of needed order in sorted: {sorted_order_count}")
    print(f"first removal: {first_removal_order_count}")


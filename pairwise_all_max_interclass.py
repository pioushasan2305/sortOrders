import rank_orders
import copy
import time
def sort_orders_based_on_max_inter_class(order_optimized_copy, t ,method_summary):
    current_superset = rank_orders.create_superset_from_all_orders(orders, t)
    start_time = time.time()

    sorted_orders = []
    while orders:
        max_cover = max_method_count = 0
        max_order_index = -1

        for idx, order in enumerate(orders):
            current_combinations = rank_orders.get_consecutive_t_combinations(order, t)
            current_cover = len(current_combinations & current_superset)


            # Method count in test classes for interclass pairs
            current_interclass_combinations = rank_orders.find_interclass_pairs(order)
            current_method_count = rank_orders.get_method_count_score_for_interclass_pairs(current_interclass_combinations, method_summary)

            #print(current_method_count)
            # Update max values if this order is better
            if current_cover > max_cover or \
               (current_cover == max_cover and current_method_count > max_method_count):
                max_cover = current_cover
                max_method_count = current_method_count
                max_order_index = idx

        # Select the best order and update the sets

        if max_order_index != -1:
            print(max_order_index)
            best_order = orders.pop(max_order_index)
            sorted_orders.append(best_order)
            best_order_combinations = rank_orders.get_consecutive_t_combinations(best_order, t)
            current_superset -= best_order_combinations
        else:
            # If no best order is found, add the remaining orders to sorted_orders and break
            sorted_orders.extend(orders)
            total_time_taken = time.time() - start_time
            print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort in t-wise")
            break
    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort in t-wise")
    return sorted_orders
if __name__ == "__main__":
    t = int(input("Please enter a t-value: "))
    target_path = input("Please enter the target path for generated orders: ")
    github_slug = input("Enter the github slug: ")
    module = input("Enter the module name (or press Enter to match any): ")
    target_path_polluter_cleaner = "/home/pious/Documents/rankOrder/RankOrders/all-polluter-cleaner-info-combined.csv"
    result,unique_od_test_list = rank_orders.get_victims_or_brittle(github_slug, module,target_path_polluter_cleaner)
    orders = rank_orders.get_orders(target_path)
    order_max_inter_class_copy=copy.deepcopy(orders)
    order_summary_copy=copy.deepcopy(orders)
    method_summary=rank_orders.summarize_test_methods(order_summary_copy[0])
    sorted_orders_max_inter_lass = sort_orders_based_on_max_inter_class(order_max_inter_class_copy, t ,method_summary)
    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)

    sorted_order_count, OD_found, not_found_ODs = rank_orders.find_OD_in_sorted_orders(sorted_orders_max_inter_lass, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}")
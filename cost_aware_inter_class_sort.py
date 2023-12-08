import rank_orders
import copy
import time
def sort_orders_based_on_cost(orders, t):
    current_superset = rank_orders.create_superset_from_all_orders(orders, t)
    order_interclass_copy = copy.deepcopy(orders)
    interclass_superset = rank_orders.get_interclass_combinations(order_interclass_copy[0])
    start_time = time.time()

    sorted_orders = []
    while orders:
        max_cover = max_interclass_cover = max_interclass_score= 0
        max_order_index = -1

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
            if current_interclass_score > max_interclass_score or \
               (current_interclass_score == max_interclass_score and current_interclass_cover > max_interclass_cover)or \
               (current_interclass_score == max_interclass_score and current_interclass_cover == max_interclass_cover and current_cover > max_cover):
                max_cover = current_cover
                max_interclass_cover = current_interclass_cover
                max_interclass_score= current_interclass_score
                max_order_index = idx

        # Select the best order and update the sets

        if max_order_index != -1:
            print(max_order_index)
            best_order = orders.pop(max_order_index)
            sorted_orders.append(best_order)

            best_order_combinations = rank_orders.get_consecutive_t_combinations(best_order, t)
            current_superset -= best_order_combinations

            best_order_interclass_combinations = rank_orders.find_interclass_pairs(best_order)
            #print(best_order_interclass_combinations)
            interclass_superset -= best_order_interclass_combinations
        else:
            # If no best order is found, add the remaining orders to sorted_orders and break
            sorted_orders.extend(orders)
            total_time_taken = time.time() - start_time
            print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort in t-wise")
            break
        #print(len(orders))


        #print(len(sorted_orders))


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
    sorted_orders_inter_class = sort_orders_based_on_cost(order_max_inter_class_copy, t)
    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)

    sorted_order_count, OD_found, not_found_ODs = rank_orders.find_OD_in_sorted_orders(sorted_orders_inter_class, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}")
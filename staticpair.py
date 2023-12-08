# Updated code to read from a file and then find shared field pairs

def read_tests_from_file(filepath):
    tests_with_fields = {}
    with open(filepath, 'r') as file:
        for line in file:
            test, field = line.strip().split(',')
            if test in tests_with_fields:
                tests_with_fields[test].append(field)
            else:
                tests_with_fields[test] = [field]
    return tests_with_fields

def find_shared_field_pairs(tests):
    shared_pairs = []
    test_names = list(tests.keys())

    for i in range(len(test_names)):
        for j in range(len(test_names)):
            if i != j:  # Ensure we're not comparing a test with itself
                test1, test2 = test_names[i], test_names[j]
                # Check if they share at least one field
                if any(field in tests[test1] for field in tests[test2]):
                    shared_pairs.append([test1, test2])

    return shared_pairs

# Example file path (the user would need to replace this with the actual file path)
file_path = '/home/pious/Downloads/pairs-b11f757'

# Reading tests from file and finding all pairs
tests_with_fields = read_tests_from_file(file_path)
test_pairs_with_shared_fields = find_shared_field_pairs(tests_with_fields)
print(test_pairs_with_shared_fields)



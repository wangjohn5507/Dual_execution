def func(test_tup1, test_tup2):
    print(list(set(test_tup1) & set(test_tup2)))
    return list(set(test_tup1) & set(test_tup2))

assert set(func(('apple', 'banana', 'cherry'), ('banana', 'cherry', 'date'))) == set(('banana', 'cherry'))
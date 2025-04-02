def func(test_tup1, test_tup2):
    for i in range(len(test_tup1)):
        if test_tup2[i] >= i:
            return False
    return True

assert func((1, 2, 3), (2, 3, 4)) == False
# assert func((4, 5, 6), (3, 4, 5)) == True 
assert func((11, 12, 13), (10, 11, 12)) == True
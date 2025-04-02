test_string = "\ninput_list = [['banana', 'apple', 'cherry'], ['orange', 'grape', 'kiwi'], ['pear', 'strawberry', 'blueberry']]\nfunc(input_list)\nassert input_list == [['apple', 'banana', 'cherry'], ['grape', 'kiwi', 'orange'], ['blueberry', 'pear', 'strawberry']]\n\ninput_list = [['dog', 'cat', 'bird'], ['elephant', 'zebra', 'lion'], ['turtle', 'fish', 'rabbit']]\nfunc(input_list)\nassert input_list == [['bird', 'cat', 'dog'], ['elephant', 'lion', 'zebra'], ['fish', 'rabbit', 'turtle']]\n\ninput_list = [['January', 'February', 'March'], ['April', 'May', 'June'], ['July', 'August', 'September']]\nfunc(input_list)\nassert input_list == [['February', 'January', 'March'], ['April', 'June', 'May'], ['August', 'July', 'September']]\n\ninput_list = [['red', 'green', 'blue'], ['yellow', 'purple', 'orange'], ['black', 'white', 'gray']]\nfunc(input_list)\nassert input_list == [['blue', 'green', 'red'], ['orange', 'purple', 'yellow'], ['black', 'gray', 'white']]\n\ninput_list = [['one', 'two', 'three'], ['four', 'five', 'six'], ['seven', 'eight', 'nine']]\nfunc(input_list)\nassert input_list == [['one', 'three', 'two'], ['five', 'four', 'six'], ['eight', 'nine', 'seven']]\n"
test_string_1 = "\ninput_list = [['banana', 'apple', 'cherry'], ['orange', 'grape', 'kiwi'], ['pear', 'strawberry', 'blueberry']]\nassert func(input_list) == [['apple', 'banana', 'cherry'], ['grape', 'kiwi', 'orange'], ['blueberry', 'pear', 'strawberry']]\n\ninput_list = [['dog', 'cat', 'rabbit'], ['elephant', 'lion', 'tiger'], ['zebra', 'giraffe', 'hippo']]\nassert func(input_list) == [['cat', 'dog', 'rabbit'], ['elephant', 'lion', 'tiger'], ['giraffe', 'hippo', 'zebra']]\n\ninput_list = [['January', 'February', 'March'], ['April', 'May', 'June'], ['July', 'August', 'September']]\nassert func(input_list) == [['February', 'January', 'March'], ['April', 'June', 'May'], ['August', 'July', 'September']]\n\ninput_list = [['red', 'green', 'blue'], ['yellow', 'purple', 'orange'], ['pink', 'brown', 'black']]\nassert func(input_list) == [['blue', 'green', 'red'], ['orange', 'purple', 'yellow'], ['black', 'brown', 'pink']]\n\ninput_list = [['one', 'two', 'three'], ['four', 'five', 'six'], ['seven', 'eight', 'nine']]\nassert func(input_list) == [['one', 'three', 'two'], ['five', 'four', 'six'], ['eight', 'nine', 'seven']]\n"
test_string_2 = "\ninput_list = [['banana', 'apple', 'cherry'], ['orange', 'grape', 'pear']]\nfunc(input_list)\nassert input_list == [['apple', 'banana', 'cherry'], ['grape', 'orange', 'pear']]\n\ninput_list = [['zebra', 'lion', 'elephant'], ['monkey', 'giraffe', 'tiger']]\nfunc(input_list)\nassert input_list == [['elephant', 'lion', 'zebra'], ['giraffe', 'monkey', 'tiger']]\n\ninput_list = [['kiwi', 'pineapple', 'mango'], ['strawberry', 'blueberry', 'raspberry']]\nfunc(input_list)\nassert input_list == [['kiwi', 'mango', 'pineapple'], ['blueberry', 'raspberry', 'strawberry']]\n\ninput_list = [['dog', 'cat', 'rabbit'], ['hamster', 'guinea pig', 'ferret']]\nfunc(input_list)\nassert input_list == [['cat', 'dog', 'rabbit'], ['ferret', 'guinea pig', 'hamster']]\n\ninput_list = [['sunflower', 'rose', 'tulip'], ['daisy', 'lily', 'orchid']]\nfunc(input_list)\nassert input_list == [['rose', 'sunflower', 'tulip'], ['daisy', 'lily', 'orchid']]\n"
test_string_3 = "assert func([['banana', 'apple', 'cherry'], ['orange', 'grape', 'kiwi'], ['pear', 'strawberry', 'blueberry']]) == [['apple', 'banana', 'cherry'], ['grape', 'kiwi', 'orange'], ['blueberry', 'pear', 'strawberry']]\nassert func([['zoo', 'elephant', 'lion'], ['dog', 'cat', 'bird'], ['apple', 'banana', 'cherry']]) == [['elephant', 'lion', 'zoo'], ['bird', 'cat', 'dog'], ['apple', 'banana', 'cherry']]\nassert func([['carrot', 'potato', 'tomato'], ['onion', 'garlic', 'ginger'], ['broccoli', 'cabbage', 'lettuce']]) == [['carrot', 'potato', 'tomato'], ['garlic', 'ginger', 'onion'], ['broccoli', 'cabbage', 'lettuce']]\nassert func([['one', 'two', 'three'], ['four', 'five', 'six'], ['seven', 'eight', 'nine']]) == [['one', 'three', 'two'], ['five', 'four', 'six'], ['eight', 'nine', 'seven']]\nassert func([['red', 'green', 'blue'], ['yellow', 'purple', 'orange'], ['pink', 'brown', 'black']]) == [['blue', 'green', 'red'], ['orange', 'purple', 'yellow'], ['black', 'brown', 'pink']]"
test_string = test_string_1 + test_string_2 + test_string_3

def seperate_assertions(test_string):
    test_list = []
    tests = [test.strip() for test in test_string.split('\n') if test.strip() != '']
    record = ''
    for test in tests:
        if test.startswith('assert'):
            if record:
                test_list.append(record + '\n' + test)
                record = ''
            else:
                test_list.append(test)
        else:
            record += '\n' + test
    if record:
        test_list.append('assert ' + record)
    return test_list

test_1 = seperate_assertions(test_string_1)
test_2 = seperate_assertions(test_string_2)
test_3 = seperate_assertions(test_string_3)


tests = test_1 + test_2 + test_3

print(len(tests))
for idx, test in enumerate(tests):
    print(idx, test)
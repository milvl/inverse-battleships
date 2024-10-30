import timeit
import random

class TestObj:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"TestObj({self.name})"
    

ITERATIONS = 100000000

def assign_test():
    start = timeit.default_timer()
    obj = TestObj("test")
    for i in range(ITERATIONS):
        obj.name = str(random.randint(0, 100))
        a = obj.name
    print(timeit.default_timer() - start)

    obj = dict()
    start = timeit.default_timer()
    for i in range(ITERATIONS):
        obj["name"] = str(random.randint(0, 100))
        a = obj["name"]
    print(timeit.default_timer() - start)


def create_test():
    start = timeit.default_timer()
    for i in range(ITERATIONS):
        obj = TestObj("test")
    print(timeit.default_timer() - start)

    start = timeit.default_timer()
    for i in range(ITERATIONS):
        obj = dict()
        obj["name"] = "test"
    print(timeit.default_timer() - start)


def create_and_assign_test():
    start = timeit.default_timer()
    for i in range(ITERATIONS):
        obj = TestObj("test")
        obj.name = str(random.randint(0, 100))
        a = obj.name
    print(timeit.default_timer() - start)

    start = timeit.default_timer()
    for i in range(ITERATIONS):
        obj = dict()
        obj["name"] = "test"
        obj["name"] = str(random.randint(0, 100))
        a = obj["name"]
    print(timeit.default_timer() - start)


def read_test():
    obj = TestObj("test")
    start = timeit.default_timer()
    for i in range(ITERATIONS):
        a = obj.name
    print(timeit.default_timer() - start)

    obj = dict()
    obj["name"] = "test"
    start = timeit.default_timer()
    for i in range(ITERATIONS):
        a = obj["name"]
    print(timeit.default_timer() - start)


def practical_test():
    obj = TestObj("test")
    obj_dict = dict()
    time1 = 0
    time2 = 0
    time3 = 0
    time4 = 0
    for i in range(ITERATIONS):
        random_data = str(random.randint(0, 100))
        start = timeit.default_timer()
        obj.name = random_data
        a = obj.name
        time1 += timeit.default_timer() - start

        start = timeit.default_timer()
        new_obj = TestObj("test")
        new_obj.name = random_data
        a = new_obj.name
        time2 += timeit.default_timer() - start

        start = timeit.default_timer()
        obj_dict["name"] = random_data
        a = obj_dict["name"]
        time3 += timeit.default_timer() - start

        start = timeit.default_timer()
        new_dict = dict()
        new_dict["name"] = random_data
        a = new_dict["name"]
        time4 += timeit.default_timer() - start
    print(time1)
    print(time2)
    print(time3)
    print(time4)


# print("Assign test")
# assign_test()
# print("Create test")
# create_test()
# print("Create and assign test")
# create_and_assign_test()
# print("Read test")
# read_test()
print("Practical test")
practical_test()

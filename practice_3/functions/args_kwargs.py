def add_numbers(*args):
    return sum(args)

print(add_numbers(1, 2, 3, 4))



def print_info(**kwargs):
    for key, value in kwargs.items():
        print(key, ":", value)

print_info(name="Alice", age=25)


def show_data(*args, **kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)

show_data(10, 20, city="New York", country="USA")
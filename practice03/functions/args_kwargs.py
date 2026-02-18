# Accept any number of positional and keyword arguments.
def show_info(*args, **kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)


# Send mixed arguments to the function.
show_info("Python","Practice","JIO", topic="functions", level="beginner") 

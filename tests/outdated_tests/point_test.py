from geometry.point import Point
import matplotlib.pyplot as plt

def test_properties(set_point : Point, do_graph : bool):
    if set_point is not None:
        print(f"The point is {set_point}")
        print(f"The dimension of the point is {set_point.dimension}")
        print(f"The distance from the origin is {set_point.distance_from_origin}")
        if do_graph:
            fig, ax = plt.subplots()
            x = [0, set_point.coordinates[0]]
            y = [0, set_point.coordinates[1]]
            ax.plot(x, y)
            ax.text(0, 0, "Origin")
            ax.text(x[1]/2, y[1]/2, f"Length: {set_point.distance_from_origin}")
            ax.text(set_point.coordinates[0], set_point.coordinates[1], "Point")
            plt.show()
    else:
        print("Please initialise your point.")
        x = float(input("Enter the x coordinate of the point: "))
        y = float(input("Enter the y coordinate of the point: "))
        set_point = Point((x, y))
        test_properties(set_point, do_graph)

def test_methods(set_point : Point, do_graph : bool):
    if set_point is not None:
        print(f"The point is {set_point}")
        print(f"The angle of the point is {set_point.angle()}")
        print(f"The polar coordinates of the point are {set_point.polar_coordinates()}")
        
    else:
        print("Please initialise your point.")
        x = float(input("Enter the x coordinate of the point: "))
        y = float(input("Enter the y coordinate of the point: "))
        set_point = Point((x, y))
        test_methods(set_point, do_graph)

def test_point():
    print("This is the test for the class Point")
    print(Point.__doc__)
    x = input("Read, and then enter 'c' to continue: ")
    while x.lower() == 'c':
        set_point = None
        do_set = False
        y = input("Do you want to use the same point for every method? (y/n): ")
        if y.lower() == 'y':
            x = float(input("Enter the x coordinate of the point: "))
            y = float(input("Enter the y coordinate of the point: "))
            set_point = Point((x, y))
            do_set = True
        graph = input("Do you want to graph the point? (y/n): ")
        do_graph = False
        if graph.lower() == 'y':
            do_graph = True
        print("Now, we test properties.")
        test_properties(set_point, do_graph)
        print("Now, we test methods.")

        x = input("To continue testing, enter 'c': ")

test_point()
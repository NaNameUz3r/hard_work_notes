class Shape:
    def __init__(
        self,
        x: int,
        y: int,
    ):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Hello from base Shape"


class SerializerMixin:
    """
    A mixin class for serializing .
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        raise Exception("This is a mixin class and cannot be instantiated.")

    def serialize(self):
        return ",".join([(f"{k}={v}") for k, v in self.__dict__.items()])


class ReprMixin:
    """
    Naive example for overriding methods with Mixins.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        raise Exception("This is a mixin class and cannot be instantiated.")

    def __repr__(self):
        return "Hello from ReprMixin"


class Rectangle(Shape, SerializerMixin, ReprMixin):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ):
        super().__init__(x=x, y=y)
        self.width = width
        self.height = height


class Circle(ReprMixin, Shape, SerializerMixin):
    def __init__(
        self,
        x: int,
        y: int,
        radius: int,
    ):
        super().__init__(x=x, y=y)
        self.radius = radius


rectangle = Rectangle(
    x=1,
    y=2,
    width=3,
    height=4,
)

circle = Circle(
    x=1,
    y=2,
    radius=3,
)


serializer = SerializerMixin()
# > Exception: This is a mixin class and cannot be instantiated.

print(rectangle.serialize())
print(circle.serialize())
# > x=1,y=2,width=3,height=4
# > x=1,y=2,radius=3

# Method Overriding in Python working from left to right:
print(rectangle)
# > Hello from base Shape
print(circle)
# > Hello from ReprMixin

# 2. Class level

### 2.1 Class Too Large (SRP Violation), or Too Many Instances Created in the Program (Consider Why This Is a Bad Sign).

Например, некоторая сущность типа Сотрудник или Работник и тд. может быть спроетирована плохим образом изначально или кошмарно усложнена в процессе доработки системы, так, что класс отражающий подобную сущность будет включать в себя множество разных методов: разнообразные геттеры и сеттеры меняющие состояние в БД сеттеры, и все остальные методы, которые на первый субьективно-белковый взягляд имеют отношение к этой сущности (посчитать зарплату и тд).

Думаю что к подобным проблемам приводит отсутствие этапа проектирования и вообще размышления на уровне интерфесов и абстрактных типов данных (то, что мы проходили на 3 ООАП курсе).

```python
class Employee:
    def __init__(self,
                name: str,
                position: str,
                salary: UsdSalary,):
        self.name = name
        self.position = position
        self.salary = salary
        self.performance_reviews = []

    def calculate_this_month_salary(self):
        ...

    def generate_performance_report(self):
        ...

    def update_employee_profile(self):
        ...

    def get_name(self):
        ...

    def change_position(self):
        ...

    def fire_employee(self):
        ...

    # and so on
```

Что же касаемо наличия множества инстансов класса в программе, то это может говорить, опять же - об отсутствии абстркций и нарушении SRP для этого класса. То есть класс "умеет" слишком много, и нужен слишком многим частям программы. Если SRP не нарушется, возможно это просто плохой стиль кодирования и можно было бы сделать один Singleton и везде его использовать, что снизит кол-во памяти, так как инстанс будет всего один. Если Singleton тут не подойдет, возможно, можно было бы сделать фабрику или какой то пулл переиспользуемых инстансов. В любом случае это выглядит как плохой дизайн. Пример - плохой менеджмент коннектов к бд, который должен быть переделан на нормальный синглтон/пуллер или еще лучше - взять нормальную ОРМ библиотеку.

```python
class DatabaseConnector:
    def __init__(self, db_url:str):
        self.db_url = db_url
        self.connection = None

    def connect(self):
        ...

    def execute_query(self, query):
        ...

db_connector_1 = DatabaseConnector("database_url_1")
db_connector_2 = DatabaseConnector("database_url_2")
```

### 2.2 Class Too Small or Doing Minor Functionality.

Если класс слишком маленький, содержит всего 1-2 метода, то стоит оценить количество инстансов этого классе в модуле/проекте и поискать лучшее место функционала инапсулированного в этот класс. Скорее всего, либо в этом же модуле есть класс в домен ответственности которого функционал этого маленького класса может быть включен. Может быть в проекте где то еще есть такие маленькие классы, все их можно собрать в отдельный модуль, в котором будет либо класс(ы) с нормальным именем и абстракцией, либо методы этих классов вообще не заслуживают быть частями класса и их можно собрать как отдельные функции хелперы в какой нибудь utils/tools пакет (всякие хэлперы-сериализаторы и прочее).

```python
class Convertor():
    def __init__(self, obj: Any):
        self.object = obj

    def convert(self):
        if isinstance(self.object, uuid.UUID):
            return str(self.object)
        if isinstance(self.object, sometype):
            return othertype(self.object)
        # and so on
```

### 2.3. A method in the class appears more suitable for another class.

Тут опять же из за нарушения или отстутствия абстракицй и отстстувия рационального мышления в моменте решения задачи
можно положить некоторый функционал в класс, вообще не подходящий для этого. Например, у есть есть отдельный класс для загрузки платежных документов в S3 хранилище. Метод в этом же классе, который, например, считает общее количество
документов в баккете выглядит, мягко говоря, странно.

```python
from minio import Minio
from typing import Any

class InvoiceSaver:
    def __init__(self, minio_client: Minio):
        self.minio_client = minio_client

    def upload_file(self, bucket_name: str, file_path: str, object_name: str):
        ...

    def download_file(self, bucket_name: str, object_name: str, destination_path: str):
        ...

    def get_total_invocies(self, bucket_name: str, destination_path: str):
        ...
```

### 2.4. The class holds data that is pushed into it from multiple places in the program.

Такого вообще по хорошему быть не должно, потому что кажды класс, который хранит какое то состояние, должен это состояние в себе инкапсулировать и больше "снаружи" никто это состояние изменять и видеть никак не должен. К сожаленю в Python нарушить состояние в классах очень легко:

```python
class BankAccount:
    def __init__(self):
        self._account_number = ""
        self._balance = 0.0

    @property
    def account_number(self):
        return self._account_number

    def set_account_number(self, account_number):
        self._account_number = account_number

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        self._balance += amount

    def withdraw(self, amount):
        if amount <= self._balance:
            self._balance -= amount
        else:
            print("Insufficient funds.")

account = BankAccount()
account.set_account_number("108108108")

another_account = BankAccount()
another_account.account_number = account.account_number  # Violation
another_account.deposit(1000.0)
```

Решение этого - скрывать такие классы за абстрактными типами данных, напрямую BankAccount не должен нигде в системе инициализироваться, а состояние вообще должно быть иммутабельным.

### 2.5. The class depends on the implementation details of other classes.

Базовая ситуация в системе/модуле с высокой связностью классов. Один класс слишком сильно (да и... вообще?) полагается на
конкретную реализцию другого класса. Кошмарный пример:


```python
class PaymentGateway:
    def process_payment(self, amount_to_process: SomeMoneyType):
        """
            payment processing business logic
        """
        ...

class OrderProcessor:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway

    def process_order(self, order: Order):
        total_amount = order.calculate_total_cost()
        self.payment_gateway.process_payment(total_amount)

class Order:
    def __init__(self, items):
        self.items = items

    def calculate_total_cost(self):
        return sum(item.price for item in self.items)

payment_gateway = PaymentGateway()
order_processor = OrderProcessor(payment_gateway)
order = Order(items=[Item("ProductA", 10), Item("ProductB", 20)])

order_processor.process_order(order)
```

Решение - это все нужно переделать, нормально спроектировав систему типов.

### 2.6. Typecasting down the hierarchy (parent classes are cast to child classes).

Звучит как нарушение LSP. Например вот такая с труктура:

```python
class BaseEvent:
    def __init__(self, event_type):
        self.type = event_type

class ClickEvent(BaseEvent):
    def __init__(self):
        super().__init__('Click')

def process_event(event):
    if isinstance(event, ClickEvent):
        print("Handling ClickEvent")
    else:
        print("Handling generic event")

generic_event = Event('Generic')
click_event = ClickEvent()

process_event(generic_event)
process_event(click_event)
```

Решением (скорее всего не самым лучшим) могут являться ковариантные обработчики событий, которые будут обрабатывать конкретный тип эвентов:

```python
from typing import TypeVar, Generic, Type, Dict

T = TypeVar("T", covariant=True)


class BaseEvent:
    def __init__(self, event_type):
        self.type = event_type


class ClickEvent(BaseEvent):
    def __init__(self):
        self.type = "Click"


class SaveEvent(BaseEvent):
    def __init__(self):
        self.type = "Save"


class EventHandler(Generic[T]):
    def handle_event(self, event: T):
        raise NotImplementedError("Subclasses must implement handle_event method")


class GenericEventHandler(EventHandler[BaseEvent]):
    def handle_event(self, event: BaseEvent):
        print(f"Handling GenericEvent: {event.type}")


class ClickEventHandler(EventHandler[ClickEvent]):
    def handle_event(self, event: ClickEvent):
        print(f"Handling ClickEvent: {event.type}")


class SaveEventHandler(EventHandler[SaveEvent]):
    def handle_event(self, event: SaveEvent):
        print(f"Handling SaveEvent: {event.type}")


class EventManager:
    def __init__(self):
        self.handlers: Dict[Type[BaseEvent], EventHandler[BaseEvent]] = {}

    def register_handler_for_event_type(
        self, event_type: Type[BaseEvent], handler: EventHandler[BaseEvent]
    ):
        self.handlers[event_type] = handler

    def handle_event(self, event: BaseEvent):
        handler = self.handlers.get(type(event))
        if handler:
            handler.handle_event(event)
        else:
            print(f"No handler registered for event type: {type(event).__name__}")


def main():
    event_manager = EventManager()

    event_manager.register_handler_for_event_type(BaseEvent, GenericEventHandler())
    event_manager.register_handler_for_event_type(ClickEvent, ClickEventHandler())
    event_manager.register_handler_for_event_type(SaveEvent, SaveEventHandler())

    events = [
        BaseEvent("Strange Event"),
        ClickEvent(),
        SaveEvent(),
    ]

    for event in events:
        event_manager.handle_event(event)

```

### 2.7. When a subclass is created for a certain class, it becomes necessary to create subclasses for some other classes as well.


В случае, когда система абстракций является "ментально"-нечеткой и разделена на различные иерархии классов, это может привести к необходимости внесения изменений в несколько мест одновременно. Снова, и как обычно, похоже что это возникает из за сильной связности между модулями, где конкретные реализации классов зависят друг от друга.

Вот пример, уровня штанов на лямках:

```python
class BaseShape:
    def draw(self):
        pass

class Circle(BaseShape):
    def draw(self):
        print("Drawing a circle")

class Square(BaseShape):
    def draw(self):
        print("Drawing a square")

# and so on
```

Представим что мы уже запустили этот сложный код, и теперь нам надо внести измненения во всех наследников, чтобы изменить логику draw. Босс сказал что нужно выводить цвет фигуры, и мы начинаем страдать:

```python
class Shape:
    def draw(self):
        pass

class Circle(Shape):
    def draw(self):
        print("Drawing a colored circle")

class Square(Shape):
    def draw(self):
        print("Drawing a colored square")

# and so on
```

Ситуацию можно было бы улучить с помощью миксинов:

```python
class Shape:
    def draw(self):
        pass

class ColoredMixin:
    def draw_colored(self):
        pass

class Circle(Shape, ColoredMixin):
    def draw(self):
        print("Drawing a circle")

    def draw_colored(self):
        print("Drawing a colored circle")

class Square(Shape, ColoredMixin):
    def draw(self):
        print("Drawing a square")

    def draw_colored(self):
        print("Drawing a colored square")
```

или Визитёра:

```python

from abc import ABC, abstractmethod


# === Base Shapes ===

class Shape(ABC):
    @abstractmethod
    def accept(self, visitor, *args, **kwargs):
        pass


class Circle(Shape):
    def accept(self, visitor, *args, **kwargs):
        visitor.visit_circle(self, *args, **kwargs)


class Square(Shape):
    def accept(self, visitor, *args, **kwargs):
        visitor.visit_square(self, *args, **kwargs)


# === Visitors ===

class ColorVisitor:
    def visit_circle(self, circle, color):
        print(f"Setting color of a circle to {color}")
        self.color = color

    def visit_square(self, square, color):
        print(f"Setting color of a square to {color}")


# === Colored Shapes ===

class ColoredCircle(Circle):
    def __init__(self, color):
        self.color = color


class ColoredSquare(Square):
    def __init__(self, color):
        self.color = color

```


### 2.8. Subclasses do not use methods and attributes of parent classes, or override parent methods.

Такое происходит в любой запутанной, хоть сколько большой системе. Когда нет четкой документации и понимания дизайна
и архитектуры, мы можем начать переопределять методы в наследниках, потому что не можем нормально понять интерфейс и назначение методов родителя.

В результет может быть наштампована целая кучу дочерних классов, которые теряют связь с интерфейсом родительского класса, не используя методы этого родителя, или переопределяя их (или и то, и другое в разных сочетаниях).

Пример из сферического вакуума при неглубокой иерархии, разумеется, в живом проекте с глубокой иерархией классов кошмар будет более очевиден:

```python
class RequestAnalyzer:
    def __init__(self, request_data):
        self.request_data = request_data

    def analyze_request(self):
        ...

    def preprocess_data(self):
        ...

    def log_analysis(self):
        ...

class GetRequestAnalyzer(RequestAnalyzer):
    def analyze_request(self):
        # Overriding the method to analyze GET requests
        ...

class PostRequestAnalyzer(RequestAnalyzer):
    def __init__(self, request_data, post_data):
        super().__init__(request_data)
        self.post_data = post_data

    def analyze_request(self):
        # Overriding the method to analyze POST requests
        ...

```


# 3. Application Level.

### 3.1. One modification requires changes in several classes.

Возьмем типовой сценарий, где у нас есть некоторое веб-приложение, какой то магазин, который делает фулстек Олег.

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class ShoppingCart:
    def __init__(self, user):
        self.user = user
        self.items = []

    def add_item(self, item):
        self.items.append(item)

```

Ну и как обычно приходят новые требования: надо добавить возможность уведомления пользователя о незавершенном заказе. Олег приступает:

```python
from threading import Timer

class User:
    def __init__(self, name, email, notification_service):
        self.name = name
        self.email = email
        self.notification_service = notification_service

    def notify_forgotten_cart(self, message):
        self.notification_service(self.name, message)

class ShoppingCart:
    def __init__(self, user):
        self.user = user
        self.items = []
        self.timer = None

    def add_item(self, item):
        self.items.append(item)
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(300, self.checkout_reminder)
        self.timer.start()

    def checkout_reminder(self):
        if not self.items:
            return
        self.user.notify_forgotten_cart("Your shopping cart has items. Complete your order!")
        self.timer = None

class NotificationService:
    """
    Class for sending notifications to customers.
    """
    def send_notification(self, user_name, notification):
        pass

```

Пойдя таким путем, если придется добавлять, например, sms уведомления, то придется снова вносить изменения в ShoppingCart и пользователя. Все проблемы тут снова из за плохой абстракции и нарушения SRP.

Разумеется, не требовалось бы вносить изменения в несколько классов, если бы проектировщик Олег строго следовал SRP.
Почему вообще ShoppingCart имеет в себе какой то таймер, а User отправляет уведомления?

### 3.2. Using complex design patterns where a simpler and straightforward design could suffice.

Кажется что любой паттерн проектирования может стать анитипаттерном, если его использования не оправданно, бессмысленно, или вообще не подходит для решения поставленной задачи. Возможна ситуация, когда вместо размышления о системе и проектирования оправданной системы классов разработчики, веруя в карго культ паттернов, стремятся по наитию закодить проект с использованием каких то паттернов, которые, как им кажутся, идеально подходят. Но все белковые механизмы ошибаются.

Например, какая то простая система обработки заказов небольшого магазина может быть закодирована так, c паттерном аля-Стратегия:

```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: Money):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: Money):
        ...

class PayPalPayment(PaymentStrategy):
    def pay(self, amount: Money):
        ...

class Order:
    def __init__(self,
                amount: Money,
                payment_strategy: PaymentStrategy):
        self.amount = amount
        self.payment_strategy = payment_strategy

    def process_order(self):
        self.payment_strategy.pay(self.amount)
```

Но оправданно ли это? нужно ли вообще, если метод оплаты можно передавать заказу в конструктор с помощью композиции?

```python
class PaymentMethod:
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentMethod):
    def pay(self, amount):
        ...

class PayPalPayment(PaymentMethod):
    def pay(self, amount):
        ...

class Order:
    def __init__(self,
                amount: Money,
                payment_method: PaymentMethod):
        self.amount = amount
        self.payment_method = payment_method

    def process_order(self):
        self.payment_method.pay(self.amount)
```

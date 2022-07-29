from typing import Callable, TypeVar, overload

F = TypeVar("F", bound=Callable[..., str])

class MacrosEnvironment:
    @overload
    def macro(self, v: F) -> F:
        """
        Registers a variable as a macro in the template,
        i.e. in the variables dictionary:

            env.macro(myfunc)

        Optionally, you can assign a different name:

            env.macro(myfunc, 'funcname')


        You can also use it as a decorator:

        @env.macro
        def foo(a):
            return a ** 2

        More info:
        https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2
        """
        ...
    @overload
    def macro(self, v: F, name: str = "") -> F: ...

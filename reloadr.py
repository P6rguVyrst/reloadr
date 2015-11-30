"""Reloadr - Python library for hot code reloading
(c) 2015 Hugo Herter
"""

__author__ = "Hugo Herter"
__version__ = 0.1

import inspect
import redbaron
import threading
import types
from time import sleep


def get_new_class_source(target):
    filepath = inspect.getsourcefile(target)
    red = redbaron.RedBaron(open(filepath).read())
    return red.find('class', target.__name__).dumps()


def reload_class(target):
    source = get_new_class_source(target)
    module = inspect.getmodule(target)
    locals_ = {}
    exec(source, module.__dict__, locals_)
    return locals_[target.__name__]._target


def get_new_function_source(target):
    filepath = inspect.getsourcefile(target)
    red = redbaron.RedBaron(open(filepath).read())
    return red.find('def', target.__name__).dumps()


def reload_function(target):
    source = get_new_function_source(target)
    module = inspect.getmodule(target)
    locals_ = {}
    exec(source, module.__dict__, locals_)
    return locals_[target.__name__]._target


class ClassReloadr:
    def __init__(self, target):
        self._target = target
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._init_args = args
            self._init_kwargs = kwargs
            self._instance = self._target.__call__(*args, **kwargs)
            return self._instance
        else:
            return self._instance.__call__(*args, **kwargs)

    def _reload(self):
        self._target = reload_class(self._target)
        self._instance.__class__ = self._target

    def _autoreload(self, interval=1):
        while True:
            self._reload()
            sleep(interval)

    def _start_autoreload(self, interval=1):
        thread = threading.Thread(target=self._autoreload)
        print(thread)
        thread.start()
        print(thread)


class FuncReloadr:
    def __init__(self, target):
        self._target = target
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._init_args = args
            self._init_kwargs = kwargs
            self._instance = self._target.__call__(*args, **kwargs)
            return self._instance
        else:
            return self._instance.__call__(*args, **kwargs)

    def _reload(self):
        self._instance = reload_function(self._target)

    def _autoreload(self, interval=1):
        while True:
            self._reload()
            sleep(interval)

    def _start_autoreload(self, interval=1):
        thread = threading.Thread(target=self._autoreload)
        print(thread)
        thread.start()
        print(thread)


def reloadr(target):
    if isinstance(target, types.FunctionType):
        return FuncReloadr(target)
    else:
        return ClassReloadr(target)
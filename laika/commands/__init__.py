import importlib
import pkgutil


def find_available_command_modules():
    commands_path = __path__  # type: ignore  # mypy issue #1422
    modules = (
        importlib.import_module("laika.commands.%s" % module_info.name)
        for module_info in pkgutil.iter_modules(commands_path)
    )
    return (
        module
        for module in modules
        if hasattr(module, "register") and callable(getattr(module, "register"))
    )

def _get_version(package_name: str) -> str:
    try:
        from importlib.metadata import version
    except ImportError:
        try:
            from importlib_metadata import version  # type: ignore
        except ImportError:
            return "UNKNOWN"

    return version(package_name)


__version__ = _get_version("laika-deploy")

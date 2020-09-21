from enum import Enum


class Color(Enum):
    red = "1"
    green = "2"
    yellow = "3"
    blue = "4"
    magenta = "5"
    cyan = "6"
    white = "7"
    clear = "9"

    @classmethod
    def of(cls, color_or_name):
        if isinstance(color_or_name, cls):
            return color_or_name
        return cls[color_or_name]


def render(fg=None, bg=None, bold=None):
    attrs = []

    if bold is not None:
        attrs.append("1" if bold else "22")

    if fg is not None:
        attrs.append("3" + Color.of(fg).value)

    if bg is not None:
        attrs.append("4" + Color.of(bg).value)

    return ("\033[%sm" % ";".join(attrs)) if attrs else ""


def formatted_span(fg=None, bg=None, bold=None):
    attrs_in = {}
    attrs_out = {}

    if bold:
        attrs_in["bold"] = True
        attrs_out["bold"] = False

    if fg:
        attrs_in["fg"] = Color.of(fg)
        attrs_out["fg"] = Color.clear

    if bg:
        attrs_in["bg"] = Color.of(bg)
        attrs_out["bg"] = Color.clear

    def renderer(msg):
        return render(**attrs_in) + str(msg) + render(**attrs_out)

    return renderer

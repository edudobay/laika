from .term_color import formatted_span


def null_formatter(color):
    def format_message(message):
        return message

    return format_message


class Reporter:
    def __init__(self, color=True):
        self.color = formatted_span if color else null_formatter

    def success(self, message):
        print(self.color("green")("✔ %s" % message))

    def info(self, message):
        print(self.color("yellow")("> %s" % message))

    def error(self, message):
        print(self.color("red")("ERROR: %s" % message))

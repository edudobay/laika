from .term_color import formatted_span as color


class Reporter:
    def success(self, message):
        print(color('green')('✔ %s' % message))

    def info(self, message):
        print(color('yellow')('> %s' % message))

    def error(self, message):
        print(color('red')('ERROR: %s' % message))

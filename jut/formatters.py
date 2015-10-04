"""
formatter module with various supported `jut run` output formats

"""

from jut.common import info

import json


class Formatter(object):

    def __init__(self, options):
        self.options = options

    def start(self):
        """
        handle the start of your output format
        """
        pass

    def point(self, point):
        """
        handle formatting a point within your format
        """
        pass

    def stop(self):
        """
        handle the stop of your output format
        """
        pass


class JSONFormatter(Formatter):

    def __init__(self, options):
        Formatter.__init__(self, options)
        self.previous_point = False

    def start(self):
        if not self.options.persist:
            info('[')

    def point(self, point):
        if self.previous_point:
            info(',')
        info(json.dumps(point, indent=4))
        self.previous_point = True

    def stop(self):
        if not self.options.persist:
            info(']')

class TextFormatter(Formatter):

    def __init__(self, options):
        Formatter.__init__(self, options)


    def point(self, point):
        line = []

        if 'time' in point:
            timestamp = point['time']
            del point['time']
            line.append(timestamp)

        keys = sorted(point.keys())
        line += [str(point[key]) for key in keys]
        info(' '.join(line))


class CSVFormatter(Formatter):

    def __init__(self, options):
        Formatter.__init__(self, options)
        self.current_headers = []

    def point(self, point):
        line = []

        if 'time' in point:
            keys = sorted(point.keys())
            keys.remove('time')
            keys.insert(0, 'time')

        else:
            keys = sorted(point.keys())

        if self.current_headers != keys:
            info('#%s' % ','.join(keys))
            self.current_headers = keys

        line += [str(point[key]) for key in keys]
        info(','.join(line))



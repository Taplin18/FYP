#!/usr/bin/env python3


class Stats:

    def __init__(self):
        """
        Initialises stats.
        """
        self.result = ""

    def load_stats(self, sbf_stats):
        """
        Returns the stats of the filter.
        :param sbf_stats: a dictionary of stats from the filter.
        :return: a string of HTML to list the stat results.
        """
        self.sbf_stats = sbf_stats
        k = list(self.sbf_stats.keys())
        for i in range(0, len(k)):
            self.result += "<li class=\"collection-item\">{}: {}</li>".format(k[i], self.sbf_stats[k[i]])
        return self.result

    def load_initial_stats(self):
        """
        Returns the initial stats of the filter.
        :return: a string of HTML to list the stat results.
        """
        self.result += "<li class=\"collection-item\">Number of cells: 16</li>"
        return self.result

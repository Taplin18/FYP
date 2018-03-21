#!/usr/bin/env python3


class Layout:

    def __init__(self):
        """
        Initialises stats and table layout.
        """
        self.stats = ""
        self.table = ""
        self.check = ""

    def load_stats(self, sbf_stats):
        """
        Returns the stats of the filter.
        :param sbf_stats: a dictionary of stats from the filter.
        :return: a string of HTML to display the stat results.
        """
        self.sbf_stats = sbf_stats
        k = list(self.sbf_stats.keys())
        self.stats = ""
        for i in range(0, len(k)):
            self.stats += "<li class=\"collection-item\">{}: {}</li>".format(k[i], self.sbf_stats[k[i]])
        return self.stats

    def load_initial_stats(self):
        """
        Returns the initial stats of the filter.
        :return: a string of HTML to display the stat results.
        """
        self.stats = "<li class=\"collection-item\">Number of cells: 16</li>"
        return self.stats

    def load_table(self, sbf_table):
        """
        Returns the table contents.
        :param sbf_table: an array of the filter.
        :return: a string of HTML to display the contents of the filter.
        """
        self.sbf_table = sbf_table
        self.table = ""

        for i in range(0, pow(2, 4)):
            self.table += "<td>{}</td>".format(str(self.sbf_table[i]))
        return self.table

    def load_initial_table(self):
        """
        Returns the initial table contents.
        :return: a string of HTML to display the contents of the filter.
        """
        self.table = ""
        for i in range(0, pow(2, 4)):
            self.table += "<td>0</td>"
        return self.table

    def load_check_result(self, value, result):
        """
        Returns the results of the check.
        :param value: the value that was checked.
        :param result: the result of the check.
        :return: a string of HTML to display the result of the check.
        """
        self.value = value
        self.result = result
        if int(self.result) == 0:
            self.check += "<li class=\"collection-item\">{} is not in the filter.</li>".format(str(self.value))
        else:
            self.check += "<li class=\"collection-item\">{} is in area {}.</li>".format(str(self.value),
                                                                                        str(self.result))

        return self.check

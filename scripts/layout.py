import ast


class Layout:

    def __init__(self, num_cells):
        """
        Initialises stats and table layout.
        :param num_cells: the number of cells in the filter (2^num_cells).
        """
        self.num_cells = num_cells
        self.stats = ""
        self.table = ""
        self.check = ""
        self.hash_family = []

    def __del__(self):
        pass

    def load_stats(self, sbf_stats):
        """
        Returns the stats of the filter.
        :param sbf_stats: a dictionary of stats from the filter.
        :return: a string of HTML to display the stat results.
        """
        self.sbf_stats = sbf_stats
        self.hash_family = ast.literal_eval(self.sbf_stats["Hash family"])
        k = list(self.sbf_stats.keys())
        self.stats = ""
        for i in range(0, len(k)):
            if k[i] == "Hash family":
                self.hf = ', '.join(map(str, self.hash_family))
                self.stats += "<li class=\"collection-item\"><b>{}:</b> {}</li>".format(k[i], self.hf.upper())
            else:
                self.stats += "<li class=\"collection-item\"><b>{}:</b> {}</li>".format(k[i], self.sbf_stats[k[i]])

        del self.hf
        del self.sbf_stats
        return self.stats

    def load_table(self, sbf_table):
        """
        Returns the table contents.
        :param sbf_table: an array of the filter.
        :return: a string of HTML to display the contents of the filter.
        """
        self.sbf_table = sbf_table
        self.table = "<tr>"

        for i in range(0, pow(2, self.num_cells)):
            if (i % 64 == 0) and (i != 0):
                self.table += "</tr><tr>"
            self.table += "<td>{}</td>".format(str(self.sbf_table[i]))
        self.table += "</tr>"

        del self.sbf_table
        return self.table

    def highlight_table(self, sbf_table, results):
        print(results)
        print(self.hash_family)
        self.sbf_table = sbf_table
        self.results = results
        self.indexes = []
        self.table = "<tr>"

        for hf in self.hash_family:
            self.indexes.append(self.results[hf][0])

        for i in range(0, pow(2, self.num_cells)):
            if (i % 64 == 0) and (i != 0):
                self.table += "</tr><tr>"
            if i in self.indexes:
                self.table += "<td style=\"background-color: red\">{}</td>".format(str(self.sbf_table[i]))
            else:
                self.table += "<td>{}</td>".format(str(self.sbf_table[i]))
        self.table += "</tr>"

        del self.sbf_table
        del self.results
        del self.indexes
        return self.table


    def load_check_result(self, value, results):
        """
        Returns the results of the check.
        :param value: the value that was checked.
        :param results: a dictionary with the hash function as the key and list [index, area] as the value.
        :return: a string of HTML to display the result of the check.
        """
        self.value = value
        self.results = results

        self.check = "<div class=\"section\"><ul class=\"collection\">"
        if int(self.results) == 0:
            self.check += "<li class=\"collection-item\">{} is not in the filter.</li>".format(str(self.value))
        else:
            self.check += "<li class=\"collection-item\">{} is in area {}.</li>".format(str(self.value),
                                                                                        str(self.results))
        self.check += "</ul></div>"

        del self.value
        del self.results
        return self.check

    def no_check_result(self):
        self.check = "<tr>"
        for i in self.hash_family:
            self.check += "<th>{}</th>".format(i.upper())
        self.check += "</tr><tr>"
        for i in range(0, len(self.hash_family)):
            self.check += "<td></td>"
        self.check += "</tr>"

        return self.check

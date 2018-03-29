import ast
import csv
from pathlib import Path


class Layout:

    def __init__(self, num_cells):
        """
        Initialises stats and table layout.
        :param num_cells: the number of cells in the filter (2^num_cells).
        """
        self.dataset = self._get_dataset_path()
        self.delimiter = ','
        self.num_cells = num_cells
        self.stats = ""
        self.table = ""
        self.check = ""
        self.conclusion = ""
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
                self.stats += "<li class=\"collection-item\"><b>{}:</b> {}</li>".format(str(k[i]),
                                                                                        str(self.hf.upper()))
            else:
                self.stats += "<li class=\"collection-item\"><b>{}:</b> {}</li>".format(str(k[i]),
                                                                                        str(self.sbf_stats[k[i]]))

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
        """
        Return the table contents with the check values highlighted.
        :param sbf_table: an array of the filter.
        :param results: a dictionary with the hash function as the key and list [index, area] as the value.
        :return: a string of HTML to display the contents of the filter with highlighted vaules.
        """
        self.sbf_table = sbf_table
        self.results = results
        self.indexes = self._get_indexes(self.results)
        self.table = "<tr>"

        for i in range(0, pow(2, self.num_cells)):
            if (i % 64 == 0) and (i != 0):
                self.table += "</tr><tr>"
            if i in self.indexes:
                self.table += "<td class=\"tooltip\" id=\"{}\" style=\"background-color: red\">" \
                              "{}" \
                              "<span class=\"tooltiptext\">{}</span>" \
                              "</td>".format(str(i), str(self.sbf_table[i]), str(self._tooltip(i, self.results)))
            else:
                self.table += "<td id=\"{}\" >{}</td>".format(str(i),
                                                              str(self.sbf_table[i]))
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
        :return: a string of HTML to display the result of the check (a table and a conclusion).
        """
        self.value = value
        self.results = results
        self.indexes = self._get_indexes(self.results)
        self.areas = []
        self.conclusion = ""
        self.check = "<tr>{}".format(str(self._result_header()))

        for i in self.indexes:
            self.check += "<td><a href=\"#{}\">{}</a></td>".format(str(self.results[i][0]), str(self.results[i][1]))
            self.areas.append(self.results[i][1])
        self.check += "</tr>"

        self.min_area = min(int(m) for m in self.areas)
        if self.min_area == 0:
            self.conclusion += "The value {} is not in the spatial bloom filter.".format(str(self.value))
        else:
            self.conclusion += "The value {} is in area {} as that is the lowest area.".format(str(self.value),
                                                                                               str(self.min_area))

        del self.value
        del self.results
        del self.indexes
        del self.areas
        del self.min_area
        return self.check, self.conclusion

    def no_check_result(self):
        """
        Return an empty table body when no value has been checked.
        :return: the HTML of an empty table body.
        """
        self.check = "<tr>{}".format(str(self._result_header()))

        for i in range(0, len(self.hash_family)):
            self.check += "<td></td>"
        self.check += "</tr>"

        return self.check, self.conclusion

    def csv_table(self):
        self.csv_layout = ""
        with open(self.dataset, 'r') as dataset_file:
            dataset_reader = csv.reader(dataset_file, delimiter=self.delimiter)
            for row in dataset_reader:
                self.csv_layout += "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1])
        return self.csv_layout

    def _tooltip(self, index, results):
        """
        Get the hash function to display in the tooltip.
        :param index: the index value.
        :param results: a dictionary with the hash function as the key and list [index, area] as the value.
        :return: the hash function to display in the tooltip.
        """
        self.index = index
        self.results = results
        self.cnt = 0
        self.k = list(self.results.keys())
        self.v = list(self.results.values())

        for i in self.v:
            if i[0] == self.index:
                return self.k[self.cnt].upper()
            self.cnt += 1

    def _get_indexes(self, results):
        """
        Extract the filter index from the check result.
        :param results: a dictionary with the hash function as the key and list [index, area] as the value.
        :return: the indexes of the check result.
        """
        self.results = results
        self.index_list = []

        for hf in self.hash_family:
            self.index_list.append(self.results[hf][0])

        return self.index_list

    def _result_header(self):
        """
        Return the table header which contains the hash function names.
        :return: the HTML of of the table header.
        """
        self.result_header = ""

        for i in self.hash_family:
            self.result_header += "<th>{}</th>".format(str(i.upper()))
        self.result_header += "</tr><tr>"

        return self.result_header

    def _get_dataset_path(self):
        """
        Returns the correct path to the cork csv.
        :return: the path to the cork csv.
        """
        aws = "/var/www/demo/dataset/cork.csv"
        if Path(aws).is_file():
            return aws
        else:
            return "dataset/cork.csv"

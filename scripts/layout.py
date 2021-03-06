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
        self.hash_family = ast.literal_eval(self.sbf_stats["Hash Family"])
        k = list(self.sbf_stats.keys())
        self.stats = ""
        for i in range(0, len(k)):
            if k[i] == "Hash family":
                hf = ', '.join(map(str, self.hash_family))
                self.stats += "<li class=\"collection-item\"><b>{}:</b> {}</li>".format(str(k[i]),
                                                                                        str(hf.upper()))
            else:
                self.stats += "<li class=\"collection-item\"><b>{}:</b> {}</li>".format(str(k[i]),
                                                                                        str(self.sbf_stats[k[i]]))

        del self.sbf_stats
        return self.stats

    def area_stats(self, stats1, stats2):
        self.stats1 = stats1
        self.stats2 = stats2
        k1 = sorted(list(self.stats1.keys()))
        k2 = sorted(list(self.stats2.keys()))
        self.property, self.other_stats = "", ""

        for i in range(1, 5):
            self.property += "<tr><td>{}</td>".format(k1[i-1])
            for j in self.stats1[k1[i-1]]:
                self.property += "<td>{}</td>".format(j)
            self.property += "</tr>"

        for i in range(1, 5):
            self.other_stats += "<tr><td>{}</td>".format(k2[i-1])
            for j in self.stats2[k2[i-1]]:
                self.other_stats += "<td>{}</td>".format(j)
            self.other_stats += "</tr>"

        del self.stats1
        del self.stats2

        return self.property, self.other_stats

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
        :return: a string of HTML to display the contents of the filter with highlighted values.
        """
        self.sbf_table = sbf_table
        self.results = results
        self.indexes = self._get_indexes(self.results)
        self.table = "<tr>"

        for i in range(0, pow(2, self.num_cells)):
            if (i % 64 == 0) and (i != 0):
                self.table += "</tr><tr>"
            if i in self.indexes:
                self.table += "<td class=\"tooltip\" id={} style=\"background-color: red\">" \
                              "{}" \
                              "<span class=\"tooltiptext\">{}</span>" \
                              "</td>".format(str(i), str(self.sbf_table[i]), str(self._tooltip(i, self.results)))
            else:
                self.table += "<td id={}>{}</td>".format(str(i),
                                                         str(self.sbf_table[i]))
        self.table += "</tr>"

        del self.sbf_table
        del self.results
        del self.indexes
        return self.table

    def load_check_result(self, value, results, incor_vals):
        """
        Returns the results of the check.
        :param value: the value that was checked.
        :param results: a dictionary with the hash function as the key and list [index, area] as the value.
        :param incor_vals: a dictionary with the coordinate as the key and list [real_area, [returned areas]] as
                               the value.
        :return: a string of HTML to display the result of the check (a table and a conclusion).
        """
        self.value = value
        self.results = results
        self.incor_vals = incor_vals
        self.areas = []
        self.conclusion = ""
        self.check = "<tr>{}".format(str(self._result_header()))

        for i in self.hash_family:
            self.check += "<td><a href=\"#{}\">{}</a></td>".format(str(self.results[i][0]), str(self.results[i][1]))
            self.areas.append(self.results[i][1])
        self.check += "</tr>"

        self.min_area = min(int(m) for m in self.areas)
        if self.incor_vals.get(value) is not None:
            self.conclusion += "<li>{} is in Area of Interest {}.</li>" \
                               "<li>However, it really belongs to Area of Interest" \
                               " {} but the cells were overwritten.</li>".format(str(self.value), str(self.min_area),
                                                                                 str(self.incor_vals[self.value][0]))
        elif self.min_area == 0:
            self.conclusion += "<li>{} is not in the filter.</li>".format(str(self.value))
        else:
            self.conclusion += "<li>{} is in Area of Interest {}.</li>".format(str(self.value), str(self.min_area))

        del self.value
        del self.results
        del self.incor_vals
        del self.areas
        del self.min_area
        return self.check, self.conclusion

    def no_check_result(self):
        """
        Return an empty table body when no value has been checked.
        :return: the HTML of an empty table body.
        """
        self.conclusion = ""
        self.check = "<tr>{}".format(str(self._result_header()))

        for i in range(0, len(self.hash_family)):
            self.check += "<td></td>"
        self.check += "</tr>"

        return self.check, self.conclusion

    def csv_table(self):
        """
        Return a table of the cork.csv contents
        :return: the HTML of a table containing the cork.csv contents.
        """
        self.csv_layout = ""
        with open(self.dataset, 'r') as dataset_file:
            dataset_reader = csv.reader(dataset_file, delimiter=self.delimiter)
            for row in dataset_reader:
                self.csv_layout += "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1])
        return self.csv_layout

    def incorrect_areas(self, incorrect_vals):
        """
        Return the information about the coordinates with the wrong area of interest.
        :param incorrect_vals: a dictionary with the coordinate as the key and list [real_area, [returned areas]] as
                               the value.
        :return: HTML of table containing the incorrect values.
        """
        self.incorrect_vals = incorrect_vals
        self.coordinates = list(self.incorrect_vals.keys())
        self.incorrect = ""

        for i in self.coordinates:
            self.a = self.incorrect_vals[i]
            self.incorrect += "<tr><td>{}</td>" \
                              "<td>{}</td>" \
                              "<td>{}</td>" \
                              "<td>{}</td></tr>".format(i, self.a[0], min(int(m) for m in self.a[1]), self.a[1])
        del self.incorrect_vals
        del self.coordinates
        del self.a

        return self.incorrect

    def false_positive_area(self, fp_values):
        """
        Return the information about the coordinates not in the SBF but return an area of interest.
        :param fp_values: a dictionary with the coordinate as the key and a list of the areas of interest it returned.
        :return: HTML table to display the false positive values.
        """
        self.fp_values = fp_values
        self.coordinates = list(self.fp_values.keys())
        self.fp = ""
        for i in self.coordinates:
            self.a = self.fp_values[i]
            self.fp += "<tr><td>{}</td><td>{}</td>" \
                       "<td>{}</td></tr>".format(i, min(int(m) for m in self.a), self.a)
        del self.fp_values
        del self.coordinates
        del self.a

        return self.fp

    def edit_details(self, hash_fam):
        """
        List the hash functions used in the SBF.
        :param hash_fam: the hash functions currently used.
        :return: the HTML to list the hash functions selected.
        """
        self.hash_family = hash_fam
        self.hash_functions = ""
        for hf in self.hash_family:
            self.hash_functions += "<li>{}</li>".format(str(hf.upper()))
        return self.hash_functions

    def hash_family_options(self, allowed_hashes):
        """
        Checkboxes of the hash functions that be used for the hash family.
        :param allowed_hashes: a list of allowed hash functions.
        :return: HTML to display the hash functions as checkboxes.
        """
        self.allowed_hashes = allowed_hashes
        self.checkboxes = ""
        for hf in self.allowed_hashes:
            if hf in self.hash_family:
                self.checkboxes += \
                    "<li><input type=\"checkbox\" checked=\"checked\" id={} name=\"hf\" class=\"options\" value={}>" \
                    "<label for={}>{}</label></li>".format(str(hf), str(hf), str(hf),
                                                           str(hf.upper()))
            else:
                self.checkboxes += "<li><input type=\"checkbox\" id={} name=\"hf\" class=\"options\" value={}>" \
                                   "<label for={}>{}</label></li>".format(str(hf), str(hf), str(hf),
                                                                          str(hf.upper()))

        del self.allowed_hashes
        return self.checkboxes

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

    @staticmethod
    def _get_dataset_path():
        """
        Returns the correct path to the cork csv.
        :return: the path to the cork csv.
        """
        aws = "/var/www/demo/dataset/cork.csv"
        if Path(aws).is_file():
            return aws
        else:
            return "dataset/cork.csv"

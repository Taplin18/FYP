import numpy as np
import scripts.sbf as sbf
import matplotlib.pyplot as plt


class CompareResults:

    HFS = ['md5', 'sha1', 'sha256']
    MAX_SBF_SIZE = 32

    def __init__(self):
        self.sbf_sizes = self._create_sbfs()

    def _create_sbfs(self):
        sizes = {}
        for x in range(1, self.MAX_SBF_SIZE+1):
            test = sbf.sbf(self.HFS, x)
            test.insert_from_file()
            test.update_stats()
            if x < 10:
                sizes["0{}".format(x)] = test
            else:
                sizes["{}".format(x)] = test
            print(x)
        return sizes

    def ffp(self):
        keys = sorted(list(self.sbf_sizes.keys()))

        performance = []
        for y in keys[6:21]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            performance.append(filter_stats['Filter False Positive Probability'])

    def plot_ffp(self):
        keys = sorted(list(self.sbf_sizes.keys()))
        y_pos = np.arange(len(keys[6:21]))

        performance = []
        for y in keys[6:21]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            performance.append(filter_stats['Filter False Positive Probability'])

        plt.figure(num=None, figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')
        plt.bar(y_pos, performance, align='center', alpha=1)
        plt.xticks(y_pos, keys[6:21])
        plt.ylabel('False Positive Probability')
        plt.xlabel('Spatial Bloom Filter Sizes')
        plt.title('False Positive Probability')

        plt.show()


if __name__ == '__main__':
    stats = CompareResults()
    stats.ffp()

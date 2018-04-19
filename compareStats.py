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

        for y in keys[:20]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            print('size {}: {}'.format(y, filter_stats['Filter False Positive Probability']))

    def graph_fpp(self):
        objects = sorted(list(self.sbf_sizes.keys()))

        performance = []
        for y in objects[:20]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            performance.append(filter_stats['Filter False Positive Probability'])

        fig = plt.figure(num=None, figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')
        plt.title("False Positive Probability")
        plt.ylabel('False Positive Probability')
        plt.xlabel('Spatial Bloom Filter Sizes')
        plt.plot(objects[:20], performance, 'bo-')
        plt.gca().invert_yaxis()
        plt.show()

    def hash_collision(self):
        keys = sorted(list(self.sbf_sizes.keys()))

        for y in keys[:25]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            print('size {}: {}'.format(y, filter_stats['Number of Hash Collisions']))

    def graph_hash_col(self):
        objects = sorted(list(self.sbf_sizes.keys()))

        performance = []
        for y in objects[:25]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            performance.append(filter_stats['Number of Hash Collisions'])

        fig = plt.figure(num=None, figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')
        plt.title('Hash Collisions')
        plt.ylabel('Number of Hash Collisions')
        plt.xlabel('Spatial Bloom Filter Sizes')
        plt.plot(objects[:25], performance, 'bo-')
        plt.gca().invert_yaxis()
        plt.show()

    def sparsity(self):
        keys = sorted(list(self.sbf_sizes.keys()))

        for y in keys[:30]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            print('size {}: {}'.format(y, filter_stats['Filter Sparsity']))

    def graph_sparsity(self):
        objects = sorted(list(self.sbf_sizes.keys()))

        performance = []
        for y in objects[:30]:
            test = self.sbf_sizes[y]
            filter_stats = test.get_stats()
            performance.append(filter_stats['Filter Sparsity'])

        fig = plt.figure(num=None, figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')
        plt.title('Sparsity')
        plt.ylabel('Filter Sparsity')
        plt.xlabel('Spatial Bloom Filter Sizes')
        plt.plot(objects[:30], performance, 'bo-')
        plt.show()


if __name__ == '__main__':
    stats = CompareResults()
    stats.ffp()
    stats.graph_fpp()
    stats.hash_collision()
    stats.graph_hash_col()
    stats.sparsity()
    stats.graph_sparsity()

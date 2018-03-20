#!/usr/bin/env python3


class Stats:

    def __init__(self, sbf_stats):
        self.sbf_stats = sbf_stats
        self.result = """
        <div class="col s12 m6">
            <div class="card horizontal">
                <div class="card-stacked">
                    <div class="card-content">
                        <span class="card-title">SBF Stats</span>
                        <div class="divider"></div>
                        <div class="section">
                            <ul class="collection">
                            
        """

    def get_stats(self):
        k = list(self.sbf_stats.keys())
        for i in range(0, len(k)):
            self.result += "<li class=\"collection-item\">{}: {}</li>".format(k[i], self.sbf_stats[k[i]])
        self.result += "</ul></div></div></div></div></div>"
        return self.result

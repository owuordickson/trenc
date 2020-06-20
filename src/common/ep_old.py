# -*- coding: utf-8 -*-
"""
@author: "Dickson OWUOR"
@credits: "Anne LAURENT, Joseph ORERO"
@version: "1.0"
@email: "owuordickson@gmail.com"
@created: "26 March 2020"

EP (Emerging Pattern): this class stores attributes of an (jumping) emerging pattern

"""

import json


class JEP:

    def __init__(self, pattern, t_lag=None):
        self.pattern = pattern
        self.t_lag = t_lag  # only available for TGPs
        self.pattern_info = self.format_info()

    def format_info(self):
        if self.t_lag is None:
            json_txt = {"pattern": str(self.pattern.get_tuples()), "type": "Jumping Emerging GP"}
            return json.dumps(json_txt, indent=4)
        else:
            json_txt = {"pattern": str(self.pattern.get_tuples()), "type": "Jumping Emerging TGP",
                        "time_lag": self.t_lag.to_string()}
            return json.dumps(json_txt, indent=4)


class EP(JEP):

    def __init__(self, pattern, gr, t_lag=None, t_lags=None):
        self.gr = gr  # only available for GPs
        self.t_lags = t_lags  # only available for TGPs
        super().__init__(pattern, t_lag)

    def format_info(self):
        if self.t_lag is None:
            json_txt = {"pattern": str(self.pattern.get_tuples()), "type": "Emerging GP",
                        "growth_rate": self.gr}
            return json.dumps(json_txt, indent=4)
        else:
            if self.t_lags is None:
                json_txt = {"pattern": str(self.pattern.get_tuples()), "type": "Emerging TGP",
                            "time_lag": self.t_lag.to_string(), "growth_rate": self.gr}
            else:
                t_lags_txt = []
                for obj in self.t_lags:
                    t_lag = obj[0]
                    gr = obj[1]
                    txt = {"time_lag": self.t_lag.to_string(), "growth_rate": gr}
                    t_lags_txt.append(txt)
                json_txt = {"pattern": str(self.pattern.get_tuples()), "type": "Emerging TGP",
                            "time_lag": self.t_lag.to_string(), "emergence": t_lags_txt}
            return json.dumps(json_txt, indent=4)

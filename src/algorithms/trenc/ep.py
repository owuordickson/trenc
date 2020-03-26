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
from src.algorithms.trenc.fuzzy_mf import FuzzyMF
from src.algorithms.trenc.handle_data import HandleData


class JEP:

    def __init__(self, pattern, t_lag=None):
        self.pattern = pattern
        self.t_lag = t_lag  # only available for TGPs
        self.pattern_info = self.format_info()

    def format_info(self):
        pat = str(HandleData.format_gp(self.pattern))
        if self.t_lag is None:
            json_txt = {"pattern": pat, "type": "Jumping Emerging GP"}
            return json.dumps(json_txt, indent=4)
        else:
            t_lag_txt = EP.format_time_lag(self.t_lag)
            json_txt = {"pattern": pat, "type": "Jumping Emerging TGP",
                        "time_lag": t_lag_txt}
            return json.dumps(json_txt, indent=4)

    @staticmethod
    def format_time_lag(t_lag):
        tlag_fmt = FuzzyMF.get_time_format(t_lag[0])
        sup = t_lag[1]
        t_lag_txt = ("~ " + tlag_fmt[0] + str(tlag_fmt[1]) +
                     " " + str(tlag_fmt[2]) + " : " + str(sup))
        return t_lag_txt


class EP(JEP):

    def __init__(self, pattern, gr, t_lag=None, t_lags=None):
        self.gr = gr  # only available for GPs
        self.t_lags = t_lags  # only available for TGPs
        super().__init__(pattern, t_lag)

    def format_info(self):
        pat = str(HandleData.format_gp(self.pattern))
        if self.t_lag is None:
            json_txt = {"pattern": pat, "type": "Emerging GP",
                        "growth_rate": self.gr}
            return json.dumps(json_txt, indent=4)
        else:
            t_lag_txt = EP.format_time_lag(self.t_lag)
            if self.t_lags is None:
                json_txt = {"pattern": pat, "type": "Emerging TGP",
                            "time_lag": t_lag_txt, "growth_rate": self.gr}
            else:
                t_lags_txt = []
                for obj in self.t_lags:
                    t_lag = obj[0]
                    gr = obj[1]
                    t_lag_txt = EP.format_time_lag(t_lag)
                    txt = {"time_lag": t_lag_txt, "growth_rate": gr}
                    t_lags_txt.append(txt)
                json_txt = {"pattern": pat, "type": "Emerging TGP",
                            "time_lag": t_lag_txt, "emergence": t_lags_txt}
            return json.dumps(json_txt, indent=4)

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
from .gp import GP, TGP, TimeLag


class GEP(GP):

    def __init__(self, gp=GP(), gr=None):
        self.gradual_items = gp.gradual_items
        self.support = gp.support
        self.growth_rate = gr

    def jsonify(self):
        if self.growth_rate is not None:
            json_txt = {"pattern": str(self.get_tuples()),
                        "type": "Emerging GP",
                        "growth_rate": self.growth_rate}
        else:
            json_txt = {"pattern": str(self.get_tuples()),
                        "type": "Jumping Emerging GP"}
        return json.dumps(json_txt, indent=4)


class TimeLag_gr(TimeLag):

    def __init__(self, tstamp=0, supp=0, gr=0):
        super().__init__(tstamp, supp)
        self.growth_rate = gr


class TGEP(TGP):

    def __init__(self, gp=GP(), t_lag=TimeLag()):
        super().__init__(gp, t_lag)
        self.gr_timelags = list()

    def add_timestamp(self, tstamp, sup, gr):
        self.gr_timelags.append(TimeLag_gr(tstamp=tstamp, supp=sup, gr=gr))

    def jsonify(self):
        if len(self.gr_timelags) <= 0:
            json_txt = {"pattern": str(self.get_tuples()),
                        "type": "Jumping Emerging TGP",
                        "time_lag": self.time_lag.to_string()}
        else:
            t_lags_txt = []
            for gr_tlag in self.gr_timelags:
                txt = {"time_lag": gr_tlag.to_string(), "growth_rate": gr_tlag.growth_rate}
                t_lags_txt.append(txt)
            json_txt = {"pattern": str(self.get_tuples()), "type": "Emerging TGP",
                        "time_lag": self.time_lag.to_string(), "emergence": t_lags_txt}
        return json.dumps(json_txt, indent=4)

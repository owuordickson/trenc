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
from .gp import GP


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

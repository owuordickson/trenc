[![Build Status](https://travis-ci.org/owuordickson/trenc.svg?branch=master)](https://travis-ci.org/owuordickson/trenc)

## TRENC

A python implementation of Temporal gRadual Emerging aNt Colony optimization (TRENC) algorithm.

### Requirements:

You will be required to install the following python dependencies before using <em><strong>TRENC</strong></em> algorithm:
```
                   install python (version => 3.6)

```

```
                    $ pip install numpy
                    $ pip install python-dateutil scikit-fuzzy

```

### Usage:

Example with a data-set and specified values<br>
```
$python init_trenc.py -f DATASET.csv -c 0 -s 0.5 -r 0.5 -p 1
```

Output:
```
Run-time: 0.1587989330291748 seconds
Algorithm: TRENC 
No. of data sets: 8
No. of (data set) attributes: 5
Size of 1st data set: 17
Minimum support: 0.5
Minimum representativity: 0.5
Multi-core execution: True
Number of cores: 4


0. Time
1. exercise_hours**
2. exercise_sessions
3. stress_level
4. calories

File: ../data/DATASET.csv
Patterns

{
    "pattern": "{'3+', '4+'}",
    "type": "Emerging TGP",
    "time_lag": "~ +2.4285714285714284 weeks : 0.5",
    "emergence": [
        {
            "time_lag": "~ +1.0285714285714285 weeks : 1.0",
            "growth_rate": 0.9829268292682928
        },
        {
            "time_lag": "~ +2.4285714285714284 weeks : 0.5",
            "growth_rate": 0.8857142857142853
        }
    ]
}
{
    "pattern": "{'3-', '4-'}",
    "type": "Emerging TGP",
    "time_lag": "~ +2.1857142857142855 weeks : 0.5",
    "emergence": [
        {
            "time_lag": "~ +2.1857142857142855 weeks : 0.5",
            "growth_rate": 0.9299999999999998
        }
    ]
}


 --- end --- 
```


### License:

* MIT

### References:

* Dickson Owuor, Anne Laurent, and Joseph Orero (2019). Mining Fuzzy-temporal Gradual Patterns. In the proceedings of the 2019 IEEE International Conference on Fuzzy Systems (FuzzIEEE). IEEE. doi:10.1109/FUZZ-IEEE.2019.8858883.
* Runkler, T. A. (2005), Ant colony optimization of clustering models. Int. J. Intell. Syst., 20: 1233-1251. doi:10.1002/int.20111

[![Build Status](https://travis-ci.org/owuordickson/trenc.svg?branch=master)](https://travis-ci.org/owuordickson/trenc)

## Border T-GRAANK
A python implementation of the <i>Border Temporal-GRAdual rANKing</i> algorithm. The algorithm is built from two algorithms: <em><strong>MBD-LL</strong>Border</em> and <em>T-GRAANK</em>.<br>
<!-- Research paper published at FuzzIEEE 2019 International Conference on Fuzzy Systems (New Orleans): link<br> -->

### Requirements:
You will be required to install the following python dependencies before using <em><strong>Border</strong>T-GRAANK</em> algorithm:
```
                   install python (version => 2.7)

```

```
                    $ pip install numpy
                    $ pip install python-dateutil scikit-fuzzy

```

### Usage:
Use it a command line program with the local package:
```
$python init_bordertgraank.py -f fileName.csv -c refCol -s minSup  -r minRep -p allowPara -m cores
```

The input parameters (required) are: ```fileName.csv, refColumn, minSupport, minRepresentativity```. You are required to use a <strong>file</strong> in csv format and make sure the <i>timestamp column</i> is the first column in the file. You specify:
* <strong>reference item (refCol)</strong> - column\attribute that is the base of the temporal transformations
* <strong>minimum support(minSup)</strong> - threshold count of frequent FtGPs
* <strong>mimimum representativity (minRep)</strong> - threshold count of transformations to be performed on the data-set
* <strong>allow multiprocessing (allowPara)</strong> - binary for allowing parallel multiprocessing or not
* <strong>number of cores (cores)</strong> - explicitly indicate number of cores to be reserved for usage

Example with a data-set and specified values<br>
```
$python init_bordertgraank.py -f DATASET.csv -c 0 -s 0.52 -r 0.5 -p 1
```

Output:
```
Run-time: 0.5971848964691162 seconds
Algorithm: Border-TGRAANK 
No. of data sets: 8
No. of (dataset) attributes: 5
Minimum support: 0.5
Minimum representativity: 0.5
Multi-core execution: True
Number of cores: 4


Emerging Pattern | Time Lags: (Transformation n, Transformation m)

[[('1+', '4+'), '4+']] | ('~ +6.0 days : 1.0', '~ +4.8 days : 1.0')
[[('4+', '3+'), '4+']] | ('~ +6.0 days : 1.0', '~ +4.8 days : 1.0')
[[('1+', '3-'), '3-']] | ('~ +6.0 days : 1.0', '~ +1.1428571428571428 weeks : 0.5')

Total: 3 FtGEPs found!
------------------------------------------------------------------------
```

### License:
* MIT

### References:
* Dong, G. and Li, J. (1999). Efficient mining of emerging patterns: Discovering trends and differences. In Proceedings of the Fifth ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, KDD '99, pages 43-52, New York, NY, USA.
* Laurent, A., Lesot, M.-J., and Rifqi, M. (2015). Mining emerging gradual patterns. In 2015 Conference of the International Fuzzy Systems Association and the European Society for Fuzzy Logic and Technology (IFSA-EUSFLAT-15). Atlantis Press.

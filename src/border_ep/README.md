
## Border T-GRAANK
A python implementation of the <i>Border Temporal-GRAdual rANKing</i> algorithm. The algorithm is formulated through the combination of two algorithms: <em><strong>MBD-LL</strong>Border</em> and <em>T-GRAANK</em>.<br>
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
$python border_tgraank.py -t pType -f fileName.csv -c refCol -s minSup  -r minRep
```

The input parameters are: ```fileName.csv, refColumn, minSupport, minRepresentativity```. You are required to use a <strong>file</strong> in csv format and make sure the <i>timestamp column</i> is the first column in the file. You specify:
* <strong>pattern type (pType)</strong> - choose between mining: (1) fuzzy-temporal patterns or (2) emerging fuzzy-temporal patterns
* <strong>reference item (refCol)</strong> - column\attribute that is the base of the temporal transformations
* <strong>minimum support(minSup)</strong> - threshold count of frequent FtGPs
* <strong>mimimum representativity (minRep)</strong> - threshold count of transformations to be performed on the data-set

Example with a data-set and specified values<br>
```
$python border_tgraank.py -t 2 -f DATASET.csv -c 0 -s 0.52 -r 0.5
```

Output:
```
Dataset Ok
Total Data Transformations: 8 | Minimum Support: 0.52
------------------------------------------------------------------------
1 : exercise_hours**
2 : exercise_sessions
3 : stress_level
4 : calories
Emerging Pattern | Time Lags: (Dataset 1, Dataset 2)
[[('4+', '3+'), '4+']] : ('~ +6.0 days : 1.0', '~ +4.8 days : 1.0')
[['2+', ('2+', '1+')]] : ('~ +6.0 days : 1.0', '~ +1.35 weeks : 1.0')
[[('4+', '3+'), '4+']] : ('~ +6.0 days : 1.0', '~ +1.35 weeks : 1.0')

Total: 3 FtGEPs found!
------------------------------------------------------------------------
```

### License:
* MIT

### References:
* Dong, G. and Li, J. (1999). Efficient mining of emerging patterns: Discovering trends and differences. In Proceedings of the Fifth ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, KDD '99, pages 43-52, New York, NY, USA.
* Laurent, A., Lesot, M.-J., and Rifqi, M. (2015). Mining emerging gradual patterns. In 2015 Conference of the International Fuzzy Systems Association and the European Society for Fuzzy Logic and Technology (IFSA-EUSFLAT-15). Atlantis Press.

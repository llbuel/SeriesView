# SeriesView
 
A program to visualize the partial sums of a series using a simple test input.

For example, the sum 

$\sum_{n=1}^{10} \frac{(-1)^{n+1}}{n^3}$

could be entered as:

    SV> seriesview('n',0,10,'(-1)^(n+1)/n^3')

Showing:

![screenshot1](/docs/Figure_1.png?raw=true)

Currently, the function supports the basic operations for exponentiation, negatives, addition, subtraction, multiplication, and division. It also supports multiple ways of inputting expressions, such as implied multiplication (not explicitly using `*`). In addition, the function supports custom summation iterating variables.

## To do:

* Inclusion of common mathematical functions such as `sin()` or `sqrt()`
* Including support of common mathematical constants such as $\pi$ or **e**
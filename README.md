# Multiplayer Minesweeper

This repository is an implementation of the MIT OCW 6.005 course problem assignment 6
(2011 version, now outdated and archived [here](http://dspace.mit.edu/handle/1721.1/106923)). Visit
[this page](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-005-software-construction-spring-2016/)
for the currently active version of the course.

You can find informations for this problem set in the `Instructions.pdf` on the project root directory.

## Basic usage
To run this project the [PyCharm IDE](https://www.jetbrains.com/pycharm/) is recommended.

## Implementation notes:
* Python was chosen over Java, although Java was requested on the problem assignment. The reasons for this choice are inherently personal to the implementer of this project.
 (Briefly: I had used Java for all of the previous assignments, and I didn't program in another language from some time. So I decided to pick Python, even
 though learning the many things about the language and its library required me some additional days.)
* Currently, the user connection is closed regardless of the DEBUG flag. (See Problem 5, point a. or point 3. of the DIG message specification for more infos.)
* Point b. in Problem 5 is still incomplete (i.e. the multiple client connections are not threadsafe - but the Board is).

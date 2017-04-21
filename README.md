# Multiplayer Minesweeper

To run this project the [PyCharm IDE](https://www.jetbrains.com/pycharm/) is recommended.

This project is based on the fall 2011 version of the MIT OCW 6.005 course (Elements of Software Construction).
This course is now outdated and has been replaced by the newer [MIT OCW 6.005 (spring 2016 version)](https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-005-software-construction-spring-2016/),
whose site should contain links to the older versions. I didn't make enough searches to be sure, but it seems that the site of the 2011
version is only downloadable offline (through a [link on the 2016 course](https://hdl.handle.net/1721.1/106923)) and no longer reachable online.

Some notes on the execution:
* Python was chosen over Java, although Java was requested on the problem assignment. The reasons for this choice are inherently personal to the implementer of this project.
 (Briefly: I had used Java for all of the previous assignments, and I didn't program in another language from some time. So I decided to pick Python, even
 though learning the many things about the language and its library required me some additional days.)
* Currently, the user connection is closed regardless of the DEBUG flag. (See Problem 5, point a. or point 3. of the DIG message specification for more infos.)
* Point b. in Problem 5 is still incomplete (i.e. the multiple client connections are not threadsafe - but the Board is).

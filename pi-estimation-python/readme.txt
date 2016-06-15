This is a simple application for estimating the PI number with Monte Carlo method. It can be calculated by comparing area of a circle inside a square to the area of the square.

This program randomly generates points inside the unit square. It then checks to see if the point is inside the circle, i.e. if x^2 + y^2 < R^2, where x and y are the coordinates of the point and R is the radius of the circle. The program sums points inside the circle (M).

PI is then approximated as 4*M / N, where N the the number of generated point.

This example includes:
- description of input parameters, i.e. the number of samples, in the 'input.json' file,
- Scalarm adapters in form of Python scripts (input_writer, executor and output reader), 
- and simulation "binaries" which is a simple Python script that performs the calculations.

These files can be registered in Scalarm as a simulation scenario. Python is the only dependencies for this application to run.

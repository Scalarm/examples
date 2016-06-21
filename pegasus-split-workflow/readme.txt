This example is a Pegasus workflow use case, which intends show integration between both tools Scalarm and Pegasus.

The most easy way to run it is to download our Scalarm-Pegasus tutorial virtual machine (http://www.scalarm.com/index.php?action=download), which has Scalarm and Pegasus installed and configured.

The workflow case is a classic split workflow, which takes 1 file as input and produces several output files.

You can take a look at https://pegasus.isi.edu/documentation/tutorial_scientific_workflows.php to read more about different basic workflow shapes.

This example includes:
- description of input parameters - it accepts file names which should be processed (store them in the 'inputs' folder and rezip 'inputs' and 'split-workflow' folders into 'simulation-binaries.zip'),
- Scalarm adapters in form of Python scripts (input_writer, executor and progress monitor), 
- and simulation "binaries" which includes packed 'inputs' and 'split-workflow' folders.

These files can be registered in Scalarm as a simulation scenario. Python and Pegasus are dependencies for this application to run.

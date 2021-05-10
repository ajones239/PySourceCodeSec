# PySourceCodeSec

## What is it?
PySourceCodeSec is a security source code analyzer for Python. Its aim is to find security vulnerabilities in Python source code using machine learning. PySourceCodeSec is quite flexible in a number of different ways, such as which machine learning algorithms to use, which vulnerabilities to look for, and what features of source code to check for. PySourceCodeSec is written completely in Python. 

PySourceCodeSec includes the necessary tools to create your own dataset and machine learning models. There is a sample fetch tool which downloads Python code off GitHub (don't worry, it only downloads files in the public domain so no need to worry about licensing issues). There is also a sample labeller tool to turn your Python sample code into a dataset (CSV file) that can be easily used to create machine learning models.

PySourceCodeSec has been rigorously tested on Linux, but it should work on Mac and Windows too. If you have CUDA libraries installed, PySourceCodeSec will automatically take advantage of your GPU when training the neural network.

## The Code
The codebase for PySourceCodeSec is divided into three modules: the data collection module (fetch_tool), the data processing module (labeller), and the machine learning module (ml). All interface code is defined in pysourcecodesec.py.

### fetch_tool
The fetch tool consists of a single class with a few globally defined variables and helper functions. The fetch tool runs its own thread and simply downloads code from GitHub using the Python GitHub API.

### labeller
The labeller was designed similarly to the fetch tool. It is a single class that runs in its own thread. However, there are two files in the labeller module. The labeller.py file contains the actual labeller class, while the features.py file contains functions for defining various features of source code as well as global constant variables that are referenced in other modules.

### ml
The machine learning module contains six files. There is a file for the MLManager class, which acts as the point of contact for interacting with the machine learning components. Actions such as creating new models, analyzing files, and saving/loading existing models to disk are all controlled though the MLManager class. There is also an abstract class MLModel, defined in its own file, that defines some abstract methods each machine learning class must implement. It is used more like an interface, although implemented as an abstract class since Python does not support interfaces. There are two classes, each with its own file, that extend the MLModel class. These are the logistic regression model and the neural network model. There is also a status file that defined the ModelStatus enum, and the ml_exception file to define a custom MLException class.

### Defaults
#### Machine learning algorithms
PySourceCodeSec includes a logistic regression model and an artificial neural network built using the Keras sequential API.
#### Vulnerabilities
PySourceCodeSec checks for possible command injection vulnerabilities, primarily surrounding the use of user input and creating subprocesses, hardcoded credentials such as usernames, passwords, and network interfaces, as well as possible command injection through the loading of yaml files.
#### Source Code Features
Machine learning algorithms classify items based on features of the item it is classifying. In the case of PySourceCodeSec, the item being classified is a line of Python source code. The default features (and their types) defined for a line of Python source code are:

>the number of hardcoded strings (integer)

>whether there are variables named 'user', 'password', or other names indicative of hardcoded credentials (boolean)

>wordcount (integer)

>whether open() is used (boolean)

>whether popen() is used (boolean)

>whether system() is used (boolean)

>whether exec() is used (boolean)

>whether eval() is used (boolean)

>whether input() is used (boolean)

>whether there are hardcoded IP addresses present (boolean)

>whether there are yaml related functions used (boolean)

>whether the statement is conditional (boolean)

>number of function/method invocations (integer)

## How do I install it?
### Clone the repository
>git clone https://github.com/ajones239/PySourceCodeSec
### Install Dependencies 
>python3 -m pip install -r requirements.txt

PySourceCodeSec is ready for use.

## How do I use it?
There are two ways to use PySourceCodeSec.
### Interactive Mode
>./pysourcecodesec.sh -i

This will display a menu on your terminal and prompt you for commands. The interface is straight forward to use and allows for all actions to be done in real time. 

### CLI Mode
You can also specify what you want to do using option flags. Here are a list of common option flags

-a <algorithm>     the algorithm to (create if -c is present, use for analysis if -f is present)

-f <file name>     the file or directory to analyze

-c                 create a new model

-e                 use existing saved model

-s                 save the model after creating it

For a complete list of options, run the program with the '-h' option.

## How can I...
PySourceCodeSec can be easily modified. However, as of now there is no way to make changes to the tool without making some modifications to the source code.

### ...add new machine learning algorithms?
To add a new machine learning algorithm, there are a few things that must be done.

1) In ml/ml_manager.py, you must add the name (as a string) of your algorithm to the algorithms variable. 

2) To access your new algorithm, you must add your shorthand name (specified on the command line) and actual name (the name from step one) as a key value pair in the names variable located at the top of pysourcecodesec.py.

3) Create a new Python class for your algorithm. It must extend MLModel (located in ml/ml_model.py) and override all abstract methods. Namely, it must include methods get_status, train, get_model, load_model, and classify. For more information on what these methods should do, check out the ml_model.py source.

### ...change the features of source code?
To change the features of source code, you will need to edit labeller/features.py. 

1) Write a function for each feature you want to define. The function should input a line of source code as a string, and output an integer. You can use other output types if you use a custom algorithm that supports it, but the default algorithms assume a numeric type for all fields.

2) change the features variable, located at the bottom of labeller/features.py, to reflect the functions you want to use.

### ...change which vulnerabilities are checked for?
PySourceCodeSec uses Bandit, an existing static source code analyzer, to label code samples as vulnerable or not. Bandit uses modular tests to check for specific vulnerabilities. You can change the default modules, and even use your own custom ones.

1) The Bandit command is located near the top of labeller/features.py. To ensure the tool continues to work, make sure the Bandit output format is not changed. There is a list of default Bandit modules you can select from at the top of file as well.

2) Under the Bandit command in labeller/features.py, there is a variable labels. The keys are the Bandit test modules, and the values are the labels being used in the dataset. Update this file with your new Bandit modules and whatever you want to classify them as.

3) That's it! Although to ensure high accuracy in your machine learning model, you should consider changing the features if you changed the default vulnerabilities being checked for.


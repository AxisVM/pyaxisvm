# **PyAxisVM**

The official python package of AxisVM, a Structural Analysis & Design Software.

## **Overview**

The PyAxisVM project offers a high-level interface to AxisVM, making its operations available directly from Python. It builds on top of Microsoft's COM technology and supports all the features of the original AxisVM COM type library, making you able to
  
* build, manipulate and analyse AxisVM models

* find solutions with iterative methods

* build extension modules

on top of that, **PyAxisVM** ehnaces the type library with python's slicing mechanism and context management that enables writing clean, concise, and radable code.


## **Documentation and Issues**

The ***AxisVM API Reference Guide*** is available in pdf format,  you can download it _[***here***](https://axisvm.eu/axisvm-downloads/#application)_.


It is highly recommended to install **PyAxisVM** in a dedicated virtual enviroment to avoid conflicts with other libraries. Onw of the reasons for this is that the `comtypes` package throws an error for empty SafeArrays. This issue is solved and a pull request has been made. Because of this, until the request gets accepted, it is important to uninstall exisitng installations of `comtypes` before installing **PyAxisVM**. When you install **PyAxisVM**, a corrected version of `comtypes` gets installed automatically. Installing **PyAxisVM** in a dedicated virtual enviroment naturally dissolves this issue.


Please feel free to post issues and other questions at PyAxisVM Issues. This is the best place to post questions and code.

## **Installation**
This is optional, but we suggest you to create a dedicated virtual enviroment to avoid conflicts with your other projects. Create a folder, open a command shell in that folder and use the following command

```console
>>> python -m venv venv_name
```

Once the enviroment is created, activate it via typing

```console
>>> .\venv_name\Scripts\activate
```

The AxisVM python package can be installed (either in a virtual enviroment or globally) from PyPI using `pip` on Python >= 3.5:

```console
>>> pip install axisvm
```

## **Dependencies**

You will need a local licenced copy of AxisVM prior and including 13r2. To get a copy of AxisVM, please visit our _[***homepage***](https://axisvm.eu/)_.


## **Getting Started**


### **Register the AxisVM Type Library**

If this is not your first time using AxisVM through a COM interface on your machine, you should already have a registered type library and you can skip this step. Otherwise, follow the instructions at the beginning of the ***AxisVM API Reference Guide***.


### **Launch AxisVM**

The `axisvm.com.client` submodule implements various tools to handle the client side operations of creating a COM connection. Import the module and start a new application instance with the `start_AxisVM` method.


```python
from axisvm.com.client import start_AxisVM
axapp = start_AxisVM(visible=True)
```

To test the connection, you can query the path of the executable being run by typing `axapp.FullExePath`.

### **Basic Usage**

If the connection is complete, create a new model and get an interface to it.


```python
modelId = axapp.Models.New()
axmodel = axapp.Models.Item[modelId]
```

Every time you create a new AxisVM instance with the `start_AxisVM` command, an attempt is made to import the type library as a python module, or to generate one if necessary. The generated module is then accessible as `axisvm.com.tlb`.
 
The next block of commands adds a line to the scene:


```python
from axisvm.com.tlb import lgtStraightLine, RLineGeomData
n1 = axmodel.Nodes.Add(0, 0, 0)
n2 = axmodel.Nodes.Add(1, 1, 1)
l1 = axmodel.Lines.Add(n1, n2, lgtStraightLine, RLineGeomData())
```

Put AxisVM on top and scale model to fill up the current view:


```python
axapp.BringToFront()
axmodel.FitInView()
```

At the end of your session, release the connection and close the application simply by typing


```python
axapp.UnLoadCOMClients()
axapp.Quit()
```

## **Tips and Tricks**

**PyAxisVM** wraps up the COM type library, allowing users to exploit the elegant and concise syntax python provides, while leaving everything on the table. If for example, we wanted to calculate areas of surface elements, the out of box solution would be something like

```python
areas = []
for i in range(axmodel.Surfaces.Count):
    areas.append(axmodel.Surfaces.Item[i+1].Area)
```

or using a list comprehension

```python
areas = [axmodel.Surfaces.Item[i+1].Area for i in range(axmodel.Surfaces.Count)]
```

With **PyAxisVM**, evaluation of single entity properties over collections is as easy as

```python
areas = [s.Area for s in axmodel.Surfaces]
```

or simply

```python
areas = axmodel.Surfaces[:].Area
```

To get a full overview about the pythonic usage of COM services, check out this jupyter notebook.

## **License and Acknowledgments**

PyAxisVM is licensed under the MIT license.

This module, PyAxisVM makes no commercial claim over AxisVM whatsoever. This tool extends the functionality of AxisVM by adding a Python interface to the AxisVM COM service without changing the core behavior or license of the original software. The use of PyAxisVM requires a legally licensed local copy of AxisVM.

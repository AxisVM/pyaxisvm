![alt text](https://github.com/AxisVM/DynamoToAxisVM/blob/master/Documentation/images/AxisVM%20logo.bmp)
# **PyAxisVM**

The official python package of **AxisVM**, a Structural Analysis & Design Software.

## **Overview**

The **PyAxisVM** project offers a high-level interface to **AxisVM**, making its operations available directly from Python. It builds on top of Microsoft's COM technology and supports all the features of the original **AxisVM** COM type library, making you able to
  
* build, manipulate and analyse **AxisVM** models

* find better solutions with iterative methods

* combine the power of **AxisVM** with third-party Python libraries

* build extension modules

On top of that, **PyAxisVM** ehnaces the type library with Python's slicing mechanism, context management and more, that enables writing clean, concise, and readable code.

## **Installation**
This is optional, but we suggest you to create a dedicated virtual enviroment to avoid conflicts with your other projects. Create a folder, open a command shell in that folder and use the following command

```console
>>> python -m venv venv_name
```

Once the enviroment is created, activate it via typing

```console
>>> .\venv_name\Scripts\activate
```

The **AxisVM** python package can be installed (either in a virtual enviroment or globally) from PyPI using `pip` on Python >= 3.5:

```console
>>> pip install axisvm
```

## **Documentation and Issues**

The ***AxisVM API Reference Guide*** is available in pdf format,  you can download it _[***here***](https://axisvm.eu/axisvm-downloads/#application)_.


It is highly recommended to install **PyAxisVM** in a dedicated virtual enviroment to avoid conflicts with other libraries. One of the reasons for this is that the `comtypes` package throws an error for empty SafeArrays. This issue is fixed and a pull request has been made. Until the request gets accepted, it is important to uninstall exisitng installations of `comtypes` before installing **PyAxisVM**. Alternatively, you can install **PyAxisVM** using the `--force-reinstall` flag. 

```console
>>> pip install --force-reinstall axisvm
```

If `comtypes` is not yet installed or you install **PyAxisVM** in a dedicated virtual enviroment, a corrected version of `comtypes` gets installed automatically. 

Please feel free to post issues and other questions at **PyAxisVM** Issues. This is the best place to post questions and code.

## **Dependencies**

You will need a local licenced copy of **AxisVM** prior and including 13r2. To get a copy of **AxisVM**, please visit our _[***homepage***](https://axisvm.eu/)_.


## **Getting Started**


### **Register the AxisVM Type Library**

If this is not your first time using **AxisVM** through a COM interface on your machine, you should already have a registered type library and you can skip this step. Otherwise, follow the instructions at the beginning of the ***AxisVM API Reference Guide***.


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

Every time you create a new **AxisVM** instance with the `start_AxisVM` command, an attempt is made to import the type library as a python module, or to generate one if necessary. The generated module is then accessible as `axisvm.com.tlb`.
 
The next block of commands adds a line to the scene:


```python
from axisvm.com.tlb import lgtStraightLine, RLineGeomData
n1 = axmodel.Nodes.Add(0, 0, 0)
n2 = axmodel.Nodes.Add(1, 1, 1)
l1 = axmodel.Lines.Add(n1, n2, lgtStraightLine, RLineGeomData())
```

Put **AxisVM** on top and scale model to fill up the current view:


```python
axapp.BringToFront()
axmodel.FitInView()
```

At the end of your session, release the connection and close the application simply by typing


```python
axapp.UnLoadCOMClients()
axapp.Quit()
```

Take a look at the jupyter notebooks in the _[***examples***](https://github.com/AxisVM/pyaxisvm/tree/main/examples)_ folder of this repository for more use cases.

## **Tips and Tricks**

**PyAxisVM** wraps up the COM type library, allowing users to exploit the elegant and concise syntax Python provides, while leaving everything on the table. If for example, we wanted to calculate areas of surface elements, the out of box solution would be something like

```python
areas = []
for i in range(axmodel.Surfaces.Count):
    areas.append(axmodel.Surfaces.Item[i+1].Area)
```

or using a list comprehension

```python
areas = [axmodel.Surfaces.Item[i+1].Area for i in range(axmodel.Surfaces.Count)]
```

With **PyAxisVM**, evaluation of single item properties over collections is as easy as

```python
areas = [s.Area for s in axmodel.Surfaces]
```

or simply

```python
areas = axmodel.Surfaces[:].Area
```

Click [***here***](https://github.com/AxisVM/pyaxisvm/blob/6abfebdfd26a76721836e1b490465d1f5a474a83/tips_and_tricks.md) to get a full overview about the pythonic usage of the library.

## **License and Acknowledgments**

**PyAxisVM** is licensed under the MIT license.

This module, **PyAxisVM** makes no commercial claim over AxisVM whatsoever. This tool extends the functionality of **AxisVM** by adding a Python interface to the **AxisVM** COM service without changing the core behavior or license of the original software. The use of **PyAxisVM** requires a legally licensed local copy of **AxisVM**.

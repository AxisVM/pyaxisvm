# **Tips and Tricks**

This notebook sums up the changes in syntax, compared to the 'raw' usage of the COM type library. Everything the API provides out of the box is still available and is working according to the docs, but the syntax of Python provides a few shortcuts to make coding easier.

### **Collections and Slicing**

When accessing items of collection-like COM classes (like `IAxisVMDomains`, `IAxisVMSurfaces`, anything having an `Item` method), you can use the slicing mechanism of python. Suppose that we have an `IAxisVMModel`  instance called `axm`. The model has several domains, each of them having the property `Weight`. Let say we want to calculate the weight of all domains. The out of box solution for this would be something like
  
```python
weights=[]
for i in range(axm.Surfaces.Count):
    weights.append(axm.Surfaces.Item[i+1].Weight)
weight = sum(weights)
```
or using a list comprehension

```python
weight = sum([axm.Surfaces.Item[i+1].Weight for i in range(axm.Surfaces.Count)])
```

or maybe even this

```python
surfaces = [axm.Surfaces.Item[i+1] for i in range(axm.Surfaces.Count)]
weight = sum(map(lambda s : s.Weight, surfaces))
```

Anyhow, although there is nothing inherently wrong with these approaches, they clearly doesn't measure up to

```python
# if you are new to this, the colon means 'all indices in range' 
weight = sum(axm.Surfaces[:].Weight)
```

or

```python
weight = sum(s.Weight for s in axm.Surfaces)
```

or maybe

```python
weight = sum(map(lambda s : s.Weight, axm.Surfaces))
```

Notice how the loops here are carried out over the collection object itself. This is because collection types implement the so-called iterator protocol. 

It is also possible to provide negative indices:

```python
axm.Surfaces[-1].Weight # equivalent to axm.Surfaces[axm.Surfaces.Count].Weight
axm.Surfaces[-2].Weight # equivalent to axm.Surfaces[axm.Surfaces.Count - 1].Weight
```

Without further due, some other use cases that exploit Python's slicing mechanism:

```python
axm.Surfaces[1, 5, 7].Weight
axm.Surfaces[1:4].Weight  # equivalent to axm.Surfaces[1, 2, 3].Weight
axm.Surfaces[1:8:2].Weight  # equivalent to axm.Surfaces[1, 3, 5, 7].Weight
axm.Surfaces[8:1:-2].Weight  # equivalent to axm.Surfaces[8, 6, 4, 2].Weight
```

Furthermore, instead of typing `axm.Surfaces.Count`, you can use `len(axm.Surfaces)` to get the number of surfaces in the model.

**Be aware here, that the index of the first item in any iterable COM object is 1, opposed to the zero-indexed nature of Python.**

### **Context Management**

If you have some experience with AxisVM and COM, you know about the methods `BeginUpdate` and `EndUpdate`. With python, you don't need to care about this, instead you can simply use the `with` statement like this

```python
with axm as model:
    # do some modification here on the model
    ...
```

### **Accessing the Type Library**

When a new instace of `IAxisVMApplication` is created, the type library is generated on demand. After that, the type library can be accessed as

```python
import axisvm.com.tlb as axtlb
```

### **Daemon**

When creating a new interface, you can do it like

```python
from axisvm.com.client import start_AxisVM
axvm = start_AxisVM(visible=True, daemon=True)
```

The keyword argument `daemon=True` is a simple shortcut, equivalent to 

```python
from axisvm.com.client import start_AxisVM
import axisvm.com.tlb as axtlb
axapp = start_AxisVM(visible=True, daemon=False)
axapp.CloseOnLastReleased = True
axapp.AskCloseOnLastReleased = False
axapp.AskSaveOnLastReleased = False
axapp.ApplicationClose = axtlb.acEnableNoWarning
```

As a result of these settings, if the COM server is shut down, AxisVM shuts down either, hence the term `daemon`. Shutting down the COM server can be done as:

```python
axapp.Quit()
```

or

```python
del axapp
```

The difference here is that in the second case `axapp` gets garbage collected (killing the connection before), whereas in the first case it only kills the connection.
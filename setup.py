
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="axisvm",                     
    version="0.0.4",                        
    author="Inter-CAD Ltd",
    author_email = 'bbalogh@axisvm.eu',
    url = 'https://github.com/AxisVM/pyaxisvm',   
    download_url = 'https://github.com/AxisVM/pyaxisvm/archive/refs/tags/v_0_0_2.zip',                     
    keywords = ['AxisVM', 'Axis', 'Civil Engineering'],
    description="A python package for AxisVM",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where='src'),   
    classifiers=[
        'Development Status :: 3 - Alpha',     
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',
    ],                                      
    python_requires='>=3.6',                             
    package_dir={'':'src'},     
    install_requires=[            
          'setuptools',
          'wheel',
          'comtypes',
          'pywin32'
      ],
)


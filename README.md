Py-Bedrock
==========

Py-Bedrock providers Python utilities to configure and deploy Mochi-based
services using Python.

Running the Jupyter demo
------------------------

Create a spack environment and add the required packages in it.

```
spack env create py-bedrock-demo
spack env activate py-bedrock-demo
spack add py-mochi-bedrock
spack add py-jupyterlab-server
spack install
```

Deactivate and re-activate the environment for the PYTHONPATH variable to
be updated.

```
spack env deactivate
spack env activate py-bedrock-demo
```

Run the Jupyter server.

```
jupyter notebook --ip 0.0.0.0 --port 8888
```

Then from your browser, open the `notebooks/Demo.ipynb` notebook,
and start playing!

# (C) 2018 The University of Chicago
# See COPYRIGHT in top-level directory.


"""
.. module:: local
   :synopsis: This package helps deploy a Bedrock service on a local machine

.. moduleauthor:: Matthieu Dorier <mdorier@anl.gov>


"""
from .spec import ProcSpec


def deploy(
        spec: 'ProcSpec',
        bedrock_binary: str = 'bedrock',
        log_level: str = 'info',
        config_file_name: str = None,
        workdir: str = '.'):
    from subprocess import Popen, DEVNULL
    from tempfile import NamedTemporaryFile
    config = spec.to_json()
    protocol = spec.margo.mercury.protocol
    input_file = None
    if config_file_name is None:
        input_file = NamedTemporaryFile(
            prefix='bedrock-',
            dir=workdir,
            delete=False,
            suffix='.json')
        config_file_name = input_file.name
    with open(config_file_name, 'w+') as f:
        f.write(config)
    cmd = [bedrock_binary, protocol,
           '-v', log_level,
           '-c', config_file_name]
    Popen(cmd,
          stdin=DEVNULL,
          stdout=DEVNULL,
          stderr=DEVNULL,
          shell=True)

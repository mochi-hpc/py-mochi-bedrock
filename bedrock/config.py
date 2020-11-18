# (C) 2018 The University of Chicago
# See COPYRIGHT in top-level directory.


"""
.. module:: config
   :synopsis: This package helps configure a Bedrock deployment

.. moduleauthor:: Matthieu Dorier <mdorier@anl.gov>


"""


import json
import attr
from attr import Factory
from attr.validators import instance_of, in_
from typing import List, NoReturn, Union, Any


def _check_validators(instance, attribute, value):
    """Generic hook function called by the attr package when setattr is called,
    to run the validators corresponding to the attribute being modified."""
    attribute.validator(instance, attribute, value)
    return value


@attr.s(auto_attribs=True, on_setattr=_check_validators, kw_only=True)
class SpecListDecorator:
    """The SpecListDecorator class is used in various places in this module
    to wrap a list object and provide an identical API, with some checks
    being done when the list is modified:
    - All the elements have the same type (provided in constructor)
    - All the elements have a unique name attribute
    - All the elements appear only once in the list
    Additionally, this class allows looking elements by their name attribute.
    """

    _list: list = attr.ib(validator=instance_of(list))
    _type: type = attr.ib(
        validator=instance_of(type),
        default=Factory(lambda self: type(self._list[0]), takes_self=True))

    def _find_with_name(self, name: str):
        match = [e for e in self._list if e.name == name]
        if len(match) == 0:
            return None
        else:
            return match[0]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._list[key]
        elif isinstance(key, str):
            match = self._find_with_name(key)
            if match is None:
                raise KeyError(f'No item found with name "{key}"')
            return match
        else:
            raise TypeError(f'Invalid key type {type(key)}')

    def __setitem__(self, key: int, spec):
        if key < 0 or key >= len(self._list):
            KeyError('Invalid index')
        if not isinstance(spec, self._type):
            raise TypeError(f'Invalid type  {type(spec)} ' +
                            f'(expected {self._type})')
        match = self._find_with_name(val.name)
        if match is not None:
            if self.index(match) != key:
                raise KeyError(
                    'Conflicting object with the same name ' +
                    f'"{spec.name}"')
        self._list[key] = spec

    def __delitem__(self, key: Union[int, str]):
        if isinstance(key, int):
            self._list.__delitem__(key)
        elif isinstance(key, str):
            match = self._find_with_name(spec.name)
            if match is None:
                raise KeyError('Invalid name {key}')
            index = self.index(match)
            self._list.__delitem__(index)
        else:
            raise TypeError(f'Invalid key type')

    def append(self, spec: Any) -> NoReturn:
        if not isinstance(spec, self._type):
            raise TypeError(f'Invalid type  {type(spec)} ' +
                            f'(expected {self._type})')
        match = self._find_with_name(spec.name)
        if match is not None:
            raise KeyError(
                'Conflicting object with the same name ' +
                f'"{spec.name}"')
        self._list.append(spec)

    def index(self, arg: Any) -> int:
        if isinstance(arg, str):
            match = self._find_with_name(spec.name)
            if match is None:
                raise ValueError(f'Object named "{arg}" not in the list')
            else:
                return match
        else:
            return self._list.index(arg)

    def clear(self) -> NoReturn:
        self._list.clear()

    def copy(self) -> list:
        return self._list.copy()

    def count(self, value) -> int:
        if isinstance(value, str):
            match = self._find_with_name(value)
            if match is None:
                return 0
            else:
                return 1
        else:
            return self._list.count(value)

    def extend(self, l):
        for s in  l:
            self.append(s)

    def insert(self, index: int, spec: Any) -> NoReturn:
        if not isinstance(spec, self._type):
            raise TypeError(f'Invalid type  {type(spec)} ' +
                            f'(expected {self._type})')
        match = self._find_with_name(spec.name)
        if match is not None:
            raise KeyError(
                'Conflicting object with the same name ' +
                f'"{spec.name}"')
        self._list.insert(index, spec)

    def pop(self, index: int):
        return self._list.pop(index)

    def remove(self, spec):
        if isinstance(spec, str):
            match = self._find_with_name(spec)
            if match is None:
                raise ValueError(f'{spec} not in list')
            self.remove(match)
        else:
            self._list.remove(spec)

    def __iter__(self):
        return iter(self._list)


@attr.s(auto_attribs=True, on_setattr=_check_validators, kw_only=True)
class MercurySpec:
    """Mercury configuration.

    :param address: Address or protocol (e.g. "na+sm")
    :type address: str

    :param listening: Whether the process is listening for RPCs
    :type listening: bool

    :param ip_subnet: TODO
    :type ip_subnet: str

    :param auth_key: TODO
    :type auth_key: str

    :param auto_sm: Automatically rely on shared-memory
    :type auto_sm: bool

    """

    address: str = attr.ib(validator=instance_of(str))
    listening: bool = attr.ib(default=True, validator=instance_of(bool))
    ip_subnet: str = attr.ib(default='', validator=instance_of(str))
    auth_key: str = attr.ib(default='', validator=instance_of(str))
    auto_sm: bool = attr.ib(default=False, validator=instance_of(bool))
    max_contexts: int = attr.ib(default=1, validator=instance_of(int))
    na_no_block: bool = attr.ib(default=False, validator=instance_of(bool))
    na_no_retry: bool = attr.ib(default=False, validator=instance_of(bool))
    no_bulk_eager: bool = attr.ib(default=False, validator=instance_of(bool))
    no_loopback: bool = attr.ib(default=False, validator=instance_of(bool))
    request_post_incr: int = attr.ib(default=256, validator=instance_of(int))
    request_post_init: int = attr.ib(default=256, validator=instance_of(int))
    stats: bool = attr.ib(default=False, validator=instance_of(bool))
    version: str = attr.ib(default='unknown', validator=instance_of(str))

    def to_dict(self) -> dict:
        return attr.asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'MercurySpec':
        return MercurySpec(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str) -> 'MercurySpec':
        data = json.loads(json_string)
        return MercurySpec.from_dict(data)

    def validate(self) -> NoReturn:
        attr.validate(self)


@attr.s(auto_attribs=True,
        on_setattr=_check_validators,
        kw_only=True,
        hash=False,
        eq=False)
class PoolSpec:
    """Argobots pool configuration."""

    name: str = attr.ib(
        validator=instance_of(str))
    kind: str = attr.ib(
        default='fifo_wait',
        validator=in_(['fifo', 'fifo_wait']))
    access: str = attr.ib(
        default='mpmc',
        validator=in_(['private', 'spsc', 'mpsc', 'spmc', 'mpmc']))

    def to_dict(self) -> dict:
        return attr.asdict(self)

    @staticmethod
    def from_dict(data) -> 'PoolSpec':
        return PoolSpec(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str) -> 'PoolSpec':
        data = json.loads(json_string)
        return PoolSpec.from_dict(data)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other) -> bool:
        return id(self) == id(other)

    def __ne__(self, other) -> bool:
        return id(self) != id(other)

    def validate(self) -> NoReturn:
        attr.validate(self)


@attr.s(auto_attribs=True, on_setattr=_check_validators, kw_only=True)
class SchedulerSpec:
    """Argobots scheduler configuration."""

    type: str = attr.ib(
        default='basic_wait',
        validator=in_(['default', 'basic', 'prio', 'randws', 'basic_wait']))
    pools: List[PoolSpec] = attr.ib()

    @pools.validator
    def _check_pools(self, attribute, value):
        if len(value) == 0:
            raise ValueError('Scheduler must have at least one pool')
        for pool in value:
            if not isinstance(pool, PoolSpec):
                raise TypeError(f'Invalid type {type(value)} in list of pools')

    def to_dict(self) -> dict:
        return {'type': self.type, 'pools': [pool.name for pool in self.pools]}

    @staticmethod
    def from_dict(data: dict, abt_spec: 'ArgobotsSpec') -> 'SchedulerSpec':
        scheduler = SchedulerSpec()
        scheduler.type = data['type']
        pool_refs = abt_spec.pools
        pools = []
        for pool_ref in data['pools']:
            if isinstance(pool_ref, int):
                if pool_ref < 0 or pool_ref >= len(pool_refs):
                    raise IndexError(f'Pool index {pool_ref} out of range')
                pools.append(pool_refs[pool_ref])
            elif isinstance(pool_ref, str):
                matches = [p for p in pool_refs if p.name == pool_ref]
                if len(matches) == 0:
                    raise NameError(f'Pool {pool_ref} not found')
                pools.append(matches[0])
            else:
                raise TypeError(f'Invalid pool ref type {type(pool_ref)}')
        scheduler.pools = pools
        return scheduler

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str,
                  abt_spec: 'ArgobotsSpec') -> 'SchedulerSpec':
        data = json.loads(json_string)
        return SchedulerSpec.from_dict(data, abt_spec)

    def validate(self) -> NoReturn:
        attr.validate(self)


@attr.s(auto_attribs=True,
        on_setattr=_check_validators,
        kw_only=True,
        hash=False,
        eq=False)
class XstreamSpec:
    """Argobots xstream configuration."""

    name: str = attr.ib(
        default='__undefined__',
        validator=instance_of(str))
    cpubind: int = attr.ib(default=-1, validator=instance_of(int))
    affinity: List[int] = attr.ib(
        factory=list, validator=instance_of(list))
    scheduler: SchedulerSpec = attr.ib(
        validator=instance_of(SchedulerSpec),
        factory=SchedulerSpec)

    @name.validator
    def _check_name(self, attribute, value):
        if len(value) == 0:
            raise ValueError('name cannot be empty')

    def to_dict(self) -> dict:
        filter = attr.filters.exclude(attr.fields(type(self)).scheduler)
        data = attr.asdict(self, filter=filter)
        data['scheduler'] = self.scheduler.to_dict()
        return data

    @staticmethod
    def from_dict(data: dict, abt_spec: 'ArgobotsSpec') -> 'XstreamSpec':
        scheduler_args = data['scheduler']
        scheduler = SchedulerSpec.from_dict(scheduler_args, abt_spec)
        args = data.copy()
        del args['scheduler']
        xstream = XstreamSpec(**args)
        xstream.scheduler = scheduler

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str, abt_spec: 'ArgobotsSpec') -> 'XstreamSpec':
        data = json.loads(json_string)
        return XstreamSpec.from_dict(data, abt_spec)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other) -> bool:
        return id(self) == id(other)

    def __ne__(self, other) -> bool:
        return id(self) != id(other)

    def validate(self) -> NoReturn:
        attr.validate(self)
        self.scheduler.validate()


def _default_xstream_list():
    scheduler = SchedulerSpec(pools=[PoolSpec(name='__primary__')])
    return [XstreamSpec(name='__primary__', scheduler=scheduler)]


@attr.s(auto_attribs=True, on_setattr=_check_validators, kw_only=True)
class ArgobotsSpec:
    """ArgobotsSpec configuration."""

    abt_mem_max_num_stacks: int = attr.ib(
        default=8, validator=instance_of(int))
    abt_thread_stacksize: int = attr.ib(
        default=2097152, validator=instance_of(int))
    version: str = attr.ib(default='unknown', validator=instance_of(str))
    _xstreams: List[XstreamSpec] = attr.ib(
        default=Factory(_default_xstream_list),
        validator=instance_of(list))
    _pools: List[PoolSpec] = attr.ib(
        factory=list,
        validator=instance_of(list))

    @abt_mem_max_num_stacks.validator
    def _check_abt_mem_max_num_stacks(self, attribute, value):
        if value < 0:
            raise ValueError('Invalid abt_mem_max_num_stacks (should be >= 0)')

    @abt_thread_stacksize.validator
    def _abt_thread_stacksize(self, attribute, value):
        if value <= 0:
            raise ValueError('Invalid abt_thread_stacksize (should be > 0)')

    @_pools.validator
    def _check_pools(self, attribute, value):
        for pool in value:
            if not isinstance(pool, PoolSpec):
                raise TypeError(
                    '_pools should contain only PoolSpec objects')

    @_xstreams.validator
    def _check_xstreams(self, attribute, value):
        for es in value:
            if not isinstance(es, XstreamSpec):
                raise TypeError(
                    'xstreams should contain only XstreamSpec objects')

    @property
    def xstreams(self) -> SpecListDecorator:
        return SpecListDecorator(list=self._xstreams, type=XstreamSpec)

    @property
    def pools(self):
        return SpecListDecorator(list=self._pools, type=PoolSpec)

    def new_pool(self, *args, **kwargs) -> PoolSpec:
        p = PoolSpec(*args, **kwargs)
        self.pools.append(p)
        return p

    def new_xtream(self, *args, **kwargs) -> XstreamSpec:
        es = XstreamSpec(*args, **kwargs)
        self.xstreams.append(es)
        return es

    def add(self, thing: Union[PoolSpec, XstreamSpec]) -> NoReturn:
        if isinstance(thing, PoolSpec):
            self.pools.append(thing)
        elif isinstance(thing, XstreamSpec):
            self.xstreams.append(thing)
        else:
            raise TypeError(f'Cannot add object of type {type(thing)}')

    def to_dict(self) -> dict:
        filter = attr.filters.exclude(attr.fields(type(self))._pools,
                                      attr.fields(type(self))._xstreams)
        data = attr.asdict(self, filter=filter)
        data['pools'] = [p.to_dict() for p in self.pools]
        data['xstreams'] = [x.to_dict() for x in self.xstreams]
        return data

    @staticmethod
    def from_dict(data: dict) -> 'ArgobotsSpec':
        args = data.copy()
        del args['pools']
        del args['xstreams']
        abt = ArgobotsSpec(**args)
        pool_list = data['pools']
        for pool_args in pool_list:
            abt.pools.add(PoolSpec.from_dict(pool_args))
        xstream_list = data['xstreams']
        for xstream_args in xstream_list:
            abt.xstreams.add(XstreamSpec.from_dict(xstream_args, abt))
        return abt

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str) -> 'ArgobotsSpec':
        return ArgobotsSpec.from_dict(json.loads(json_string))

    def validate(self):
        attr.validate(self)
        if len(self._xstreams):
            raise ValueError('No XstreamSpec found')
        for es in self._xstreams:
            es.validate()
            if len(es.scheduler.pools) == 0:
                raise ValueError(
                    f'Scheduler in XstreamSpec "{es.name}" has no pool')
            for p in es.scheduler.pools:
                if p not in self._pools:
                    raise ValueError(
                        f'Pool "{p.name}" in XstreamSpec "{es.name}" was ' +
                        'not added to the ArgobotsSpec')
        for p in self._pools:
            p.validate()


def _mercury_from_args(arg) -> MercurySpec:
    if isinstance(arg, MercurySpec):
        return arg
    elif isinstance(arg, dict):
        return MercurySpec(**arg)
    elif isinstance(arg, str):
        return MercurySpec(address=arg)
    else:
        raise TypeError(f'cannot convert type {type(arg)} into a MercurySpec')


@attr.s(auto_attribs=True, on_setattr=_check_validators, kw_only=True)
class MargoSpec:
    """MargoSpec configuration."""

    mercury: MercurySpec = attr.ib(
        converter=_mercury_from_args,
        validator=instance_of(MercurySpec))
    argobots: ArgobotsSpec = attr.ib(
        factory=ArgobotsSpec, validator=instance_of(ArgobotsSpec))
    progress_timeout_ub_msec: int = attr.ib(
        default=100, validator=instance_of(int))
    enable_profiling: bool = attr.ib(
        default=False, validator=instance_of(bool))
    enable_diagnostics: bool = attr.ib(
        default=False, validator=instance_of(bool))
    handle_cache_size: int = attr.ib(
        default=32, validator=instance_of(int))
    profile_sparkline_timeslice_msec: int = attr.ib(
        default=1000, validator=instance_of(int))
    progress_pool: PoolSpec = attr.ib(default=None)
    rpc_pool: PoolSpec = attr.ib(default=None)

    def to_dict(self) -> dict:
        filter = attr.filters.exclude(attr.fields(type(self)).argobots,
                                      attr.fields(type(self)).mercury,
                                      attr.fields(type(self)).progress_pool,
                                      attr.fields(type(self)).rpc_pool)
        data = attr.asdict(self, filter=filter)
        data['argobots'] = self.argobots.to_dict()
        data['mercury'] = self.mercury.to_dict()
        if self.progress_pool is None:
            data['progress_pool'] = None
        else:
            data['progress_pool'] = self.progress_pool.name
        if self.rpc_pool is None:
            data['rpc_pool'] = None
        else:
            data['rpc_pool'] = self.rpc_pool.name
        return data

    @staticmethod
    def from_dict(self, data: dict) -> 'MargoSpec':
        abt_args = data['argobots']
        hg_args = data['mercury']
        argobots = ArgobotsSpec.from_dict(abt_args)
        mercury = MercurySpec.from_dict(hg_args)
        rpc_pool = None
        progress_pool = None
        if data['rpc_pool'] is not None:
            rpc_pool = argobots.find_pool(data['rpc_pool'])
        if data['progress_pool'] is not None:
            progress_pool = argobots.find_pool(data['progress_pool'])
        args = data.copy()
        args['argobots'] = argobots
        args['mercury'] = mercury
        args['rpc_pool'] = rpc_pool
        args['progress_pool'] = progress_pool
        return MargoSpec(**args)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str) -> 'MargoSpec':
        return MargoSpec.from_dict(json.loads(json_string))

    def validate(self):
        attr.validate(self)
        self.mercury.validate()
        self.argobots.validate()
        if self.progress_pool is None:
            raise ValueError('progress_pool not set in MargoSpec')
        if self.rpc_pool is None:
            raise ValueError('rpc_pool not set in MargoSpec')
        if self.progress_pool not in self.argobots._pools:
            raise ValueError(
                f'progress_pool "{self.progress_pool.name}" not found' +
                ' in ArgobotsSpec')
        if self.rpc_pool not in self.argobots._pools:
            raise ValueError(
                f'rpc_pool "{self.rpc_pool.name}" not found' +
                ' in ArgobotsSpec')


@attr.s(auto_attribs=True, on_setattr=_check_validators, kw_only=True)
class AbtIOSpec:
    """ABT-IO configuration."""

    name: str = attr.ib(validator=instance_of(str))
    pool: PoolSpec = attr.ib(validator=instance_of(PoolSpec))

    def to_dict(self) -> dict:
        return {'name': self.name,
                'pool': self.pool.name}

    @staticmethod
    def from_dict(data: dict, abt_spec: ArgobotsSpec) -> 'AbtIOSpec':
        name = data['name']
        pool = abt_spec.find_pool(data['pool'])
        abtio = AbtIOSpec(name=name, pool=pool)
        return abtio

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str,  abt_spec: ArgobotsSpec) -> 'AbtIOSpec':
        return AbtIOSpec.from_dict(json.loads(json_string), abt_spec)


def _margo_from_args(arg) -> MargoSpec:
    if isinstance(arg, MargoSpec):
        return arg
    elif isinstance(arg, dict):
        return MargoSpec(**arg)
    elif isinstance(arg, str):
        return MargoSpec(mercury=arg)
    else:
        raise TypeError(f'cannot convert type {type(arg)} into a MargoSpec')


@attr.s(auto_attribs=True, on_setattr=_check_validators, kw_only=True)
class ProcSpec:
    """Process configuration."""

    margo: MargoSpec = attr.ib(
        validator=instance_of(MargoSpec),
        converter=_margo_from_args)
    _abt_io: List[AbtIOSpec] = attr.ib(
        init=False, factory=list,
        validator=instance_of(list))

    @property
    def abt_io(self) -> SpecListDecorator:
        return SpecListDecorator(list=self._abt_io, type=AbtIOSpec)

    def to_dict(self):
        data = {'margo': self.margo.to_dict(),
                'abt_io': [a.to_dict() for a in self._abt_io]}
        return data

    @staticmethod
    def from_dict(data: dict):
        margo = MargoSpec.from_dict(data['margo'])
        abt_io = []
        if 'abt_io' in data:
            for a in data['abt_io']:
                abt_io.append(AbtIOSpec.from_dict(a, margo.argobots))
        return ProcSpec(margo=margo, abt_io=abt_io)

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_string: str):
        return ProcSpec.from_dict(json.loads(json_string))

    def validate(self):
        attr.validate(self)
        for a in self._abt_io:
            p = a.pool
            if p not in self.margo.argobots.pools:
                raise ValueError(f'Pool "{p.name}" used by ABT-IO instance' +
                                  ' not found in margo.argobots.pools')


attr.resolve_types(MercurySpec, globals(), locals())
attr.resolve_types(PoolSpec, globals(), locals())
attr.resolve_types(SchedulerSpec, globals(), locals())
attr.resolve_types(XstreamSpec, globals(), locals())
attr.resolve_types(ArgobotsSpec, globals(), locals())
attr.resolve_types(MargoSpec, globals(), locals())
attr.resolve_types(AbtIOSpec, globals(), locals())
attr.resolve_types(ProcSpec, globals(), locals())

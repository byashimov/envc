# WIP: envc

Loads configuration from environment using type hints.    
Inspired by Go [kelseyhightower/envconfig](https://github.com/kelseyhightower/envconfig)

Set:

```shell
export HOST=github.com
export PORT=443
export TIMEOUT=10s
```

Use:

```python
from envc import load

@dataclass
class Database:
    host: str
    port: int
    timeout: timedelta

config = load(Database)
assert config.host == "github.com"
assert config.port == 443
assert config.timeout == timedelta(seconds=10)
```

## Contents

[TOC]

## Key features

- duration support
- nested configurations
- dict, list, tuple parsing
- custom types support
- zero dependency

### Duration support

Inspired by Go [ParseDuration](https://pkg.go.dev/time#ParseDuration).  
Use `TIMEOUT=10s` instead of "TIMEOUT_S=10" or mandatory comments: 

```python
@dataclass
class Database:
    timeout: timedelta

config = load(Database)
assert config.timeout.total_seconds() == 10.0            # Seconds
assert config.timeout.total_seconds() * 1000 == 10000.0  # Milliseconds
```

Warning: make sure you use `total_seconds()` 
instead of `seconds` or any other attribute (hour, minute, etc).
That is a common gotcha: attributes do not convert time, they return initial values.


### Nested configurations

Attribute names used as prefix for env variables.

```python
@dataclass
class Connection:
    pool_size: int

@dataclass
class Database:
    connection: Connection

@dataclass
class Config:
    database: Database

# export DATABASE_CONNECTION_POOL_SIZE=3
config = load(Config)
assert config.database.pool_size == 3
```

### Dict, list, tuple, "whatever iterable it is" parsing

Comma separated values parsed to the given iterable.  
Colon and comma separated values parsed to the given mapping. 

```shell
export PARAMS = "foo:1,bar:2"
export DIGITS = "1,2,3"
export UNIQUE = "foo,foo,foo,bar"
export FROZEN = "4,5,6"
export HOST = "localhost,5432"
```

```python
@dataclass
class Generics:
    params: Dict[str, int]
    digits: List[int]
    unique: Set[str]
    frozen: Tuple[int, ...]
    host: Tuple[str,int]  # fixed length tuple

config = load(Generics)
assert config.params == {"foo": 1, "bar": 2}
assert config.digits == [1, 2, 3]
assert config.unique == {"foo", "bar"}
assert config.frozen == (4, 5, 6)
assert config.host == ("localhost", 5432)
```

**Warning:** typing validation is kinda unstable and tricky part of Python. 
It's always a good idea to keep it simple.

### Custom types support

A classifier can be passed to `load` to support custom types.  
Classifier is a function 
which returns a callback 
which converts environment variable to the final type.

```python
from envc import classifier

def my_classifier(cls) -> Callable[[str], Any]:
    if issubclass(cls, MyHello):
        return lambda c: MyHello(f"{c}, hello!", lol=True)
    # Other types goes through the default pipeline
    return classifier(cls)

load(MyConfig, classifier=my_classifier)
```

**Be warned:** generic types from `typing` module does not support `issubclass` check.  
Your classifier should be ready for that.

## Prefix

Var names prefix can be passed as a keyword to `load`.

```python
@cdataclass
class Database:
    host: str

# export DB_HOST=foo    
config = load(Database, prefix='DB')
assert config.host == 'foo'
```

## Aliases/explicit 

Explicit var names can be passed in some cases.

```python
@cdataclass
class Database:
    __envc__ = {
        "kind": "TYPE",
    }
    kind: str

# export DB_HOST=foo    
config = load(Database, prefix='DB')
assert config.host == 'foo'
```


## Alternatives

Lots of them can be found [here](https://pypi.org/search/?q=envconfig).

# Basic Example

```python
from python_configuration_system import ConfigLoader, ConfigSchema, StringField

schema = ConfigSchema(
    name="example",
    fields=[
        StringField(name="service_name", description="Service name."),
    ],
)

loader = ConfigLoader(schema=schema, sources=[])
config = loader.resolve(overrides={"service_name": "demo"})

print(config.require("service_name"))
```

This example uses only public package-root exports.

`ConfigLoader.resolve()` is implemented for minimal orchestration. It does not
implement profile inheritance, profile-specific file loading, remote
configuration, live reload, secret storage, or CLI behavior.

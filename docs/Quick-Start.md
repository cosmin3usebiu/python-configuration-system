# Quick Start

This quick start shows the implemented configuration flow. It does not imply
release readiness or API freeze.

```python
from python_configuration_system import (
    ConfigLoader,
    ConfigSchema,
    EnvConfigSource,
    IntegerField,
    StringField,
)

schema = ConfigSchema(
    name="service",
    fields=[
        StringField(name="service_name", description="Service name."),
        IntegerField(name="port", description="Port.", default=8080),
    ],
)

loader = ConfigLoader(
    schema=schema,
    sources=[EnvConfigSource(prefix="APP_")],
)

config = loader.resolve(overrides={"service_name": "example"})

print(config["service_name"])
print(config.require("port"))
```

`ConfigLoader.resolve()` loads registered sources, applies overrides as highest
precedence, validates the merged result, and returns `ResolvedConfig`.

R001 remains unapproved, API-unfrozen, architecture-unfrozen, and not in Release
Phase.

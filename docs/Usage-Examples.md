# Usage Examples

## Override-Driven Resolution

```python
from python_configuration_system import ConfigLoader, ConfigSchema, StringField

schema = ConfigSchema(
    name="app",
    fields=[StringField(name="name", description="Application name.")],
)

config = ConfigLoader(schema=schema, sources=[]).resolve(
    overrides={"name": "demo"},
)

assert config["name"] == "demo"
```

## Unsupported Profile Inheritance

`ConfigProfile` is public but non-frozen. Profile inheritance is not
implemented. A requested profile with `extends` set causes
`ConfigLoader.resolve()` to raise `ProfileResolutionError`.

## Non-Claims

These examples do not declare approval, API freeze, Release Phase, release
readiness, production readiness, or package publication readiness.

from abc import ABC, abstractmethod

__all__ = ("Plugin", "Routes", "Extend", "Overwrite", "Route")
VALID_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}


class Route:

    def __init__(self, path, endpoint, methods=("GET",)):
        if not path.startswith("/"):
            raise ValueError("Path must start with '/'")
        if not all(method in VALID_METHODS for method in methods):
            raise ValueError(f"Invalid HTTP methods: {methods}")

        self.path = path
        self.endpoint = endpoint
        self.methods = methods

    def serialize_route(self):
        return self.path, self.endpoint, self.methods


class Overwrite:
    def __init__(self, *args: Route):
        self.routes = args

    def serialize_routes(self):
        return tuple((route.serialize_route() for route in self.routes))


class Extend:
    def __init__(self, *args: Route):
        self.routes = args

    def serialize_routes(self):
        return tuple((route.serialize_route() for route in self.routes))


class Routes:
    def __init__(self, overwrite: Overwrite, extend: Extend):
        self.overwrite_routes = overwrite.serialize_routes()
        self.extend_routes = extend.serialize_routes()


class Plugin(ABC):

    @abstractmethod
    async def execute(self) -> Routes:
        raise NotImplementedError("Execute function must be implemented in order for plugin to work!")



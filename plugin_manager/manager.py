import importlib
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from starlette.applications import Starlette
from starlette.routing import Route
from colorama import Fore, Style

from plugin_manager.exceptions import PluginValidationError, PluginLoadError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginManager:
    REQUIRED_FIELDS = {"name", "author", "description", "version", "entry_point"}

    def __init__(self, app: Starlette, routes: List[Route]):
        if not isinstance(app, Starlette):
            raise TypeError("app must be a Starlette instance")
        if not isinstance(routes, list):
            raise TypeError("routes must be a list")

        self.app = app
        self._routes = routes
        self._plugins: List[Dict[str, Any]] = []
        self._load_plugins()

    @property
    def plugins(self) -> List[Dict[str, Any]]:
        return self._plugins

    @property
    def routes(self) -> List[Route]:
        return self._routes

    def _validate_plugin_manifest(self, module: Any, plugin_name: str) -> Dict[str, Any]:
        plugin_data = {
            "name": getattr(module, "name", None),
            "dir": plugin_name,
            "author": getattr(module, "author", None),
            "description": getattr(module, "description", None),
            "version": getattr(module, "version", None),
            "license": getattr(module, "license", None),
            "email": getattr(module, "email", None),
            "website": getattr(module, "website", None),
            "entry_point": getattr(module, "entry_point", None)
        }

        missing_fields = self.REQUIRED_FIELDS - {k for k, v in plugin_data.items() if v is not None}
        if missing_fields:
            raise PluginValidationError(f"Missing required fields: {', '.join(missing_fields)}")

        return plugin_data

    def _load_plugins(self) -> None:
        try:
            plugins_dir = Path(__file__).resolve().parent.parent / "plugins"
            if not plugins_dir.exists():
                logger.error(f"Plugins directory not found: {plugins_dir}")
                return

            plugin_files = [p for p in os.listdir(plugins_dir) if not p.startswith("_")]
        except Exception as e:
            logger.error(f"Failed to read plugins directory: {e}")
            return

        for plugin in plugin_files:
            try:
                module = importlib.import_module(f"plugins.{plugin}.manifest")
                plugin_data = self._validate_plugin_manifest(module, plugin)
                self._plugins.append(plugin_data)
                logger.info(f"Successfully loaded plugin: {plugin_data['name']}")

            except ImportError as e:
                logger.error(f"Failed to import plugin {plugin}: {e}")
            except PluginValidationError as e:
                logger.error(f"Plugin {plugin} validation failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading plugin {plugin}: {e}")

    def update_routes(self, plugins_data: List[Dict[str, Any]]) -> None:
        try:
            routes_dict = {route.path: route for route in self._routes if isinstance(route, Route)}

            for plugin in plugins_data:
                for route_to_overwrite in plugin.get('overwrite_routes', []):
                    if not isinstance(route_to_overwrite, (list, tuple)) or len(route_to_overwrite) != 3:
                        logger.error(f"Invalid route format in plugin {plugin['name']}")
                        continue

                    path, handler, methods = route_to_overwrite
                    if path in routes_dict:
                        try:
                            original_index = self._routes.index(routes_dict[path])
                            self._routes[original_index] = Route(path, handler, methods=methods)
                            routes_dict[path] = self._routes[original_index]
                        except Exception as e:
                            logger.error(f"Failed to update route {path}: {e}")

        except Exception as e:
            logger.error(f"Failed to update routes: {e}")

    async def load_plugins(self) -> None:
        for plugin in self._plugins:
            try:
                entry_module = importlib.import_module(f"plugins.{plugin['dir']}.plugin")
                entry_class = getattr(entry_module, plugin["entry_point"])
                plugin_instance = entry_class()

                routes = await plugin_instance.execute()
                if not hasattr(routes, 'overwrite_routes') or not hasattr(routes, 'extend_routes'):
                    raise PluginLoadError(f"Plugin {plugin['name']} has invalid routes format")

                plugin_index = self._plugins.index(plugin)
                self._plugins[plugin_index].update({
                    "overwrite_routes": routes.overwrite_routes,
                    "extend_routes": routes.extend_routes
                })

                for extend_route in routes.extend_routes:
                    if not isinstance(extend_route, (list, tuple)) or len(extend_route) != 3:
                        logger.error(f"Invalid extend route format in plugin {plugin['name']}")
                        continue

                    path, handler, methods = extend_route
                    self.app.routes.insert(0, Route(path, handler, methods=methods))

            except ImportError as e:
                logger.error(f"Failed to import entry point for plugin {plugin['name']}: {e}")
            except PluginLoadError as e:
                logger.error(str(e))
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin['name']}: {e}")

        self.update_routes(self._plugins)
        loaded_plugins = ", ".join(plugin["name"] for plugin in self._plugins)
        print(f"{Fore.GREEN}Plugins loaded({len(self._plugins)}): {loaded_plugins}{Style.RESET_ALL}")

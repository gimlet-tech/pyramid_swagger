"""
Module for automatically serving /api-docs* via Pyramid.
"""
import simplejson

from .ingest import build_schema_mapping


def register_swagger_endpoints(config):
    """Create and register pyramid endpoints for /api-docs*.

    """
    schema_dir = config.registry.settings.get(
        'pyramid_swagger.schema_directory',
        None
    )
    resource_listing, resource_mapping = build_schema_mapping(schema_dir)
    with open(resource_listing) as input_file:
        register_resource_listing(config, simplejson.load(input_file))

    for name, filepath in resource_mapping.items():
        with open(filepath) as input_file:
            register_api_declaration(config, name, simplejson.load(input_file))


def register_resource_listing(config, resource_listing):
    """Registers an endpoint at /api-docs.

    :param config: Configurator instance for our webapp
    :type config: pyramid Configurator
    :param resource_listing: JSON representing a resource listing
    :type resource_listing: dict
    """
    def view_for_resource_listing(request):
        # Thanks to the magic of closures, this means we gracefully return JSON
        # without file IO at request time.
        return resource_listing

    route_name = 'api_docs'
    config.add_route(route_name, '/api-docs')
    config.add_view(
        view_for_resource_listing,
        route_name=route_name,
        renderer='json'
    )


def register_api_declaration(config, resource_name, api_declaration):
    """Registers an endpoint at /api-docs.

    :param config: Configurator instance for our webapp
    :type config: pyramid Configurator
    :param resource_name: The `path` parameter from the resource listing for
        this resource.
    :type resource_name: string
    :param api_declaration: JSON representing an api declaration
    :type api_declaration: dict
    """
    def view_for_api_declaration(request):
        # Thanks to the magic of closures, this means we gracefully return JSON
        # without file IO at request time.
        return api_declaration

    # NOTE: This means our resource paths are currently constrained to be valid
    # pyramid routes! (minus the leading /)
    route_name = 'apidocs-{0}'.format(resource_name)
    config.add_route(route_name, '/api-docs/{0}'.format(resource_name))
    config.add_view(
        view_for_api_declaration,
        route_name=route_name,
        renderer='json'
    )

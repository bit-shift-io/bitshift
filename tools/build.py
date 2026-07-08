#!/usr/bin/env python3
# https://staticjinja.readthedocs.io/en/latest/user/advanced.html

from staticjinja import Site
from jinja2 import Environment, FileSystemLoader
import logging
import os
import json

class RelEnvironment(Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)

class MySite(Site):
    #def is_template(self, filename):
    #    return filename.endswith(".html")

    def is_static(self, filename):
        return not filename.endswith(".html") and not filename.endswith(".css")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    searchpath = os.path.join(project_root, "templates")
    outpath = os.path.join(project_root, "public")

    env_globals={
    }

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    environment = RelEnvironment(
        loader=FileSystemLoader(searchpath=searchpath, encoding='utf8', followlinks=True)
    )
    environment.globals.update(env_globals)

    site = MySite(environment=environment, outpath=outpath, searchpath=searchpath, encoding='utf8')

    # enable automatic reloading
    site.render(use_reloader=False)
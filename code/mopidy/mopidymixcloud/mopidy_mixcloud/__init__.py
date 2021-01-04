from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '3.1415.9265'

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-Mixcloud'
    ext_name = 'mixcloud'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['users']=config.String(optional=True)
        schema['tags']=config.String(optional=True)
        schema['search_max']=config.Integer(optional=True)
        schema['refresh_period']=config.Integer(optional=True)
        schema['ignore_exclusive']=config.Boolean(optional=True)
        return schema

    def setup(self, registry):
        from .mopidy_mixcloud import MopidyMixcloud
        registry.add('backend', MopidyMixcloud)

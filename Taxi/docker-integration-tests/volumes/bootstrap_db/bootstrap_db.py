#!/usr/bin/env python
# -*- coding: utf-8 -*

import bootstrap_config_defaults_cache
import bootstrap_mongo
import bootstrap_redis


def main():
    bootstrap_mongo.init()
    bootstrap_redis.init()
    bootstrap_config_defaults_cache.init()


if __name__ == '__main__':
    main()

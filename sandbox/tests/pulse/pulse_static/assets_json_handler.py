import unittest

from sandbox.projects.sandbox_ci.pulse.pulse_static.assets_json_handler import AssetsJsonHandler

assets_json = {
    'main': '//serp-static-testing.s3.yandex.net/web4/freeze/6j1qtU8BUivaOpvzZJoVIt-UuuM.js',
    'entries': {
        'features/Collections_list/Collections_list@desktop': {
            'main': {
                'ru': 0
            }
        }
    },
    'chunks': [
        [
            {
                'name': 'chunk.0.0',
                'js': {
                    'url': '//serp-static-testing.s3.yandex.net/web4/freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.js'
                }
            }
        ]
    ]
}

assets_json_combined = [
    {
        'platform': 'desktop',
        'config': {
            'main': '//serp-static-testing.s3.yandex.net/web4/freeze/6j1qtU8BUivaOpvzZJoVIt-UuuM.js',
            'entries': {
                'features/Collections_list/Collections_list@desktop': {
                    'main': {
                        'ru': 0
                    }
                }
            },
            'chunks': [
                [
                    {
                        'name': 'chunk.0.0',
                        'js': {
                            'url': '//serp-static-testing.s3.yandex.net/web4/freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.js'
                        }
                    }
                ]
            ]
        }
    },
    {
        'platform': 'touch-phone',
        'config': {
            'main': '//serp-static-testing.s3.yandex.net/web4/freeze/mClGLrYZZ_siEuPsFxXSAD1UVXw.js',
            'entries': {
                'features/Collections_list/Collections_list@touch-phone': {
                    'main': {
                        'ru': 0
                    }
                }
            },
            'chunks': [
                [
                    {
                        'name': 'chunk.0.0',
                        'js': {
                            'url': '//serp-static-testing.s3.yandex.net/web4/freeze/IttcUhNg8ZDBy-SeGFiUQZZZjwI.js'
                        }
                    }
                ]
            ]
        }
    }
]

assets_json_components_experiments = {
    'main': '//serp-static-testing.s3.yandex.net/web4/freeze/6j1qtU8BUivaOpvzZJoVIt-UuuM.js',
    'chunks': {
        '123': [
            {
                'name': '123.0',
                'js': {
                    'url': '//serp-static-testing.s3.yandex.net/web4/freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.js'
                }
            }
        ]
    },
    'entries': {
        'features/Collections_list/Collections_list@desktop': {
            'main': {
                'ru': '123'
            }
        }
    },
    'componentsExperiments': {
        'components-experiments/test/desktop': {
            'hash': '9ec5e183abf00d3cdf5d'
        },
        'components-experiments/test/touch-phone': {
            'hash': 'a4c3ca79910b9de85b27'
        }
    }
}


class TestAssetsJsonHandler(unittest.TestCase):
    def test_files_from_single_assets_json(self):
        assets = AssetsJsonHandler()
        assets.parse(assets_json, use_main_chunk=1)
        self.assertDictEqual(assets.get_files(), {
            'common': ['freeze/main-react-bundle-common.js'],
            'desktop bundles': [
                '.build/features/Collections_list/Collections_list@desktop.css',
                '.build/features/Collections_list/Collections_list@desktop.js'
            ],
        })

    def test_symlinks_from_single_assets_json(self):
        assets = AssetsJsonHandler()
        assets.parse(assets_json, use_main_chunk=1)
        self.assertListEqual(assets.get_symlinks(), [
            ('freeze/6j1qtU8BUivaOpvzZJoVIt-UuuM.js', 'freeze/main-react-bundle-common.js'),
            ('freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.js', '.build/features/Collections_list/Collections_list@desktop.js'),
            ('freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.css', '.build/features/Collections_list/Collections_list@desktop.css'),
        ])

    def test_files_from_combined_assets_json(self):
        self.maxDiff = None
        assets = AssetsJsonHandler()
        for section in assets_json_combined:
            assets.parse(use_main_chunk=1, **section)

        self.assertDictEqual(assets.get_files(), {
            'desktop': ['freeze/main-react-bundle-desktop.js'],
            'desktop bundles': [
                '.build/features/Collections_list/Collections_list@desktop.css',
                '.build/features/Collections_list/Collections_list@desktop.js'
            ],
            'touch-phone': ['freeze/main-react-bundle-touch-phone.js'],
            'touch-phone bundles': [
                '.build/features/Collections_list/Collections_list@touch-phone.css',
                '.build/features/Collections_list/Collections_list@touch-phone.js'
            ],
        })

    def test_symlinks_from_combined_assets_json(self):
        assets = AssetsJsonHandler()
        for config in assets_json_combined:
            assets.parse(use_main_chunk=1, **config)
        self.assertListEqual(assets.get_symlinks(), [
            ('freeze/6j1qtU8BUivaOpvzZJoVIt-UuuM.js', 'freeze/main-react-bundle-desktop.js'),
            ('freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.js', '.build/features/Collections_list/Collections_list@desktop.js'),
            ('freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.css', '.build/features/Collections_list/Collections_list@desktop.css'),
            ('freeze/mClGLrYZZ_siEuPsFxXSAD1UVXw.js', 'freeze/main-react-bundle-touch-phone.js'),
            ('freeze/IttcUhNg8ZDBy-SeGFiUQZZZjwI.js', '.build/features/Collections_list/Collections_list@touch-phone.js'),
            ('freeze/IttcUhNg8ZDBy-SeGFiUQZZZjwI.css', '.build/features/Collections_list/Collections_list@touch-phone.css'),
        ])

    def test_files_from_components_experiments_json(self):
        assets = AssetsJsonHandler()
        assets.parse(assets_json_components_experiments, platform='desktop', use_main_chunk=1)
        self.assertDictEqual(assets.get_files(), {
            'desktop': ['freeze/main-react-bundle-desktop.js'],
            'desktop bundles': [
                '.build/features/Collections_list/Collections_list@desktop.css',
                '.build/features/Collections_list/Collections_list@desktop.js'
            ],
            'desktop component experiments': [
                '.build/components-experiments/test/desktop.css',
                '.build/components-experiments/test/desktop.js'
            ]
        })

    def test_symlinks_from_components_experiments_json(self):
        assets = AssetsJsonHandler()
        assets.parse(assets_json_components_experiments, platform='desktop', use_main_chunk=1)
        self.assertListEqual(assets.get_symlinks(), [
            (
                'freeze/6j1qtU8BUivaOpvzZJoVIt-UuuM.js',
                'freeze/main-react-bundle-desktop.js'
            ),
            (
                'freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.js',
                '.build/features/Collections_list/Collections_list@desktop.js'
            ),
            (
                'freeze/w0N5kH9JUVs14StMdLWDJFfm9_4.css',
                '.build/features/Collections_list/Collections_list@desktop.css'
            ),
            (
                '.build/components-experiments/test/desktop.9ec5e183abf00d3cdf5d.js',
                '.build/components-experiments/test/desktop.js'
            ),
            (
                '.build/components-experiments/test/desktop.9ec5e183abf00d3cdf5d.css',
                '.build/components-experiments/test/desktop.css'
            ),
        ])

from projects.common import wheels


def test_configure_environment():
    calculated = {
        key.split('-')[0]
        for key in wheels.build_deps_for_venv_packages(
            ['numpy', 'scikit-learn', 'scipy', 'pandas'],
        )
    }
    answer = {
        'numpy',
        'scikit_learn',
        'joblib',
        'scipy',
        'six',
        'python_dateutil',
        'pytz',
        'pandas',
    }
    assert calculated == answer

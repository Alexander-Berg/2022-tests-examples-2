from taxi_dashboards import validator


def test_configs(config_file_path):
    config_validator = validator.ConfigValidator()
    validator.validate_one(config_file_path, validator=config_validator)

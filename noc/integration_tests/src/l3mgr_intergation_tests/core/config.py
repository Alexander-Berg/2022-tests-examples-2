import envtoml as toml
from box import Box
from dotenv import load_dotenv


SECRETS_PATH = "/etc/tt/integtest.env"

load_dotenv("/etc/tt/integtest.env")


def init_base_config(path):
    base_config = toml.load(path)

    return Box(base_config)

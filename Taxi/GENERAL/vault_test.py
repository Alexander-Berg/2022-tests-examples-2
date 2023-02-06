from business_models import send_mail
from business_models.config_holder import ConfigHolder

# token = ConfigHolder().vault_token
# send_mail('kvdavydova@yandex-team.ru', 'kvdavydova@yandex-team.ru', 'vault', token)

from vault_client.instances import Production as VaultClient
vault_token = ConfigHolder().vault_token
client = VaultClient(
    authorization='OAuth {}'.format(vault_token)
)
head_version = client.get_version('sec-01ez9ax2fyn06vq04d39qwhx5t')

print head_version['value']['token']
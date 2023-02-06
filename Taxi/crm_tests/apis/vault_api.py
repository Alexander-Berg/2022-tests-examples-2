class VaultApi:

    def __init__(self, vault_url, vault_client):
        self.vault_url = vault_url
        self.vault_client = vault_client

    def vault_create(self, secret_name, key, value):
        # создать секрет
        secret_uuid = self.vault_client.create_secret(secret_name)
        self.vault_client.create_secret_version(
            secret_uuid,
            {key: value},
        )
        return secret_uuid

    def vault_get_value(self, secret_id, key):
        # достать значение из секрета
        head_version = self.vault_client.get_version(secret_id)
        return head_version['value'][key]

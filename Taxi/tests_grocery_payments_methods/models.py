import dataclasses
import typing


@dataclasses.dataclass
class SbpBankInfo:
    bank_name: str
    logo_url: str = 'logo_url'
    schema: str = 'schema'
    package_name: typing.Optional[str] = 'package_name'

    def to_raw(self):
        return dict(
            bankName=self.bank_name,
            logoURL=self.logo_url,
            schema=self.schema,
            package_name=self.package_name,
        )

    def to_raw_response(self):
        return dict(
            bank_name=self.bank_name,
            logo_url=self.logo_url,
            schema=self.schema,
            package_name=self.package_name,
        )

    def to_exp_meta(self):
        return dict(bank_name=self.bank_name)

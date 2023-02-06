from tests_eats_business_rules.core.admin import helper


async def test_create(taxi_eats_business_rules):
    await (
        helper.AdminTest()
        .request(
            'penalty_rule%5Bbusiness%5D=shop&'
            'penalty_rule%5BdeliveryType%5D=native&'
            'penalty_rule%5Btype%5D=refund&'
            'penalty_rule%5BpenaltyPercent%5D=123456&'
            'penalty_rule%5BmaxGMVPercent%5D=12345&'
            'penalty_rule%5BstartDate%5D=08.07.2021&'
            'penalty_rule%5BfinishDate%5D=31.07.2021&'
            'penalty_rule%5Bduration%5D=12243&'
            'penalty_rule%5Bregions%5D%5B%5D=1&'
            'penalty_rule%5Bregions%5D%5B%5D=878&'
            'penalty_rule%5Bbrands%5D%5B%5D=43&'
            'penalty_rule%5Bbrands%5D%5B%5D=1457&'
            'penalty_rule%5Bbrands%5D%5B%5D=281&'
            'penalty_rule%5BexcludedBrands%5D%5B%5D=1637&'
            'penalty_rule%5BexcludedBrands%5D%5B%5D=2371&'
            'penalty_rule%5Bclients%5D=123%2C+1234%2C+12345&'
            'penalty_rule%5BexcludedClients%5D=321%2C+5432&'
            'penalty_rule%5B_token%5D='
            'p2rTvRVc7ncMoKDlP3KPbs7UzoCAxMoYyFl39a7dEHE',
        )
        .run(taxi_eats_business_rules)
    )

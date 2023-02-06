from typing import List

from tests_eats_products import eats_upsell_recommendations


def find_recommendations(detailed_data: List[dict]) -> List[dict]:
    result = []
    for data in detailed_data:
        if data['type'] == 'upsell_recommendations':
            result.extend(data['payload']['recommendations'])

    return result


def merge_recommendations(
        recommendations: List[dict],
) -> List[eats_upsell_recommendations.Recommendation]:
    result = []
    for recommendation in recommendations:
        for item in recommendation['items']:
            result.append(
                eats_upsell_recommendations.Recommendation(
                    public_id=item['public_id'],
                    source=item['promoted']['source'],
                ),
            )

    return result

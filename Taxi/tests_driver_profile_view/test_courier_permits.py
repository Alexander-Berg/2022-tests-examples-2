# import weasyprint
import pytest


@pytest.mark.skip(reason='no weasyprint in tier0')
async def test_driver_banners(taxi_driver_profile_view, mockserver):
    @mockserver.handler('/render-template/convert')
    def _convert_handler(request):
        html = weasyprint.HTML(string=request.get_data())
        return mockserver.make_response(
            response=html.write_pdf(),
            headers={'Content-Type': 'application/pdf'},
        )

    response = await taxi_driver_profile_view.post(
        'eda/courier-permits',
        json={
            'name': 'Иван Иванович Иванов',
            'phone': '+7(123)456-7890',
            'date': '2020-04-08T17:05:48.372Z',
            'city': 'Москва',
        },
    )
    assert response.status_code == 200

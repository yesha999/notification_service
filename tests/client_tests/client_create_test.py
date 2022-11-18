import pytest


@pytest.mark.django_db
class TestCreate:
    def test_correct_create(self, client):
        data = {"phone": 79994567890, "tag": "some_tag", "timezone": "UTC"}
        post_response = client.post('/mailing/client/create', data=data)
        get_response = client.get(f"/mailing/client/{post_response.data['id']}")
        assert post_response.status_code == 201
        assert get_response.status_code == 200  # Заодно протестировали стандартный гет запрос
        assert post_response.data["phone"] == 79994567890
        assert get_response.data["tag"] == "some_tag"

    def test_incorrect_phone_create(self, client):
        data1 = {"phone": 89994567890, "tag": "some_tag", "timezone": "UTC"}
        data2 = {"phone": 799945678901, "tag": "some_tag", "timezone": "UTC"}
        post_response1 = client.post('/mailing/client/create', data=data1)
        post_response2 = client.post('/mailing/client/create', data=data2)

        assert post_response1.status_code == 400
        assert post_response2.status_code == 400

    def test_incorrect_timezone_create(self, client):
        data = {"phone": 79994567890, "tag": "some_tag", "timezone": "qwerty"}
        post_response = client.post('/mailing/client/create', data=data)
        assert post_response.status_code == 400

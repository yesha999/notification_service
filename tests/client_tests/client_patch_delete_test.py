import pytest


@pytest.mark.django_db
class TestPut:
    def test_correct_put(self, client):
        data = {"phone": 79994567890, "tag": "some_tag", "timezone": "UTC"}
        post_response = client.post('/mailing/client/create', data=data)
        change_data = {"phone": 79014567890, "tag": "some_tag_change", "timezone": "Europe/Moscow"}
        put_response = client.put(f"/mailing/client/{post_response.data['id']}", data=change_data,
                                  content_type="application/json")

        assert put_response.status_code == 200
        assert put_response.data["phone"] == 79014567890
        assert put_response.data["tag"] == "some_tag_change"
        assert put_response.data["timezone"] == "Europe/Moscow"

    def test_incorrect_put_timezone(self, client):
        data = {"phone": 79994567890, "tag": "some_tag", "timezone": "UTC"}
        post_response = client.post('/mailing/client/create', data=data)
        change_data = {"phone": 79994567890, "tag": "some_tag_change", "timezone": "somE_Zone"}
        put_response = client.put(f"/mailing/client/{post_response.data['id']}", data=change_data,
                                  content_type="application/json")

        assert put_response.status_code == 400

    def test_incorrect_put_phone(self, client):
        data = {"phone": 79994567890, "tag": "some_tag", "timezone": "UTC"}
        post_response = client.post('/mailing/client/create', data=data)
        change_data = {"phone": 799945678905555, "tag": "some_tag_change", "timezone": "Europe/Moscow"}
        put_response = client.put(f"/mailing/client/{post_response.data['id']}", data=change_data,
                                  content_type="application/json")

        assert put_response.status_code == 400


@pytest.mark.django_db
class TestDelete:
    def test_delete_client(self, client):
        data = {"phone": 79994567890, "tag": "some_tag", "timezone": "UTC"}
        post_response = client.post('/mailing/client/create', data=data)
        delete_response = client.delete(f"/mailing/client/{post_response.data['id']}")
        get_response = client.get(f"/mailing/client/{post_response.data['id']}")

        assert delete_response.status_code == 204
        assert get_response.status_code == 404

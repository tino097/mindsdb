from http import HTTPStatus
from unittest.mock import MagicMock, call

import mindsdb.api.http.namespaces.config as config_module


def mock_config(monkeypatch, data):
    config_mock = MagicMock()

    def getitem(key):
        return data[key]

    def get_value(key, default=None):
        return data.get(key, default)

    config_mock.__getitem__.side_effect = getitem
    config_mock.get.side_effect = get_value
    config_mock.update = MagicMock()
    config_factory = MagicMock(return_value=config_mock)
    monkeypatch.setattr(config_module, "Config", config_factory)
    return config_mock


class TestGetConfig:
    def test_get_success(self, client, monkeypatch):
        config_data = {
            "auth": {"http_auth_enabled": True},
            "api": {
                "http": {"host": "127.0.0.1", "port": "47334"},
                "mysql": {"host": "127.0.0.1", "port": "47335"},
            },
            "default_llm": {"provider": "gpt"},
            "default_embedding_model": {"name": "embed"},
            "default_reranking_model": {"name": "rerank"},
        }
        mock_config(monkeypatch, config_data)
        api_status = {"http": True, "mysql": False}
        monkeypatch.setattr(
            config_module,
            "get_api_status",
            MagicMock(return_value=api_status),
        )

        response = client.get("/api/config/")

        assert response.status_code == HTTPStatus.OK
        body = response.get_json()
        assert body["auth"]["http_auth_enabled"] is True
        assert body["default_llm"] == {"provider": "gpt"}
        assert body["api"]["http"]["running"] is True
        assert body["api"]["mysql"]["running"] is False


class TestPutConfig:
    def test_put_merges_and_overwrites(self, client, monkeypatch):
        config_data = {
            "auth": {
                "http_auth_enabled": True,
                "username": "admin",
                "password": "secret",
            },
        }
        config_mock = mock_config(monkeypatch, config_data)

        payload = {
            "default_llm": {"provider": "gpt-4-turbo"},
            "auth": {"http_auth_enabled": False},
        }

        response = client.put("/api/config/", json=payload)

        assert response.status_code == HTTPStatus.OK
        assert config_mock.update.call_args_list == [
            call({"default_llm": {"provider": "gpt-4-turbo"}}, overwrite=True),
            call({"auth": {"http_auth_enabled": False}}),
            call(payload),
        ]

    def test_put_unknown_top_level_key(self, client, monkeypatch):
        mock_config(monkeypatch, {"auth": {"http_auth_enabled": True}})

        response = client.put("/api/config/", json={"unknown_field": "x"})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "Unknown argumens" in response.get_json()["detail"]

    def test_put_unknown_auth_key(self, client, monkeypatch):
        config_data = {
            "auth": {
                "http_auth_enabled": True,
                "username": "user",
                "password": "pass",
            },
        }
        mock_config(monkeypatch, config_data)

        response = client.put("/api/config/", json={"auth": {"invalid": True}})

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "Unknown argumens" in response.get_json()["detail"]

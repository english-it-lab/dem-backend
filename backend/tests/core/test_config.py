from app.core.config import Settings


def test_cors_origins_list_splits_and_strips():
    settings = Settings(cors_origins="http://a.test, http://b.test,,http://c.test ")

    assert settings.cors_origins_list == ["http://a.test", "http://b.test", "http://c.test"]


def test_cors_origins_default_covers_vite_and_nginx():
    settings = Settings(cors_origins="http://localhost:5173,http://localhost:8080")

    assert settings.cors_origins_list == ["http://localhost:5173", "http://localhost:8080"]

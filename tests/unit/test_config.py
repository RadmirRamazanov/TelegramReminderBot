import logging

import pytest
from pydantic import ValidationError

from bot.config import Settings


class TestSettingsValidation:
    def test_корректный_уровень_логирования_info(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        assert Settings().log_level == "INFO"

    def test_уровень_логирования_в_нижнем_регистре(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("LOG_LEVEL", "debug")
        assert Settings().log_level == "DEBUG"

    def test_неверный_уровень_логирования(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("LOG_LEVEL", "VERBOSE")
        with pytest.raises(ValidationError):
            Settings()

    def test_корректный_интервал_планировщика(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("SCHEDULER_INTERVAL", "30")
        assert Settings().scheduler_interval == 30

    def test_нулевой_интервал_планировщика(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("SCHEDULER_INTERVAL", "0")
        with pytest.raises(ValidationError):
            Settings()

    def test_отрицательный_интервал_планировщика(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("SCHEDULER_INTERVAL", "-10")
        with pytest.raises(ValidationError):
            Settings()


class TestSettingsProperties:
    def test_log_level_int_info(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        assert Settings().log_level_int == logging.INFO

    def test_log_level_int_debug(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        assert Settings().log_level_int == logging.DEBUG

    def test_log_level_int_warning(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        assert Settings().log_level_int == logging.WARNING

    def test_значения_по_умолчанию(self, monkeypatch):
        monkeypatch.setenv("BOT_TOKEN", "1234567890:test_token_example")
        settings = Settings()
        assert settings.timezone == "Europe/Moscow"
        assert settings.scheduler_interval == 60
        assert settings.log_level == "INFO"

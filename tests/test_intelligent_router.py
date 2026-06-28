"""Tests for aih.intelligent_router — routing stub and fallback logic."""

from __future__ import annotations

import unittest
from unittest import mock

from aih.intelligent_router import intelligent_route


class IntelligentRouteTests(unittest.TestCase):
    def test_stub_mode_uses_classify_mode(self) -> None:
        result = intelligent_route("fix the bug in the harness")
        self.assertEqual(result, "implementation")

    def test_debug_request(self) -> None:
        result = intelligent_route("debug docker compose login failure")
        self.assertEqual(result, "debug")

    def test_review_request(self) -> None:
        result = intelligent_route("review this PR for security issues")
        self.assertEqual(result, "review")

    def test_research_request(self) -> None:
        result = intelligent_route("research the latest OpenAI API docs")
        self.assertEqual(result, "research")

    def test_non_stub_model_falls_back(self) -> None:
        with mock.patch("aih.intelligent_router.load_config") as mock_cfg:
            mock_cfg.return_value = mock.MagicMock(router_model="gpt-4")
            with mock.patch.dict("os.environ", {"AIH_AGENT_API_KEY": ""}):
                result = intelligent_route("review this code")
                self.assertEqual(result, "implementation")

    def test_non_stub_model_uses_httpx(self) -> None:
        with mock.patch("aih.intelligent_router.load_config") as mock_cfg:
            mock_cfg.return_value = mock.MagicMock(router_model="gpt-4")
            with mock.patch.dict("os.environ", {"AIH_AGENT_API_KEY": "test_key"}):
                mock_client_instance = mock.MagicMock()
                mock_response = mock.MagicMock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": '{"mode": "debug", "confidence": 0.99}'}}]
                }
                mock_client_instance.post.return_value = mock_response
                
                # Mock httpx.Client context manager
                mock_client_class = mock.MagicMock()
                mock_client_class.return_value.__enter__.return_value = mock_client_instance
                
                with mock.patch("httpx.Client", mock_client_class):
                    result = intelligent_route("debug this issue")
                    self.assertEqual(result, "debug")

    def test_httpx_rate_limit_retry_fallback(self) -> None:
        with mock.patch("aih.intelligent_router.load_config") as mock_cfg:
            mock_cfg.return_value = mock.MagicMock(router_model="gpt-4")
            with mock.patch.dict("os.environ", {"AIH_AGENT_API_KEY": "test_key"}):
                mock_client_instance = mock.MagicMock()
                
                import httpx
                mock_err = httpx.HTTPStatusError("429 Too Many Requests", request=mock.MagicMock(), response=mock.MagicMock())
                mock_err.response.status_code = 429
                
                mock_client_instance.post.side_effect = mock_err
                mock_client_class = mock.MagicMock()
                mock_client_class.return_value.__enter__.return_value = mock_client_instance
                
                with mock.patch("httpx.Client", mock_client_class), mock.patch("time.sleep"):
                    result = intelligent_route("review this code")
                    # Should fallback after retries
                    self.assertEqual(result, "implementation")


if __name__ == "__main__":
    unittest.main()

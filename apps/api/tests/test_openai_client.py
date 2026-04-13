from app.services.openai_client import OpenAIClientService


def test_openai_client_stub_mode_returns_stubbed_payload():
    client = OpenAIClientService(
        api_key="your-openai-api-key",
        base_url="https://api.openai.com/v1",
        model="gpt-4.1-mini",
    )

    payload = client.create_response("hello")

    assert payload["id"].startswith("resp_")
    assert payload["conversation_id"].startswith("conv_")
    assert payload["tool_calls"] == []
    assert "local-stub" in payload["output_text"]

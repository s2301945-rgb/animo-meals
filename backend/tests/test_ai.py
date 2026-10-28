import json

import httpx
from pydantic import SecretStr
import pytest

from app.ai import AIError, extract_preferences
from app.config import Settings
from app.ai_smoke_test import validate_key_input

VALID = {'budget_php': 100.0, 'preferred_food': 'chicken', 'include_drink': True,
         'avoid_spicy': True, 'prefer_same_stall': True, 'exclusions': ['pork']}


def config():
    return Settings(_env_file=None, groq_api_key=SecretStr('fake-test-key'))


def response_for(content, finish='stop'):
    return {'choices': [{'finish_reason': finish, 'message': {'content': content}}]}


def test_extracts_validated_data_and_sends_strict_schema():
    def handle(request):
        assert str(request.url) == 'https://api.groq.com/openai/v1/chat/completions'
        assert request.headers['Authorization'] == 'Bearer fake-test-key'
        assert 'fake-test-key' not in str(request.url)
        payload = json.loads(request.content)
        schema = payload['response_format']['json_schema']
        assert schema['strict'] is True
        assert schema['schema']['additionalProperties'] is False
        assert set(schema['schema']['required']) == set(VALID)
        return httpx.Response(200, json=response_for(json.dumps(VALID)))
    result = extract_preferences('100 pesos, chicken, drink, no spicy food or pork.',
                                 config(), httpx.MockTransport(handle))
    assert result.budget_php == 100
    assert result.exclusions == ['pork']


@pytest.mark.parametrize('status,code', [(401, 'authentication'), (403, 'permission'),
                                      (429, 'rate_limit'), (500, 'provider'), (400, 'provider')])
def test_provider_failures_do_not_leak_response_or_credentials(status, code):
    transport = httpx.MockTransport(lambda _: httpx.Response(status, text='private-provider-content'))
    with pytest.raises(AIError) as failure:
        extract_preferences('100 pesos', config(), transport)
    assert failure.value.code == code
    assert 'private-provider-content' not in str(failure.value)
    assert 'fake-test-key' not in str(failure.value)


def test_timeout_is_safe():
    def handle(request):
        raise httpx.ReadTimeout('private transport details', request=request)
    with pytest.raises(AIError, match='timed out'):
        extract_preferences('100 pesos', config(), httpx.MockTransport(handle))


@pytest.mark.parametrize('content', [
    'not json', '{}', '[]',
    json.dumps({**VALID, 'budget_php': -1}),
    json.dumps({**VALID, 'budget_php': 100.001}),
    json.dumps({**VALID, 'budget_php': '100'}),
    json.dumps({**VALID, 'invented_price': 50}),
])
def test_invalid_output_rejected(content):
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=response_for(content)))
    with pytest.raises(AIError) as failure:
        extract_preferences('100 pesos', config(), transport)
    assert failure.value.code == 'invalid_output'


def test_incomplete_response_rejected():
    transport = httpx.MockTransport(lambda _: httpx.Response(
        200, json=response_for(json.dumps(VALID), finish='length')))
    with pytest.raises(AIError):
        extract_preferences('100 pesos', config(), transport)


def test_missing_preferences_remain_unknown():
    data = {field: None for field in VALID}
    data['exclusions'] = []
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=response_for(json.dumps(data))))
    result = extract_preferences('Find lunch.', config(), transport)
    assert result.budget_php is None
    assert result.include_drink is None


@pytest.mark.parametrize('request_text', ['', '   ', 'a' * 2001])
def test_invalid_input_does_not_contact_provider(request_text):
    with pytest.raises(AIError) as failure:
        extract_preferences(request_text, config())
    assert failure.value.code == 'invalid_input'


def test_no_key_does_not_contact_provider():
    with pytest.raises(AIError) as failure:
        extract_preferences('100 pesos', Settings(_env_file=None, groq_api_key=SecretStr('')))
    assert failure.value.code == 'not_configured'


@pytest.mark.parametrize('key_text', [
    'a-database-password', 'gsk_...masked', 'Groq API key: gsk_' + 'A' * 40,
    '"gsk_' + 'A' * 40 + '"', 'gsk_short',
])
def test_key_entry_rejects_labels_passwords_and_masked_values(key_text):
    with pytest.raises(AIError) as failure:
        validate_key_input(key_text)
    assert failure.value.code == 'key_format'
    assert key_text not in str(failure.value)


def test_complete_key_format_can_proceed_to_provider_validation():
    validate_key_input('gsk_' + 'A' * 40)

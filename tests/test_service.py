from kqm.service import fetch_snapshot, parse_weight_overrides


def test_fetch_snapshot_mock_returns_reconciled_agents():
    snapshot = fetch_snapshot(mock=True)
    names = {a.agent_name for a in snapshot.agents}
    assert names == {"Gekko", "Fade"}


def test_fetch_snapshot_mock_balance_from_fixture_wallet():
    snapshot = fetch_snapshot(mock=True)
    assert snapshot.balance == 4700


def test_fetch_snapshot_mock_marks_version_and_shard():
    snapshot = fetch_snapshot(mock=True)
    assert snapshot.client_version == "mock"
    assert snapshot.shard == "na"


def test_fetch_snapshot_mock_exposes_static_agent_data():
    snapshot = fetch_snapshot(mock=True)
    gekko_uuid = next(a.agent_uuid for a in snapshot.agents if a.agent_name == "Gekko")
    assert snapshot.agents_static[gekko_uuid]["displayName"] == "Gekko"


def test_fetch_snapshot_mock_has_fetched_at_timestamp():
    snapshot = fetch_snapshot(mock=True)
    assert snapshot.fetched_at  # non-empty ISO timestamp string


def test_parse_weight_overrides_applies_valid_pairs():
    weights = parse_weight_overrides(["buddy=10", "spray=0"], {"buddy": 5, "spray": 1, "skin": 3})
    assert weights == {"buddy": 10.0, "spray": 0.0, "skin": 3}


def test_parse_weight_overrides_ignores_malformed_entries():
    weights = parse_weight_overrides(["not-a-pair", "buddy=nan-ish"], {"buddy": 5})
    assert weights == {"buddy": 5}

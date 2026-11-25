"""Compatibility checks without an API account or network access."""

import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aiohttp import ClientError
from homeassistant.const import CONF_API_KEY

from custom_components.ukho_tides.config_flow import ConfigFlow, OptionsFlowHandler
from custom_components.ukho_tides.const import CONF_STATIONS
from custom_components.ukho_tides.sensor import UkhoTidesSensor


def prediction(hours, event_type="HighWater", height=4.2):
    return {
        "tidal_event_datetime": datetime.now(timezone.utc) + timedelta(hours=hours),
        "tidal_event": SimpleNamespace(event_type=event_type, height=height),
    }


def sensor(data):
    return UkhoTidesSensor(
        SimpleNamespace(data=data, station={"station_id": "0060"}, last_update_success=True),
        "COWES",
    )


def test_preserves_station_identity_and_prediction_contract():
    events = [prediction(2), prediction(8, "LowWater", 0.9)]
    entity = sensor(events)
    assert entity.unique_id == "0060"
    assert entity.name == "COWES Tide"
    assert entity.state == "Rising"
    assert entity.available
    attrs = entity.extra_state_attributes
    assert attrs["predictions"] == [
        [event["tidal_event_datetime"].strftime("%Y-%m-%d %H:%M:%S"), event["tidal_event"].height]
        for event in events
    ]
    assert attrs["next_high_tide_height"] == "4.2m"
    assert attrs["next_low_tide_height"] == "0.9m"


def test_empty_or_expired_predictions_are_unavailable():
    for data in (None, [], [prediction(-1)]):
        entity = sensor(data)
        assert not entity.available
        assert entity.state is None
        assert entity.icon is None
        assert "next_high_tide_at" not in entity.extra_state_attributes


def test_shorter_response_drops_old_extrema():
    entity = sensor([prediction(2), prediction(8, "LowWater")])
    assert "next_low_tide_at" in entity.extra_state_attributes
    entity.coordinator.data = [prediction(3)]
    assert "next_low_tide_at" not in entity.extra_state_attributes


def test_countdown_does_not_wrap_at_24_hours():
    entity = sensor([prediction(30)])
    assert entity.extra_state_attributes["next_high_tide_in"].startswith("29h ")


def test_coordinator_failure_is_unavailable():
    entity = sensor([prediction(2)])
    entity.coordinator.last_update_success = False
    assert not entity.available


def test_options_flow_uses_managed_config_entry_and_isolates_edits():
    entry = SimpleNamespace(
        entry_id="test-entry", data={CONF_API_KEY: "not-a-real-key", CONF_STATIONS: [
            {"station_id": "0060", "station_name": "Original"}
        ]}, options={CONF_STATIONS: [{"station_id": "0060", "station_name": "COWES"}]},
    )
    original = deepcopy(entry.options)
    flow = ConfigFlow.async_get_options_flow(entry)
    assert isinstance(flow, OptionsFlowHandler)
    flow.handler = entry.entry_id
    flow.hass = SimpleNamespace(config_entries=SimpleNamespace(async_get_known_entry=lambda _: entry))
    client = SimpleNamespace(async_get_stations=AsyncMock(return_value=[SimpleNamespace(id="0060", name="Cowes")]))
    with (
        patch("custom_components.ukho_tides.config_flow.async_get_clientsession", return_value=None),
        patch("custom_components.ukho_tides.config_flow.UkhoTides", return_value=client),
        patch("custom_components.ukho_tides.config_flow.er.async_get", return_value=object()),
        patch("custom_components.ukho_tides.config_flow.er.async_entries_for_config_entry", return_value=[]),
    ):
        result = asyncio.run(flow.async_step_init())
    assert result["type"] == "form"
    assert flow.data[CONF_STATIONS][0]["station_name"] == "COWES"
    flow.data[CONF_STATIONS][0]["station_name"] = "Changed"
    assert entry.options == original


def test_options_flow_api_failure_still_returns_form():
    entry = SimpleNamespace(
        entry_id="test-entry", options={},
        data={CONF_API_KEY: "not-a-real-key", CONF_STATIONS: [{"station_id": "0060"}]},
    )
    flow = OptionsFlowHandler()
    flow.handler = entry.entry_id
    flow.hass = SimpleNamespace(config_entries=SimpleNamespace(async_get_known_entry=lambda _: entry))
    client = SimpleNamespace(async_get_stations=AsyncMock(side_effect=ClientError("offline")))
    with (
        patch("custom_components.ukho_tides.config_flow.async_get_clientsession", return_value=None),
        patch("custom_components.ukho_tides.config_flow.UkhoTides", return_value=client),
    ):
        result = asyncio.run(flow.async_step_init())
    assert result["type"] == "form"
    assert result["errors"]["base"] == "cannot_connect"

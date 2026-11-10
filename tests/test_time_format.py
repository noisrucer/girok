from girok.commands.task.utils import decode_time_format


def test_valid_times() -> None:
    assert decode_time_format("00:00") == (True, "00:00:00")
    assert decode_time_format("09:30") == (True, "09:30:00")
    assert decode_time_format("23:59") == (True, "23:59:00")


def test_invalid_times_rejected() -> None:
    invalid = ("1299", "19:99", "9:00", "24:00", "12ab", "", "23:59:59", "2:30")
    for bad in invalid:
        valid, _ = decode_time_format(bad)
        assert not valid, bad


import pytest

import services.waitlist_service as waitlist


# ---------- Scheduling policy ----------

def test_change_policy_accepts_fcfs():
    assert waitlist.change_policy("FCFS") is True
    assert waitlist.get_policy() == "FCFS"


def test_change_policy_accepts_priority():
    assert waitlist.change_policy("PRIORITY") is True
    assert waitlist.get_policy() == "PRIORITY"


def test_change_policy_rejects_invalid_policy():
    original = waitlist.get_policy()

    assert waitlist.change_policy("INVALID") is False
    assert waitlist.get_policy() == original


# ---------- Priority and aging ----------

def test_score_increases_with_waiting_time():
    row = {
        "priority": 1,
        "waited": waitlist.AGING_SECONDS * 2
    }

    assert waitlist.score(row) == pytest.approx(3.0)


def test_priority_scheduling_prefers_higher_score():
    waitlist.change_policy("PRIORITY")

    urgent = {
        "priority": 3,
        "waited": 0,
        "request_time": 2,
        "waitlist_id": 2
    }

    general = {
        "priority": 1,
        "waited": 0,
        "request_time": 1,
        "waitlist_id": 1
    }

    assert waitlist.rank_key(urgent) < waitlist.rank_key(general)


def test_fcfs_prefers_earlier_request():
    waitlist.change_policy("FCFS")

    earlier = {
        "priority": 1,
        "waited": 0,
        "request_time": 10,
        "waitlist_id": 2
    }

    later = {
        "priority": 3,
        "waited": 0,
        "request_time": 20,
        "waitlist_id": 1
    }

    assert waitlist.rank_key(earlier) < waitlist.rank_key(later)


def test_fcfs_breaks_ties_by_waitlist_id():
    waitlist.change_policy("FCFS")

    first = {
        "priority": 1,
        "waited": 0,
        "request_time": 10,
        "waitlist_id": 1
    }

    second = {
        "priority": 1,
        "waited": 0,
        "request_time": 10,
        "waitlist_id": 2
    }

    assert waitlist.rank_key(first) < waitlist.rank_key(second)


# ---------- Queue positions ----------

def test_queue_positions_are_calculated_per_slot(monkeypatch):
    queues = {
        101: [
            {"waitlist_id": 5},
            {"waitlist_id": 8},
        ],
        202: [
            {"waitlist_id": 12},
        ],
    }

    monkeypatch.setattr(
        waitlist,
        "ranked_queues",
        lambda *args, **kwargs: queues
    )

    positions = waitlist.queue_positions()

    assert positions == {
        5: 1,
        8: 2,
        12: 1,
    }


# ---------- Ranked queues ----------

def test_ranked_queues_groups_requests_by_slot(monkeypatch):
    rows = [
        {
            "slot_id": 101,
            "waitlist_id": 2,
            "priority": 1,
            "waited": 0,
            "request_time": 20,
        },
        {
            "slot_id": 101,
            "waitlist_id": 1,
            "priority": 3,
            "waited": 0,
            "request_time": 10,
        },
        {
            "slot_id": 202,
            "waitlist_id": 3,
            "priority": 2,
            "waited": 0,
            "request_time": 15,
        },
    ]

    monkeypatch.setattr(
        waitlist,
        "query_all",
        lambda *args, **kwargs: [dict(row) for row in rows]
    )

    waitlist.change_policy("PRIORITY")
    queues = waitlist.ranked_queues()

    assert set(queues.keys()) == {101, 202}
    assert [r["waitlist_id"] for r in queues[101]] == [1, 2]
    assert [r["waitlist_id"] for r in queues[202]] == [3]

    assert all("score" in row for queue in queues.values() for row in queue)


# Restore the default policy after tests.
@pytest.fixture(autouse=True)
def restore_policy():
    original = waitlist.get_policy()
    yield
    waitlist.change_policy(original)

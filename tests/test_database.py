import database


def test_add_and_list_victim():
    database.add_victim("instagram", "user@test.com", "pass123", "1.2.3.4")
    rows = database.get_all_victims()
    assert any(r[2] == "user@test.com" and r[3] == "pass123" for r in rows)


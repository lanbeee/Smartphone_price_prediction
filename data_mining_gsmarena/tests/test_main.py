from pyquery import PyQuery

from main import load_processed_phone_links, store_phone_names, get_next_page, get_list_of_phones_in_the_given_page, \
    populate_phone_detail, get_all_phone_details
from tests.test_constants import list_of_phones, phone_details, one_more_phone_details, list_of_phones_with_next_page


def test_load_phone_names_returns_saved_phone_names():
    expected = ['a.php', 'b.php']
    actual = load_processed_phone_links("data/load_test.txt")
    assert actual == expected


def test_store_phone_names_get_saved():
    store_phone_names(["c.php", "d.php"], "data/store_test.txt")


def test_get_next_page_returns_next_page_link():
    content = "<html><body><a class='pages-next' href='next-page' "\
              "title='Next page'></a></body></html>"

    expected = "http://www.gsmarena.com/next-page"
    actual = get_next_page(PyQuery(content))
    assert actual == expected


def test_get_next_page_returns_none_when_its_last_page():
    content = "<html><body><a class='pages-next' href='#1' " \
              "title='Next page'></a></body></html>"

    actual = get_next_page(PyQuery(content))
    assert actual is None


def test_get_each_phone_in_the_given_page():
    expected = ["a.php", "b.php"]
    actual = get_list_of_phones_in_the_given_page(PyQuery(list_of_phones))
    assert actual == expected


def test_get_phone_details_returns_expected_data(requests_mock):
    expected = {"key": "value", "name": "Mobile Name"}
    actual = populate_phone_detail(PyQuery(phone_details))
    assert actual == expected


def test_get_all_phone_details_returns_expected_data(requests_mock):
    requests_mock.get("http://given-page", text=list_of_phones)
    requests_mock.get("https://www.gsmarena.com/a.php", text=phone_details)
    requests_mock.get("https://www.gsmarena.com/b.php", text=one_more_phone_details)

    expected_phones = [{"key": "value", "name": "Mobile Name"}]
    expected_processed_phone_links = ["a.php"]

    actual_processed_phone_links, actual_phones = get_all_phone_details(["b.php"], "http://given-page", 0)
    assert actual_phones == expected_phones
    assert actual_processed_phone_links == expected_processed_phone_links


def test_get_all_phone_details_for_next_pages(requests_mock):
    requests_mock.get("http://given-page", text=list_of_phones_with_next_page)
    requests_mock.get("http://www.gsmarena.com/next-page.php", text=list_of_phones)
    requests_mock.get("https://www.gsmarena.com/a.php", text=phone_details)
    requests_mock.get("https://www.gsmarena.com/b.php", text=one_more_phone_details)

    expected_phones = [{"key": "value", "name": "Mobile Name"}]
    expected_processed_phone_links = ["a.php"]

    actual_processed_phone_links, actual_phones = get_all_phone_details(["b.php"], "http://given-page", 0)
    assert actual_phones == expected_phones
    assert actual_processed_phone_links == expected_processed_phone_links


def test_get_all_phone_details_for_next_pages_with_page_no(requests_mock):
    requests_mock.get("http://given-page", text=list_of_phones_with_next_page)

    expected = []

    actual_processed_phone_links, actual_phones = get_all_phone_details(["b.php"], "http://given-page", 0, 1)
    assert len(actual_processed_phone_links) == 0
    assert actual_phones == expected

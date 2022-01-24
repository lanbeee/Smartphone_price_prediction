import pandas as pd
import time
import requests
from pyquery import PyQuery
from pathlib import Path


def get_file_name(file_path):
    count = len(list(Path(file_path).glob('*.csv')))
    return count + 1


def process_request(link):
    response = requests.get(link)
    if response.status_code != 200:
        print(f"Request failed with {response.status_code} with reason {response.text}")
        raise Exception()
    return response.text


def load_processed_phone_links(file_name):
    phones_list = []
    with open(file_name, "r") as phone_file:
        for phone in phone_file:
            phones_list.append(phone.strip())

    return phones_list


def store_phone_names(processed_phone_links, file_name):
    with open(file_name, "a") as phone_file:
        for phone in processed_phone_links:
            phone_file.write(phone + "\n")


def get_next_page(page_details):
    next_page_link = page_details.find("a[title='Next page']").attr("href")
    next_page = f"http://www.gsmarena.com/{next_page_link}"
    return None if next_page_link == "#1" or next_page_link is None else next_page


def get_list_of_phones_in_the_given_page(root):
    phones_list = []
    phones = root("#review-body").find("ul").find("li")

    for phone in phones.items():
        phones_list.append(phone.find("a").attr("href"))

    return phones_list


def populate_phone_detail(phone_details):
    phones_data = {}

    phone_name = phone_details.find(".specs-phone-name-title").text()
    specs = phone_details.find("#specs-list")
    feature_categories = specs.find("table")

    for feature_category in feature_categories.items():
        features = feature_category.find("tr")
        for feature in features.items():
            feature_name = feature.find("td").eq(0).find("a").text()
            feature_value = feature.find("td").eq(1).text()
            phones_data[feature_name] = feature_value

    phones_data["name"] = phone_name
    return phones_data


def get_all_phone_details(existing_phones, link, time_to_wait, page_no=None):
    phone_list = []
    processed_phones = []
    current_page = 1

    try:
        while link is not None:
            if page_no is not None and current_page > page_no:
                break

            phones_response = process_request(link)
            root = PyQuery(phones_response)
            phone_links = get_list_of_phones_in_the_given_page(root)

            for phone_link in phone_links:
                if phone_link in existing_phones:
                    continue

                time.sleep(time_to_wait)
                details = process_request("https://www.gsmarena.com/" + phone_link)
                phone_details = PyQuery(details)
                phone_detail = populate_phone_detail(phone_details)
                phone_list.append(phone_detail)
                processed_phones.append(phone_link)

            current_page = current_page + 1
            link = get_next_page(root)
    except Exception as e:
        print(e)

    return processed_phones, phone_list


def create_data_frame_from_dict(phone_details):
    cols = set()
    for phone_detail in phone_details:
        for key in phone_detail.keys():
            cols.add(key)

    data = []

    for phone_detail in phone_details:
        data_row = []
        for column in cols:
            if column in phone_detail:
                data_row.append(phone_detail[column])
            else:
                data_row.append("")

        data.append(data_row)

    return pd.DataFrame(data=data, columns=cols)


def create_combined_csv():
    import pandas as pd
    filenames = [f"src/data/{i}.csv" for i in range(1, 8)]
    combined = pd.concat([pd.read_csv(file) for file in filenames])
    combined.to_csv("combined.csv")


if __name__ == '__main__':
    processed_phones = load_processed_phone_links("src/data/phones.txt")
    current_processed_phones, phone_data = get_all_phone_details(processed_phones,
                                                                 "https://www.gsmarena.com/samsung-phones-9.php",
                                                                 120)
    store_phone_names(current_processed_phones, "src/data/phones.txt")
    phones_data_frame = create_data_frame_from_dict(phone_data)
    phones_data_frame.to_csv(f"src/data/{get_file_name('src/data/')}.csv")

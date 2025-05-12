import time

from database.agent import Agent, EnumDatabaseNames, EnumCollectionNames
from scrap.facebook import EnumStatus
import requests
import re

class DataTreatment:
    @staticmethod
    def extract_formated_address(unformatted_address: str) -> dict:
        params = {
            'q': unformatted_address,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1
        }

        headers = {
            'User-Agent': 'MeuApp/1.0 (meuemail@example.com)'
        }

        response = requests.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
        data = response.json()

        if not data:
            return {'city': None, 'state': None, 'country': None, 'postcode': None}

        addr = data[0].get('address', {})

        city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality')

        return {
            'city': city,
            'state': addr.get('state'),
            'country': addr.get('country'),
            'postcode': addr.get('postcode')
        }

    @staticmethod
    def extract_item_prices(all_items: list[dict]) -> list[dict]:
        formatted_items = []

        def extract_price_parts(raw_price: str):
            # Match common currency formats
            parts = re.split(r'R\$|U\$|US\$|\s+', raw_price)
            # Remove empty parts and strip whitespace
            parts = [p.strip() for p in parts if p.strip()]
            return parts

        for item in all_items:
            raw_price = item['price']
            prices = extract_price_parts(raw_price)
            if len(prices) == 2:
                item['price'] = prices[0]
                item['old_price'] = prices[1]
            elif(len(prices) == 1):
                item['price'] = prices[0]

            formatted_items.append(item)

        return formatted_items

    @staticmethod
    def extract_item_address(all_items: list[dict]) -> list[dict]:
        items_with_formatted_addresses = []
        
        for item in all_items:
            formatted_address = DataTreatment.extract_formated_address(item['location'])
            if formatted_address.get('city'):
                item['city'] = formatted_address['city']
            if formatted_address.get('state'):
                item['state'] = formatted_address['state']
            if formatted_address.get('country'):
                item['country'] = formatted_address['country']
            if formatted_address.get('postcode'):
                item['postcode'] = formatted_address['postcode']
            items_with_formatted_addresses.append(item)

        return items_with_formatted_addresses

    @staticmethod
    def main():
        try:
            agent = Agent(EnumDatabaseNames.DIGITAL_MARKETPLACE.value)
            database = agent.database
            collection = database[EnumCollectionNames.FACEBOOK_MARKET_PLACE.value]
            all_items = collection.find({'status': EnumStatus.COMPLEMENT_INFORMATION.value})

            cleaned_price_items = DataTreatment.extract_item_prices(all_items)
            formatted_address_items = DataTreatment.extract_item_address(cleaned_price_items)

            for item in formatted_address_items:
                collection.update_one({'_id': item['_id']}, {'$set': {'status': EnumStatus.CLEAN_DATA.value}})

            database[EnumCollectionNames.FACEBOOK_CLEANED_DATA.value].insert_many(cleaned_price_items)
            return True ##Success
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    DataTreatment.main()


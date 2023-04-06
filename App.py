from typing import Optional, Dict, Tuple, Union
import os
import requests
import pytesseract

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from tabulate import tabulate
import json
import logging
from termcolor import colored

logging.basicConfig(filename='app.log', level=logging.DEBUG)

def fetch_items_data():
    """
    Fetches the mapping data for OSRS items from the OSRS Wiki API.

    Returns:
        dict: A dictionary of item data, including the item ID, name, buy limit, high alch value, and more.
    """
    api_url = 'https://prices.runescape.wiki/api/v1/osrs/mapping'
    try:
        response = requests.get(api_url)
        data = response.json()
        return data
    except (requests.exceptions.RequestException, KeyError, Exception) as e:
        print(f"Error: {e}")
        return None


# Set up API endpoint
headers = {'PriceCalc': 'Cheeto'}
api_url = 'https://prices.runescape.wiki/api/v1/osrs/latest'

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

style = Style.from_dict({
    'banner': 'green',
    'prompt': 'cyan',
    'input': 'yellow',
    'header': 'bold magenta',
    'profit': 'bold green',
    'loss': 'bold red',
    'gold': 'cyan',
})

BANNER = '''                                                                    
     _/_/_/  _/_/_/_/      _/_/_/_/_/                            _/                      
  _/        _/                _/      _/  _/_/    _/_/_/    _/_/_/    _/_/    _/  _/_/   
 _/  _/_/  _/_/_/            _/      _/_/      _/    _/  _/    _/  _/_/_/_/  _/_/        
_/    _/  _/                _/      _/        _/    _/  _/    _/  _/        _/           
 _/_/_/  _/_/_/_/          _/      _/          _/_/_/    _/_/_/    _/_/_/  _/            
'''
def get_item_prices(item_id: str) -> Tuple[Optional[int], Optional[str], Optional[int], Optional[str]]:
    """
    Returns the high and low prices and corresponding times for an item.
    If the item_id is not found in the API data, returns None for all values.
    """
    api_url = 'https://prices.runescape.wiki/api/v1/osrs/latest'
    try:
        response = requests.get(api_url, params={'id': item_id})
        data = response.json()
        if item_id in data:
            high_price = data[item_id]['high']
            high_time = data[item_id]['highTime']
            low_price = data[item_id]['low']
            low_time = data[item_id]['lowTime']
            return high_price, high_time, low_price, low_time
        else:
            return None, None, None, None
    except (requests.exceptions.RequestException, KeyError, Exception) as e:
        logging.error(f"Error getting item prices: {e}")
        return None, None, None, None

def get_sell_price_api(items_dict):
    """
    Fetches the latest sell prices for all items in the given dictionary of items.
    Returns a dictionary mapping item names to sell prices (both high and low).
    """
    api_url = 'https://prices.runescape.wiki/api/v1/osrs/latest'
    sell_prices = {}
    item_ids = [str(info['id']) for info in items_dict.values()]
    try:
        response = requests.get(api_url, params={'ids': ','.join(item_ids)}, headers=headers)
        data = response.json()
        for item_name, item_info in items_dict.items():
            if not isinstance(item_info, dict):
                raise TypeError('Item info is not a dictionary')
            item_id = item_info['id']
            if str(item_id) in data:
                item_data = data[str(item_id)]
                high_price = item_data['high']
                low_price = item_data['low']
                sell_prices[item_name] = {'high': high_price, 'low': low_price}
            else:
                sell_prices[item_name] = None
    except (requests.exceptions.RequestException, KeyError, TypeError) as e:
        print(f"Error: {e}")
        sell_prices = {item_name: None for item_name in items_dict.keys()}
    return sell_prices

def display_live_grid(total_profit: float, last_entered_gp: Union[int, str], recommendations: list) -> None:
    """
    Display the top 10 most profitable items to trade in a table format with their buy price, sell price, 
    maximum units, and profit per gp, and total profit made based on the input gp amount.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    headers = ['Item', 'Profit/GP', 'Sell Price', 'Buy Price', 'Max Units']
    data = []
    for recommendation in recommendations:
        item_name, profit_per_gp, sell_price, buy_price, max_units = recommendation
        if profit_per_gp > 0:
            color = 'green'
        else:
            color = 'red'
        data.append((item_name, colored(f"{profit_per_gp:.2f}", color), sell_price, buy_price, max_units))
    print_formatted_text(tabulate(data, headers=headers, tablefmt='grid'))

    last_entered_gp_str = format(last_entered_gp, ',') if isinstance(last_entered_gp, (int, float)) else last_entered_gp
    print(colored(f"\nProfit/loss total: {total_profit:.2f} | Your gold: {last_entered_gp_str}\n", 'cyan'))

def calculate_profit(total_gp, item_name, high_price, low_price, items_dict, max_units=1):
    """
    Calculates the profit per gp for a given item based on the total gp the user has and the item's price information.

    Args:
        total_gp (float): The total amount of gold the user has.
        item_name (str): The name of the item for which the profit needs to be calculated.
        high_price (float): The high price of the item on the Grand Exchange.
        low_price (float): The low price of the item on the Grand Exchange.
        max_units (int): The maximum number of units of the item that can be bought.
        items_dict (dict): A dictionary containing the ID and buy price of each item.

    Returns:
        The profit per gp for the given item.
    """
    # Fetch the latest sell prices for all items from the API
    sell_prices = get_sell_price_api(items_dict)

    # Get the sell price for the item
    sell_price = sell_prices.get(item_name)
    if sell_price is None:
        return 0

    # Take 1% tax into account
    tax = min(int(sell_price * max_units * 0.01), 5000000)
    sell_price -= tax

    # Get the buy price and buy limit from the item's dictionary
    item_info = items_dict.get(item_name)
    if item_info is None:
        return 0
    buy_price = item_info["buy_price"]
    buy_limit = item_info.get("limit", float("inf"))

    max_units = min(max_units, buy_limit, int(total_gp / buy_price))

    profit = sell_price * max_units - buy_price * max_units

    if buy_price == 0:
        return 0
    profit_per_gp = profit / (buy_price * max_units)

    return profit_per_gp
def fetch_all_items():
    """
    Fetches information about all OSRS items using the Old School RuneScape API.

    Returns:
    List: A list of dictionaries, with each dictionary containing information about an OSRS item.
    """
    base_url = "https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/items.json"
    all_items = []
    for category in range(1, 38):
        for alpha in 'abcdefghijklmnopqrstuvwxyz':
            page = 1
            while True:
                url = f"{base_url}?category={category}&alpha={alpha}&page={page}"
                response = requests.get(url)
                if response.status_code != 200:
                    break
                data = response.json()
                items = data["items"]
                if not items:
                    break
                all_items.extend(items)
                page += 1
    return all_items

def get_recommendations(total_gp):
    """
    Calculates the top 10 most profitable trades that can be made with the given amount of gp.

    Args:
    total_gp (float): The total amount of gp that the user has.

    Returns:
    List: A list of tuples containing the top 10 recommendations. Each tuple contains the following items:
          (1) The name of the item
          (2) The profit per gp that can be made from trading the item
          (3) The current high price of the item on the Grand Exchange
          (4) The current low price of the item on the Grand Exchange
          (5) The maximum number of units of the item that can be bought with the user's gp
    """
    if total_gp is None:
        print("Invalid input. Please enter a valid gp amount. Use 'k' for thousand, 'm' for million, or 'b' for billion.")
        return []

    item_profits = []

    items_data = fetch_items_data()
    items_dict = {item_data['name']: {'id': item_data['id'], 'buy_price': item_data['high_alch']} for item_data in items_data.values()}

    for item_data in items_data.values():
        item_id = item_data['id']
        item_name = item_data['name']

        # Fetch the item information using the item ID
        high_price, high_time, low_price, low_time = get_item_prices(item_id)

        # Calculate the profit
        max_units = min(int(total_gp / low_price), item_data.get("buy_limit", float("inf")))
        profit_per_gp = calculate_profit(total_gp, item_name, high_price, low_price, items_dict, max_units)

        item_profits.append((item_name, profit_per_gp, high_price, low_price, max_units))

    # Sort the items by profit per gp in descending order
    sorted_item_profits = sorted(item_profits, key=lambda x: x[1], reverse=True)

    # Return the top recommendations
    return sorted_item_profits[:10]

def calculate_profit(total_gp, item_name, high_price, low_price, max_units=1, items_dict=None):
    """
    Calculate the profit per GP for buying and selling an item.

    Parameters:
    total_gp (float): The total amount of gold the user has to work with.
    item_name (str): The name of the item to calculate the profit for.
    high_price (float): The highest price the item has been sold for recently.
    low_price (float): The lowest price the item has been sold for recently.
    max_units (int): The maximum number of units of the item that can be bought.
    items_dict (dict): A dictionary containing the ID and buy price of each item.

    Returns:
    float: The profit per GP for buying and selling the item.
    """
    buy_limits = {}

    # Fetch the latest sell prices for all items from the API
    sell_prices = get_sell_price_api(items_dict)

    # Get the sell price for the item
    sell_price = sell_prices.get(item_name)
    if sell_price is None:
        return 0

    # Take 1% tax into account
    tax = min(int(sell_price * max_units * 0.01), 5000000)
    sell_price -= tax

    # Get the buy price from the item's dictionary
    item_info = items_dict.get(item_name)
    if item_info is None:
        return 0
    buy_price = item_info["buy_price"]

    max_units = min(max_units, items_dict[item_name].get("buy_limit", float("inf")), int(total_gp / buy_price))

    profit = sell_price * max_units - buy_price * max_units

    if buy_price == 0:
        return 0
    profit_per_gp = profit / (buy_price * max_units)

    return profit_per_gp

def parse_gold_input(gp_input: str) -> Optional[int]:
    """
    Parses a string containing a number with an optional 'k', 'm', or 'b' suffix representing
    thousands, millions, or billions, respectively.

    Args:
        gp_input (str): The input string to be parsed.

    Returns:
        int: The integer value of the input string, multiplied by the appropriate factor based on any suffix.
    """
    if not isinstance(gp_input, str):
        return None

    gp_input = gp_input.lower()

    if gp_input.endswith('k'):
        return int(float(gp_input[:-1]) * 1000)
    elif gp_input.endswith('m'):
        return int(float(gp_input[:-1]) * 1000000)
    elif gp_input.endswith('b'):
        return int(float(gp_input[:-1]) * 1000000000)
    else:
        try:
            return int(gp_input)
        except ValueError:
            return None

def main():
    """
    The main function for running the OSRS price calculator.

    Prompts the user to input how much GP they have, then fetches the top
    10 most profitable items they can buy and sell using that GP. Displays
    the results in a grid with relevant information for each item.
    """
    session = PromptSession(style=style)
    last_entered_gp = ''
    while True:
        try:
            gp_input = session.prompt('How much gp do you have? ')
            last_entered_gp = gp_input
            total_gp = parse_gold_input(gp_input)
            if total_gp is None:
                raise ValueError("Invalid input. Please enter a valid gp amount. Use 'k' for thousand, 'm' for million, or 'b' for billion.")
            recommendations = get_recommendations(total_gp)
            total_profit = sum([r[1] for r in recommendations])
            display_live_grid(total_profit, last_entered_gp, recommendations)
        except ValueError as e:
            logging.error(f"Error: {e}")
            print(f"{e}\nInvalid input. Please enter a valid gp amount. Use 'k' for thousand, 'm' for million, or 'b' for billion.")
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Error: {e}")
            print(f"Error: {e}")
            input("Press Enter to continue...")

if __name__ == '__main__':
    main()

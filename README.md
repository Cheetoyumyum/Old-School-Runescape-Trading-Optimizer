```
                                                                  
     _/_/_/  _/_/_/_/      _/_/_/_/_/                            _/                      
  _/        _/                _/      _/  _/_/    _/_/_/    _/_/_/    _/_/    _/  _/_/   
 _/  _/_/  _/_/_/            _/      _/_/      _/    _/  _/    _/  _/_/_/_/  _/_/        
_/    _/  _/                _/      _/        _/    _/  _/    _/  _/        _/           
 _/_/_/  _/_/_/_/          _/      _/          _/_/_/    _/_/_/    _/_/_/  _/            
```
=====================

This is a Python application that helps you find the most profitable items to trade in Old School RuneScape (OSRS). It uses data from the OSRS Wiki API to fetch the latest prices and limits for all OSRS items, and calculates the profit per gold piece (gp) that can be made from buying and selling each item. It then recommends the top 10 most profitable items based on your current amount of gp.

Requirements
------------
- Python 3.6 or higher
- requests
- pytesseract
- prompt_toolkit
- tabulate
- json
- logging
- termcolor

You can install these requirements by running `pip install -r requirements.txt` in your terminal.

Note that `pytesseract` requires Tesseract OCR to be installed on your system. You can download Tesseract OCR from [here](https://github.com/tesseract-ocr/tesseract) and install it according to your system requirements.

APIs
----
This application uses the following APIs:

- OSRS Wiki API - for fetching item information and limits
- OSRS Grand Exchange API - for fetching the latest prices for items

Usage
-----
To run the application, simply run `python App.py` in your terminal.

When prompted, enter the amount of gp you have. You can use 'k' for thousand, 'm' for million, or 'b' for billion. The application will then fetch the top 10 most profitable items you can buy and sell using that gp, and display the results in a grid format with relevant information for each item, including the profit per gp, sell price, buy price, and maximum units.

You can exit the application at any time by pressing `Ctrl-C`.

License
-------
This project is licensed under the MIT License - see the `LICENSE` file for details.

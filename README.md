# HouseHunt: Your personal immo helper

Helps in making your house hunt a little easier and organised. 
Currently works in Germany for its most popular immobilien website.

* Automatically crawl a given url from the most popular immobilien website in germany 
* extract meaningful information about the offer.
* Automatically store the data and the link of the offer to a google spreadsheet
* Run it by yourself or let it run as a cron and be the first to be informed of any new offers
* Get the competitive edge when it comes to getting the information about new offers.

__Let the script do its job of collecting and storing the data.
Your job is to filter the once which you like and make an appointment. 
Further releases could include functionality to directly apply for relevant offers__

### IMPORTANT
* The script is tied to the layout of the website (just like any other crawler out there)
So if the script starts to break, raise an github issue and I will try to fix it as soon as possible.
Even better, make a fix and create a pull request :)


## Special Libraries Required

* [gspread](https://github.com/burnash/gspread) 
* BeautifulSoup

## Setting up google spreadsheet

This project can automatically send the data to a google spreadsheet. 
Look at  [gspread](https://github.com/burnash/gspread) for setting up a google spreadsheet

## BASIC USAGE 

```
python house_hunt.py config.ini
```



## CONFIGURATION PARAMETERS

Take a look at config_sample.ini for example parameters

```REGIONS``` 

active: specify a comma separated list of areas that you want to run the script on. 
Each element in the csv must be its own section in the config file

```AUTH```

key_location: file location of the authentication key generated for accessing google sheet.
See [gspread](https://github.com/burnash/gspread) for setting up a google spreadsheet

google_sheet_id: Hash id of the google sheet to use. Of the form:
```https://docs.google.com/spreadsheets/d/<hash_id>
```

```area1```

This config section name should correspond to the one specified in the REGIONS.active

url: Do a manual search on the website. Fine-tune the filters about m2, price etc. Take a look at the result on the webiste.
 Copy the url for the search and paste it in this config file. This script will then use that url and parse all the results
 for you.

worksheet: The name of the sheet inside the google sheet specified in AUTH.google_sheet_id, 
            where you want to save the results of this search criteria  


### Feedback

Create an issue or drop me an email if you face issues using the script or need specific help.
If you have still not guessed which website it crawls, [Google](http://goo.gl/08xkmA) it :)

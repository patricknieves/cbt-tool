# Identification of Cross-Blockchain Transactions: A Feasibility Study


### Prerequisites


Install mysql
```
sudo apt-get install mysql-server
```
Install MySQLdb
```
sudo apt-get install python-pip python-dev libmysqlclient-dev
pip install mysqlclient
```


Install Tor
```
sudo apt install tor
```
Configure Tor file  under /etc/tor/torrc:
```
ControlPort 9051
CookieAuthentication 1
```
Restart Tor:
```
sudo service tor restart
```

Install needed libraries
```
pip install requests
pip install stem
pip install flask
pip install flask-restful

```


### Running Scraper

Run all processes 
```
python main/scraper/Scraper.py
```

Run processes separately
```
python main/scraper/Shapeshift.py
python main/scraper/Data_retriever.py
```

### Running Scraper

First adjust settings in main/Settings.py before running.

Then run the tool:
```
python main/Main.py
```
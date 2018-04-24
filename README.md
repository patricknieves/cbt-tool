# Identification of Cross-Blockchain Transactions: A Feasibility Study


### Prerequisites

If not already done, install Python 2.7

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


### Running the scraper

Run all processes 
```
python main/scraper/Scraper.py
```

Run processes separately
```
python main/scraper/Shapeshift.py
python main/scraper/Data_retriever.py
```

### Running the recognition algorithm

First adjust settings in main/Settings.py before running.

Then run the tool:
```
python main/Main.py
```

### Using Systemd:

All algorithms were started using Systemd

A service file for the scraper algorithm e.g. must look like this (assuming the project is in the folder home/cbt-tool/):

```
[Unit]
Description=Shapeshift Scraper
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python2.7 /home/cbt-tool/main/scraper/Scraper.py
Restart=always
User=patrick
WorkingDirectory=/home/cbt-tool/main/scraper
Environment="PYTHONPATH=/home/cbt-tool:/home/cbt-tool/main:/home/cbt-tool/main/scraper:/usr/lib/python2.7:/usr/lib/python2.7/plat-x86_64-linux-gnu:/usr/lib/python2.7/lib-tk:/usr/lib/python2.7/lib-old:/usr/lib/python2.7/lib-dynload:/home/patrick/.local/lib/python2.7/site-packages:/usr/local/lib/python2.7/dist-packages:/usr/lib/python2.7/dist-packages"


[Install]
WantedBy=multi-user.target
```

The service can then be started using following commands:
```
sudo systemctl daemon-reload
ssudo systemctl enable tool-rest.service
sudo systemctl start tool-rest.service
```
Check the status of the service:
```
sudo systemctl status tool-rest.service
```
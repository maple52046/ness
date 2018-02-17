# TWSE Stock Data Loader

This is a data loader which is used to download stock data from TWSE (Taiwan Stock Exchange Corporation).


## System Setup

### Install Ubuntu 16.04

This program is developed on an AWS Ubuntu instance. To setup this program quickly, it's recommended you to choose Ubuntu (16.04) as your operating system:

  - [Get Ubuntu](https://www.ubuntu.com/download) installar from Canonical Ltd.
  - Launch Ubuntu instance on [AWS](https://console.aws.amazon.com/ec2/).
  - Other...

### Install Python environments

This program is written with Python 3. To run this program, you need to:

```bash
sudo apt install python3 python3-lxml python3-pymysql python3-yaml python3-requests python3-sqlalchemy python3-influxdb
```

### Install MariaDB

This program use MariaDB to store static data like stock list.

Install MariaDB by reference the instructions of [official guide](https://downloads.mariadb.org/mariadb/repositories/#mirror=ossplanet&distro=Ubuntu&distro_release=xenial--ubuntu_xenial&version=10.2):

```bash
sudo apt install software-properties-common
sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8
echo 'deb [arch=amd64,i386,ppc64el] http://ftp.ubuntu-tw.org/mirror/mariadb/repo/10.2/ubuntu xenial main' | sudo tee /etc/apt/sources.list.d/mariadb.list
sudo apt update
sudo apt install mariadb-server
```

After MariaDB is installed on your system, you need to login to MariaDB with command `sudo mysql` , create a database and account from this program with the following commands:

```sql
> create database ness;
> grant all privileges on ness.* to 'ness'@'localhost';
```

Then, edit `config.ini` to configure database connection:

```ini
[mariadb]
connection = mysql://ness:ness@localhost/ness?charset=utf8
```

### Install InfluxDB

This program use InfluxDB to store dynamic data.

Install InfluxDB by reference the instructions of [official guide](https://portal.influxdata.com/downloads#influxdb):

```bash
wget https://dl.influxdata.com/influxdb/releases/influxdb_1.4.2_amd64.deb
sudo dpkg -i influxdb_1.4.2_amd64.deb
sudo systemctl start influxdb
```

Then, edit `config.ini` to configure database connection:

```ini
[influxdb]
host = localhost
port = 8086
user = root
password = root
database = ness
```

## Usage

### Import TW0050 concept stocks

Steps:

1. Download source html file from https://www.cnyes.com/twstock/Etfingredient/0050.htm
2. Run `tw0050.py` to extract and store the concepts of tw0050

```
python3 tw0050.py tw0050.html
```

### Get Stocks data

```
python3 fetcher.py
```

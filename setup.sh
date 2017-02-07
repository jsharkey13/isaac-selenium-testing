#!/usr/bin/env bash


# Add Google's public key to apt:
wget -q -O - "https://dl-ssl.google.com/linux/linux_signing_key.pub" | sudo apt-key add -
# And add Google to the apt sources list:
echo 'deb http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list

# Update apt-get:
sudo apt-get update

# We need to install pip, to make adding Python packages much simpler:
sudo apt-get -y install python-pip

# We need this for headless display emulation:
sudo apt-get -y install xvfb
# And this one to make it work seamlessly in Python:
sudo pip install pyvirtualdisplay

# Install the web browsers themselves:
sudo apt-get -y install google-chrome-stable
sudo apt-get -y install firefox

# Install Selenium for Python:
sudo pip install selenium

# Install Python Imaging Library:
sudo apt-get -y install python-imaging

# Firefox needs the GeckoDriver executable:
cd /tmp
wget "https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-linux64.tar.gz"
tar -xvzf geckodriver*
mv geckodriver /usr/local/bin
cd /usr/local/bin
sudo chmod +x geckodriver

# Chrome needs the ChromeDriver executable.
# Allow opening of zip files:
sudo apt-get -y install unzip
# Get and extract the ChromeDriver executable:
cd /tmp
wget "https://chromedriver.storage.googleapis.com/2.27/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin
cd /usr/local/bin
sudo chmod +x chromedriver
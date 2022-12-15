#!/bin/bash

echo "Installer LOCAL version of $(basename $(git rev-parse --show-toplevel)), branch $(git rev-parse --abbrev-ref HEAD
)"
echo '--> Check Python version...'
if [ "$(python3 -c 'import sys; print(sys.version_info.minor)')" -lt 6 ]
then
  echo 'Projects need python3 to be at least 3.6'
  exit 1
fi

# venv
echo '--> Creating virtual environment and installing dependencies...'
python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade pip wheel setuptools | grep -v 'already satisfied'
pip3 install --requirement requirements.txt | grep -v 'already satisfied'

pybabel compile -d app/translations


# Check .env
echo '--> Checking local .ENV file ...'
if [ ! -e .env ]; then
  echo "WARNING: Create an .env file with the following structure"
  cat <<EOF

SECRET_KEY=set-any-phrase-here-it-wll-be-used-as-your-secret
DATABASE_URL=mysql+pymysql://clcuser:test123@localhost/cl_concerts_db

EOF
    exit
fi

# Check DB connection
echo '--> Checking DB connection ...'
DBSTRING=$(cat .env | grep DATABASE_URL | sed 's/:\/\// /g;s/:/ /g;s/@/ /g;s/\// /g')
DBUSER=$(echo $DBSTRING | cut -d" " -f2)
DBPASS=$(echo $DBSTRING | cut -d" " -f3)
DBHOST=$(echo $DBSTRING | cut -d" " -f4)
DBTABLE=$(echo $DBSTRING | cut -d" " -f5)


# if ! $(echo 'SHOW TABLES;' | mysql -h $DBHOST -u ss$DBUSER -p$DBPASS $DBTABLE > /dev/null); then
if ! $(echo '' | mysql --silent --skip-column-names -e "SHOW TABLES" -h $DBHOST -u $DBUSER -p$DBPASS $DBTABLE > /dev/null); then
    echo; 
    echo "Check your mysql and create an empty DB if needed. Use as a template:"; 
    echo
    cat <<EOF
CREATE DATABASE cl_concerts_db;  
USE cl_concerts_db;  
CREATE USER 'clcuser'@'localhost' IDENTIFIED BY 'test123';  
GRANT ALL ON cl_concerts_db.* TO 'clcuser'@'localhost';  
FLUSH PRIVILEGES;  

EOF
    exit
fi

# Check conntens of DB

#DevNote: To remove all tables execute
#mysql $X --silent --skip-column-names -e "SHOW TABLES" cl_concerts_db | xargs -L1 -I% echo 'SET FOREIGN_KEY_CHECKS = 0; DROP TABLE `%`;' | mysql -v $X cl_concerts_db
echo '--> Checking DB contents ... '
if [[ 0 -eq $(echo 'SHOW TABLES;' | mysql -h $DBHOST -u $DBUSER -p$DBPASS $DBTABLE | wc -l) ]] ; then
    echo "... You have no tables, nothing indeed, poor guy. Try running:"
    echo "tools/01-download-db-from-prod.sh"
    exit
fi

# DB migration
# echo '--> Running local database migration...' 
# flask db upgrade

echo "--> Done, you have data in the DB also! Now, run:"
echo "source venv/bin/activate"
echo "FLASK_ENV=development flask run --port 5001"
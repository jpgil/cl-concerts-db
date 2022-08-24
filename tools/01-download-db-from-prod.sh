#!/bin/bash

NAME=$(basename $(git rev-parse --show-toplevel))
echo "Downloading production DB of $NAME"

cd "$(dirname "$0")"/../ || exit 1
mkdir -p backup

# This is hardcoded dude
SSHHOST=168.232.165.104
SSHUSER=clconcert2
# SSHUSER=root

echo '--> Check VENV...'
if [ ! -e venv ]; then
    echo "Execute tools/01-download-db-from-prod.sh first"
    exit
fi

echo '--> Check SSH keys...'
if ! ssh $SSHUSER@$SSHHOST -o PasswordAuthentication=no -p 22222 exit; then
    echo
    echo "Please send the contents of id_rsa.pub to admin of $NAME:"
    echo 
    cat ~/.ssh/id_rsa.pub 
    exit
fi


echo '--> Download last snapshot...'
LASTDB=$(ssh $SSHUSER@$SSHHOST -p 22222 "ls -tr1 --color=auto sql_backups| tail -n 1")
if ! rsync -a --progress -e 'ssh -p 22222' $SSHUSER@$SSHHOST:./sql_backups/$LASTDB backup; then
    echo "A problem has occurred... "
    exit
fi


echo '--> Clean local DB...'
DBSTRING=$(cat .env | grep DATABASE_URL | sed 's/:\/\// /g;s/:/ /g;s/@/ /g;s/\// /g')
DBUSER=$(echo $DBSTRING | cut -d" " -f2)
DBPASS=$(echo $DBSTRING | cut -d" " -f3)
DBHOST=$(echo $DBSTRING | cut -d" " -f4)
DBTABLE=$(echo $DBSTRING | cut -d" " -f5)
X="-h $DBHOST -u $DBUSER -p$DBPASS"

mysql $X --silent --skip-column-names -e "SHOW TABLES" $DBTABLE | xargs -L1 -I% echo 'SET FOREIGN_KEY_CHECKS = 0; DROP TABLE `%`;' | mysql $X $DBTABLE

echo '--> Repopulating local DB...'
bzcat backup/$LASTDB | mysql $X $DBTABLE


# DB migration
echo '--> Running local database migration...' 
source venv/bin/activate
flask db upgrade

echo "--> Done! Now, run:"
echo "source venv/bin/activate"
echo "FLASK_ENV=development flask run --port 5001"
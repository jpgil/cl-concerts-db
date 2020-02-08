# cl-concerts-db
Plataforma para almacenar y consultar una lista de conciertos de música docta en Chile

## Installation 
*Make sure your virtualenv is set for python3*

`git clone https://github.com/epikt/cl-concerts-db.git`  
`cd cl-concerts-db/`  
`virtualenv venv`  
`source venv/bin/activate`  
`pip install -r requirements.txt`  


There are 2 methods for installing the database:
- Preparing an empty DB ready to be filled with data: this method allows to use any sql database just changing the connection string, however is **not recommended** for testing since you'll have no data to play with
- Using a dump of the production database, my personal favourite, however, the dump has some ties to MySQL/MariaDb which could be cleaned, but it's just easier if you stick to MySQL/MariaDB as base DB. I'll explain both methods using MariaDB as base DB.


Install mariadb (mysql) and start the service
Enter to mysql (usually just typing mysql as root) and create the DB

`CREATE DATABASE cl_concerts_db;`  
`USE cl_concerts_db;`  
`CREATE USER 'clcuser'@'localhost' IDENTIFIED BY 'test123';`  
`GRANT ALL ON cl_concerts_db.* TO 'clcuser'@'localhost';`  
`FLUSH PRIVILEGES;`  

That would create an empty database called *cl_concerts_db* with a user called *clcuser* with password *test123*. You can change any of this names, but you should adapt the *DATABASE_URL* to match with them 

### Setting up the environment
There is some environmental variables which are needed to configure the application. This can be set as environmental variable or you can create a *.env* file under *cl-concertd-db/* with the entries that you need to set. The list of variables and their defaults and descriptions can be found in the *config.py file*, but the bare minimum you'll need to configure are:\
`~#cat .env `\
`SECRET_KEY=set-any-phrase-here-it-wll-be-used-as-your-secret`  \
`DATABASE_URL=mysql+pymysql://clcuser:test123@localhost/cl_concerts_db` \


### Installation with real data (recommended for testing)
For testing, it's better to have access to the real data. 
- First, from the dropbox with the backups get the uploaded files (you can download the complete 'uploads' directory as a zip and then uncompress it under cl-concerts-db directory.
- The, download from the backup dropbox the last *backup_clconcertsdb_<date>.sql.bz2* file. Uncompress it and from the shell run:
`mysql -u clcuser -p`  
`MariaDB [(none)]> use cl_concerts_db;`  
`MariaDB [cl_concerts_db]> source <path to the sql file>`  
`MariaDB [cl_concerts_db]> commit;`  
This should populate the DB. Now you're ready to start the app. Now go the cl-concerts-db directory, from there you can execute:
`flask shell`
for get into an interactive python session with all the imports and settings needed by flask. In the shell you can try running
`from app.models import Event
Event.query.all()`
for a quick test  or, instead of the shell run
`flask run`  
To start the service. The webpage dispayed on [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

### Installation (from scratch to start with an empty DB) 
From under *cl-concerts-db* run the command:
`flask db upgrade`  
This will create in the DB an structure with the empy table. Now, you'll have to manually add the required 3 profile + 1 admin user. Notice that you **cannot change the name of the profiles**
Entel to the flask shell:
`flask shell`  
and there run:
`from app.models import *`  
`db.session.add(Profile(name='Editor',description='Este perfil permite ver y editar entradas'))`                                                                                                   
`db.session.add(Profile(name='Administrador',description='Este perfil permite agregar/quitar usuarios, ver y editar entradas'))`                                                          
`db.session.add(Profile(name='Visita',description='Este perfil sólo permite ver entradas'))`  
This will create the basic profiles. Now we need a user which will be able to create new users with the proper profiles. Let's call it *admin*:
`u=User(first_name='admin',last_name='istrador',profile=Profile.query.filter_by(name='Administrador').first(),email='admin@server.com') `  
`u.set_password('test123') `  
`db.session.add(u)`  
`db.session.commit();`  

### Example of how to create a new Administrator user:
In `flask shell` run:
`from app.models import User,Profile  
newuser=User()  
newuser.first_name='MyName'  
newuser.last_name='MyLastName'  
newuser.email='myemail@email.com'  
newuser.profile=Profile.query.filter_by(name='Administrador').first()  
newuser.set_password('my password') 
db.session.commit()  `
A simple web app that is build using Scrapy and Flask to collect authors and their articles from famous new sites.

The scrapy library is used to build spiders that crawl news site and collect data and store them in MySQL database. The scrapy setup is stored in SiteSpiders folder and each spider has its own setup for example cnn_spider.py crawl the cnn website. MySQL database store the items in two tables authors and articles using scrapy item pipelines the database is populated. There is one-to-many relation between the authors.id and articles.author_id. 

Here is the schema for the tables:

![database_schema](https://github.com/UsmanCanCode/Journalist/assets/86849038/aef8497a-b617-4ee3-b71e-90e622a901fc)

Using flask, a simple web app was build stored in the flaskweb folder. The flaskweb has two routes \authors, which list all the authors from particular new site and \<id>\<author_name>, which list all the articles for particular author. The routes are build using flask blueprint model. The authors.py and articles.py has the setup for \authors and  \<id>\<author_name> views respectively. A base html template is used and store in templates folder. The data is retrieved from MySQL database and the logic is setup in db.py file. 

Here are the two routes:

![authors](https://github.com/UsmanCanCode/Journalist/assets/86849038/b1f35ab8-3784-4c44-b769-d0ac01927177)
![articles](https://github.com/UsmanCanCode/Journalist/assets/86849038/9a8dbb16-bb62-471b-8ed5-ce6043b86cd0)

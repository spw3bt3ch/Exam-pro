**Setup Project**

* Fork or clone project 
* `php artisan composer update`
* In the project root directory create another copy of .env.example and rename it to .env
* Generate application key `php artisan key:generate`
* In .env file, supply values to DB_DATABASE, DB_USERNAME, DB_PASSWORD
* `php artisan migrate`
* You can load some dummy data into database for testing `php artisan db:seed --class=LoadDummyQuestions`
* Load report question types `php artisan db:seed --class=ReportQuestionType` this is optional
* php artisan server to load app. You Got it!

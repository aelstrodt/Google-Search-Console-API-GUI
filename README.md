GUI application to make Google Search Console API requests

Features:

- Auth2 Authorization
- API Requests to the following endpoints and methods:
	- URL Crawl Errors Counts
		- Query
	- URL Crawl Errors Samples
		- Get
		- List
	- Search Analytics
		- Query
- Input parameters/ filters should follow google search console reference docs
	- Do not include quotation marks ("")
	- Do not include square brackets ([])
- API response saves in .json file with the date as file name

Python Modules Installation:

pip install httplib2
pip install oauth2client
pip install --user --upgrade google-api-python-client

Authentication

"credentials.json" file -> download OAuth2 Client Id from Google Cloud Console
Save "credentials.json" in same directory as gsc_api_gui.py
If there is no webmaster_credentials.dat file in your directory
A Browser window will open when you run the program
Follow the steps in the browser to login
Copy paste the authentication code 
From the URL in the browser to the GUI application
Authentication code is everything after the "code=" 
And before the final '#' char

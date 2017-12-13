from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import webbrowser
import tkinter as tk
import time
from googleapiclient.discovery import build
import httplib2
from googleapiclient.errors import HttpError
import json
import pandas as pd

WEBMASTER_CREDENTIALS_FILE_PATH = "webmaster_credentials.dat"
SECRETS_FILE = 'credentials.json'
CATEGORIES = ["authPermissions", "flashContent", "manyToOneRedirect",
              "notFollowed", "notFound", "other", 
              "roboted", "serverError", "soft404"]
PLATFORMS = ["mobile", "smartphoneOnly", "web"]
BOOL = ['true', 'false']
EMPTY = ""
SEARCHTYPES = ["image", "video", "web"]
DIMENSIONS = ['country', 'device', 'page', 'query', 'search', 'searchAppearance']
OPERATORS = ['contains', 'equals', 'notContains', 'notEquals']
AGGTYPES = ['auto', 'byPage', 'byProperty']
ID = 0

class Request(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master.title("Google Search API Helper")
        self.pack()
        self.frame_1 = tk.Frame(self)
        self.frame_1.pack()
        self.frame_2 = tk.Frame(self)
        self.frame_2.pack()
        self.frame_3 = tk.Frame(self)
        self.frame_3.pack()
        self.credentials = None
        self.verified_sites = []
        self.find_properties()
        tk.Label(self.frame_1, text="API Options").pack()
        self.dict = {'URL Crawl Errors Counts':
                        {'Query':{
                            'siteUrl': self.verified_sites,
                            'category': ["all"] + CATEGORIES,
                            'latestCountsOnly': BOOL,
                            'platform': ["all"] + PLATFORMS}
                        },
                    'URL Crawl Errors Samples':
                        {'Get':{
                            'siteUrl': self.verified_sites,
                            'url': EMPTY,
                            'category': CATEGORIES,
                            'platform': PLATFORMS},
                        'List':{
                            'siteUrl': self.verified_sites,
                            'category': CATEGORIES,
                            'platform': PLATFORMS}
                        },
                    'Search Analytics':
                        {'Query': {
                            'siteUrl': self.verified_sites,
                            'startDate': EMPTY,
                            'endDate': EMPTY,
                            'dimensions': EMPTY,
                            'searchType': SEARCHTYPES,
                            'dimension': EMPTY,
                            'operator': OPERATORS,
                            'expression': EMPTY ,
                            'aggregationType':AGGTYPES,
                            'rowLimit': 1000,
                            'startRow': 0
                            }
                        }
                    }
        self.response = None
        self.service = None
        self.filter_names = ['dimension', 'operator', 'expression']
        self.saved_label = tk.Label(self.frame_3, text='Response Saved!')
        self.exit_button = tk.Button(self.frame_3, text = 'Exit', command = self.done)
        self.request_label = tk.Label(self.frame_3, text = "Making request...")
        self.submit2_button = tk.Button(self.frame_3, text='Submit Another Request', command=self.handle_entries)
        self.submit_button = tk.Button(self.frame_3, text='Submit', command=self.handle_entries)
        self.option = tk.StringVar(self)
        self.method = tk.StringVar(self)
        self.option.trace('w', self.update_options)
        self.api_options = tk.OptionMenu(self.frame_1, self.option, *self.dict.keys())
        self.api_methods = tk.OptionMenu(self.frame_1, self.method, '')
        self.option.set('URL Crawl Errors Counts')
        self.api_options_width = len(max(self.dict, key=len))
        self.api_options.config(width=self.api_options_width)
        self.api_methods.config(width=self.api_options_width)
        self.api_options.pack()
        tk.Label(self.frame_1, text="API Methods").pack()
        self.api_methods.pack()
        tk.Label(self.frame_2, text="API Params").pack()
        self.pack()
        self.method.trace('w', self.set_params)
        self.set_params()
        self.submit_button.pack()
        self.master.resizable(False,False)
        self.master.tk_setPalette(background='#ececec')
    def update_options(self, *args):
        methods = self.dict[self.option.get()]
        first_method = next(iter(methods))
        self.method.set(first_method)
        menu = self.api_methods['menu']
        menu.delete(0, 'end')
        for method in methods:
            menu.add_command(label=method, command=lambda new_method=method: self.method.set(new_method))
    def set_params(self, *args):
        self.params = self.dict[self.option.get()][self.method.get()]
        try:
            for l,e in self.param_fields:
                l.pack_forget()
                e.pack_forget()
        except:
            pass
        self.param_entries = []
        self.param_fields = []
        for key, values in self.params.items():
            l = tk.Label(self.frame_2, text=key)
            l.pack()
            if isinstance(values, int):
                v = tk.StringVar(self, value = str(values))
                e = tk.Entry(self.frame_2, textvariable = v)
                e.pack()
                self.param_fields.append((l,e))
            else:
                if len(values) == 0 :
                    e = tk.Entry(self.frame_2)
                    e.pack()
                    self.param_fields.append((l,e))
                elif len(values) > 0:
                    e = tk.StringVar()
                    e.set(values[0])
                    o = tk.OptionMenu(self.frame_2, e, *values)
                    o.config(width=self.api_options_width)
                    o.pack()
                    self.param_fields.append((l,o))
            self.param_entries.append((l,e))
    def handle_entries(self):
        if self.submit2_button.winfo_ismapped(): self.submit2_button.pack_forget()
        if self.submit_button.winfo_ismapped(): self.submit_button.pack_forget()
        if self.exit_button.winfo_ismapped(): self.exit_button.pack_forget()
        if self.request_label.winfo_ismapped(): self.request_label.pack_forget()
        if self.saved_label.winfo_ismapped(): self.saved_label.pack_forget()
        self.request_params = {}
        self.filters = {}
        if self.option.get() == 'Search Analytics': self.request_params['dimensionFilterGroups'] = {}
        for l,e in self.param_entries:
            if e.get() != 'all':
                if l.cget('text') == 'dimensions':
                    self.request_params[l.cget('text')] = [e.get()]
                elif l.cget('text') in self.filter_names:
                    key = '{}'.format(l.cget('text'))
                    self.filters[key] = e.get()
                else:
                    self.request_params[l.cget('text')] = e.get()
        if self.option.get() == 'Search Analytics':
            self.filters = [self.filters]
            temp = self.request_params['dimensionFilterGroups']
            temp['filters'] = self.filters
            temp['groupType'] = 'and'
            self.request_params['dimensionFilterGroups'] = [temp]
        self.request_label.pack()
        self.handle_request()
        self.save_response()
        self.request_label.pack_forget()
        self.saved_label.pack()
        self.submit2_button.pack()
        self.exit_button.pack()

    def handle_request(self):
        if self.service == None:
            http_auth = httplib2.Http()
            http_auth = self.credentials.authorize(http_auth)
            self.service = build('webmasters', 'v3', http=http_auth)
        max_retries=5
        wait_interval=4
        retry_errors=(503, 500)
        retries = 0
        while retries <= max_retries:
            try:
                if self.option.get() == 'URL Crawl Errors Counts':
                    self.response = self.service.urlcrawlerrorscounts().query(**self.request_params).execute()
                elif self.option.get() == 'URL Crawl Errors Samples':
                    if self.method.get() == 'List':
                        self.response = self.service.urlcrawlerrorssamples().list(**self.request_params).execute()
                    elif self.method.get() == 'Get':
                        self.response = self.service.urlcrawlerrorssamples().get(**self.request_params).execute()
                elif self.option.get() == 'Search Analytics':
                    url = self.request_params['siteUrl']
                    self.request_params.pop('siteUrl',None)
                    self.response = self.service.searchanalytics().query(siteUrl = url, body = self.request_params).execute()
            except HttpError as err:
                decoded_error_body = err.content.decode('utf-8')
                json_error = json.loads(decoded_error_body)
                if json_error['error']['code'] in retry_errors:
                    time.sleep(wait_interval)
                    retries += 1
                    continue
            break
    def save_response(self):
        global ID
        file_name = "v-" + str(ID) + "-" + time.strftime("%d-%m-%Y")
        ID += 1
        with open(file_name + '.json', 'w') as fp:
            json.dump(self.response, fp)
    def done(self):
        self.master.destroy()
    def find_properties(self):
        self.storage = Storage(WEBMASTER_CREDENTIALS_FILE_PATH)
        self.credentials = self.storage.get()
        http_auth = httplib2.Http()
        http_auth = self.credentials.authorize(http_auth)
        self.service = build('webmasters', 'v3', http=http_auth)
        self.response = self.service.sites().list().execute()
        self.response = list(self.response.values())[0]
        for site in self.response:
            if site['permissionLevel'] == 'siteFullUser':
                self.verified_sites.append(site['siteUrl'])


class Credentials(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master.title('Google API Credentials')
        self.not_found_label = tk.Label(self, text="No Credentials Found")
        self.enter_auth_label = tk.Label(self, text="Enter the authentication code from the Browser:")
        self.submit_button = tk.Button(self, text= " Submit ", command=self.submit)
        self.quit_button = tk.Button(self, text= "Close", command=self.quit_app)
        self.master.resizable(False,False)
        self.master.tk_setPalette(background='#ececec')
        self.pack()
        self.credentials = None
        self.storage = None
        self.auth_code = tk.Entry(self)
        self.load_oauth2_credentials()
    def submit(self):
            self.submit_button.pack_forget()
            self.not_found_label.pack_forget()
            self.enter_auth_label.pack_forget()
            self.auth_code.pack_forget()
            auth_code = self.auth_code.get()
            self.credentials = self.flow.step2_exchange(auth_code)
            self.storage.put(self.credentials)
            if self.credentials != None: tk.Label(self, text='Credentials Saved').pack()
            self.quit_button.pack()
    def new_credentials(self):
        self.flow = flow_from_clientsecrets(
            SECRETS_FILE,
            scope="https://www.googleapis.com/auth/webmasters.readonly",
            redirect_uri="http://localhost")
        auth_uri = self.flow.step1_get_authorize_url()
        webbrowser.open(auth_uri)
        self.not_found_label.pack()
        self.enter_auth_label.pack()
        self.auth_code.pack()
        self.submit_button.pack()
    def load_oauth2_credentials(self):
        self.storage = Storage(WEBMASTER_CREDENTIALS_FILE_PATH)
        self.credentials = self.storage.get()
        if self.credentials is None or self.credentials.invalid:
            self.new_credentials()
        else:
            tk.Label(self, text='Credentials Found: Authorized').pack()
            self.quit_button.pack()
    def quit_app(self):
            self.master.destroy()

def new_root():
    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 10
    root.geometry("+%d+%d" % (x, y))
    root.deiconify()
    root.attributes('-topmost', True)
    return root

if __name__ == '__main__':

    root = new_root()
    app = Credentials(root)
    app.mainloop()

    root = new_root()
    app = Request(root)
    app.mainloop()

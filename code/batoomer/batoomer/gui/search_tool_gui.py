import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import webbrowser
from functools import partial
import numpy as np
import time

import tweepy
import json
import pandas as pd
from googleapiclient.errors import HttpError

from batoomer.twitter_nodes.search_engine import TwitterSearchEngine, GoogleSearchEngine
from batoomer.extras.nd_utils import get_text_data_parl_nd


class SearchGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # API credentials
        self.twitter_cred = {}
        self.google_cred = {}

        # Options
        self.api_option = 1
        self.sm_option = 1
        self.clf_option = 1

        self.title('Social Media Account Search Tool')
        self.geometry('1280x720')

        self.notebook = ttk.Notebook(self)

        self.MainFrame = MainFrame(self.notebook, self)
        self.ApiFrame = ApiFrame(self.notebook, self)
        self.OptionFrame = OptionFrame(self.notebook, self)
        self.AboutFrame = AboutFrame(self.notebook, self)

        self.notebook.add(self.MainFrame, text='Search')
        self.notebook.add(self.ApiFrame, text='API Keys')
        self.notebook.add(self.OptionFrame, text='Options')
        self.notebook.add(self.AboutFrame, text='About us')

        self.notebook.pack(fill='both', expand='True')

    def set_creds(self, cred, cred_type):
        if cred_type == 'twitter':
            self.twitter_cred = cred
        elif cred_type == 'google':
            self.google_cred = cred

    # Get API Credentials
    def get_creds(self):
        return self.twitter_cred, self.google_cred

    def set_api_option(self, val):
        self.api_option = val

    def get_api_option(self):
        return self.api_option

    def set_sm_option(self, val):
        self.sm_option = val

    def get_sm_option(self):
        return self.sm_option

    def set_clf_option(self, val):
        self.clf_option = val

    def get_clf_option(self):
        return self.clf_option


class MainFrame(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__()

        # --------------------- Search Interface ---------------------------------
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill='x', pady=25, padx=10)
        self.search_entry = tk.Entry(self.search_frame, bd=4)
        self.search_entry.insert(tk.END, '')
        self.search_entry.pack(side='left', fill='x', expand='true')
        self.search_button = tk.Button(self.search_frame, text='Search', height=2, width=8,
                                       command=lambda: self.search(controller=controller))
        self.search_button.pack(side='right')

        # --------------------- Result Interface ---------------------------------
        self.result_frame = tk.LabelFrame(self, bd=5, font=('Arial bold', 20))
        self.result_frame.pack(fill='both', expand='True', pady=5, padx=10)
        self.result_label = tk.Text(self.result_frame, font=('Arial', 18))
        self.hyperlink = HyperlinkManager(self.result_label)
        self.result_label.insert(tk.END, ' ')
        self.result_label.pack(side='top', fill='both', expand='True', pady=10, padx=10)

    def search(self, controller):

        self.search_button.config(state=tk.DISABLED)
        query = self.search_entry.get()
        if query != '':
            self.result_frame.config(text=f'Displaying Results For: {query}')
            self.result_label.config(state=tk.NORMAL)
            self.result_label.delete(1.0, tk.END)
            twitter_cred, google_cred = controller.get_creds()
            try:
                results = pd.DataFrame()
                if controller.get_api_option() == 1:
                    results = self.__search([query], twitter_cred, controller.get_sm_option(),
                                            controller.get_api_option())
                elif controller.get_api_option() == 2:
                    results = self.__search([query], google_cred, controller.get_sm_option(),
                                            controller.get_api_option())

                if controller.get_sm_option() == 1:
                    domain = "https://www.twitter.com/"
                else:
                    domain = ''

                if not results.empty:
                    results = results.replace(np.nan, -1)

                    # Classify Results if needed
                    if controller.get_clf_option() != 1:
                        results = self.__classify_results(results=results, credentials=twitter_cred,
                                                          clf_type=controller.get_clf_option())

                    if results.loc[0, 'Result 1'] != -1:
                        for i, col in enumerate(results.columns):
                            if col != 'Query':
                                if results.loc[0, col] == -1:
                                    break
                                self.result_label.insert(tk.END, f'{col}: ')
                                self.result_label.insert(tk.END, f'{domain + results.loc[0, col]}\n',
                                                         self.hyperlink.add(partial(webbrowser.open,
                                                                                    (domain + results.loc[0, col]))))

                    else:
                        self.result_label.insert(tk.END, f'Failed to find an Account.')

                self.result_label.config(state=tk.DISABLED)
            except Exception as err:
                tk.messagebox.showwarning(title='Error', message=f'There was a problem! \n{err}')

        else:
            tk.messagebox.showwarning(title='Warning', message=f'Please Insert a Query!')
        self.search_button.config(state=tk.NORMAL)

    @staticmethod
    def __search(queries, credentials, platform, api_type):
        results = pd.DataFrame()
        # Twitter Accounts
        if platform == 1:
            # GoogleAPI
            if api_type == 2:
                se = GoogleSearchEngine(google_api_key=credentials['google_api_key'],
                                        search_engine_id=credentials['search_engine_id'])
                for query in queries:
                    try:
                        se.search(query=query, platform='twitter')
                        result = se.get_results()
                        results = results.append(result)
                    except HttpError as err:
                        if err.resp.status == 429:
                            tk.messagebox.showwarning(title='Warning',
                                                      message=f'Rate Limit Reached! Come back after 24h!')
                            pass
                        else:
                            tk.messagebox.showwarning(title='Error', message=f'There was a problem! \n{err}')
                            pass
                    except Exception as err:
                        tk.messagebox.showwarning(title='Error', message=f'There was a problem! \n{err}')

            # TwitterAPI
            if api_type == 1:
                se = TwitterSearchEngine(twitter_credentials=credentials)

                for query in queries:
                    try:
                        se.search(query=query, count=10)
                        result = se.get_results()
                        results = results.append(result)
                    except tweepy.RateLimitError as err:
                        tk.messagebox.showwarning(title='Warning',
                                                  message=f'Rate Limit Reached! Come back after 15min!')
                        pass
                    except Exception as err:
                        tk.messagebox.showwarning(title='Error', message=f'There was a problem! \n{err}')

        # Facebook Accounts
        else:
            se = GoogleSearchEngine(google_api_key=credentials['google_api_key'],
                                    search_engine_id=credentials['search_engine_id'])

            for query in queries:
                try:
                    se.search(query=query, platform='facebook')
                    result = se.get_results()
                    results = results.append(result)
                except HttpError as err:
                    if err.resp.status == 429:
                        tk.messagebox.showwarning(title='Warning',
                                                  message=f'Rate Limit Reached! Come back after 24h!')
                        pass
                    else:
                        tk.messagebox.showwarning(title='Error', message=f'There was a problem! \n{err}')
                except Exception as err:
                    tk.messagebox.showwarning(title='Error', message=f'There was a problem! \n{err}')
        return results

    @staticmethod
    def __classify_results(results, clf_type, credentials):
        from batoomer.twitter_nodes import classification

        rst = pd.DataFrame()

        # Choose Classifier
        model_name = ''
        if clf_type == 2:
            model_name = 'classifier_parl_nd'
        elif clf_type == 3:
            model_name = 'classifier_hotel_nd'
        # Load Classifier
        # TODO Implement CLassifier_hotel_nd on modules classification and extras.nd_utils
        clf = classification.Classifier(model_name=model_name, twitter_credentials=credentials, verbose=0)

        nodes = list(results[[f'Result {i + 1}' for i in range(len(results.T) - 1)]].iloc[0].unique())
        nodes = [node for node in nodes if node != -1]
        if nodes:
            labels = clf.predict(nodes)
            fltr = pd.DataFrame([nodes, labels]).T
            fltr = fltr[fltr[1] == 1]
            if not fltr.empty:
                rst = rst.append(fltr[fltr[1] == 1][0])
            else:
                rst = rst.append([-1])
        else:
            rst.append([-1])

        rst.columns = [f'Result {i + 1}' for i in range(len(rst.T))]

        return rst


class ApiFrame(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__()

        # -------------------------- Twitter Credentials Frame -----------------------------------
        self.lf1 = tk.LabelFrame(self, text='TwitterAPI Credentials', bd=10, font=('Arial Bold', 20))
        self.lf1.pack(fill='both', padx=50, pady=20)

        # Consumer Key
        self.f1_1 = tk.Frame(self.lf1)
        self.f1_1.pack(fill='x', pady=5, padx=15)
        self.l1_1 = tk.Label(self.f1_1, text='Consumer Key', font=('Arial Bold', 15))
        self.l1_1.pack(side='left')
        self.t1_1 = tk.Label(self.f1_1, text=' ', font=('Arial', 15))
        self.t1_1.pack(side='right')

        # Consumer Secret
        self.f1_2 = tk.Frame(self.lf1)
        self.f1_2.pack(fill='x', pady=5, padx=15)
        self.l1_2 = tk.Label(self.f1_2, text='Consumer Secret', font=('Arial Bold', 15))
        self.l1_2.pack(side='left')
        self.t1_2 = tk.Label(self.f1_2, text=' ', font=('Arial', 15))
        self.t1_2.pack(side='right')

        # Access Token Key
        self.f1_3 = tk.Frame(self.lf1)
        self.f1_3.pack(fill='x', pady=5, padx=15)
        self.l1_3 = tk.Label(self.f1_3, text='Access Token Key', font=('Arial Bold', 15))
        self.l1_3.pack(side='left')
        self.t1_3 = tk.Label(self.f1_3, text=' ', font=('Arial', 15))
        self.t1_3.pack(side='right')

        # Access Token Secret
        self.f1_4 = tk.Frame(self.lf1)
        self.f1_4.pack(fill='x', pady=5, padx=15)
        self.l1_4 = tk.Label(self.f1_4, text='Access Token Secret', font=('Arial Bold', 15))
        self.l1_4.pack(side='left')
        self.t1_4 = tk.Label(self.f1_4, text=' ', font=('Arial', 15))
        self.t1_4.pack(side='right')

        self.b1_1 = tk.Button(self.lf1, text="Upload Credentials",
                              command=lambda: self.open_file(cred_type='twitter', controller=controller))
        self.b1_1.pack(side='right', pady=10, padx=10)

        self.b1_2 = tk.Button(self.lf1, text="Verify Credentials", state=tk.DISABLED,
                              command=lambda: self.verify_cred(cred_type='twitter', controller=controller))
        self.b1_2.pack(side='right', pady=10, padx=10)

        # ----------------------------- Google Credentials Frame ---------------------------------------
        self.lf2 = tk.LabelFrame(self, text='GoogleAPI Credentials', bd=10, font=('Arial Bold', 20))
        self.lf2.pack(fill='both', padx=50, pady=20)

        # GoogleAPI Key
        self.f2_1 = tk.Frame(self.lf2)
        self.f2_1.pack(fill='x', pady=5, padx=15)
        self.l2_1 = tk.Label(self.f2_1, text='GoogleAPI key', font=('Arial Bold', 15))
        self.l2_1.pack(side='left')
        self.t2_1 = tk.Label(self.f2_1, text=' ', font=('Arial', 15))
        self.t2_1.pack(side='right')

        # Custom Search Engine ID
        self.f2_2 = tk.Frame(self.lf2)
        self.f2_2.pack(fill='x', pady=5, padx=15)
        self.l2_2 = tk.Label(self.f2_2, text='Custom Search Engine', font=('Arial Bold', 15))
        self.l2_2.pack(side='left')
        self.t2_2 = tk.Label(self.f2_2, text=' ', font=('Arial', 15))
        self.t2_2.pack(side='right')

        self.b2_1 = tk.Button(self.lf2, text="Upload Credentials",
                              command=lambda: self.open_file(cred_type='google', controller=controller))
        self.b2_1.pack(side='right', pady=10, padx=10)

        self.b2_2 = tk.Button(self.lf2, text="Verify Credentials", state=tk.DISABLED,
                              command=lambda: self.verify_cred(controller=controller, cred_type='google'))
        self.b2_2.pack(side='right', pady=10, padx=10)

    def open_file(self, cred_type, controller):
        filename = tk.filedialog.askopenfilename(initialdir="/", title="Select a File",
                                                 filetypes=(("json files", "*.json"), ("all files", "*.*")))

        # Change label contents and set credentials
        if filename:
            with open(filename, "r") as file:
                file = json.load(file)
                # Read Twitter Credentials
                if cred_type == 'twitter':
                    txts = [self.t1_1, self.t1_2, self.t1_3, self.t1_4]
                    key_names = ['consumer_key', 'consumer_secret', 'access_token_key', 'access_token_secret']
                    twitter_cred = {}
                    for i, key in enumerate(file):
                        txts[i].config(text=file[key])
                        twitter_cred[key_names[i]] = file[key]
                    controller.set_creds(twitter_cred, 'twitter')
                    self.b1_2.config(state=tk.NORMAL)

                # Read Google Credentials
                elif cred_type == 'google':
                    key_names = ['google_api_key', 'search_engine_id']
                    txts = [self.t2_1, self.t2_2]
                    google_cred = {}
                    for i, key in enumerate(file):
                        txts[i].config(text=file[key])
                        google_cred[key_names[i]] = file[key]
                    controller.set_creds(google_cred, 'google')
                    self.b2_2.config(state=tk.NORMAL)

        # TODO Implement this function

    def verify_cred(self, controller, cred_type):
        twitter_cred, google_cred = controller.get_creds()
        if cred_type == 'twitter':
            auth = tweepy.OAuthHandler(twitter_cred['consumer_key'],
                                       twitter_cred['consumer_secret'])
            auth.set_access_token(twitter_cred['access_token_key'],
                                  twitter_cred['access_token_secret'])
            api = tweepy.API(auth)
            success = api.verify_credentials()

            if success:
                self.lf1.config(bg='green')
            else:
                self.lf1.config(bg='red')

        elif cred_type == 'google':
            return 1


class OptionFrame(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__()

        # --------------------- API Option -----------------------------------
        self.api_option = tk.IntVar()
        self.api_option.set(1)

        self.api_section = tk.Frame(self)
        self.api_section.pack(fill='x', pady=25, padx=10)
        self.api_label = tk.Label(self.api_section, text='Select an API:')
        self.api_label.pack(side='left', padx=5)
        self.checkbutton_twitter = tk.Radiobutton(self.api_section, text='TwitterAPI', value=1,
                                                  variable=self.api_option,
                                                  command=lambda: self.update_api_option(self.api_option, controller))
        self.checkbutton_twitter.pack(side='left', padx=20)
        self.checkbutton_google = tk.Radiobutton(self.api_section, text='GoogleAPI', value=2,
                                                 variable=self.api_option,
                                                 command=lambda: self.update_api_option(self.api_option, controller))
        self.checkbutton_google.pack(side='left', padx=20)

        # --------------------- Social Media Platform Option ---------------------------
        self.sm_option = tk.IntVar()
        self.sm_option.set(1)

        self.sm_section = tk.Frame(self)
        self.sm_section.pack(fill='x', pady=5, padx=10)
        self.sm_label = tk.Label(self.sm_section, text='Social Media Platform:')
        self.sm_label.pack(side='left', padx=5)
        self.sm_checkbutton_twitter = tk.Radiobutton(self.sm_section, text='Twitter', value=1,
                                                     variable=self.sm_option,
                                                     command=lambda: self.update_sm_option(self.sm_option,
                                                                                           controller))
        self.sm_checkbutton_twitter.pack(side='left', padx=20)
        self.sm_checkbutton_facebook = tk.Radiobutton(self.sm_section, text='Facebook', value=2,
                                                      variable=self.sm_option, state=tk.DISABLED,
                                                      command=lambda: self.update_sm_option(self.sm_option,
                                                                                            controller))
        self.sm_checkbutton_facebook.pack(side='left', padx=20)

        # --------------------- Classifier Option -------------------------------------
        self.clf_option = tk.IntVar()
        self.clf_option.set(1)

        self.clf_section = tk.Frame(self)
        self.clf_section.pack(fill='x', padx=10, pady=25)
        self.clf_label = tk.Label(self.clf_section, text='Classifier:')
        self.clf_label.pack(side='left', padx=5)
        self.clf_checkbutton_none = tk.Radiobutton(self.clf_section, text='None', value=1,
                                                   variable=self.clf_option,
                                                   command=lambda: self.update_clf_option(self.clf_option, controller))
        self.clf_checkbutton_none.pack(side='left', padx=20)
        self.clf_checkbutton_parl = tk.Radiobutton(self.clf_section, text='Members of Parliament', value=2,
                                                   variable=self.clf_option,
                                                   command=lambda: self.update_clf_option(self.clf_option, controller))
        self.clf_checkbutton_parl.pack(side='left', padx=20)
        self.clf_checkbutton_hotel = tk.Radiobutton(self.clf_section, text='Hotels', value=3,
                                                    variable=self.clf_option,
                                                    command=lambda: self.update_clf_option(self.clf_option, controller))
        self.clf_checkbutton_hotel.pack(side='left', padx=20)

    def update_api_option(self, api_option, controller):
        if api_option.get() == 2:
            self.sm_checkbutton_facebook.config(state=tk.NORMAL)
        elif api_option.get() == 1:
            self.sm_checkbutton_facebook.config(state=tk.DISABLED)
            self.clf_checkbutton_parl.config(state=tk.NORMAL)
            self.clf_checkbutton_hotel.config(state=tk.NORMAL)
            self.sm_option.set(1)
            controller.set_sm_option(1)

        controller.set_api_option(api_option.get())

    def update_sm_option(self, sm_option, controller):
        if sm_option.get() == 2:
            self.clf_checkbutton_parl.config(state=tk.DISABLED)
            self.clf_checkbutton_hotel.config(state=tk.DISABLED)
            self.clf_option.set(1)
            controller.set_clf_option(1)
        elif sm_option.get() == 1:
            self.clf_checkbutton_parl.config(state=tk.NORMAL)
            self.clf_checkbutton_hotel.config(state=tk.NORMAL)

        controller.set_sm_option(sm_option.get())

    def update_clf_option(self, clf_option, controller):
        controller.set_clf_option(clf_option.get())


class AboutFrame(ttk.Frame):
    def __init__(self, container, controller):
        super().__init__()

        desc = "This tool was developed during the thesis: Classification of social media nodes." \
               "\n\nDemocritus University of Thrace 2021-2022, Department of Electrical and Computer Engineering "
        self.lf1 = tk.Text(self, bd=10, font=('Arial', 15))
        self.lf1.insert(tk.END, desc)
        self.lf1.config(state=tk.DISABLED)
        self.lf1.pack(fill='both', expand='True', padx=20, pady=20)


class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return


if __name__ == '__main__':
    app = SearchGUI()
    app.mainloop()

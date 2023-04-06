import tkinter as tk
import requests
import base64
import time

GET_URL = "http://192.168.8.1/reqproc/proc_get?multi_data=1&cmd="
POST_URL = "http://192.168.8.1/reqproc/proc_post"

class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.GUI()
        self.update_GUI()
    
    def GUI(self):
        self.title("Router Controler")
        self.geometry("300x300")
        self.label = tk.Label(self, text="Control your Router without a Browser")
        self.label.pack()
        
        self.login_frame = tk.Frame(self, padx=10, pady=10)
        self.login_frame.pack()

        self.data_control_frame = tk.Frame(self, padx=10, pady=10)
        self.data_control_frame.pack()

        self.network_speed_frame = tk.Frame(self, padx=10, pady=10)
        self.network_speed_frame.pack()

        self.password_field = tk.Entry(self.login_frame,show="*")
        self.password_field.insert(0,'admin1')
        self.password_field.pack()

        self.button_login = tk.Button(self.login_frame, text="Login",command=lambda: self.log('in'))
        self.button_login.pack()


        self.button_connect_data = tk.Button(self.data_control_frame, text="Connect Mobile Data",command=lambda: self.switch_mobile_data('on'))
        self.button_connect_data.pack(side="left")

        self.button_discconect_data = tk.Button(self.data_control_frame, text="Disconnect Mobile Data",command=lambda: self.switch_mobile_data('off'))
        self.button_discconect_data.pack(side="left")

        self.network_options = tk.StringVar(self)
        self.Network_modes = ["4G Only","3G Only","Auto"]
        self.network_mode_selector = tk.OptionMenu(self, self.network_options, *self.Network_modes,command=self.setNetworkMode)
        self.network_mode_selector.pack()

        self.network_download_speed = tk.Label(self.network_speed_frame, text="")
        self.network_download_speed.pack(side='left')

        self.network_upload_speed = tk.Label(self.network_speed_frame, text="")
        self.network_upload_speed.pack(side='left')

        self.button_logout = tk.Button(self.login_frame, text="Logout",command=lambda: self.log('out'))
        self.button_logout.pack()
    
    def check_state(self):
        login_info_url = f"{GET_URL}loginfo%2Cppp_status%2Csub_network_type%2Crealtime_tx_thrpt%2Crealtime_rx_thrpt"
        response = self.session.get(login_info_url)
        if response.status_code == 200:
            data = response.json()
            if data["loginfo"] == "ok" :
                logged = True
            elif data["loginfo"] == "":
                logged = False
            if data["ppp_status"] == "ppp_connected" :
                mobile_data = True
            elif data["ppp_status"] == "ppp_disconnected":
                mobile_data = False
            elif data["ppp_status"] == "ppp_connecting":
                mobile_data = "connecting"
            if data["sub_network_type"] == "FDD_LTE" :
                net_mode = 0
            elif data["sub_network_type"] == "WCDMA" or "HSPA++":
                net_mode = 1
            network_download_speed = data['realtime_rx_thrpt']
            network_upload_speed = data['realtime_tx_thrpt']
        return logged,mobile_data,net_mode,network_download_speed,network_upload_speed
    
    def update_GUI(self):
        logged,data_on,net_mode,d,u = self.check_state()
        if logged:
            self.button_login.configure(state='disabled')
            self.button_logout.configure(state='normal')
            if data_on:
                self.button_connect_data.configure(state="disabled")
                self.button_discconect_data.configure(state="normal")
                self.network_mode_selector.configure(state='disabled')
            elif not data_on:
                self.button_connect_data.configure(state="normal")
                self.button_discconect_data.configure(state="disabled")
                self.network_mode_selector.configure(state='normal')
            elif data_on == 'connecting':
                self.button_connect_data.configure(state="disabled")
                self.button_discconect_data.configure(state="disabled")
            try:
                self.network_download_speed.configure(text = str(int(d)/1024))
                self.network_upload_speed.configure(text = str(int(u)/1024))
            except:
                pass
        else:
            self.button_login.configure(state='normal')
            self.button_logout.configure(state='disabled')
            self.button_connect_data.configure(state="disabled")
            self.button_discconect_data.configure(state="disabled")
            self.network_download_speed.configure(text = "")
            self.network_upload_speed.configure(text = "")
        self.network_options.set(self.Network_modes[net_mode])


        self.after(200,self.update_GUI)
        
    def log(self,type):
        if type == "in":
            base64_bytes = base64.b64encode(self.password_field.get().encode('utf-8'))
            encoded_password = base64_bytes.decode('utf-8')
            payload = {"goformId":"LOGIN","password":encoded_password}
        elif type == "out":
            payload = {"goformId":"LOGOUT"}
        try:
            self.session.post(POST_URL,data=payload)
        except:
            pass
    
    def switch_mobile_data(self,switch):
        if switch == "on":
            payload = {"notCallback":"true","goformId":"CONNECT_NETWORK"}
        elif switch == "off":
            payload =  {"notCallback":"true","goformId":"DISCONNECT_NETWORK"}
        self.session.post(POST_URL,data=payload)

    def setNetworkMode(self,option):
        if option == '3G Only':
            payload = {"BearerPreference":"Only_WCDMA","goformId":"SET_BEARER_PREFERENCE"}
        elif option == '4G Only':
            payload = {"BearerPreference":"Only_LTE","goformId":"SET_BEARER_PREFERENCE"}
        elif option == 'Auto':
            payload = {"BearerPreference":"NETWORK_auto","goformId":"SET_BEARER_PREFERENCE"}
        else:
            pass
        response = self.session.post(POST_URL,data=payload)

app = Main()
app.mainloop()

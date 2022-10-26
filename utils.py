import json
from datetime import datetime
import pytz

from whatsapp_api.notification import SendMessage

def reader():
    with open ("env.json",mode="r+") as d:
        data = json.load(d)

    return data


def parse_date(date:str) -> str:
    m = {
        'enero': "01",
        'febrero': "02",
        'marzo': "03",
        'abril': "04",
        'mayo': "05",
        'junio': "06",
        'julio': "07",
        'agosto': "08",
        'septiembre': "09",
        'octubre': "10",
        'noviembre': "11",
        'diciembre': "12"
        }
    date = f"{date[:-6]} {date[-4:]}"
    fecha = date.split(" ")
    mes =  fecha[0]
    dia =  fecha[1]
    anio = fecha[2]

    try:
        out = str(m[mes.lower()])
        return( anio + "-" +  out + "-" + dia)
    except:
        raise ValueError('No es un mes')

def parse_local_time(time:str, date:str) -> str:
    local = pytz.timezone("America/Lima")
    time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M:%S')
    full_date = f"{parse_date(date)} {time}"
    naive = datetime.strptime(full_date, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    return local_dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

def get_value_data_popup(raw_data:dict) -> dict:
    value_data = {
        "field_name":raw_data["fields[field_name][value]"],
        "field_lastname":raw_data["fields[field_apellidos][value]"],
        "field_email":raw_data["fields[field_email][value]"],
        "field_numero":raw_data["fields[field_numero][value]"],
        "field_time":parse_local_time(raw_data["meta[time][value]"], raw_data["meta[date][value]"])
    }
    return value_data  

def get_value_data_triage(raw_data:dict) -> dict:
    value_data = {
        "field_email":raw_data["Correo"],
        "field_numero":raw_data["Número de contacto"],
        "field_time":parse_local_time(raw_data["Time"], raw_data["Date"])
    }
    return value_data  


class WriterState():
    def __init__(self,value_data:dict) -> None:
        self.value_data = value_data

    def remove_user(self) -> bool:
        with open('./user_state.json', mode='r+') as d:
            user_state = json.load(d)
            for item in user_state["user_notification"]:
                print(self.value_data["field_numero"])
                print(item["field_numero"])
                print(item)
                if item["field_numero"] == self.value_data["field_numero"]:
                    user_state["user_notification"].remove(item)
                        
        with open('./user_state.json', mode="w") as dw:
            dw.write(json.dumps(user_state, indent = 4))                     
            return True 

    def add_user(self) -> bool:
        with open('./user_state.json', mode='r+') as d:
            user_state = json.load(d)
            user_state_data = {
                "field_numero":self.value_data["field_numero"],
                "field_email":self.value_data["field_email"],
                "field_time":self.value_data["field_time"]
            }
            user_state["user_notification"].append(user_state_data)
            d.seek(0)
            json.dump(user_state, d, indent = 4)
        return True 


def help(value_data):
    #url = "https://hook.us1.make.com/ekirtpo39os96b5dsjgosp3nx1di1e5b"
    #print(requests.post(url, raw_data).text)
    

    template = {
        "name": "sample_purchase_feedback",
        "language": {"code": "es"},
        "components": [
            {
                "type": "header",
                "parameters": [
                    {
                        "type": "image",
                        "image": {
                            "link": "https://cdn.discordapp.com/attachments/826683941053399091/928700680661782628/unknown.png"
                        },
                    }
                ],
            },
            {"type": "body", "parameters": [{"type": "text", "text": f"{value_data['field_name']} {value_data['field_lastname']}"}]},
        ],
    }

    sender = SendMessage(
        id_whats=str(reader()['ID_WHATSAPP']),
        acces_token=(reader()['FACEBOOK_ACCESS_TOKEN']),
        phone=value_data["field_numero"]
    )
    print(sender.template(template))    
    return None


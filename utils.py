import json
from datetime import datetime, timedelta

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
    time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M:%S')
    full_date = f"{parse_date(date)} {time}"
    naive = datetime.strptime(full_date, "%Y-%m-%d %H:%M:%S") - timedelta(hours=5) + timedelta(minutes=15) 
    
    return naive.strftime("%Y-%m-%d %H:%M:%S")

def get_value_data_popup(raw_data:dict) -> dict:
    value_data = {
        "field_name":raw_data["Nombres"],
        "field_lastname":raw_data["Apellidos"],
        "field_email":raw_data["Correo"],
        "field_numero":raw_data["Celular"],
        "field_time":parse_local_time(raw_data["Time"], raw_data["Date"])
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
                if item["field_numero"] == self.value_data["field_numero"]:
                    user_state["user_notification"].remove(item)
                        
        with open('./user_state.json', mode="w") as dw:
            dw.write(json.dumps(user_state, indent = 4))                     
            return True 

    def add_user(self) -> bool:
        with open('./user_state.json', mode='r+') as d:
            user_state = json.load(d)
            user_state_data = {
                "field_name":self.value_data["field_name"],
                "field_lastname":self.value_data["field_lastname"],
                "field_numero":self.value_data["field_numero"],
                "field_email":self.value_data["field_email"],
                "field_time":self.value_data["field_time"]
            }
            user_state["user_notification"].append(user_state_data)
            d.seek(0)
            json.dump(user_state, d, indent = 4)
        return True 


def help_secondary(value_data):
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
        acces_token=(reader()['FACEBOOK_ACCESS_TOKEN']+"4"),
        phone=value_data["field_numero"]
    )
    print(sender.template(template))  
    return None

def help_primary(value_data):
    #url = "https://hook.us1.make.com/ekirtpo39os96b5dsjgosp3nx1di1e5b"
    #print(requests.post(url, raw_data).text)
    template_popup = {
        "name": "send_notification_popup",
        "language": {"code": "es"},
        "components": [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": "Masami"}],
            }
        ],
    }

    sender = SendMessage(
        id_whats=str(reader()['ID_WHATSAPP']),
        acces_token=(reader()['FACEBOOK_ACCESS_TOKEN']),
        phone=value_data["field_numero"]
    )
    print(sender.template(template_popup) )
    return None

def help_triaje(value_data):
    text = "Gracias por completar el *triaje online*🙌\nNuestros especialistas analizarán su caso y estaremos en contacto de 2 a 3 días hábiles 😉"
    sender = SendMessage(
        id_whats=str(reader()['ID_WHATSAPP']),
        acces_token=(reader()['FACEBOOK_ACCESS_TOKEN']),
        phone=value_data["field_numero"]
    )
    print(sender.message_text(text))
    return None

def dead_line()-> bool:
    phone_dict = {}
    with open("user_state.json",'r+') as d:
        data = json.load(d)["user_notification"]
        for item in data:
            t = item["field_time"]
            res = datetime.strptime(t,"%Y-%m-%d %H:%M:%S")- datetime.now()
            if  res.total_seconds()/60 <= 0 :
                phone_dict[f"{item['field_name']} {item['field_lastname']}"] = item["field_numero"]
                data.remove(item)
            
    with open('./user_state.json', mode="w") as dw:
        dw.write(json.dumps(data, indent = 4))                     
            

    for key,val in phone_dict.items():
   
        text = f"{key}! vimos que aún no completaste el triaje online😥\nAquí te dejamos el link 👇\nhttps://idt.digitaliatec.com/triage-online\nTe esperamos!🤗"
        sender = SendMessage(
            id_whats=str(reader()['ID_WHATSAPP']),
            acces_token=(reader()['FACEBOOK_ACCESS_TOKEN']),
            phone=val
        )
        print(sender.message_text(text) )
 
    return None

import requests

class SendMessage:
    def __init__(self,phone:str,id_whats:str ,acces_token: str) -> None:
        self.head = {
            "Authorization":f"Bearer {acces_token}"
        }
        self.url = f"https://graph.facebook.com/v14.0/{id_whats}/messages/"
        self.phone = phone


    def template(self,json_components: dict):
        json_template = {
            "messaging_product": "whatsapp",
            "to": f"51{self.phone}",
            "type": "template",
            "template": json_components
        }
        return requests.post(self.url, headers=self.head, json=json_template).json()
    

    

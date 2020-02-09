from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from requests import get
from os import system
from bs4 import BeautifulSoup
from random import randint
import os,sys,time

lore = ''
res = []
dados = []
stage = 0
stage_lol = 0
incoming_msg = ''
messages_pre = ''
fileDir = os.path.dirname(os.path.abspath(__file__))


class lol_quiz():

    random_list = [] 

    def __init__(self):
        global stage_lol
        stage_lol +=1

    def Atualizar(self):
        check= 1
        print("Buscando por atualizações...")
        request = get(f"https://br.op.gg/champion/statistics")
        champions = BeautifulSoup(request.text,"html.parser").find_all(class_="champion-index__champion-item__name")
        for champion in champions:
            try:
                open(f"champions/{champion.get_text()}.txt")
                if "" ==  open(f"champions/{champion.get_text()}.txt").read() :
                    print(f"Ih ta sem nada :{champion.get_text()} ")
                    raise 
            except:
            
                if check==0:
                    print(f"Atualização Encontrada")
                    check=1
                print(f"Inserindo : {champion.get_text()}")
                with open(f"{fileDir}/champions/{champion.get_text()}.txt","w") as file:
                   
                    file.write(self._Atualizar_Campeao(champion.get_text()))
                    file.close()
        if(check==1 and champion==champions[-1]):
            print("Atualização Finalizada")
        elif (champion==champions[-1]):
            print("Tudo Ok, Nada para atualizar")



    def _Atualizar_Campeao(self,champion_row):

        driver= webdriver.Firefox()

        if(champion_row=="Wukong"):
            champion_link="monkeyking" 
        elif champion_row=="Nunu & Willump":
            champion_link ="nunu" 
            champion_row ="nunu"
        else:
            champion_link  = champion_row.lower().replace(".","").replace("'","").replace(" ","")

        driver.get(f"https://universe.leagueoflegends.com/pt_BR/story/champion/{champion_link}/")
        driver.execute_script("window.scrollBy(0,800)")
        texto = driver.find_element_by_id("CatchElement").text
        driver.quit()
        texto = texto.replace("’","'").replace(champion_row,"*Campeão Secreto*")

        return texto

    def iniciar(self):
        global stage,stage_lol,dados
        dados = self._Gerar_Champ()
        print(f"Campeão: {dados[0]}")
        stage_lol=1
        stage="lol"
        return f"Bem Vindo ao Quiz League Of Legends \n\n Tentativas Restantes:{6-stage_lol} \n\n As posições em que o campeão joga são(é):\n {dados[1]}"

    def _Gerar_Champ(self):
        request = get(f"https://br.op.gg/champion/statistics")
        champions = BeautifulSoup(request.text,"html.parser").find_all(class_="champion-index__champion-item__name")
        champion_name = champions[randint(0,len(champions)-1)]
        champion_lane = champion_name.find_next_sibling().get_text()
        return [champion_name.get_text(),champion_lane]


    def Repostas_LOL(self,mes_com):
        global stage,stage_lol,res,lore
        frase = ""
       
        if(stage_lol==2):
            lore = open(f"{fileDir}/champions/{dados[0]}.txt").read()
            res = [i for i in range(len(lore)) if lore.startswith(".", i)]

        if(len(res)-1==len(self.random_list)):
            stage = 0
            return "As dicas acabaram desculpe, iremos começar novamente"
           
        
        while len(frase)<3:
            random_num = randint(0,len(res)-2)
            if random_num in self.random_list:
                continue
            frase = lore[res[random_num]+1:res[random_num+1]+1]

        if mes_com.lower()==dados[0].lower():
            stage = 0
            return f"Parabens Você Acertou!!"
        elif(stage_lol==6):
            stage = 0
            return f"Você Perdeu as Tentativas Acabaram"

        
        self.random_list.append(random_num)
        return f"Tentativas Restantes:{6-stage_lol} \n\n Eis uma frase de sua lore: {frase}"


def frase_gerador():
    count = randint(1,9656)
    count_id = randint(0,19)
    request = get(f"https://www.pensador.com/frases/{count}/")
    quotes_all = BeautifulSoup(request.text,"html.parser")
    quotes_fr = quotes_all.find_all(class_="frase")[count_id].get_text()
    quotes_author = quotes_all.find_all(class_="frase")[count_id].find_next_sibling().get_text()
    return(f"{quotes_fr} - {quotes_author}") 


SECRET_KEY = 'My secret key'
app = Flask(__name__)
app.config.from_object(__name__)

callers = {
    "+559991184567": "Italo",
    "+12349013030": "Finn",
    "+12348134522": "Chewy",
}

command_select=0
@app.route("/", methods=['GET', 'POST'])
def hello():
    global stage

    
    message_command = request.values.get('Body')
    print(message_command)
    system("pause")
    if(stage==0):
        if "lol quiz" in message_command.lower():
            message = lol_quiz().iniciar()
        elif "lol atualizar" in message_command.lower():
            lol_quiz().Atualizar()

    elif(stage=="lol"):
        message = lol_quiz().Repostas_LOL(message_command.lower())
        
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
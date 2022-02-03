import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from time import sleep
import argparse
from random import shuffle


STATE_ONE = "Slaganje ekipe"
STATE_TWO = "Dijeljenje karata"
STATE_THREE = "Odredivanje aduta"
STATE_FOUR = "Igranje ruke"
STATE_FIVE = "Bodovanje i rezultat"
STATE_SIX = "Kraj igre"


bojeKarte = ["H","T","K","P"]
vrijednostKarte = ["7","8","9","X","D","B","K","A"]
sveKarte = ['HD', 'HB', 'HK', 'H8', 'HA', 'H7', 'HX', 'H9', 'KD', 'KB', 'KK', 'K8', 'KA', 'K7', 'KX', 'K9', 
            'PD', 'PB', 'PK', 'P8', 'PA', 'P7', 'PX', 'P9', 'TD', 'TB', 'TK', 'T8', 'TA', 'T7', 'TX', 'T9']
bodoviAdut = {'D': 20, '9': 14, 'A': 11, 'X': 10, 'K': 4, 'B': 3, '8': 0, '7': 0}
bodoviOstali = {'A': 11, 'X': 10, 'K': 4, 'B': 3, 'D': 2, '9': 0, '8': 0, '7': 0}
vrijednostAdutLista = ["7","8","B","K","X","A","9","D"]
vrijednostOstaliLista = ["7","8","9","D","B","K","X","A"]

class Karte:
    def __init__(self, boja, karte, adut):
        self.boja = boja
        self.sveKarteLista = karte
        self.adut = adut
        self.imaKarata = False
        if(len(karte) > 0):
            self.imaKarata = True
    def sortirajKarte(self, bodoviDict):
        self.sveKarteLista = sorted(self.sveKarteLista, key = lambda ele: bodoviDict[ele])
    def azurirajStanjePrvaKarta(self, stanje):
        self.prvaRukaBodovi = dict(stanje)
    def vratiPrvuKartu(self):
        if(self.imaKarata):
            self.kartePrva = sorted(self.sveKarteLista, key = lambda ele: self.prvaRukaBodovi[ele], reverse=True)
            karta = self.kartePrva[0]
            bodovi = self.prvaRukaBodovi.get(karta)
            return [karta,bodovi]
        else:
            return None
    def vratiSveKarte(self):
        return self.sveKarteLista
    def imaKarataIzBoje(self):
        return self.imaKarata
    def makniIzRuke(self,karta):
        self.sveKarteLista.remove(karta)
        if(len(self.sveKarteLista) == 0):
            self.imaKarata = False
    def vratiJacuKartu(self,karta):
        if(self.adut):
            indexKarte = vrijednostAdutLista.index(karta)
            for kartaURuci in self.sveKarteLista:
                indexVlastiteKarte = vrijednostAdutLista.index(kartaURuci)
                if indexVlastiteKarte > indexKarte:
                    return self.boja+kartaURuci
            return None
        else:
            indexKarte = vrijednostOstaliLista.index(karta)
            for kartaURuci in self.sveKarteLista:
                indexVlastiteKarte = vrijednostOstaliLista.index(kartaURuci)
                if indexVlastiteKarte > indexKarte:
                    return self.boja+kartaURuci
            return None
    def vratiNajslabijuKartu(self):
        if(self.imaKarata):
            return self.boja+self.sveKarteLista[0]
        else:
            return None
        
        

class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()

class StateOne(State):   #slaganje ekipe
    async def run(self):
        id_organizator = "primatelj@rec.foi.hr"
        msg = Message(
            to=id_organizator,
            body=f"{self.agent.jid}",
            metadata={
                "performative": "inform",
                "ontology": "bela",
                "intent": "registriraj"}
        )
        await self.send(msg)
        print("Čekam poruku sa popisom svih igrača...")

        msg = await self.receive(timeout=100)
        if(msg.get_metadata("ontology") == "bela" and msg.get_metadata("intent") == "igraci"):
            global igraciList
            global igracListIndex
            global suigracID
            global sljedeciIgracID
            igraciList = eval(msg.body)
            igracListIndex = igraciList.index(f"{self.agent.jid}")
            if(igracListIndex == 1):
                suigracID = igraciList[3]
                sljedeciIgracID = igraciList[0]
            elif(igracListIndex == 2):
                suigracID = igraciList[4]
                sljedeciIgracID = igraciList[3]
            elif(igracListIndex == 3):
                suigracID = igraciList[1]
                sljedeciIgracID = igraciList[4]
            elif(igracListIndex == 4):
                suigracID = igraciList[2]
                sljedeciIgracID = igraciList[1]
            sleep(3) 
        self.set_next_state(STATE_TWO)

class StateTwo(State):   #djeljenje karata
    async def run(self):
        
        if(str(self.agent.jid) == igraciList[1]):
            sleep(1)
            print("Zapocinjem djeljenje karata")
            dijeljeneKarte = sveKarte
            shuffle(dijeljeneKarte)
            brojac = 0
            for igracIndex in range(1,5): #unutar igraciList nulti je organizator
                msg = Message(
                    to=igraciList[igracIndex],
                    body=str(dijeljeneKarte[brojac:brojac+8]),
                    metadata={
                        "performative": "inform",
                        "ontology": "bela",
                        "intent": "karteIgraca"}
                )
                await self.send(msg)
                brojac += 8
        msg = await self.receive(timeout=100)
        if(msg.get_metadata("ontology") == "bela" and msg.get_metadata("intent") == "karteIgraca"):
            global karteIgraca
            global karteIgracaAdut
            global karteIgracaOstale
            karteIgraca = eval(msg.body)
            print(f"Karte igraca {self.agent.jid} su {karteIgraca}")
            self.set_next_state(STATE_THREE)
        

class StateThree(State):  #odabir aduta
    async def run(self):
        zadnjiIgrac = False
        global odabraniAdut
        if(str(self.agent.jid) == igraciList[2]): #drugi agent prvi odabire adut
            sleep(1)
            print("Zapocinjem sa odabirom aduta")
            odabraniAdut = self.odaberiAdut(zadnjiIgrac)
            msg = Message(
                to=igraciList[3],
                body=f"{[odabraniAdut,str(self.agent.jid)]}",
                metadata={
                    "performative": "inform",
                    "ontology": "bela",
                    "intent": "adut"}
            )
            await self.send(msg)
        else:
            msg = await self.receive(timeout=100)
            if(msg.get_metadata("ontology") == "bela" and msg.get_metadata("intent") == "adut"):
                poruka = eval(msg.body)
                if(poruka[0] == "nema-aduta"):
                    if(str(self.agent.jid) == igraciList[1]):
                        zadnjiIgrac = True
                    odabraniAdut = self.odaberiAdut(zadnjiIgrac)
                else:
                    odabraniAdut = poruka[0]

            msg = Message(
                to=sljedeciIgracID,
                body=f"{[odabraniAdut,str(self.agent.jid)]}",
                metadata={
                    "performative": "inform",
                    "ontology": "bela",
                    "intent": "adut"}
            )
            await self.send(msg)
            
        msg = await self.receive(timeout=100)
        if(msg.get_metadata("ontology") == "bela" and msg.get_metadata("intent") == "adut-final"):
            odabraniAdut = msg.body
            print(f"Na kraju je odabran adut {odabraniAdut}")

        global brojacRuku
        brojacRuku = 0
        self.set_next_state(STATE_FOUR)

    def odaberiAdut(self,zadnjiIgrac): #metoda za odabir aduta
        vrijednostiBojeAdut = {'K': 0, 'T': 0, 'H': 0, 'P': 0}
        vrijednostiBojeOstali = {'K': 0, 'T': 0, 'H': 0, 'P': 0}
        for karta in karteIgraca:
            boja = karta[:1]
            vrijednost = karta[1]
            vrijednostiBojeAdut[boja] += int(bodoviAdut[vrijednost])
            vrijednostiBojeOstali[boja] += int(bodoviOstali[vrijednost])
        vrijednostiBojeAdut = sorted(vrijednostiBojeAdut.items(), key=lambda x:x[1]) #sortirani elementi prvi je najmanji
        if(zadnjiIgrac): #odabir aduta na muss
            print(f"Agent {self.agent.jid} je odabrao adut {vrijednostiBojeAdut[3][0]}") #vidjeti je li [3][0] ili [3][1]
            return vrijednostiBojeAdut[3][0]  #vracamo samo boju sa najvecim bodovima
        elif(vrijednostiBojeAdut[3][1] > 30): #ako su dobri bodovi u adutu za igraca
            print(f"Agent {self.agent.jid} je odabrao adut {vrijednostiBojeAdut[3][0]}")
            return vrijednostiBojeAdut[3][0]
        else:
            print(f"Agent {self.agent.jid} nije odabrao adut")
            return "nema-aduta"
                

class StateFour(State):   #igranje ruke
    async def run(self):
        sleep(1)
        global brojacRuku
        igraneKarte = []
        if(brojacRuku == 0):    #potrebno pozvati samo na pocetku
            self.soritrajKarte()

        print("Sve karte u ruci na pocetku igranja")
        print(f"Karo karte: {self.karoKarte.sveKarteLista}")
        print(f"Herc karte: {self.hercKarte.sveKarteLista}")
        print(f"Pik karte:  {self.pikKarte.sveKarteLista}")
        print(f"Tref karte: {self.trefKarte.sveKarteLista}")
        print()
        
        if(brojacRuku < 8):


            if(str(self.agent.jid) == igraciList[2]):
                karta = self.odigrajPrvuKartu()
                print(f"Agent odabrao kartu {karta}")
                msg = Message(
                    to=sljedeciIgracID,
                    body=f"['{karta}']",
                    metadata={
                        "performative": "inform",
                        "ontology": "bela",
                        "intent": "igranje-karta"}
                )
                await self.send(msg)
                
                while True:
                    msg = await self.receive(timeout=1000)
                    print(msg.body)
                    if(msg.get_metadata("ontology") == "bela" and msg.get_metadata("intent") == "igranje-karta-nastavak"):
                        break
                    
            else:
                msg = await self.receive(timeout=1000)
                if(msg.get_metadata("ontology") == "bela" and msg.get_metadata("intent") == "igranje-karta"):
                    igraneKarte = eval(msg.body)
                    print(f"Do sada igrane karte: {igraneKarte}")
                    karta = self.odigrajKartu(igraneKarte)
                    print(f"Agent odabrao kartu {karta}")
                    igraneKarte.append(karta)
                    
                    msg = Message(
                    to=sljedeciIgracID,
                    body=f"{igraneKarte}",
                    metadata={
                        "performative": "inform",
                        "ontology": "bela",
                        "intent": "igranje-karta"}
                    )
                    await self.send(msg)

            brojacRuku += 1
            self.set_next_state(STATE_FOUR)
        else:
            self.set_next_state(STATE_FIVE)
    
    def odigrajKartu(self, odigraneKarte):
        zadnjaKartaVrijednost = odigraneKarte[-1][1]
        zadnjaKartaBoja = odigraneKarte[-1][:1]

        for karteBoje in self.sveKarteURuci:
            if(karteBoje.boja == zadnjaKartaBoja):
                odigranaBoja = karteBoje
        
        karta = odigranaBoja.vratiJacuKartu(zadnjaKartaVrijednost)
        if(karta != None):
            odigranaBoja.makniIzRuke(karta[1])
            return karta
        karta = odigranaBoja.vratiNajslabijuKartu()
        if(karta != None):
            odigranaBoja.makniIzRuke(karta[1])
            return karta
        karta = self.karteAdut.vratiNajslabijuKartu()
        if(karta != None):
            self.karteAdut.makniIzRuke(karta[1])
            return karta
        ostaleBoje = self.sveKarteURuciOstale

        for ostalaBoja in ostaleBoje:
            karta = ostalaBoja.vratiNajslabijuKartu()
            if(karta != None):
                ostalaBoja.makniIzRuke(karta[1])
                return karta

    def odigrajPrvuKartu(self):
        kartaAdut = []
        if(self.karteAdut.imaKarata):
            kartaAdut = self.karteAdut.vratiPrvuKartu()
        else:
            kartaAdut = ["",0]

        kartaOstalo = ["", 0]
        for karteBoja in self.sveKarteURuciOstale:
            if(karteBoja.imaKarata == True):
                kartaOstaloTemp = karteBoja.vratiPrvuKartu()
            else:
                kartaOstaloTemp = ["",0]
            if(kartaOstaloTemp[1] > kartaOstalo[1]):
                kartaOstalo[0] = kartaOstaloTemp[0]
                kartaOstalo[1] = kartaOstaloTemp[1]
                bojaOstalo = karteBoja.boja
                karteBojaKlasa = karteBoja
        if(kartaAdut[1] > kartaOstalo[1]):
            self.karteAdut.makniIzRuke(kartaAdut[0])
            return str(f"{self.karteAdut.boja}" + f"{kartaAdut[0]}")
        else:
            karteBojaKlasa.makniIzRuke(kartaOstalo[0])
            return str(f"{bojaOstalo}" + f"{kartaOstalo[0]}")

    def soritrajKarte(self):
        self.karteKaro = []
        self.karteHerc = []
        self.kartePik = []
        self.karteTref = []
        for karta in karteIgraca:
            boja = karta[:1]
            if(boja == "K"):
                self.karteKaro.append(karta[1])
            elif(boja == "H"):
                self.karteHerc.append(karta[1])
            elif(boja == "P"):
                self.kartePik.append(karta[1])
            elif(boja == "T"):
                self.karteTref.append(karta[1])
        
        self.bodoviIgranjeAdut = {'7': 90, '8': 90, 'B': 80, 'K': 70, 'X': 60, 'A': 30, '9': 20, 'D': 150}
        self.bodoviIgranjeOstali = {'7': 70, '8': 60, '9': 50, 'D': 40, 'B': 30, 'K': 20, 'X': 10, 'A': 100}

        bodoviAdutSort = {'7': 0, '8': 1, 'B': 2, 'K': 3, 'X': 4, 'A': 5, '9': 6, 'D': 7}
        bodoviOstaliSort = {'7': 0, '8': 1, '9': 2, 'D': 3, 'B': 4, 'K': 5, 'X': 6, 'A': 7}

        self.karoKarte = Karte("K",self.karteKaro,"K" == odabraniAdut)
        self.hercKarte = Karte("H",self.karteHerc,"H" == odabraniAdut)
        self.pikKarte = Karte("P",self.kartePik,"P" == odabraniAdut)
        self.trefKarte = Karte("T",self.karteTref,"T" == odabraniAdut)
        
        self.sveKarteURuci = [self.karoKarte,self.hercKarte,self.pikKarte,self.trefKarte]
        self.sveKarteURuciOstale = []

        for karteBoja in self.sveKarteURuci:
            if karteBoja.adut:
                karteBoja.sortirajKarte(bodoviAdutSort)
                karteBoja.azurirajStanjePrvaKarta(self.bodoviIgranjeAdut)
                self.karteAdut = karteBoja
            else:
                karteBoja.sortirajKarte(bodoviOstaliSort)
                karteBoja.azurirajStanjePrvaKarta(self.bodoviIgranjeOstali)
                self.sveKarteURuciOstale.append(karteBoja)

class StateFive(State):    #Bodovanje i rezultat
    async def run(self):
        msg = await self.receive(timeout=1000)
        if(msg.get_metadata("ontology") == "bela" and msg.get_metadata("intent") == "stanje-igre"):
            if(msg.body == "nova-igra"):
                print("Nastavljamo sa novim krugom igranja")
                print("")
                self.set_next_state(STATE_TWO)
            if(msg.body == "gotova-igra"):
                self.set_next_state(STATE_SIX)

class StateSix(State):    #Kraj igre
    async def run(self):
        print("Zahvaljujem na igranju :D")

class Igrac(Agent):
    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_THREE, state=StateThree())
        fsm.add_state(name=STATE_FOUR, state=StateFour())
        fsm.add_state(name=STATE_FIVE, state=StateFive())
        fsm.add_state(name=STATE_SIX, state=StateSix())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_FOUR)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_FOUR)
        fsm.add_transition(source=STATE_FOUR, dest=STATE_FIVE)
        fsm.add_transition(source=STATE_FIVE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_FIVE, dest=STATE_SIX)
        self.add_behaviour(fsm)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-jid", type=str, help="JID agenta", default="posiljatelj@rec.foi.hr")
    parser.add_argument("-pwd", type=str, help="Lozinka agenta", default="tajna")
    #parser.add_argument("-jid", type=str, help="JID agenta", default="brajic@rec.foi.hr")
    #parser.add_argument("-pwd", type=str, help="Lozinka agenta", default="lozinka")
    #parser.add_argument("-jid", type=str, help="JID agenta", default="ime@rec.foi.hr")
    #parser.add_argument("-pwd", type=str, help="Lozinka agenta", default="lozinka")
    args = parser.parse_args()

    fsmagent = Igrac(args.jid, args.pwd)
    future = fsmagent.start()
    future.result()
    
    while fsmagent.is_alive():
        try:
            sleep(1)
        except KeyboardInterrupt:
            print("Agent je prekinut")
            fsmagent.stop()
            break
    spade.quit_spade()

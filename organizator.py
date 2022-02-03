import spade
from spade.agent import Agent
from spade.behaviour import TimeoutBehaviour, CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from time import sleep

vrijednostAdutLista = ["7","8","B","K","X","A","9","D"]
vrijednostOstaliLista = ["7","8","9","D","B","K","X","A"]
bodoviAdut = {'D': 20, '9': 14, 'A': 11, 'X': 10, 'K': 4, 'B': 3, '8': 0, '7': 0}
bodoviOstali = {'A': 11, 'X': 10, 'K': 4, 'B': 3, 'D': 2, '9': 0, '8': 0, '7': 0}

class Primatelj(Agent):
    class PorukeBelaRegistracija(CyclicBehaviour):
        async def run(self):
            
            msg = await self.receive(timeout=100)
            if msg:
                self.agent.igraci.append(msg.body)
                print(f"Igrač {msg.body} je registriran za igru")
                self.agent.br_igraca += 1
                print(f"Trenutno je {self.agent.br_igraca} igrač/a u igri")

                if self.agent.br_igraca == 4:
                    print("Sakupljeno je dovoljno igrača, započinjem igru...")
                    #igraciDict = {'organizator': f"{self.agent.jid}", 'igrac1': f"{self.agent.igraci[0]}", 'igrac2': f"{self.agent.igraci[1]}", 'igrac3': f"{self.agent.igraci[2]}", 'igrac4': f"{self.agent.igraci[3]}"}
                    #igraciDictStr = str(igraciDict)
                    #igraciList = [f"{self.agent.jid}", f"{self.agent.igraci[0]}", f"{self.agent.igraci[1]}", "treci@foi.rec.hr", "cetvrti@foi.rec.hr"]
                    #igraciListStr = str(igraciList)
                    self.agent.tim1 = [self.agent.igraci[0],self.agent.igraci[2]]
                    self.agent.tim2 = [self.agent.igraci[1],self.agent.igraci[3]]
                    self.igraciList = [f"{self.agent.jid}", f"{self.agent.igraci[0]}", f"{self.agent.igraci[1]}", f"{self.agent.igraci[2]}", f"{self.agent.igraci[3]}"]
                    for igrac_id in self.agent.igraci:
                        msg = Message(
                            to=igrac_id,
                            body=str(self.igraciList),
                            metadata={
                                "performative": "inform",
                                "ontology": "bela",
                                "intent": "igraci"}
                        )
                        await self.send(msg)

    class OdredivanjeAduta(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=100)
            if msg:
                sleep(1)
                poruka = eval(msg.body)
                self.agent.adut = poruka
                print(f"Organizator primio adut vrijednosti {poruka[0]} od igraca {poruka[1]}")
                for igrac_id in self.agent.igraci:
                    msg = Message(
                        to=igrac_id,
                        body=f"{poruka[0]}",
                        metadata={
                            "performative": "inform",
                            "ontology": "bela",
                            "intent": "adut-final"}
                    )
                    await self.send(msg)
                
    class PracenjeIgre(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=100)
            if msg:
                odigraneKarte = eval(msg.body)
                print(f"Primljene su karte {odigraneKarte}")
                self.agent.brojRuku += 1 
                adut = self.agent.adut[0]
                bodoviRuke = 0
                
                najjacaKarta = odigraneKarte[0]
                if(najjacaKarta[:1] == adut):
                    indexNajKarta = vrijednostAdutLista.index(najjacaKarta[1])
                else:
                    indexNajKarta = vrijednostOstaliLista.index(najjacaKarta[1])
                
                for karta in odigraneKarte:
                    if(karta[:1] == adut):
                        indexKarta = vrijednostAdutLista.index(karta[1])
                        bodoviRuke += bodoviAdut[karta[1]]
                    else:
                        indexKarta = vrijednostOstaliLista.index(karta[1])
                        bodoviRuke += bodoviOstali[karta[1]]
                    if indexNajKarta < indexKarta:
                        if (karta[:1] == adut and najjacaKarta[:1] == adut) or (karta[:1] == adut and najjacaKarta[:1] != adut):
                            najjacaKarta = karta
                            indexNajKarta = indexKarta
                
                if(najjacaKarta == odigraneKarte[1] or najjacaKarta == odigraneKarte[3]):
                    self.agent.bodoviTim[0] += bodoviRuke
                    if(self.agent.brojRuku == 8):
                        self.agent.bodoviTim[0] += 10
                else:
                    self.agent.bodoviTim[1] += bodoviRuke
                    if(self.agent.brojRuku == 8):
                        self.agent.bodoviTim[1] += 10
                msg = Message(
                    to=self.agent.igraci[1],
                    body="test",
                    metadata={
                    "performative": "inform",
                    "ontology": "bela",
                    "intent": "igranje-karta-nastavak"}
                )
                await self.send(msg)
                if(self.agent.brojRuku == 8):
                    adutPozivatelj = self.agent.adut[1]
                    self.agent.brojRuku = 0

                    if(adutPozivatelj == self.agent.igraci[0] or adutPozivatelj == self.agent.igraci[2]):
                        if(self.agent.bodoviTim[0] > 81):
                            self.agent.ukupanRezultat[0] += self.agent.bodoviTim[0]
                        else:
                            self.agent.ukupanRezultat[1] += 162
                    else:
                        if(self.agent.bodoviTim[1] > 81):
                            self.agent.ukupanRezultat[1] += self.agent.bodoviTim[0]
                        else:
                            self.agent.ukupanRezultat[0] += 162
                    print(f"Ukupan rezultat: {self.agent.ukupanRezultat}")

                    poruka = "nova-igra"
                    if(self.agent.ukupanRezultat[0] > 200):
                        print("Pobijedio je tim 1, čestitamo")
                        poruka="gotova-igra"
                    if(self.agent.ukupanRezultat[1] > 200):
                        print("Pobijedio je tim 2, čestitamo")
                        poruka="gotova-igra"
                    sleep(3)

                    print(f"Saljem nastavak igre sa porukom {poruka}")
                    for igrac_id in self.agent.igraci:
                        msg = Message(
                            to=igrac_id,
                            body=poruka,
                            metadata={
                                "performative": "inform",
                                "ontology": "bela",
                                "intent": "stanje-igre"}
                        )
                        await self.send(msg)


    async def setup(self):
        self.br_igraca = 0
        self.igraci = []
        self.bodoviTim = [0,0]
        self.brojRuku = 0
        self.adut = []
        self.ukupanRezultat = [0,0]

        registracijaTemplate = spade.template.Template(
            metadata={"ontology": "bela", "intent": "registriraj"}
        )
        adutTemplate = spade.template.Template(
            metadata={"ontology": "bela", "intent": "adut"}
        )
        igraKarteTemplate = spade.template.Template(
            metadata={"ontology": "bela", "intent": "igranje-karta"}
        )
        ponasanjeKP = self.PorukeBelaRegistracija()
        self.add_behaviour(ponasanjeKP, registracijaTemplate)
        adutPonasanje = self.OdredivanjeAduta()
        kartePonasanje = self.PracenjeIgre()
        self.add_behaviour(kartePonasanje, igraKarteTemplate)
        self.add_behaviour(adutPonasanje, adutTemplate)
        print("Organizator uspješno pokrenut, čekam poruke")


if __name__ == '__main__':
    primatelj = Primatelj("primatelj@rec.foi.hr", "tajna")
    future = primatelj.start()
    future.result()

    while primatelj.is_alive():
        try:
            sleep(1)
        except KeyboardInterrupt:
            print(" Agent je prekinut")
            primatelj.stop()
            break
    spade.quit_spade()

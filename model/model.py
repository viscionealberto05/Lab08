from database.impianto_DAO import ImpiantoDAO
from database.consumo_DAO  import ConsumoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None   #la lista degli impianti viene inizializzata vuota e riempita con load_impianti()
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """

        #Uso una query SQL per leggere gli impianti, la classe DTO associata mi permette di creare l'oggetto impianto

        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """

        lista_tuple = []

        #Per ciascun impianto vado a vedere i consumi all'interno del mese selezionato dall'utente
        #aggiorno un contatore per i giorni così da poter calcolare la media alla fine,
        #concludo restituendo una lista con le tuple, che saranno una per ciascun impianto,
        #legate al consumo medio mensile dello stesso

        for impianto in self._impianti:
            somma_consumi = 0
            self.consumi_impianto = ConsumoDAO.get_consumi(impianto.id)
            counter_giorni = 0
            for consumo in self.consumi_impianto:
                #counter_giorni = 0
                if consumo.data.month == mese:
                    counter_giorni += 1
                    somma_consumi += int(consumo.kwh)
                else:
                    somma_consumi = somma_consumi
                    counter_giorni += 0

            tupla = (impianto.nome, somma_consumi/counter_giorni)
            lista_tuple.append(tupla)

        return lista_tuple


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """

        """Mediante un algoritmo ricorsivo vado prima a definire la condizione di escape che mi permette di uscire
        che in questo caso dipende dal giorno della settimana, oltre il settimo mi fermo.
        
        finchè mi trovo nella prima settimana vado a leggere per entrambi gli impianti i consumi e aggiornare
        il costo corrente, aggiungo solo alla fine l'id dell'impianto col consumo minore perchè prima verifico
        se è necessario sommare il costo di trasferimento da un impianto all'altro. Per effettuare questo controllo mi 
        serve la sequenza parziale ricevuta dalla chiamata precedente, altrimenti non sommerei mai 5.
        
        Dopo aver effettuato la verifica aggiorno la sequenza parziale, incremento il giorno (siccome la funz. ricorsiva
        opera sui singoli giorni) e poi richiamo la ricorsione"""

        if giorno > 7:
            self.__costo_ottimo = costo_corrente
            self.__sequenza_ottima = sequenza_parziale

        else:
            id_primo_impianto = self._impianti[0].id
            id_secondo_impianto = self._impianti[1].id

            consumi_primo_impianto = consumi_settimana[id_primo_impianto][giorno-1]
            consumi_secondo_impianto = consumi_settimana[id_secondo_impianto][giorno-1]

            if consumi_primo_impianto < consumi_secondo_impianto:
                costo_corrente += consumi_primo_impianto
                #sequenza_parziale.append(id_primo_impianto)
                imp_nuovo = id_primo_impianto
                ultimo_impianto = id_primo_impianto
            else:
                costo_corrente += consumi_secondo_impianto
                #sequenza_parziale.append(id_secondo_impianto)
                imp_nuovo = id_secondo_impianto
                ultimo_impianto = id_secondo_impianto

            if len(sequenza_parziale) > 0:
                if ultimo_impianto != sequenza_parziale[-1]:
                    costo_corrente += 5

            sequenza_parziale.append(imp_nuovo)

            giorno += 1

            self.__ricorsione(sequenza_parziale,giorno,ultimo_impianto,costo_corrente,consumi_settimana)


    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """

        consumi_settimana = {}

        for impianto in self._impianti:
            consumi = ConsumoDAO.get_consumi(impianto.id)
            valori_prima_settimana = []

            for consumo in consumi:
                if consumo.data.month == mese and consumo.data.day in range(1,8):

                    valori_prima_settimana.append(consumo.kwh)
                    consumi_settimana[impianto.id] = valori_prima_settimana

        return consumi_settimana


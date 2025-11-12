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
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """

        lista_tuple = []

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
        # TODO

        if giorno > 7 :
            self.__costo_ottimo = costo_corrente
            self.__sequenza_ottima = list (sequenza_parziale)

        else :
            id_impianto1 = self._impianti[0].id
            id_impianto2 = self._impianti[1].id

            #Prendo i consumi in KW dal dizionario per i consumi settimanali
            #Accedendo al valore specificando prima chiave del dizionario (id_impianto) e poi
            #indice per prendere il giorno sulla lista associata alla chiave

            consumo_impianto1 = consumi_settimana [id_impianto1] [giorno-1]
            consumo_impianto2 = consumi_settimana [id_impianto2] [giorno-1]

            if consumo_impianto1 <= consumo_impianto2 :
                id_scelto = id_impianto2
                consumo_scelto = consumo_impianto1
            else :
                id_scelto = id_impianto1
                consumo_scelto = consumo_impianto2

            costo_corrente += consumo_scelto

            if ultimo_impianto is not None and ultimo_impianto != id_scelto :
                costo_corrente += (consumo_scelto + 5)

            sequenza_parziale.append (id_scelto)
            ultimo_impianto = id_scelto
            giorno += 1

            self.__ricorsione (sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana)



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


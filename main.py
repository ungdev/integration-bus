from pulp import LpProblem, LpMinimize, LpInteger, LpVariable, LpStatus
import csv
from pydantic import BaseModel

class Participant(BaseModel):
    # Input Data
    id: int
    prenom: str
    nom: str
    mail: str
    telephone: str
    nouveau: bool
    ce: bool
    num_equipe: int | None = None
    benevole: bool
    orga: bool
    majeur: bool
    bus_manual : int | None = None

    # Output Data
    bus_assignment : int | None = None

class Equipe(BaseModel):
    # Input Data
    numero: int
    nom: str
    faction: int

    # Inner Data
    nb_nouveau: int | None = None
    nb_ce: int | None = None
    nb_membre: int | None = None
    nb_manual_assigned: int | None = None
    nb_mineur: int | None = None

    # Output Data
    bus_assignment : int | None = None

class Bus(BaseModel):

    numero: int
    capacite: int

    # Inner Data
    nb_manual_assigned: int | None = None

    # Output Data
    equipe_assignments : list[int] = []

if __name__ == "__main__":

    bus_file = "./data/bus.csv"
    participant_file = "./data/participants.csv"
    equipe_file = "./data/equipes.csv"

    dict_participants : dict[int, Participant] = {}
    dict_bus : dict[int, Bus] = {}
    dict_equipes : dict[int, Equipe] = {}

    nb_ce_par_equipe : dict[int, int] = {}
    nb_nouveau_par_equipe : dict[int, int] = {}
    nb_mineur_par_equipe : dict[int, int] = {}
    nb_manual_par_equipe : dict[int, int] = {}
    nb_manual_par_bus : dict[int, int] = {}

    nb_nouveau : int = 0
    nb_ce : int = 0
    nb_benevole : int = 0
    nb_orga : int = 0
    nb_place_dans_bus : int = 0

    MAX_ECART_FACTION = 2
    MAX_MINEUR_PAR_BUS = 50
    MIN_CE_PAR_BUS = 1


    # ----- Lecture des fichiers -----
    print("Reading Participant File")
    with open(participant_file, newline='', encoding='cp1252') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            id = int(row["id"])
            if id in dict_participants:
                raise Exception(f"Duplicate id {id} in participants.")

            dict_participants[id] = Participant(id=row['id'],
                                            prenom=row['prenom'],
                                            nom=row['nom'],
                                            mail=row['mail'],
                                            telephone=row['telephone'],
                                            nouveau=row['nouveau'],
                                            ce=row['ce'],
                                            num_equipe=row['num_equipe'] if row['num_equipe'] else None,
                                            benevole=row['benevole'],
                                            orga=row['orga'],
                                            majeur=row['majeur'],
                                            bus_manual=row['bus_manual'] if row['bus_manual'] else None)

    print("Reading Bus File"),
    with open(bus_file, newline='', encoding='cp1252') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            numero = int(row["numero"])
            if numero in dict_bus:
                raise Exception(f"Duplicate id {numero} in bus.")

            dict_bus[numero] = Bus(numero=row['numero'],
                                    capacite=row['capacite'])

    print("Reading Equipe File")
    with open(equipe_file, newline='', encoding='cp1252') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            numero = int(row["numero"])
            if numero in dict_equipes:
                raise Exception(f"Duplicate id {numero} in equipes.")

            dict_equipes[numero] = Equipe(numero=row['numero'],
                                            nom=row['nom'],
                                            faction=row['faction'])

    # ----- Résumé des données d'entrée -----
    for bus in dict_bus:
        nb_manual_par_bus[bus] = 0

    for equipe in dict_equipes:
        nb_ce_par_equipe[equipe] = 0
        nb_nouveau_par_equipe[equipe] = 0
        nb_mineur_par_equipe[equipe] = 0
        nb_manual_par_equipe[equipe] = 0

    for participant in dict_participants.values():
        if participant.nouveau:
            nb_nouveau_par_equipe[participant.num_equipe] += 1
            nb_nouveau += 1

        elif participant.ce:
            nb_ce_par_equipe[participant.num_equipe] += 1
            nb_ce += 1

        elif participant.orga:
            nb_orga += 1

        elif participant.benevole:
            nb_benevole += 1

        else:
            raise Exception(f"No role for participant {participant.id}")

        if (not participant.majeur) and participant.num_equipe:
            nb_mineur_par_equipe[participant.num_equipe] += 1

        if participant.bus_manual:
            assert participant.bus_manual in dict_bus.keys()
            nb_manual_par_bus[participant.bus_manual] += 1
            if participant.num_equipe:
                nb_manual_par_equipe[participant.num_equipe] += 1

    for id, equipe in dict_equipes.items():
        equipe.nb_nouveau = nb_nouveau_par_equipe[id]
        equipe.nb_ce = nb_ce_par_equipe[id]
        equipe.nb_mineur = nb_mineur_par_equipe[id]
        equipe.nb_manual_assigned = nb_manual_par_equipe[id]
        equipe.nb_membre = equipe.nb_ce + equipe.nb_nouveau

    for id_bus, bus in dict_bus.items():
        bus.nb_manual_assigned = nb_manual_par_bus[id_bus]
        nb_place_dans_bus += bus.capacite
        if bus.nb_manual_assigned > bus.capacite:
            raise Exception(f"Le nombre de participants fixés dans le bus {id_bus} est supérieur à la capacité du bus : {bus.nb_manual_assigned} > {bus.capacite}")

    print("---- Résumé données ----")
    print("Nb Places total :", nb_place_dans_bus)
    print("Nb Participants :", len(dict_participants))
    print("Nb Nouveaux :", nb_nouveau)
    print("Nb CE :", nb_ce)
    print("Nb Benevole :", nb_benevole)
    print("Nb Orga :", nb_orga)

    # ----- Création du programme linéaire -----

    lp = LpProblem("BUS_WEI", LpMinimize)

    # Variables

    var_bus_equipe = LpVariable.dicts("bus_equipe", [(bus, equipe) for bus in dict_bus
                                        for equipe in dict_equipes], 0, 1, LpInteger)

    # Constraints
    # 1. 1 bus par équipe (on ne divise pas les équipes)
    bus_par_equipe = {}
    for id_equipe in dict_equipes.keys():
        bus_par_equipe[id_equipe] = 0
        for id_bus in dict_bus:
            bus_par_equipe[id_equipe] += var_bus_equipe[id_bus, id_equipe]

        lp += bus_par_equipe[id_equipe] == 1

    # 2. Capacité d'un bus
    participant_dans_bus = {}
    for id_bus, bus in dict_bus.items():
        participant_dans_bus[id_bus] = 0
        for id_equipe, equipe in dict_equipes.items():
            participant_dans_bus[id_bus] += var_bus_equipe[id_bus, id_equipe] * (equipe.nb_membre - equipe.nb_manual_assigned)

        lp += participant_dans_bus[id_bus] <= bus.capacite - bus.nb_manual_assigned

    # 3. Equipe max d'écart par faction
    faction_dans_bus = {}
    for id_bus, bus in dict_bus.items():
        faction_dans_bus[id_bus] = 0
        for id_equipe, equipe in dict_equipes.items():
            faction_dans_bus[id_bus] += var_bus_equipe[id_bus, id_equipe] * equipe.faction

        lp += faction_dans_bus[id_bus] <= MAX_ECART_FACTION
        lp += faction_dans_bus[id_bus] >= -1 * MAX_ECART_FACTION

    # 4. Max mineur par bus
    mineur_dans_bus = {}
    for id_bus, bus in dict_bus.items():
        mineur_dans_bus[id_bus] = 0
        for id_equipe, equipe in dict_equipes.items():
            mineur_dans_bus[id_bus] += var_bus_equipe[id_bus, id_equipe] * equipe.nb_mineur

        lp += mineur_dans_bus[id_bus] <= MAX_MINEUR_PAR_BUS

    # 5. Min CE par bus
    ce_dans_bus = {}
    for id_bus, bus in dict_bus.items():
        ce_dans_bus[id_bus] = 0
        for id_equipe, equipe in dict_equipes.items():
            ce_dans_bus[id_bus] += var_bus_equipe[id_bus, id_equipe] * equipe.nb_ce

        lp += ce_dans_bus[id_bus] >= MIN_CE_PAR_BUS

    # print(lp)
    lp.writeLP('lp.txt')

    status = lp.solve()
    print(LpStatus[status])

    # ----- Récupération des résultats -----

    print("___________________")
    vars = {}
    for var in lp.variables():
        vars[var.name] = var.varValue
        if var.varValue != 0:
            print(var.name, "=", var.varValue)

    places_occupees_par_bus : dict[int, int] = {}
    for id_bus, bus in dict_bus.items():
        places_occupees_par_bus[id_bus] = bus.nb_manual_assigned

    for id_equipe, equipe in dict_equipes.items():
        for id_bus, bus in dict_bus.items():
            if var_bus_equipe[id_bus, id_equipe].varValue != 0:
                equipe.bus_assignment = id_bus
                bus.equipe_assignments.append(id_equipe)
                places_occupees_par_bus[id_bus] += equipe.nb_membre - equipe.nb_manual_assigned

    for id_participant, participant in dict_participants.items():
        if participant.bus_manual:
            participant.bus_assignment = participant.bus_manual

        elif participant.num_equipe:
            participant.bus_assignment = dict_equipes[participant.num_equipe].bus_assignment

    # ----- Ecriture des fichiers de sortie -----

    with open('./output/export_participant.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['id', 'prenom', 'nom', 'mail', 'telephone', 'ce', 'num_equipe', 'orga', 'majeur', 'bus_manual', 'bus_assignment'])
        for participant in dict_participants.values():
            writer.writerow([participant.id, participant.prenom, participant.nom, participant.mail, participant.telephone, participant.ce,
                             participant.num_equipe, participant.orga, participant.majeur, participant.bus_manual, participant.bus_assignment])

    with open('./output/export_bus.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['numero', 'capacite', 'places occupées', 'equipe1', 'equipe2', 'equipe3', 'equipe4', 'equipe5', 'equipe_7', 'equipe_8'])
        for id_bus, bus in dict_bus.items():
            list_equipe_bus = [bus.numero, bus.capacite, places_occupees_par_bus[id_bus]]
            list_equipe_bus.extend(bus.equipe_assignments)
            writer.writerow(list_equipe_bus)

    for id_bus in dict_bus.keys():
        with open('./output/bus' + str(id_bus) + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['Numero', 'Prenom', 'Nom', 'Equipe', 'Telephone', 'Check In Depart', 'Check In Retour'])
            num = 1
            for participant in dict_participants.values():
                if participant.bus_assignment == id_bus:
                    equipe = dict_equipes[participant.num_equipe].nom if participant.num_equipe else ''
                    writer.writerow([num, participant.prenom, participant.nom, equipe, participant.telephone, '', ''])
                    num += 1
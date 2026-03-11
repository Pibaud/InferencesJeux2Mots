def messageDépart():
    print("\n Mises en forme possible:")
    print("\n- Chercher relations entre 2 termes: <terme1> <terme2>")
    print('\n   Par exemple : "quelles sont les relations entre chat et griffer ?" écrivez : "chat griffer"')
    print("\n- Chercher si une relation existe entre deux termes: <terme1> <relation> <terme2>")
    print('\n   Par exemple : "un chat peut-il griffer ?" écrivez : "chat griffer"')
    print("\n- Chercher les raffinements d'un terme: R <terme>")
    print('\n   Par exemple : R kiwi')
    query = input("\nVotre requête : ").strip().split()
    return query

def mauvaiseRequête():
    print("Format de requête invalide. Veuillez écrire :<mode> <terme1> <relation> <terme2>")
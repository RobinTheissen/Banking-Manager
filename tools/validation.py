# Prüft, ob der String leer ist. Nimmt beliebig viele Strings an
def isEmpty(*query):
    empty = False
    for string in query:
        if len(string) == 0:
            empty = True
    return empty
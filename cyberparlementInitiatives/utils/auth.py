import secrets


def generate_vanity(min_length, max_length):
    """
    Génère un jeton de vanité cryptographiquement solide.

    Arguments nommés :
    min_length -- nombre de caractères minimum du jeton de vanité
    max_length -- nombre de caractères maximum du jeton de vanité
    """

    length = secrets.choice(range(min_length, max_length))
    choices = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ1234567890"
    vanity = ""

    for i in range(0, length):
        vanity += choices[secrets.choice(range(0, len(choices)))]
    return vanity


def generate_unique_vanity(min_length, max_length, model):
    """
    Génère un jeton de vanité unique et cryptographiquement solide.

    Arguments nommés :
    min_length -- nombre de caractères minimum du jeton de vanité
    max_length -- nombre de caractères maximum du jeton de vanité
    model -- modèle que représente le jeton de vanité

    NOTE : les jetons de vanités doivent être stockés dans le champ 'username' du modèle.
    """

    vanity = generate_vanity(min_length, max_length)

    if model.objects.filter(username=vanity).exists():
        return generate_unique_vanity(min_length, max_length, model)
    return vanity

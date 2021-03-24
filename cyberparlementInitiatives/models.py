# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save

from cyberparlementInitiatives.utils.auth import generate_unique_vanity
from cyberparlementInitiatives.utils.validation import generate_validation_token


class Candidat(models.Model):
    election = models.ForeignKey('Election', models.DO_NOTHING, db_column='idElection')  # Field name made lowercase.
    personne = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idPersonne')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'candidat'
        unique_together = (('election', 'personne'),)

    def __unicode__(self):
        return f"{self.personne.nom} {self.personne.prenom} pour {self.election.sujet}"

    def __str__(self):
        return f"{self.personne.nom} {self.personne.prenom} pour {self.election.sujet}"


class Cyberparlement(models.Model):
    nom = models.CharField(db_column='Nom', max_length=45)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=200, blank=True, null=True)  # Field name made lowercase.
    visibilite = models.CharField(db_column='Visibilite', max_length=45, blank=True, null=True)  # Field name made lowercase.
    statut = models.ForeignKey('Statutensemble', models.DO_NOTHING, db_column='Statut', blank=True, null=True)  # Field name made lowercase.
    cpparent = models.ForeignKey('self', models.DO_NOTHING, db_column='CPParent', blank=True, null=True)  # Field name made lowercase.

    # Important !
    # Champ ajouté afin de faire fonctionner le projet de TPI. Absent dans le projet final et à remplacer par une propriété.
    cyberchanceliers = models.ManyToManyField('Personne', verbose_name="Cyberchanceliers", related_name='cyberchanceliers', related_query_name='cyberchancelier')

    # Compléter cette méthode afin de retourner les cyberchanceliers (Personne) du cyberparlement donné
    # @property
    # def cyberchanceliers(self):
    #    pass

    class Meta:
        managed = True
        db_table = 'cyberparlement'

    def __unicode__(self):
        return self.nom

    def __str__(self):
        return self.nom


class Election(models.Model):
    echeance = models.DateTimeField(db_column='Echeance', blank=True, null=True)  # Field name made lowercase.
    sujet = models.CharField(db_column='Sujet', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'election'

    def __unicode__(self):
        return self.sujet

    def __str__(self):
        return self.sujet


class Forum(models.Model):
    ensemble = models.IntegerField(db_column='idEnsemble', blank=True, null=True)  # Field name made lowercase.
    nom = models.CharField(db_column='Nom', max_length=45, blank=True, null=True)  # Field name made lowercase.
    statut = models.CharField(db_column='Statut', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'forum'

    def __unicode__(self):
        return self.nom

    def __str__(self):
        return self.nom


class Genrepersonne(models.Model):
    genre = models.CharField(db_column='Genre', primary_key=True, max_length=10)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'genrepersonne'


class Initiative(models.Model):
    """
    Modèle représentant une initiative.

    **Références :**

    :model:`cyberparlementInitiatives.Cyberparlement`

    :model:`cyberparlementInitiatives.Initiative`

    :model:`cyberparlementInitiatives.Personne`
    """

    # Statuts
    STATUT_A_VALIDER = 'AVAL'
    STATUT_VALIDEE = 'VAL'
    STATUT_EN_SCRUTIN = 'ENS'
    STATUT_SCRUTIN_TERMINE = 'TER'
    STATUT_SECOND_TOUR = '2TR'

    STATUTS_INITIATIVE = [
        (STATUT_A_VALIDER, 'A valider'),
        (STATUT_VALIDEE, 'Validée'),
        (STATUT_EN_SCRUTIN, 'En scrutin'),
        (STATUT_SECOND_TOUR, 'En second tour'),
        (STATUT_SCRUTIN_TERMINE, 'Scrutin terminé'),
    ]

    # Modes de validation
    MODE_VALIDATION_SMS = 'sms'
    MODE_VALIDATION_EMAIL = 'email'
    MODE_VALIDATION_AUCUN = 'aucun'

    MODES_VALIDATION = [
        (MODE_VALIDATION_AUCUN, 'Aucun'),
        (MODE_VALIDATION_SMS, 'SMS'),
        (MODE_VALIDATION_EMAIL, 'Email'),
    ]

    cyberparlement = models.ForeignKey(Cyberparlement, models.DO_NOTHING, db_column='idCP')
    description = models.CharField(db_column='Description', max_length=1000, verbose_name='description de l\'initiative')
    nom = models.CharField(db_column='Nom', max_length=45, blank=True, null=True, verbose_name='nom de l\'initiative')
    debut_scrutin = models.DateTimeField(db_column='DebutScrutin', null=True, blank=True, verbose_name='date et heure de début du scrutin')
    fin_scrutin = models.DateTimeField(db_column='FinScrutin', null=True, blank=True, verbose_name='date et heure de fin du scrutin')
    initiateur = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idInitiateur', blank=True, null=True, verbose_name='personne initiatrice')
    statut = models.CharField(default=STATUT_A_VALIDER, max_length=5, choices=STATUTS_INITIATIVE, verbose_name='statut de l\'initiative')
    mode_validation = models.CharField(default=MODE_VALIDATION_AUCUN, max_length=5, choices=MODES_VALIDATION, verbose_name='mode de validation des votes')
    parent = models.ForeignKey('self', models.DO_NOTHING, db_column='idParent', blank=True, null=True, verbose_name='initiative parente')

    class Meta:
        managed = True
        db_table = 'initiative'

    def __unicode__(self):
        return self.nom

    def __str__(self):
        return self.nom

    @property
    def is_parent(self):
        """
        *Propriété* :
        l'initiative a-t-elle un parent ?
        """
        return Initiative.objects.filter(Q(parent_id=self.id)).count() > 0

    @property
    def blank_field(self):
        """
        *Propriété* :
        champ de vote blanc.
        inconsistant avant l'organisation du scrutin !
        """
        return Choixinitiative.objects.filter(choix=Choixinitiative.BLANK_CHOICE, initiative_id=self.id)[0]

    @property
    def total_votes(self):
        """
        *Propriété* :
        nombre total de votes sur l'initiative.
        """
        return Voteinitiative.objects.filter(Q(initiative_id=self.id)).count()

    @property
    def total_validated_votes(self):
        """
        *Propriété* :
        nombre total de votes validés, incluant les votes blancs.
        """
        if self.mode_validation == self.MODE_VALIDATION_AUCUN:
            return Voteinitiative.objects.filter(Q(initiative_id=self.id)).count()
        else:
            return Voteinitiative.objects.filter(Q(initiative_id=self.id) & Q(statut_validation=Voteinitiative.STATUT_VALIDATION_VALIDE)).count()

    @property
    def max_vote_count(self):
        """
        *Propriété* :
        nombre maximum de votes sur un choix de l'initiative.
        """

        choixinitiatives = self.choix
        maximum = 0
        for choixinitiative in choixinitiatives:
            vote_count = choixinitiative.vote_count
            if vote_count > maximum:
                maximum = vote_count

        return maximum

    @property
    def min_vote_count(self):
        """
        *Propriété* :
        nombre minimal de votes sur un choix de l'initiative.
        """

        choixinitiatives = self.choix

        minimum = self.max_vote_count
        for choixinitiative in choixinitiatives:
            vote_count = choixinitiative.vote_count
            if vote_count < minimum:
                minimum = vote_count

        return minimum

    @property
    def vote_count(self):
        """
        *Propriété* :
        compte des votes
        """

        if self.mode_validation == self.MODE_VALIDATION_AUCUN:
            return Voteinitiative.objects.filter(Q(initiative_id=self.id) & ~Q(choixinitiative=self.blank_field)).count()
        else:
            return Voteinitiative.objects.filter(Q(initiative_id=self.id) & Q(statut_validation=Voteinitiative.STATUT_VALIDATION_VALIDE) & ~Q(choixinitiative=self.blank_field)).count()

    @property
    def need_another_turn(self):
        """
        *Propriété* :
        l'initiative nécessite-t-elle un nouveau tour ?
        """

        votes = self._count_votes()

        if len(votes) <= 2:
            return False

        max_times = 0
        maximum = max(votes.values())
        for vote in votes:
            if votes[vote] == maximum:
                max_times += 1

        if max_times > 1:
            return True
        return False

    @property
    def children(self):
        """
        *Propriété* :
        enfants de l'initiative.
        """

        return Initiative.objects.filter(parent_id=self.id)

    @property
    def choix(self):
        """
        *Propriété* :
        choix de l'initiative
        """

        return Choixinitiative.objects.filter(Q(initiative_id=self.id) & ~Q(choix=self.blank_field))

    def _count_votes(self):
        """
        compte de tous les votes dans un dictionnaire.
        """

        choixinitiatives = Choixinitiative.objects.filter(initiative=self)

        votes = {}

        for choixinitiative in choixinitiatives:
            if choixinitiative.choix != Choixinitiative.BLANK_CHOICE:
                votes_choixinitiative = choixinitiative.vote_count
                votes[choixinitiative.id] = votes_choixinitiative

        return votes


class Choixinitiative(models.Model):
    """
    Modèle représentant un choix proposé pour une :cyberparlementInitiatives.Initiative:.

    **Références :**

    :model:`cyberparlementInitiatives.Initiative`
    """

    BLANK_CHOICE = 'Blanc'

    initiative = models.ForeignKey('Initiative', models.CASCADE, db_column='idInitiative')
    choix = models.CharField(db_column='Choix', max_length=45, blank=True, null=True)
    ordre = models.IntegerField(db_column='Ordre', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'choixinitiative'

    def __unicode__(self):
        return self.choix

    def __str__(self):
        return self.choix

    @property
    def vote_count(self):
        """
        *Propriété* :
        compte des votes sur le choix.
        """

        if self.initiative.mode_validation == Initiative.MODE_VALIDATION_AUCUN:
            return Voteinitiative.objects.filter(Q(initiative=self.initiative) & Q(choixinitiative=self)).count()
        else:
            return Voteinitiative.objects.filter(Q(initiative=self.initiative) & Q(choixinitiative=self) & Q(statut_validation=Voteinitiative.STATUT_VALIDATION_VALIDE)).count()

    @property
    def total_votes(self):
        """
        *Propriété* :
        nombre total de votes, incluant les votes blancs.
        """
        return Voteinitiative.objects.filter(Q(initiative=self.initiative) & Q(choixinitiative=self)).count()

    @property
    def percentage_vote(self):
        """
        *Propriété* :
        pourcentage des suffrages
        """

        if self.vote_count == 0:
            return 0
        total_votes_initiative = self.initiative.vote_count
        return self.vote_count / total_votes_initiative

    @property
    def is_winning(self):
        """
        *Propriété* :
        le choix a-t-il obtenu le plus de suffrages sur l'initiative ?
        :return: vrai si le choix a obtenu le plus de suffrages sur l'initiative
        """

        if self.vote_count == self.initiative.max_vote_count:
            return True
        return False

    @property
    def is_last(self):
        """
        *Propriété* :
        le choix a-t-il obtenu le moins de suffrages sur l'initiative ?
        """

        if self.is_winning:
            return False
        if self.vote_count == self.initiative.min_vote_count:
            return True
        return False


class Voteinitiative(models.Model):
    """
    Modèle représentant un vote de :cyberparlementInitiatives.Personne: proposé pour une :cyberparlementInitiatives.Initiative:.

    **Références :**
    :model:`cyberparlementInitiatives.Personne`
    :model:`cyberparlementInitiatives.Initiative`
    :model:`cyberparlementInitiatives.Choixinitiative`
    """

    STATUT_VALIDATION_VALIDE = 'VAL'
    STATUT_VALIDATION_NON_VALIDE = 'NVAL'

    STATUTS_VALIDATION = [
        (STATUT_VALIDATION_NON_VALIDE, 'Non validé'),
        (STATUT_VALIDATION_VALIDE, 'Validé'),
    ]

    personne = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idPersonne')
    choixinitiative = models.ForeignKey(Choixinitiative, models.DO_NOTHING, db_column='idChoixInitiative', blank=True, null=True, related_name='choix_initiative')
    timestamp = models.DateTimeField(db_column='Timestamp', verbose_name='date et heure du vote')
    initiative = models.ForeignKey(Initiative, models.DO_NOTHING, db_column='idInitiative')
    code_validation = models.CharField(max_length=5, db_column='CodeValidation', blank=True, null=True, verbose_name='code de validation')
    statut_validation = models.CharField(max_length=5, db_column='StatutValidation', default=STATUT_VALIDATION_NON_VALIDE, verbose_name='statut de validation')

    class Meta:
        managed = True
        db_table = 'voteinitiative'
        unique_together = (('personne', 'choixinitiative'),)


def generate_validation_code(sender, instance, *args, **kwargs):
    """
    Fonction générant un code de validation cryptographiquement robuste à chaque vote.
    """
    if not instance.code_validation or instance.code_validation is None:
        instance.code_validation = generate_validation_token(5)


pre_save.connect(generate_validation_code, sender=Voteinitiative)  # Signal se déclenchant avant l'enregistrement dans la base de donnée


class Membrecp(models.Model):
    personne = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idPersonne')
    cyberparlement = models.ForeignKey(Cyberparlement, models.DO_NOTHING, db_column='idCyberParlement')  # Field name made lowercase.
    rolecp = models.ForeignKey('Rolemembrecp', models.DO_NOTHING, db_column='RoleCP')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'membrecp'
        unique_together = (('id', 'personne'),)


class Message(models.Model):
    forum = models.ForeignKey(Forum, models.DO_NOTHING, db_column='idForum', blank=True, null=True)  # Field name made lowercase.
    auteur = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idAuteur', blank=True, null=True)  # Field name made lowercase.
    contenu = models.CharField(db_column='Contenu', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'message'


class Personne(AbstractUser):
    nom = models.CharField(db_column='Nom', max_length=45)
    prenom = models.CharField(db_column='Prenom', max_length=45)
    genre = models.ForeignKey(Genrepersonne, models.DO_NOTHING, db_column='Genre', blank=True, null=True)
    adresse = models.CharField(db_column='Adresse', max_length=45, blank=True, null=True)
    npa = models.IntegerField(db_column='NPA', blank=True, null=True)
    localite = models.CharField(db_column='Localite', max_length=45)
    statut = models.ForeignKey('Statutpersonne', models.DO_NOTHING, db_column='Statut', blank=True, null=True)
    datenaissance = models.DateField(db_column='DateNaissance', blank=True, null=True)
    notel = models.CharField(db_column='NoTel', max_length=45, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'personne'

    def __unicode__(self):
        return f"{self.nom} {self.prenom}"

    def __str__(self):
        return f"{self.nom} {self.prenom}"


def give_default_username(sender, instance, *args, **kwargs):
    """
    Fonction ajoutant un nom d'utilisateur unique par défaut en générant un jeton de vanité.
    """
    instance.username = generate_unique_vanity(5, 10, Personne)


pre_save.connect(give_default_username, sender=Personne)  # Signal se déclenchant avant l'enregistrement dans la base de donnée


class Rolemembrecp(models.Model):
    rolecp = models.CharField(db_column='RoleCP', primary_key=True, max_length=45)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'rolemembrecp'


class Statutensemble(models.Model):
    statuttexte = models.CharField(db_column='StatutTexte', primary_key=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'statutensemble'

    def __unicode__(self):
        return self.statuttexte

    def __str__(self):
        return self.statuttexte


class Statutpersonne(models.Model):
    statuttexte = models.CharField(db_column='StatutTexte', primary_key=True, max_length=45)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'statutpersonne'

    def __unicode__(self):
        return self.statuttexte

    def __str__(self):
        return self.statuttexte


class Voteelection(models.Model):
    personne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idPersonne')
    candidat = models.ForeignKey(Candidat, models.DO_NOTHING, db_column='idCandidat', blank=True, null=True)
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'voteelection'
        unique_together = (('id', 'personne'),)

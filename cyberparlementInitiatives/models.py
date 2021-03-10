# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models.signals import pre_save

from cyberparlementInitiatives.utils.auth import generate_unique_vanity


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


class Choixinitiative(models.Model):
    initiative = models.ForeignKey('Initiative', models.CASCADE, db_column='idInitiative')  # Field name made lowercase.
    choix = models.CharField(db_column='Choix', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ordre = models.IntegerField(db_column='Ordre', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'choixinitiative'

    def __unicode__(self):
        return self.choix

    def __str__(self):
        return self.choix


class Cyberparlement(models.Model):
    nom = models.CharField(db_column='Nom', max_length=45)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=200, blank=True, null=True)  # Field name made lowercase.
    visibilite = models.CharField(db_column='Visibilite', max_length=45, blank=True, null=True)  # Field name made lowercase.
    statut = models.ForeignKey('Statutensemble', models.DO_NOTHING, db_column='Statut', blank=True, null=True)  # Field name made lowercase.
    cpparent = models.ForeignKey('self', models.DO_NOTHING, db_column='CPParent', blank=True, null=True)  # Field name made lowercase.

    # Important !
    # Champ ajouté afin de faire fonctionner le projet de TPI. Absent dans le projet final et remplacé par une méthode.
    cyberchanceliers = models.ManyToManyField('Personne', verbose_name="Cyberchanceliers", related_name='cyberchanceliers', related_query_name='cyberchancelier')

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
    # Statuts
    STATUT_A_VALIDER = 'AVAL'
    STATUT_VALIDEE = 'VAL'

    STATUTS_INITIATIVE = [
        (STATUT_A_VALIDER, 'A valider'),
        (STATUT_VALIDEE, 'Validée'),
    ]

    MODE_VALIDATION_SMS = 'sms'
    MODE_VALIDATION_EMAIL = 'email'
    MODE_VALIDATION_AUCUN = 'aucun'

    # Modes de validation
    MODES_VALIDATION = [
        (MODE_VALIDATION_AUCUN, 'Aucun'),
        (MODE_VALIDATION_SMS, 'SMS'),
        (MODE_VALIDATION_EMAIL, 'Email'),
    ]

    cyberparlement = models.ForeignKey(Cyberparlement, models.DO_NOTHING, db_column='idCP')
    nom = models.CharField(db_column='Nom', max_length=45, blank=True, null=True)
    description = models.CharField(db_column='Description', max_length=1000)
    debut_scrutin = models.DateTimeField(db_column='DebutScrutin', null=True, blank=True)
    fin_scrutin = models.DateTimeField(db_column='FinScrutin', null=True, blank=True)
    initiateur = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idInitiateur', blank=True, null=True)
    statut = models.CharField(default=STATUT_A_VALIDER, max_length=5, choices=STATUTS_INITIATIVE)
    mode_validation = models.CharField(default=MODE_VALIDATION_AUCUN, max_length=5, choices=MODES_VALIDATION)

    class Meta:
        managed = True
        db_table = 'initiative'

    def __unicode__(self):
        return self.nom

    def __str__(self):
        return self.nom


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
    personne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idPersonne')  # Field name made lowercase.
    candidat = models.ForeignKey(Candidat, models.DO_NOTHING, db_column='idCandidat', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'voteelection'
        unique_together = (('id', 'personne'),)


class Voteinitiative(models.Model):
    personne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idPersonne')  # Field name made lowercase.
    choixinitiative = models.ForeignKey(Choixinitiative, models.DO_NOTHING, db_column='idChoixInitiative', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp')  # Field name made lowercase.
    initiative = models.ForeignKey(Initiative, models.DO_NOTHING, db_column='idInitiative')  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'voteinitiative'
        unique_together = (('personne', 'choixinitiative'),)

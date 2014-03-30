Problem bij de presentatie:

Bij today staat Decentralized privacy-enhancing systems.. in het paper hebben we het over decentralized systems, of ze prive zijn staat in de tabel. Aanpassen dus.
Onder problems with tor -> scalability staat directory servers. Waarom, wat moeten we hierbij vertellen? Hebben deze het te druk?
	-> de directory servers is dé centrale component waarvan we de functionaliteit onder de peers willen verspreiden (decentralisatie). Deze hebben het inderdaad vrij druk omdat peers steeds de consensus moeten downloaden om het netwerk te leren kennen. Een mogelijke oplossing is om de peer discovery methodes te gebruiken van andere al gedecentraliseerde netwerken.

Plaatje NAT?
	-> moet inderdaad er nog bij

En wat is nu precies het probleem met NAT en decentralisatie en 1 billion devices?
	-> volgens mij is het probleem dat devices vaak achter 1 ip adres zitten (kijk bijv maar naar 3g) en dat je dus NAT traversal technieken moet gebruiken om de juiste smartphone achter het ip adres te bereiken. Servers (dus een gecentraliseerd systeem) hebben hier vaak geen last van dus het is daadwerkelijk een probleem van decentralisatie. Ik denk dat Wendo dit iets beter uit kan leggen omdat hij hier meer verstand van heeft ;)

Mogelijke vragen die we krijgen:

Bij het opzetten van een pad (introduction to Tor), hoe weten nodes dat ze onderdeel zijn van welk pad? Ofwel wat hun predecessor is en successor.
	-> ik geloof dat elke node één pointer bijhoudt (in de vorm van IP adres) voor elk circuit naar zijn predecessor en successor. Deze worden bij het opzetten van het circuit door de node geleerd.

Waarom willen we decentraal gaan? Enkel voor schaalbaarheid? Of lastiger om aanvallen te doen? Af van de directory servers die - alse ze gehackt zijn - malicious nodes kunnen aanwijzen?
	-> door de directory server die scalability problemen oplevert maar volgens mij zijn er meer redenen, kan iemand anders dit aanvullen?

Hoe lost decentraliteit het scalability probleem op? Die freeriders kunnen niet meer free riden ?
	-> het probleem met free riders wordt helaas niet opgelost door decentralisatie, alleen scalability m.b.t. de directory servers. Om free riders op te lossen, zou je incentives moeten gebruiken, alleen kan dit niet met een centrale autoriteit en moet je dus peer-to-peer incentives gebruiken o.i.d (zie hoofdstuk over incentives).

Torsk lijkt zich in de tabel toch als goede kandidaat? Alleen geen public implementation en niet used in practice... dat kan toch veranderen? Op github gooien en gebruiken maar! Dan zijn we er toch volgens de tabel?
	-> Torks heeft potentie maar is nog gedeeltelijk gecentraliseerd en moet denk ik beter onderzocht worden om de voor- en nadelen beter op een rijtje te krijgen.

Hebben jullie al een trend ontdekt waarin projecten zich onderscheiden van andere in serieusheid, of populariteit (our contribution)?
	-> De meer populaire projecten bevatten gemiddeld meer LOC maar dat is logisch natuurlijk. Misschien dat Rolf met wat machine learning/feature selection/mapping reduction tooltjes een leuk patroon kan ontdekken :D Kappa
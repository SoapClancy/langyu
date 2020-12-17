# langyu
This repository contains all source codes and static files for the project I worked on at the beginning of 2021, 
which is an e-commence website.

It was my first project to develop using Django, JavaScript (jQuery), HTML, CSS (Bootstrap 4). On my annual leave,
I spent 4 weeks learning from scratch and building it. Previously, I had no experience of all these but Python in 
scientific research. And it was great passion, strong curiosity in Web development and desire to challenge myself 
that drove me to finish this project.

It was planned to be deployed and used in real-world sales business. However, after it went online, the business 
partner broke the agreement and offers, although it was the partner who instigated the plan! Therefore, I shut down
the server, but I am still happy because I have learned the skills and experience.

It is in **production** environment and used to be a private repository.
Since it is now a public repository, I have masked some sensitive information in Langyu/settings.py with '******':
- Line 23, SECRET_KEY
- Line 105, the value of DATABASES['PASSWORD']
- Line 169, EMAIL_HOST_USER
- Line 170, EMAIL_HOST_PASSWORD
- Line 175, RECAPTCHA_PUBLIC_KEY
- Line 176, RECAPTCHA_PRIVATE_KEY

'******' also replaces the Google API key, Line 30 in templates/contact.html

Anyone is welcome to reuse the codes (if can be of some help) without informing me. Just make all dependencies 
installed correctly and replace the masked sensitive information. Also, because it was a project developed at 
the beginning of 2021, and some of the newest versions of dependencies have changed their APIs, some codes may need 
to be modified slightly.

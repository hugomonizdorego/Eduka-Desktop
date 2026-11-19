# Matadalan ba utilizadór Edukasaun Desktop Suite: Tetun (Tetun Prasa, ortografia INL).
# Estrutura hanesan content_en.py; naran interface tuir tradusaun Tetun Eduka-Desktop nian
# (imajen sira hatudu interface iha lian inglés).
HTML_LANG = 'tet'
FILE_SUFFIX = 'Tetun'
TITLE = 'Edukasaun Desktop Suite — Matadalan ba Utilizadór'
SUBTITLE = 'Versaun {version} · Eduka-Desktop, Eduka-Panel, Eduka-Quick no Eduka-Settings'
COVER_META = ('Desktop husi **Edukasaun OS**, halo ba eskola sira, iha sesaun LXQt Debian nian. '
              'Imajen sira: interface iha lian inglés, tema Eduka-Pastel, ekran 1366 × 768. Versaun {version}, Novembru 2026.')
FOOTER = 'Edukasaun Desktop Suite — Matadalan ba Utilizadór (Tetun)'
TOC_INTRO = ('Parte hotu-hotu husi desktop: menu hahú, panel, Sentru Asaun, konfigurasaun no buat foun sira iha versaun 0.11 '
             'Pre-Estável. Imajen sira hatudu interface iha lian inglés; naran inglés hakerek iha parénteze.')
LABELS = {'contents': 'Konteúdu', 'tip': 'Sujestaun', 'note': 'Nota', 'warn': 'Importante'}

SECTIONS = [
('intro', 'Bemvindu ba Edukasaun Desktop', [
    ('p', '**Edukasaun Desktop Suite** mak desktop husi Edukasaun OS. Ami halo nia ba eskola sira: estudante, manorin no eskritóriu '
          'eskola nian simu desktop ida ne\'ebé klaru no amigavel, ne\'ebé la\'o di\'ak iha laptop foun no mós iha komputadór tuan. '
          'Nia la\'o iha sesaun **LXQt** Debian nian, tan ne\'e nia kmaan no lais; LXQt fó sesaun, jestór arkivu (PCManFM-Qt), '
          'terminál no ferramenta barak, no Eduka aumenta nia menu hahú, panel no konfigurasaun rasik.'),
    ('h3', 'Parte sira husi suite'),
    ('table', ['Parte', 'Saida mak nia halo'], [
        ['**Eduka-Desktop**', 'Menu hahú: programa hotu tuir kategoria, kaixa buka, favoritu no informasaun sistema.'],
        ['**Eduka-Panel**', 'Barra iha okos: butaun MENU, barra tarefa, área servisu, ikone estadu, notifikasaun no relójiu.'],
        ['**Sentru Asaun**', 'Loke husi relójiu: kalendáriu no ajenda, interruptór lais, volume, brillu no butaun sesaun.'],
        ['**Eduka-Quick**', 'Lansadór lais kabuar no transparente ba programa ne\'ebé ita uza barak liu ([[Super+Q]]).'],
        ['**Eduka-Settings**', 'Janela ida ba konfigurasaun hotu: aparénsia, panel, janela, ekran, son, tekladu, mouse, utilizadór no seluk tan.'],
    ]),
    ('img', 'desktop', 'Desktop hafoin tama: ikone sira iha karuk, Eduka-Panel iha okos.'),
    ('h3', 'Buat foun iha 0.11 Pre-Estável'),
    ('ul', [
        'Eduka-Desktop loke ho klik ida iha MENU ka hanehan [[Super]] dala ida, mós bainhira Sentru Asaun loke hela.',
        'Buka iha Eduka-Desktop mós hetan pájina sira Eduka-Settings nian ("sound", "mouse", "workspace" …).',
        'Tema padraun ho kór azul mamar, hanesan kór logo Edukasaun OS nian.',
        'Pájina **Son** kompletu: ekipamentu, teste, son moos ho EasyEffects no hadi\'a ba son ne\'ebé kraak ka la iha.',
        'Área servisu, kantu ativu, fokus tuir mouse, kola ho klik klaran no istória clipboard ([[Super+V]]).',
        'Grava ekran ho son ([[Super+Alt+R]]) no **Taka ho forsa** ba programa ne\'ebé para responde.',
        'Vidru kabuar, baku no dada iha touchpad, tablet kaneta, kartaun gráfiku dedikadu ba jogu no efeitu Compiz opsionál.',
        'Apoiu di\'ak liu ba sesaun Wayland (labwc, KWin) no lista ekipamentu ne\'ebé seidauk iha driver.',
    ]),
    ('note', 'Imajen sira iha matadalan ne\'e hatudu interface iha lian inglés. Eduka-Desktop mós iha tradusaun ba Tetun, Portugés '
             'no Indonézia (Eduka-Settings → Lian no Oras).'),
]),
('login', 'Tama no sai', [
    ('p', 'Iha ekran tama, hili ita-nia konta (ka hakerek naran), hakerek liafuan-xave no hanehan [[Enter]]. Komputadór ne\'ebé iha '
          'leitór impresaun dijitál mós bele simu liman-fuan, se ita liga ida-ne\'e iha Eduka-Settings → Tama & Impresaun dijitál.'),
    ('p', 'Ekran tama oferese de\'it sesaun **Eduka-Desktop**; nia hahú LXQt ho Eduka-Panel no Eduka-Desktop. Bainhira konta foun tama '
          'dala uluk, nia prepara wallpaper, tema, tekladu no eskala ekran ne\'ebé rekomenda.'),
    ('h3', 'Ekran sai'),
    ('p', 'Hanehan [[Ctrl+Alt+Delete]], ka uza butaun sira iha okos Sentru Asaun nian, atu loke ekran sai. Klik ida halo kedas asaun: '
          '**Xave** (ita-nia programa sira kontinua loke no ita-nia liafuan-xave loke fali ekran), **Sai**, **Toba**, **Iberna** '
          '(bainhira komputadór bele), **Hahú fali** ka **Hamate**. [[Esc]] taka ekran la halo buat ida.'),
    ('img', 'leave', 'Ekran sai ho desktop kabuar iha kotuk.'),
    ('tip', 'Rai uluk ita-nia servisu antes sai, hahú fali ka hamate. [[Super+L]] taka ekran ho xave lalais bainhira ita husik komputadór.'),
]),
('menu', 'Eduka-Desktop: menu hahú', [
    ('p', 'Klik **MENU** iha panel nia rohan karuk, ka hanehan tekla [[Super]] (tekla ho logo Windows), atu loke Eduka-Desktop. Klik '
          'fali MENU, hanehan fali [[Super]] ka hanehan [[Esc]] atu taka. Menu mós loke ho klik ida de\'it bainhira Sentru Asaun ka '
          'janela ki\'ik seluk husi panel loke hela.'),
    ('img', 'menu', 'Eduka-Desktop ho kategoria Hotu (All) iha vista Grade.'),
    ('h3', 'Kategoria sira'),
    ('p', 'Koluna iha karuk hatudu kategoria sira. **Edukasaun** halibur programa ba aprende, siénsia no jogu; sira seluk tuir grupu '
          'baibain: Asesóriu, Grafiku, Internet, Eskritóriu, Programasaun, Son no Vídeu, Ferramenta sistema, Asesu universál no '
          'Preferénsia. **Hotu** hatudu programa hotu. Kategoria mamuk subar.'),
    ('h3', 'Buka'),
    ('p', 'Bainhira menu loke, hahú de\'it hakerek. Buka iha programa hotu, kategoria saida de\'it mak ita hili, no nia komprende naran, '
          'deskrisaun no liafuan-xave. [[Enter]] hahú rezultadu dahuluk. Husi 0.11 Pre-Estável, buka mós hatudu **pájina sira '
          'Eduka-Settings nian** ne\'ebé hanesan: hakerek "sound", "mouse" ka "workspace" no loke kedas konfigurasaun.'),
    ('img', 'menu-search', 'Buka "sound": pájina sira Eduka-Settings nian ne\'ebé hanesan.'),
    ('h3', 'Grade, Lista no favoritu'),
    ('ul', [
        '**Grade** hatudu kaixa boot; **Lista** hatudu naran ho deskrisaun badak (di\'ak ba leitór ekran no ekran ki\'ik).',
        'Koluna **Favoritu** iha loos rai programa ne\'ebé ita uza barak liu. Klik liman-loos programa ida → **Aumenta ba Favoritu**.',
        '**Informasaun sistema** hatudu versaun Edukasaun OS no desktop nian.',
        'Butaun sira iha okos loke Jestór arkivu, Terminál, Eduka-Settings no Kona-ba.',
        'Iha ekran ki\'ik (luan menus 900 píxel) menu uza formatu ki\'ik liu no hatudu favoritu hanesan kategoria ida.',
    ]),
    ('h3', 'Menu klik liman-loos programa nian'),
    ('ul', [
        '**Loke** hahú programa; **Halai ho kartaun gráfiku dedikadu** mosu iha laptop ne\'ebé iha kartaun gráfiku rua.',
        '**Aumenta ba Favoritu**, **Aumenta ba desktop** (ikone ida iha desktop) no **Fiksa iha barra tarefa** (butaun ida iha panel).',
        '**Aumenta ba Eduka-Quick** tau programa iha lansadór lais kabuar.',
        '**Loke pasta ne\'ebé iha** hatudu fatin arkivu programa nian.',
    ]),
]),
('panel', 'Eduka-Panel', [
    ('p', 'Eduka-Panel mak barra iha ekran nia okos. Husi karuk ba loos nia hatudu butaun MENU, programa ne\'ebé fiksa, janela ne\'ebé '
          'loke (barra tarefa), área servisu, ikone estadu no relójiu.'),
    ('h3', 'Barra tarefa'),
    ('p', 'Janela loke ida-idak iha butaun ida. Klik ida hatudu janela, klik daruak halo nia ki\'ik (minimiza). Ho área servisu barak, '
          'barra tarefa hatudu janela husi área servisu agora nian. Klik liman-loos butaun janela ida atu hetan buat barak liu:'),
    ('ul', [
        '**Ativa**, **Halo ki\'ik**, **Halo boot** ka **Restaura**, no **Taka**.',
        '**Aumenta ba Favoritu** no **Fiksa iha barra tarefa** (programa kontinua iha butaun bainhira taka).',
        '**Taka ho forsa**: taka kedas programa ida, mós bainhira nia la responde ona (haree kapítulu "Programa ne\'ebé para responde").',
    ]),
    ('img', 'task-menu', 'Menu klik liman-loos janela nian iha barra tarefa.', 'half'),
    ('h3', 'Área servisu'),
    ('p', 'Númeru **1 2 3 4** mak área servisu virtuál: desktop ketak ba knaar oioin, ezemplu lisaun ida iha área 1 no navegadór iha '
          'área 2. Klik númeru ida, rola iha númeru sira nia leten, ka hanehan [[Ctrl+Super+Left]] no [[Ctrl+Super+Right]]. Númeru '
          'área servisu hili iha Eduka-Settings → Janela no área servisu.'),
    ('h3', 'Ikone estadu'),
    ('table', ['Ikone', 'Klik', 'Klik liman-loos ka seluk tan'], [
        ['Disku ne\'ebé hasai', 'Hatudu USB no kartaun; hasai sira ho seguru.', 'Loke disku iha jestór arkivu.'],
        ['Rede', 'Rede Wi-Fi no ligasaun ho kabu.', 'Konfigurasaun rede.'],
        ['Bluetooth', 'Liga ka hamate, liga ekipamentu ida (de\'it bainhira komputadór iha Bluetooth).', 'Jestór Bluetooth.'],
        ['Son', 'Volume, ekipamentu saída no interruptór Son moos.', 'Rola atu muda volume.'],
        ['Bateria', 'Karga, tempu ne\'ebé hela no modu enerjia (laptop).', 'Konfigurasaun enerjia.'],
        ['Notifikasaun', 'Mensajen ikus sira; Keta disturba.', 'Konfigurasaun notifikasaun.'],
        ['Tekladu (US, PT …)', 'Muda tekladu nia lay-out.', 'Konfigurasaun tekladu.'],
        ['Relójiu', 'Loke Sentru Asaun.', 'Estilu no konfigurasaun relójiu.'],
    ]),
    ('img', 'sound-popup', 'Janela son: volume, saída, Son moos no konfigurasaun son.', 'half'),
    ('tip', 'Bainhira ita grava ekran, butaun mean ki\'ik **REC** mosu iha panel; klik nia atu hapara.'),
    ('h3', 'Panel nia fatin no aparénsia'),
    ('p', 'Klik liman-loos iha parte mamuk panel nian atu muda nia ba ekran nia sorin seluk, atu muda nia rohan (ovál, kabuar ka '
          'kuadradu) no atu loke konfigurasaun panel. Eduka-Panel hela iha nia fatin iha janela boot (maximiza) sira nia leten; '
          'de\'it programa iha ekran tomak (vídeo, jogu, aprezentasaun) mak taka nia.'),
]),
('action-center', 'Sentru Asaun', [
    ('p', 'Klik relójiu iha panel (ka hanehan [[Super+A]]) atu loke Sentru Asaun. Klik fali relójiu, hanehan [[Esc]] ka klik iha li\'ur '
          'atu taka.'),
    ('img', 'action-center', 'Sentru Asaun (Action Center).', 'half'),
    ('ul', [
        '**Kartaun relójiu**: oras, kumprimentu no data, ho tempu (klima) ohin nian. Klik nia ba globu mundu no zona oras; klik '
        'liman-loos ba estilu relójiu (dijitál, analójiku, ho segundu …).',
        '**Sinkroniza oras** (leten karuk): hadi\'a relójiu no zona oras husi internet.',
        '**Kaixa sira**: Rede, Bluetooth, Modu aviaun, Ekran (modu projetór), Keta disturba no Konfigurasaun. Klik liman-loos kaixa '
        'ida atu loke nia konfigurasaun.',
        '**Múzika no vídeo**: bainhira programa ida toka hela, molok, toka/pauza no tuir mai mosu iha leten.',
        '**Kalendáriu no ajenda**: hili loron ida no hanehan **+ Ajenda** atu hakerek nota ka lembrete ho oras.',
        '**Volume no brillu**; seta iha volume nia sorin hili ekipamentu saída.',
        '**Xave, Sai, Hahú fali, Hamate** iha okos.',
        'Kabun iha leten halo Sentru Asaun boot liu ka ki\'ik liu; seta iha leten loos liga modu kompaktu.',
    ]),
]),
('quick', 'Eduka-Quick', [
    ('p', 'Hanehan [[Super+Q]] atu loke Eduka-Quick iha fatin ne\'ebé pontiru mouse iha. Nia hatudu iha sírkulu ida programa ne\'ebé '
          'ita uza barak liu. Aponta ba pedasuk ida no klik, ka hanehan númeru ne\'ebé nia hatudu ([[1]] to [[9]]). [[Esc]] taka nia.'),
    ('img', 'quick', 'Eduka-Quick, lansadór lais kabuar.', 'half'),
    ('ul', [
        'Hanehan butaun mouse iha klaran transparente no dada atu muda Eduka-Quick; dala seluk nia loke iha ne\'ebá.',
        'Klik liman-loos programa ida iha Eduka-Desktop → **Aumenta ba Eduka-Quick** atu aumenta nia.',
        'Eduka-Settings → Eduka-Quick hili númeru pedasuk (4 to 12), aparénsia no programa sira.',
    ]),
]),
('notifications', 'Notifikasaun', [
    ('p', 'Programa sira hatudu mensajen badak iha okos loos, iha relójiu nia leten. Sira lakon rasik hafoin segundu balun; ikone '
          'notifikasaun iha panel rai mensajen ikus sira. Klik nia atu lee fali ka atu hamoos.'),
    ('img', 'recording-saved', 'Notifikasaun ida: gravasaun ekran rai ona.', 'half'),
    ('p', '**Keta disturba** (iha Sentru Asaun no lista notifikasaun) halo mensajen sira nonok; de\'it mensajen urjente mak sei mosu. '
          'Eduka-Settings → Eduka-Panel → Notifikasaun hili tempu hira mensajen hela no se rai sira.'),
]),
('settings', 'Eduka-Settings', [
    ('p', 'Loke Eduka-Settings husi menu (butaun **Konfigurasaun**), ho [[Super+I]], ka ho klik liman-loos iha kaixa ida Sentru Asaun '
          'nian. Pájina dahuluk, **Konfigurasaun hotu**, hatudu konfigurasaun hotu tuir grupu, ho nia kaixa buka rasik. Lista iha '
          'karuk lori ba pájina sira; pájina kona-ba asuntu hanesan fahe entrada ida ho tab iha leten.'),
    ('img', 'settings-overview', 'Konfigurasaun hotu (All Settings), pájina dahuluk Eduka-Settings nian.'),
    ('p', 'Mudansa barak liu uza kedas. **Aplika** ([[Ctrl+S]]) aplika buat hotu no janela kontinua loke; **Rai no Taka** aplika no '
          'taka. Konfigurasaun ba komputadór tomak (konta seluk, ekran tama, Kontrolu Inan-Aman, impresaun dijitál) husu liafuan-xave '
          'administradór nian. **Fila ba Padraun**, iha okos karuk, fila fali konfigurasaun padraun Edukasaun nian ba Eduka-Desktop '
          'no Eduka-Panel (tema, transparénsia, medida, lay-out, butaun menu); favoritu, programa fiksa no ekran tama la muda.'),
    ('table', ['Grupu', 'Pájina sira'], [
        ['PERSONALIZA', 'Aparénsia (Tema, Fonte sira, Efeitu) · Wallpaper & Ikone'],
        ['DESKTOP', 'Eduka-Desktop · Eduka-Quick · Eduka-Panel (Panel, Relójiu, Notifikasaun) · Janela no área servisu'],
        ['EKIPAMENTU', 'Ekran · Son (Son, Son moos, Kualidade no hadi\'a) · Tekladu (Tekladu, Atallu) · Mouse & Toke'],
        ['SISTEMA', 'Utilizadór sira · Lian no Oras · Asesibilidade · Kontrolu Inan-Aman · Tama & Impresaun dijitál · Manutensaun'],
    ]),
]),
('look', 'Aparénsia, wallpaper no fonte', [
    ('p', '**Aparénsia → Tema** hili tema ida husi tema hitu. Tema ida-idak mós fó estilu ba programa GTK no Qt no ba janela nia rohan.'),
    ('table', ['Tema', 'Ba'], [
        ['**Eduka-Pastel** (padraun)', 'Azul mamar husi logo Edukasaun OS; naroman no amigavel ba eskola.'],
        ['Eduka-Default-Theme', 'Aparénsia kalma no klaru ho kór oioin.'],
        ['**Eduka-Low-Theme**', 'Komputadór tuan tebes ka neineik: la iha transparénsia, la iha efeitu, uza memória uitoan liu.'],
        ['Liquid Glass', 'Vidru mutin ho rohan naroman (presiza kompozitór no memória 4 GB).'],
        ['Edukasaun-Dark', 'Tema nakukun ba kalan ka sala ho projetór.'],
        ['Eduka-Transparan', 'Panel no menu transparente.'],
        ['Eduka-MultiColor', 'Kór ketak ba kategoria, kaixa no butaun panel ida-idak.'],
    ]),
    ('img', 'settings-appearance', 'Aparénsia → Tema.'),
    ('ul', [
        '**Kór prinsipál**: kór butaun, interruptór no destake sira nian.',
        '**Vidru kabuar**: blur iha Eduka-Panel, Eduka-Desktop no sira-nia janela ki\'ik nia kotuk (presiza gráfiku 3D; mate iha VirtualBox).',
        '**Desktop kabuar iha ekran sai nia kotuk**: la\'o iha komputadór hotu.',
        '**Fonte sira**: letra ba desktop, dokumentu no títulu janela, nia medida no suave.',
        '**Efeitu**: animasaun no kompozitór (Automátiku di\'ak ba komputadór barak liu).',
        '**Wallpaper & Ikone**: imajen husi /usr/share/background/Edukasaun ka ita-nia rasik, slideshow, no ikone sira iha desktop.',
    ]),
]),
('desktop-panel', 'Konfigurasaun Eduka-Desktop, Eduka-Quick no Eduka-Panel', [
    ('p', '**Eduka-Desktop**: medida menu nian, Grade ka Lista, kategoria ne\'ebé hatudu, kór kaixa sira no ajuda asesibilidade.'),
    ('img', 'settings-desktop', 'Eduka-Settings → Eduka-Desktop.'),
    ('p', '**Eduka-Panel → Panel**: panel nia aas no fatin, testu butaun MENU, programa ne\'ebé fiksa no barra tarefa. **Relójiu**: '
          'relójiu dijitál ka analójiku, segundu, data no tempu (klima). **Notifikasaun**: tempu hira mensajen hela, Keta disturba no istória.'),
    ('img', 'settings-panel', 'Eduka-Settings → Eduka-Panel → Panel.'),
]),
('windows', 'Janela, área servisu no kaptura ekran', [
    ('p', '**Janela no área servisu** iha tab tolu.'),
    ('h3', 'Janela sira'),
    ('ul', [
        '**Fokus**: "Klik janela ida atu servisu iha laran" (hanesan Windows), ka "janela iha pontiru okos simu tekladu" (fokus tuir '
        'mouse; janela la sa\'e ba oin).',
        '**Kola ho klik klaran**: hili testu, depois klik butaun klaran mouse nian (ka baku ho liman-fuan tolu) atu kola.',
        '**Istória clipboard**: [[Super+V]] hatudu testu sira ne\'ebé ita kopia. Nia hela de\'it iha memória, nunka iha disku; '
        'liafuan-xave ne\'ebé kopia husi jestór liafuan-xave la rai.',
        '**Programa ne\'ebé la responde**: oferese taka ho forsa programa ida ne\'ebé la responde minutu 1, 2 ka 5 ona.',
        '**Jestór janela**: xfwm4 (rekomenda), Openbox (kmaan liu), KWin, Marco ka Compiz (efeitu 3D, instala ketak). Hili ne\'e uza '
        'husi tama tuir mai.',
    ]),
    ('img', 'settings-windows', 'Janela no área servisu → Janela.'),
    ('img', 'clipboard', 'Istória clipboard ([[Super+V]]): klik testu ida atu kopia fali.', 'half'),
    ('h3', 'Área servisu no kantu'),
    ('p', 'Hili númeru área servisu (1 to 8), se panel hatudu sira no se barra tarefa hatudu de\'it janela husi área servisu agora nian. '
          '**Kantu ativu**: dudu pontiru ba ekran nia kantu ida atu loke Eduka-Desktop, hatudu desktop, loke Sentru Asaun ka '
          'Eduka-Quick, muda área servisu, hatudu notifikasaun ka taka ekran ho xave. La akontese buat ida bainhira ita hanehan hela '
          'butaun mouse. Kantu ativu la\'o iha sesaun X11.'),
    ('img', 'settings-workspaces', 'Janela no área servisu → Área servisu no kantu.'),
    ('h3', 'Kaptura no grava'),
    ('ul', [
        '[[Print]]: ekran tomak · [[Alt+Print]]: janela ativa · [[Super+Shift+S]]: ekran nia parte ida · [[Super+Print]]: rai kedas '
        'iha Imajen/Screenshots.',
        '[[Super+Alt+R]] hahú **grava ekran** no hapara fali; butaun mean REC iha panel mós hapara.',
        'Grava son komputadór nian no, se ita hakarak, mikrofone. Vídeo sira mak arkivu MP4 iha Vídeo/Screen recordings; sira bele '
        'toka iha komputadór no telemóvel hotu.',
        '"Suave" (imajen 15, 25 ka 30 iha segundu ida) no "Medida" (arkivu ki\'ik to imajen di\'ak liu) di\'ak ba komputadór tuan no foun.',
    ]),
    ('img', 'recording', 'Bainhira grava hela: butaun mean REC ho tempu iha Eduka-Panel.'),
    ('img', 'settings-capture', 'Janela no área servisu → Kaptura no grava.'),
]),
('hang', 'Programa ne\'ebé para responde', [
    ('p', 'Dala ruma programa ida para: nia janela hela maibé nia la reaje ona. Eduka-Panel nota ida-ne\'e. Bainhira programa ida la '
          'responde minutu rua ona (ita bele muda tempu ne\'e), janela ki\'ik ida husu saida mak atu halo:'),
    ('img', 'hang-dialog', 'Programa ida la responde: Hein ka Taka ho forsa.', 'half'),
    ('ul', [
        '**Hein**: programa simu tempu tan; programa barak responde fali hafoin knaar naruk ida.',
        '**Taka ho forsa**: programa taka kedas. Servisu ne\'ebé seidauk rai iha programa ne\'e sei lakon.',
    ]),
    ('p', 'Ita mós bele taka rasik programa ne\'ebé para: hanehan [[Ctrl+Alt+Esc]] ba janela ativa, ka klik liman-loos nia butaun iha '
          'barra tarefa → **Taka ho forsa**. Eduka husu uluk. Programa ne\'ebé halo desktop la\'o (panel, jestór janela, ikone desktop) '
          'nunka taka.'),
    ('img', 'force-close', 'Taka ho forsa hafoin [[Ctrl+Alt+Esc]].', 'half'),
]),
('display', 'Ekran no gráfiku', [
    ('p', 'Pájina **Ekran** hatudu komputadór oinsá mak Eduka-Desktop hetan (laptop, komputadór meza, tablet ka másina virtuál) no '
          'ekran nia medida.'),
    ('ul', [
        '**Eskala** (75 to 200 %): halo testu, ikone, panel no janela boot liu ka ki\'ik liu hamutuk. Eskala ne\'ebé rekomenda iha marka. '
        'Eskala foun uza hafoin sai no tama fali.',
        '**Ekran no rezolusaun**: arranja monitór rua ka projetór ida (konfigurasaun monitór LXQt nian). [[Super+P]] muda modu projetór.',
        '**Gráfiku**: kartaun gráfiku sira no sira-nia driver, ho konsellu bainhira driver ka nia firmware falta. Iha laptop ho kartaun '
        'rua, jogu no programa ne\'ebé husu, hahú iha kartaun dedikadu; programa saida de\'it bele hahú iha ne\'ebá husi nia menu klik '
        'liman-loos iha Eduka-Desktop.',
    ]),
    ('img', 'settings-display', 'Ekran: komputadór nia tipu no eskala.'),
]),
('sound', 'Son', [
    ('p', 'Problema son baibain akontese iha komputadór Linux, tan ne\'e Eduka-Settings iha pájina **Son** kompletu ho tab tolu. Nia '
          'la\'o ho PipeWire no ho PulseAudio.'),
    ('h3', 'Son'),
    ('ul', [
        '**Altifalante no auskultadór**: hili saída (altifalante integradu, auskultadór, HDMI ba projetór ka televizaun, Bluetooth, '
        'USB) no nia konektór; hadi\'a volume; **Teste karuk**, **Teste rua** no **Teste loos** toka son badak ida iha sorin ida-idak.',
        '"Permite boot liu 100%" ajuda altifalante laptop ne\'ebé kmaan (son bele aat).',
        '**Mikrofone**: ekipamentu entrada, nia konektór no nia nivel.',
        '**Kartaun son**: perfíl kartaun ida-idak nian. Perfíl ho HDMI haruka son ba projetór; ba auskultadór Bluetooth '
        '"High Fidelity Playback (A2DP)" mak di\'ak liu, "Headset" ba telefone ho mikrofone.',
    ]),
    ('img', 'settings-sound', 'Son: ekipamentu, volume no teste.'),
    ('h3', 'Son moos'),
    ('p', '**EasyEffects** hadi\'a son programa hotu nian. Nia programa ketak: hanehan **Instala EasyEffects…** dala ida, depois hili son '
          'ida. Ba altifalante no auskultadór: Mate, **Lian moos** (lisaun, vídeo no telefone), Múzika, Volume hanesan, Altifalante '
          'laptop, Loudness, Auskultadór no Baixu (haat ikus mak prekonfigurasaun husi JackHack96). Ba mikrofone: **Mikrofone moos** '
          '(barullu kotuk menus ba aula online no gravasaun). Interruptór "Son moos" iha janela son panel nian liga ka hamate lalais.'),
    ('img', 'settings-clear-sound', 'Son moos ho EasyEffects.'),
    ('h3', 'Kualidade no hadi\'a'),
    ('ul', [
        '**Toka múzika ho nia taxa rasik** (44.1 ka 48 kHz) duké konverte.',
        '**Kartaun son hela moris**: segundu dahuluk la kotu no la iha kraak; projetór kontinua ho son.',
        '**Buffer son boot liu**: la iha kraak iha komputadór tuan ka okupadu (tardi uitoan).',
        '**Kualidade konversaun di\'ak liu** (uza prosesadór barak liu).',
        '**Aplika no hahú fali son** uza hili sira; **Fila konfigurasaun son ba padraun** hasai fali sira.',
        '**Haree ha\'u-nia son** buka problema baibain (son nonok, volume kmaan tebes, la iha ekipamentu, Bluetooth iha modu telefone, '
        'firmware falta) no oferese hadi\'a ho klik ida ba ida-idak.',
    ]),
    ('img', 'settings-sound-quality', 'Kualidade no hadi\'a ho rezultadu "Haree ha\'u-nia son".'),
    ('tip', 'Projetór la iha son? Hili saída HDMI iha tab Son, ka perfíl HDMI kartaun nian, no hanehan "Teste rua".'),
]),
('keyboard', 'Tekladu no atallu', [
    ('p', '**Tekladu**: lay-out sira (ezemplu US, Portugés, Indonézia), tekla ne\'ebé muda entre sira, repete tekla no Num Lock '
          '("Automátiku" liga nia iha komputadór meza no hamate iha laptop). Panel hatudu lay-out agora nian.'),
    ('img', 'settings-keyboard', 'Tekladu.'),
    ('p', '**Atallu** hatudu atallu hotu LXQt no Eduka nian hamutuk. Hasai marka iha liña ida atu husik nia tekla livre. Tekla ne\'ebé '
          'LXQt, ita ka jestór janela uza ona, nunka simu knaar daruak.'),
    ('table', ['Tekla', 'Saida mak sira halo'], [
        ['[[Super]]', 'Loke ka taka Eduka-Desktop'],
        ['[[Super+Q]]', 'Eduka-Quick'],
        ['[[Super+S]]', 'Buka programa no arkivu'],
        ['[[Super+R]] ka [[Alt+F2]]', 'Halai komandu ida'],
        ['[[Super+V]]', 'Istória clipboard'],
        ['[[Super+E]]', 'Jestór arkivu'],
        ['[[Super+I]]', 'Eduka-Settings'],
        ['[[Super+A]]', 'Sentru Asaun'],
        ['[[Super+N]]', 'Notifikasaun'],
        ['[[Super+D]]', 'Hatudu desktop (dala seluk: janela sira fila mai)'],
        ['[[Super+M]] / [[Super+Shift+M]]', 'Halo ki\'ik janela hotu / lori fali sira'],
        ['[[Super+Up]] / [[Super+Down]]', 'Halo boot / restaura janela'],
        ['[[Super+Left]] / [[Super+Right]]', 'Janela iha ekran nia metade karuk / loos'],
        ['[[Super+Shift+Left]] / [[Super+Shift+Right]]', 'Janela ba ekran iha karuk / loos'],
        ['[[Ctrl+Super+Left]] / [[Ctrl+Super+Right]]', 'Área servisu molok / tuir mai'],
        ['[[Alt+Tab]]', 'Muda entre janela sira'],
        ['[[Alt+F4]]', 'Taka janela'],
        ['[[Ctrl+Alt+Esc]]', 'Taka ho forsa programa janela ativa nian'],
        ['[[Ctrl+Shift+Esc]]', 'Jestór tarefa'],
        ['[[Ctrl+Alt+T]]', 'Terminál'],
        ['[[Super+L]]', 'Taka ekran ho xave'],
        ['[[Ctrl+Alt+Delete]]', 'Ekran sai: xave, sai, toba, hahú fali, hamate'],
        ['[[Print]] / [[Alt+Print]]', 'Kaptura ekran / janela'],
        ['[[Super+Shift+S]]', 'Kaptura área ida'],
        ['[[Super+Print]]', 'Kaptura rai kedas'],
        ['[[Super+Alt+R]]', 'Hahú ka hapara grava ekran'],
        ['[[Super+P]]', 'Ekran no projetór'],
        ['[[Super+.]]', 'Emoji no símbolu'],
        ['[[Super+Space]]', 'Lay-out tekladu tuir mai'],
        ['[[Super+U]]', 'Konfigurasaun asesibilidade'],
        ['[[Ctrl+Super+Enter]]', 'Leitór ekran liga ka hamate'],
        ['[[Ctrl+Super+O]]', 'Tekladu iha ekran liga ka hamate'],
        ['[[Super+=]]', 'Lupa'],
    ]),
    ('img', 'settings-shortcuts', 'Tekladu → Atallu.'),
]),
('mouse', 'Mouse, touchpad, ekran toke no kaneta', [
    ('ul', [
        '**Mouse**: lalais pontiru nian, butaun ba liman-karuk, lalais klik dala rua no roda.',
        '**Touchpad**: liga ka hamate, baku atu klik (liman-fuan ida karuk, liman-fuan rua loos), rola naturál, hamate bainhira '
        'hakerek, **baku no dada** (baku, tau fali liman-fuan no book) no **xave dada** (hasa\'e liman-fuan la soe saida mak ita '
        'dada; baku atu soe). Konfigurasaun ne\'ebé halo la ho touchpad rai ba bainhira hetan ida.',
        '**Ekran toke**: ekran ne\'ebé toke pertense ba, rotasaun, rola suave ho liman-fuan, jestu ho liman-fuan tolu no haat no '
        'tekladu iha ekran.',
        '**Tablet kaneta** (tab Ekran toke): ho projetór ka monitór daruak, kaneta dezeña iha ekran ida de\'it, nune\'e sírkulu '
        'kontinua kabuar.',
    ]),
    ('img', 'settings-touchpad', 'Mouse & Toke → Touchpad ho baku no dada.'),
    ('img', 'settings-touchscreen', 'Mouse & Toke → Ekran toke no tablet kaneta.'),
]),
('system', 'Utilizadór, lian, asesibilidade no Kontrolu Inan-Aman', [
    ('h3', 'Utilizadór sira'),
    ('p', 'Aumenta no hasai konta, muda naran, liafuan-xave no imajen, no hili sé mak administradór. Halo konta ida ba manorin ida-idak '
          '(Administradór) no ba estudante ka klase ida-idak (Normál). Iha eskola, rai bebeik konta administradór rua ka liu.'),
    ('img', 'settings-users', 'Utilizadór sira.'),
    ('h3', 'Lian no Oras'),
    ('p', '**Lian no Hahú**: lian Eduka-Desktop no programa seluk nian (Tetun, Portugés, Inglés, Indonézia …) no programa ne\'ebé '
          'hahú hafoin tama. **Data no Oras**: zona oras, oras husi rede no relójiu.'),
    ('h3', 'Asesibilidade'),
    ('ul', [
        '**Haree**: kontraste forte, testu boot, pontiru boot liu, movimentu menus, lupa no tekladu iha ekran.',
        '**Rona**: estadu rede, son no alerta hanesan testu iha Eduka-Panel, no son mono (tilun rua no altifalante rua toka buat hotu).',
        '**Leitór ekran**: Orca lee ekran ho lian maka\'as; hili no koko lian.',
    ]),
    ('img', 'settings-accessibility', 'Asesibilidade → Haree.'),
    ('h3', 'Kontrolu Inan-Aman no privasidade'),
    ('p', 'Kontrolu Inan-Aman hili limite tempu ba komputadór ida-ne\'e no tempu ne\'ebé permite, ho rekomendasaun tuir idade (labarik '
          'ki\'ik, eskola primária, joven sira, lisaun komputadór, TPC). Eduka-Panel hatudu lembrete amigavel atu deskansa matan no '
          'book-an, mós la ho limite tempu, no mensajen ida antes komputadór hamate. Mudansa husu liafuan-xave administradór nian. '
          '**Privasidade** hamoos arkivu foin loke, imajen ki\'ik (thumbnail) no lixu.'),
    ('img', 'settings-parental', 'Kontrolu Inan-Aman.'),
    ('h3', 'Tama & Impresaun dijitál'),
    ('p', 'Aparénsia ekran tama nian (SDDM, ka LightDM hanesan opsaun), tama automátiku (sempre husu liafuan-xave administradór nian) '
          'no tama ho impresaun dijitál: aumenta liman-fuan ida, depois liga "Uza impresaun dijitál".'),
]),
('maintenance', 'Manutensaun, memória, driver no firmware', [
    ('ul', [
        '**Harii fali lista aplikasaun**: hafoin instala ka hasai programa.',
        '**Karrega fali Eduka-Desktop** no **Hahú fali Eduka-Panel**: bainhira menu ka panel la hanesan loos ka para responde.',
        '**Hadi\'a tema no sesaun LXQt**: bainhira LXQt husu jestór janela ka tema la hanesan loos; konfigurasaun tuan rai hanesan kópia.',
        '**Driver no firmware**: hatudu ekipamentu Wi-Fi, rede, son, gráfiku no Bluetooth ne\'ebé seidauk iha driver, ho pakote '
        'firmware atu instala ("Instala firmware ne\'ebé falta…"). Depois hahú fali komputadór.',
        '**Memória**: poupa memória, avizu antes memória nakonu, programa ne\'ebé uza memória barak liu, no zram no earlyoom, ne\'ebé '
        'halo komputadór ho memória 2 to 4 GB la\'o di\'ak.',
    ]),
    ('img', 'settings-maintenance', 'Manutensaun ho Driver no firmware.'),
]),
('old-pc', 'Komputadór tuan, Wayland no Compiz', [
    ('h3', 'Komputadór tuan no neineik'),
    ('ul', [
        'Hili **Eduka-Low-Theme** (Aparénsia → Tema): la iha transparénsia no la iha efeitu.',
        'Uza **Openbox** hanesan jestór janela (Janela no área servisu → Janela) no husik kompozitór iha Automátiku.',
        'Liga zram no earlyoom (Manutensaun → Memória); husik Son moos mate iha komputadór ho memória 2 GB.',
        'Grava ekran ho "imajen 15 iha segundu ida" no "Arkivu ki\'ik".',
    ]),
    ('h3', 'Wayland'),
    ('p', 'Sesaun baibain iha eskola mak X11. Sesaun Wayland LXQt nian ba teste: Eduka-Desktop no Eduka-Panel la\'o iha ne\'ebá liuhosi '
          'XWayland, no Eduka-Settings mós hakerek konfigurasaun touchpad, mouse, tekladu, fokus, klik klaran no área servisu iha '
          'kompozitór Wayland (labwc ka KWin). Kantu ativu no Taka ho forsa automátiku la\'o de\'it iha X11.'),
    ('h3', 'Compiz'),
    ('p', 'Compiz aumenta efeitu 3D (janela nakdoko, kubu, [[Super+W]] hatudu janela hotu iha sorin-sorin). Nia instala ketak '
          '("Instala Compiz (efeitu 3D)…" iha pájina Janela) no presiza gráfiku 3D loloos. Se Compiz labele hahú, xfwm4 ka Openbox foti '
          'rasik nia fatin, nune\'e janela sira sempre iha rohan.'),
]),
('help', 'Problema no ajuda', [
    ('table', ['Problema', 'Saida mak atu halo'], [
        ['La iha son', 'Son → hili saída ne\'ebé loos no hanehan "Teste rua"; Kualidade no hadi\'a → "Haree ha\'u-nia son".'],
        ['Son kraak', 'Kualidade no hadi\'a → "Buffer son boot liu" no "Kartaun son hela moris", depois "Aplika no hahú fali son".'],
        ['Projetór la iha son', 'Hili saída HDMI ka perfíl HDMI kartaun nian.'],
        ['Wi-Fi la la\'o', 'Manutensaun → Driver no firmware: instala firmware ne\'ebé hakerek iha ne\'ebá, depois hahú fali.'],
        ['Programa ida para', 'Hein, ka [[Ctrl+Alt+Esc]] → Taka ho forsa.'],
        ['Menu ka panel la hanesan loos', 'Manutensaun → Karrega fali Eduka-Desktop / Hahú fali Eduka-Panel.'],
        ['Buat hotu ki\'ik liu ka boot liu', 'Ekran → Eskala, depois sai no tama fali.'],
        ['Komputadór neineik', 'Eduka-Low-Theme, Openbox, zram no earlyoom (kapítulu "Komputadór tuan").'],
        ['Haluha liafuan-xave', 'Administradór muda nia iha Utilizadór sira; ho tama impresaun dijitál ita bele tau liafuan-xave foun hafoin tama ho liman-fuan.'],
    ]),
    ('p', 'Kona-ba Edukasaun Desktop (menu → Kona-ba, ka Manutensaun → Kona-ba) hatudu versaun no kréditu projetu sira ne\'ebé Edukasaun '
          'Desktop uza. Sítiu web: www.edukasaunos.tl.'),
    ('img', 'about', 'Kona-ba Edukasaun Desktop.', 'half'),
]),
]
